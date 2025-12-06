"""
Tests basiques pour le Graph Analyzer
"""
import networkx as nx
from src.analyzer import GraphAnalyzer


def test_empty_graph():
    """Test avec graphe vide"""
    graph = nx.DiGraph()
    analyzer = GraphAnalyzer(graph)
    results = analyzer.analyze()
    
    assert results["metrics"]["gini"] == 0.0
    assert len(results["top_holders"]) == 0


def test_simple_graph():
    """Test avec graphe simple"""
    graph = nx.DiGraph()
    
    # Ajouter quelques nodes
    graph.add_node("0x1", balance=1000)
    graph.add_node("0x2", balance=500)
    graph.add_node("0x3", balance=200)
    
    # Ajouter quelques edges
    graph.add_edge("0x1", "0x2", weight=100, count=1)
    graph.add_edge("0x2", "0x3", weight=50, count=1)
    
    analyzer = GraphAnalyzer(graph)
    results = analyzer.analyze()
    
    assert results["metrics"]["gini"] >= 0.0
    assert len(results["top_holders"]) > 0


if __name__ == "__main__":
    test_empty_graph()
    test_simple_graph()
    print("✅ Tests passed")

