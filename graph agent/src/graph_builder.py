"""
Graph Builder Module
Construit le graphe NetworkX à partir des données blockchain
Optimisé pour vitesse (<30s constraint)
"""
import networkx as nx
from typing import Dict, List, Optional
from config import Config


class GraphBuilder:
    """
    Construit un graphe NetworkX représentant les relations entre wallets
    Nodes = Wallets
    Edges = Transactions (avec poids = montant)
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph (transactions ont une direction)
    
    def build_graph(self, token_data: Dict) -> nx.DiGraph:
        """
        Construit le graphe à partir des données token
        Selon hackathon: tous les wallets impliqués dans les 10k transactions
        """
        self.graph.clear()
        
        # Récupérer tous les wallets impliqués (pas seulement top 50)
        all_wallets = token_data.get("all_wallets", [])
        top_holders_dict = {h.get("address", ""): h for h in token_data.get("top_holders", [])}
        
        # Ajouter TOUS les nodes (wallets impliqués dans les transactions)
        for wallet_addr in all_wallets:
            holder_data = top_holders_dict.get(wallet_addr, {})
            self.graph.add_node(
                wallet_addr,
                balance=holder_data.get("balance", 0),
                transaction_count=holder_data.get("transaction_count", 0),
                is_top_holder=wallet_addr in top_holders_dict
            )
        
        # Ajouter les edges (transactions)
        transactions = token_data.get("transactions", [])
        for tx in transactions:
            from_addr = tx.get("from", "").lower()
            to_addr = tx.get("to", "").lower()
            value = tx.get("value", 0)
            ts = tx.get("timestamp", 0) or 0
            
            # S'assurer que les nodes existent
            if from_addr and to_addr:
                if from_addr not in self.graph:
                    self.graph.add_node(from_addr, balance=0, transaction_count=0, is_top_holder=False)
                if to_addr not in self.graph:
                    self.graph.add_node(to_addr, balance=0, transaction_count=0, is_top_holder=False)
                
                # Ajouter ou mettre à jour l'edge
                if self.graph.has_edge(from_addr, to_addr):
                    self.graph[from_addr][to_addr]["weight"] += value
                    self.graph[from_addr][to_addr]["count"] += 1
                    # Mise à jour des timestamps agrégés
                    prev_min = self.graph[from_addr][to_addr].get("min_ts", ts)
                    prev_max = self.graph[from_addr][to_addr].get("max_ts", ts)
                    self.graph[from_addr][to_addr]["min_ts"] = min(prev_min, ts)
                    self.graph[from_addr][to_addr]["max_ts"] = max(prev_max, ts)
                else:
                    self.graph.add_edge(
                        from_addr,
                        to_addr,
                        weight=value,
                        count=1,
                        tx_hash=tx.get("hash", ""),
                        # Timestamps agrégés pour détection burst/net-flow
                        min_ts=ts,
                        max_ts=ts
                    )
        
        return self.graph
    
    def format_for_react_force_graph(
        self, 
        graph: nx.DiGraph, 
        analysis_results: Dict
    ) -> Dict:
        """
        Formate le graphe pour React Force Graph
        Format attendu:
        {
          "nodes": [{"id": "...", "group": 1, ...}],
          "links": [{"source": "...", "target": "...", "value": 100, ...}]
        }
        """
        # Mapper les communautés (clusters) pour le group
        community_map = {}
        for cluster in analysis_results.get("suspicious_clusters", []):
            cluster_id = cluster.get("cluster_id", 0)
            for wallet in cluster.get("wallets", []):
                community_map[wallet] = cluster_id
        
        # Mapper les mixer flags
        mixer_flags = {}
        for flag in analysis_results.get("mixer_flags", []):
            mixer_flags[flag.get("address", "")] = flag.get("is_mixer", False)
        
        # Mapper PageRank
        pagerank = analysis_results.get("metrics", {}).get("pagerank", {})
        
        # Construire les nodes
        nodes = []
        for node_id in graph.nodes():
            node_data = {
                "id": node_id,
                "group": community_map.get(node_id, 0),
                "pagerank": round(pagerank.get(node_id, 0), 4),
                "is_mixer": mixer_flags.get(node_id, False),
                "balance": graph.nodes[node_id].get("balance", 0)
            }
            nodes.append(node_data)
        
        # Construire les links
        links = []
        wash_trade_pairs = {
            (wt.get("from", ""), wt.get("to", "")) 
            for wt in analysis_results.get("wash_trade_pairs", [])
        }
        
        for from_addr, to_addr, data in graph.edges(data=True):
            link_data = {
                "source": from_addr,
                "target": to_addr,
                "value": data.get("weight", 0),
                "count": data.get("count", 1),
                "is_wash_trade": (from_addr, to_addr) in wash_trade_pairs
            }
            links.append(link_data)
        
        return {
            "nodes": nodes,
            "links": links
        }
    
    def get_graph_stats(self) -> Dict:
        """Retourne des statistiques sur le graphe"""
        return {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "is_connected": nx.is_weakly_connected(self.graph) if self.graph.number_of_nodes() > 0 else False,
            "density": nx.density(self.graph)
        }

