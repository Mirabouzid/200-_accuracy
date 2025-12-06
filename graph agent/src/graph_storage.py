"""
Graph Storage Module
Optionnel: Sauvegarde le graphe dans Neo4j ou Memgraph pour visualisation locale
"""
from typing import Dict, Optional
import networkx as nx
from config import Config


class GraphStorage:
    """
    Sauvegarde le graphe dans une base de données graphe (Neo4j ou Memgraph)
    Optionnel - seulement si l'utilisateur le demande
    """
    
    def __init__(self, storage_type: str = "neo4j"):
        """
        Args:
            storage_type: "neo4j" ou "memgraph"
        """
        self.storage_type = storage_type.lower()
        self.driver = None
        
    def save_graph(
        self, 
        graph: nx.DiGraph, 
        token_address: str,
        analysis_results: Dict
    ) -> Dict:
        """
        Sauvegarde le graphe dans la base de données
        
        Returns:
            Dict avec stats de sauvegarde
        """
        if self.storage_type == "neo4j":
            return self._save_to_neo4j(graph, token_address, analysis_results)
        elif self.storage_type == "memgraph":
            return self._save_to_memgraph(graph, token_address, analysis_results)
        else:
            raise ValueError(f"Storage type {self.storage_type} not supported. Use 'neo4j' or 'memgraph'")
    
    def _save_to_neo4j(
        self, 
        graph: nx.DiGraph, 
        token_address: str,
        analysis_results: Dict
    ) -> Dict:
        """Sauvegarde dans Neo4j"""
        try:
            from neo4j import GraphDatabase
            
            # Configuration Neo4j depuis .env ou defaults
            neo4j_uri = Config.NEO4J_URI if hasattr(Config, 'NEO4J_URI') else "bolt://localhost:7687"
            neo4j_user = Config.NEO4J_USER if hasattr(Config, 'NEO4J_USER') else "neo4j"
            neo4j_password = Config.NEO4J_PASSWORD if hasattr(Config, 'NEO4J_PASSWORD') else "neo4j"
            
            print(f"  💾 Connecting to Neo4j at {neo4j_uri}...")
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            driver.verify_connectivity()
            
            with driver.session() as session:
                # Créer constraints
                try:
                    session.run("""
                        CREATE CONSTRAINT wallet_address IF NOT EXISTS 
                        FOR (w:Wallet) REQUIRE w.address IS UNIQUE
                    """)
                    session.run("""
                        CREATE CONSTRAINT token_address IF NOT EXISTS 
                        FOR (t:Token) REQUIRE t.address IS UNIQUE
                    """)
                except:
                    pass  # Constraints may already exist
                
                # Créer node Token
                session.run("""
                    MERGE (t:Token {address: $address})
                    ON CREATE SET t.created_at = timestamp()
                """, address=token_address.lower())
                
                # Mapper PageRank et autres métriques
                pagerank = analysis_results.get("metrics", {}).get("pagerank", {})
                mixer_flags = {f["address"]: f["is_mixer"] for f in analysis_results.get("mixer_flags", [])}
                
                # Batch insert nodes et edges
                batch_size = 500
                nodes_list = list(graph.nodes(data=True))
                edges_list = list(graph.edges(data=True))
                
                nodes_created = 0
                relationships_created = 0
                
                # Insert nodes
                for i in range(0, len(nodes_list), batch_size):
                    batch = nodes_list[i:i + batch_size]
                    
                    cypher = """
                    UNWIND $nodes AS node
                    MERGE (w:Wallet {address: toLower(node.address)})
                    ON CREATE SET 
                        w.balance = node.balance,
                        w.transaction_count = node.transaction_count,
                        w.is_top_holder = node.is_top_holder,
                        w.pagerank = node.pagerank,
                        w.is_mixer = node.is_mixer
                    ON MATCH SET
                        w.balance = node.balance,
                        w.transaction_count = node.transaction_count,
                        w.pagerank = node.pagerank,
                        w.is_mixer = node.is_mixer
                    RETURN count(w) as count
                    """
                    
                    nodes_data = []
                    for node_id, data in batch:
                        nodes_data.append({
                            "address": str(node_id),
                            "balance": float(data.get("balance", 0)),
                            "transaction_count": int(data.get("transaction_count", 0)),
                            "is_top_holder": bool(data.get("is_top_holder", False)),
                            "pagerank": float(pagerank.get(node_id, 0)),
                            "is_mixer": bool(mixer_flags.get(node_id, False))
                        })
                    
                    result = session.run(cypher, nodes=nodes_data)
                    nodes_created += result.single()["count"]
                
                # Insert edges
                for i in range(0, len(edges_list), batch_size):
                    batch = edges_list[i:i + batch_size]
                    
                    cypher = """
                    UNWIND $edges AS edge
                    MATCH (from:Wallet {address: toLower(edge.from)})
                    MATCH (to:Wallet {address: toLower(edge.to)})
                    CREATE (from)-[t:TRANSFERRED {
                        txHash: edge.tx_hash,
                        value: edge.weight,
                        count: edge.count,
                        tokenAddress: edge.token_address,
                        chain: edge.chain,
                        timestamp: timestamp()
                    }]->(to)
                    RETURN count(t) as count
                    """
                    
                    edges_data = []
                    for from_addr, to_addr, data in batch:
                        edges_data.append({
                            "from": str(from_addr),
                            "to": str(to_addr),
                            "tx_hash": str(data.get("tx_hash", "")),
                            "weight": float(data.get("weight", 0)),
                            "count": int(data.get("count", 1)),
                            "token_address": token_address.lower(),
                            "chain": str(analysis_results.get("metrics", {}).get("chain", "ethereum"))
                        })
                    
                    result = session.run(cypher, edges=edges_data)
                    relationships_created += result.consume().counters.relationships_created
                
                # Lier Token aux wallets
                session.run("""
                    MATCH (t:Token {address: $token_address})
                    MATCH (w:Wallet)
                    WHERE w.is_top_holder = true
                    MERGE (w)-[:HOLDS]->(t)
                """, token_address=token_address.lower())
                
                # Stats finales
                stats = session.run("""
                    MATCH (w:Wallet)
                    WITH count(w) as wallet_count
                    MATCH ()-[t:TRANSFERRED]->()
                    RETURN wallet_count, count(t) as transfer_count
                """).single()
                
                driver.close()
                
                return {
                    "success": True,
                    "storage_type": "neo4j",
                    "nodes_created": nodes_created,
                    "relationships_created": relationships_created,
                    "total_wallets": stats["wallet_count"],
                    "total_transfers": stats["transfer_count"],
                    "uri": neo4j_uri
                }
                
        except ImportError:
            return {
                "success": False,
                "error": "Neo4j driver not installed. Run: pip install neo4j"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_to_memgraph(
        self, 
        graph: nx.DiGraph, 
        token_address: str,
        analysis_results: Dict
    ) -> Dict:
        """Sauvegarde dans Memgraph (compatible Cypher comme Neo4j mais plus rapide)"""
        try:
            from neo4j import GraphDatabase  # Memgraph utilise le même driver Neo4j
            
            # Memgraph utilise le même protocole Bolt que Neo4j
            memgraph_uri = Config.MEMGRAPH_URI if hasattr(Config, 'MEMGRAPH_URI') else "bolt://localhost:7687"
            memgraph_user = Config.MEMGRAPH_USER if hasattr(Config, 'MEMGRAPH_USER') else ""
            memgraph_password = Config.MEMGRAPH_PASSWORD if hasattr(Config, 'MEMGRAPH_PASSWORD') else ""
            
            print(f"  💾 Connecting to Memgraph at {memgraph_uri}...")
            # Use no-auth when credentials are blank (default Memgraph setup)
            if (memgraph_user or memgraph_password):
                driver = GraphDatabase.driver(memgraph_uri, auth=(memgraph_user, memgraph_password))
            else:
                driver = GraphDatabase.driver(memgraph_uri)
            driver.verify_connectivity()
            
            # Memgraph utilise le même Cypher que Neo4j, donc même code
            # Mais généralement plus rapide pour les insertions
            with driver.session() as session:
                # Créer constraints (Memgraph supporte aussi)
                try:
                    session.run("""
                        CREATE CONSTRAINT ON (w:Wallet) ASSERT w.address IS UNIQUE
                    """)
                    session.run("""
                        CREATE CONSTRAINT ON (t:Token) ASSERT t.address IS UNIQUE
                    """)
                except:
                    pass
                
                # Même logique que Neo4j
                pagerank = analysis_results.get("metrics", {}).get("pagerank", {})
                mixer_flags = {f["address"]: f["is_mixer"] for f in analysis_results.get("mixer_flags", [])}
                
                # Token node
                session.run("""
                    MERGE (t:Token {address: $address})
                    ON CREATE SET t.created_at = timestamp()
                """, address=token_address.lower())
                
                # Nodes (batch pour performance)
                nodes_list = list(graph.nodes(data=True))
                batch_size = 100
                for i in range(0, len(nodes_list), batch_size):
                    batch = nodes_list[i:i + batch_size]
                    for node_id, data in batch:
                        session.run("""
                            MERGE (w:Wallet {address: toLower($address)})
                            ON CREATE SET 
                                w.balance = $balance,
                                w.transaction_count = $tx_count,
                                w.is_top_holder = $is_top,
                                w.pagerank = $pagerank,
                                w.is_mixer = $is_mixer
                            ON MATCH SET
                                w.balance = $balance,
                                w.pagerank = $pagerank,
                                w.is_mixer = $is_mixer
                        """, 
                            address=str(node_id),
                            balance=float(data.get("balance", 0)),
                            tx_count=int(data.get("transaction_count", 0)),
                            is_top=bool(data.get("is_top_holder", False)),
                            pagerank=float(pagerank.get(node_id, 0)),
                            is_mixer=bool(mixer_flags.get(node_id, False))
                        )
                
                # Edges (batch pour performance)
                edges_list = list(graph.edges(data=True))
                batch_size = 100
                for i in range(0, len(edges_list), batch_size):
                    batch = edges_list[i:i + batch_size]
                    for from_addr, to_addr, data in batch:
                        session.run("""
                            MATCH (from:Wallet {address: toLower($from_addr)})
                            MATCH (to:Wallet {address: toLower($to_addr)})
                            CREATE (from)-[t:TRANSFERRED {
                                txHash: $tx_hash,
                                value: $weight,
                                count: $count,
                                tokenAddress: $token_address,
                                chain: $chain,
                                timestamp: timestamp()
                            }]->(to)
                        """,
                            from_addr=str(from_addr),
                            to_addr=str(to_addr),
                            tx_hash=str(data.get("tx_hash", "")),
                            weight=float(data.get("weight", 0)),
                            count=int(data.get("count", 1)),
                            token_address=token_address.lower(),
                            chain=str(analysis_results.get("metrics", {}).get("chain", "ethereum"))
                        )
                
                # Link Token
                session.run("""
                    MATCH (t:Token {address: $token_address})
                    MATCH (w:Wallet)
                    WHERE w.is_top_holder = true
                    MERGE (w)-[:HOLDS]->(t)
                """, token_address=token_address.lower())
                
                # Stats
                stats = session.run("""
                    MATCH (w:Wallet)
                    WITH count(w) as wallet_count
                    MATCH ()-[t:TRANSFERRED]->()
                    RETURN wallet_count, count(t) as transfer_count
                """).single()
                
                driver.close()
                
                return {
                    "success": True,
                    "storage_type": "memgraph",
                    "total_wallets": stats["wallet_count"],
                    "total_transfers": stats["transfer_count"],
                    "uri": memgraph_uri
                }
                
        except ImportError:
            return {
                "success": False,
                "error": "Neo4j driver not installed. Run: pip install neo4j"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

