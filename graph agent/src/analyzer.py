"""
Graph Analyzer Module
Implémente les algorithmes d'analyse : Leiden, PageRank, Gini
Optimisé pour vitesse (<30s constraint)
"""
import networkx as nx
import numpy as np
from typing import Dict, List
from leidenalg import find_partition, ModularityVertexPartition
import igraph as ig
from config import Config


class GraphAnalyzer:
    """
    Analyse le graphe avec différents algorithmes
    """
    
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.results = {}
        self.community_algorithm_used = None
    
    def analyze(self, community_mode: str = "auto") -> Dict:
        """
        Lance toutes les analyses et retourne les résultats
        community_mode: "auto" | "leiden" | "louvain"
        """
        if self.graph.number_of_nodes() == 0:
            return self._empty_results()
        
        # 1. PageRank (rapide)
        pagerank = self._calculate_pagerank()
        
        # 2. Détection de communautés selon mode
        if community_mode == "leiden":
            communities = self._detect_communities_leiden()
            self.community_algorithm_used = "leiden"
        elif community_mode == "louvain":
            communities = self._detect_communities_louvain()
            self.community_algorithm_used = "louvain"
        else:
            # AUTO: Heuristique simple basée sur la taille du graphe
            n = self.graph.number_of_nodes()
            m = self.graph.number_of_edges()
            if n < 400 and m < 2000:
                communities = self._detect_communities_louvain()
                self.community_algorithm_used = "louvain"
            else:
                communities = self._detect_communities_leiden()
                self.community_algorithm_used = "leiden"
        
        # 3. Gini Coefficient (mesure centralisation)
        gini = self._calculate_gini()
        
        # 4. Identifier les clusters suspects
        suspicious_clusters = self._identify_suspicious_clusters(communities)
        
        # 5. Top holders avec leurs métriques
        top_holders = self._get_top_holders(pagerank)
        
        self.results = {
            "metrics": {
                "pagerank": pagerank,
                "gini": gini,
                "communities": communities,
                "community_algorithm": self.community_algorithm_used or community_mode
            },
            "suspicious_clusters": suspicious_clusters,
            "top_holders": top_holders,
            "mixer_flags": [],  # Sera rempli par RiskScorer
            "wash_trade_pairs": []  # Sera rempli par WashTradeDetector
        }
        
        return self.results
    
    def _calculate_pagerank(self) -> Dict[str, float]:
        """Calcule PageRank pour identifier les wallets influents"""
        try:
            # PageRank avec NetworkX (rapide)
            pagerank = nx.pagerank(self.graph, max_iter=50)  # Limiter itérations pour vitesse
            return pagerank
        except:
            return {}
    
    def _detect_communities_leiden(self) -> Dict[int, List[str]]:
        """
        Détecte les communautés avec Leiden Algorithm
        Plus rapide et meilleur que Louvain
        """
        if self.graph.number_of_nodes() < 2:
            return {}
        
        try:
            # Convertir NetworkX vers igraph (nécessaire pour leidenalg)
            # Utiliser seulement le graphe non-dirigé pour communauté
            undirected = self.graph.to_undirected()
            
            # Créer graphe igraph
            edges = list(undirected.edges())
            if not edges:
                return {}
            
            ig_graph = ig.Graph()
            ig_graph.add_vertices(list(undirected.nodes()))
            ig_graph.add_edges(edges)
            
            # Appliquer Leiden
            partition = find_partition(
                ig_graph,
                ModularityVertexPartition,
                n_iterations=5  # Limiter pour vitesse
            )
            
            # Formater les résultats
            communities = {}
            for i, community_id in enumerate(partition.membership):
                node_id = list(undirected.nodes())[i]
                if community_id not in communities:
                    communities[community_id] = []
                communities[community_id].append(node_id)
            
            return communities
            
        except Exception as e:
            print(f"  ⚠️ Leiden error: {e}, falling back to simple clustering")
            # Fallback: chaque node est sa propre communauté
            return {i: [node] for i, node in enumerate(self.graph.nodes())}
    
    def _detect_communities_louvain(self) -> Dict[int, List[str]]:
        """
        Détecte les communautés avec l'algorithme Louvain (via igraph community_multilevel)
        """
        if self.graph.number_of_nodes() < 2:
            return {}
        
        try:
            undirected = self.graph.to_undirected()
            edges = list(undirected.edges())
            if not edges:
                return {}
            
            ig_graph = ig.Graph()
            ig_graph.add_vertices(list(undirected.nodes()))
            ig_graph.add_edges(edges)
            
            # Appliquer Louvain via multilevel
            partition = ig_graph.community_multilevel()
            membership = partition.membership
            
            communities = {}
            for i, community_id in enumerate(membership):
                node_id = list(undirected.nodes())[i]
                if community_id not in communities:
                    communities[community_id] = []
                communities[community_id].append(node_id)
            
            return communities
        except Exception as e:
            print(f"  ⚠️ Louvain error: {e}, falling back to simple clustering")
            return {i: [node] for i, node in enumerate(self.graph.nodes())}
    
    def _calculate_gini(self) -> float:
        """
        Calcule le coefficient de Gini pour mesurer la centralisation
        Gini > 0.9 = token dangereusement centralisé
        """
        if self.graph.number_of_nodes() == 0:
            return 0.0
        
        # Utiliser les balances des holders
        balances = [
            self.graph.nodes[node].get("balance", 0) 
            for node in self.graph.nodes()
        ]
        
        if not balances or sum(balances) == 0:
            return 0.0
        
        # Calculer Gini
        balances = np.array(sorted(balances))
        n = len(balances)
        cumsum = np.cumsum(balances)
        
        # Formule Gini
        gini = (2 * np.sum((np.arange(1, n + 1)) * balances)) / (n * np.sum(balances)) - (n + 1) / n
        
        return float(gini)
    
    def _identify_suspicious_clusters(self, communities: Dict[int, List[str]]) -> List[Dict]:
        """
        Identifie les clusters suspects basés sur:
        - Taille du cluster (petits clusters fermés = suspect)
        - Densité interne élevée
        - Peu de connexions externes
        """
        suspicious = []
        
        for cluster_id, wallets in communities.items():
            if len(wallets) < 2:
                continue
            
            # Calculer densité interne
            subgraph = self.graph.subgraph(wallets)
            internal_edges = subgraph.number_of_edges()
            possible_edges = len(wallets) * (len(wallets) - 1)
            density = internal_edges / possible_edges if possible_edges > 0 else 0
            
            # Calculer connexions externes
            external_edges = 0
            for wallet in wallets:
                for neighbor in self.graph.successors(wallet):
                    if neighbor not in wallets:
                        external_edges += 1
                for neighbor in self.graph.predecessors(wallet):
                    if neighbor not in wallets:
                        external_edges += 1
            
            # Critères de suspicion
            is_suspicious = (
                density > 0.5 or  # Densité élevée
                (len(wallets) <= 10 and external_edges < len(wallets))  # Cluster fermé
            )
            
            if is_suspicious:
                suspicious.append({
                    "cluster_id": cluster_id,
                    "wallets": wallets,
                    "size": len(wallets),
                    "density": round(density, 3),
                    "external_connections": external_edges,
                    "risk_level": "high" if density > 0.7 else "medium"
                })
        
        return suspicious
    
    def _get_top_holders(self, pagerank: Dict[str, float]) -> List[Dict]:
        """Retourne les top holders avec leurs métriques"""
        holders = []
        
        for node in self.graph.nodes():
            holders.append({
                "address": node,
                "balance": self.graph.nodes[node].get("balance", 0),
                "pagerank": round(pagerank.get(node, 0), 4),
                "degree": self.graph.degree(node)
            })
        
        # Trier par PageRank
        holders.sort(key=lambda x: x["pagerank"], reverse=True)
        
        return holders[:Config.MAX_HOLDERS]
    
    def _empty_results(self) -> Dict:
        """Retourne des résultats vides si pas de données"""
        return {
            "metrics": {
                "pagerank": {},
                "gini": 0.0,
                "communities": {}
            },
            "suspicious_clusters": [],
            "top_holders": [],
            "mixer_flags": [],
            "wash_trade_pairs": []
        }

