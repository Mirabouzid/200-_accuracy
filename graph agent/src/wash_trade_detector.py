"""
Wash Trade Detector Module
Détecte les transactions répétées entre mêmes paires (wash trading)
Amélioré: fenêtre temporelle (burst) et filtrage whitelist protocoles
"""
import networkx as nx
from typing import Dict, List
from config import Config


class WashTradeDetector:
    """
    Détecte les patterns de wash trading:
    - Transactions répétées entre mêmes paires
    - Volume élevé entre peu de wallets
    - Concentration temporelle (burst)
    - Filtrage des adresses de protocoles connus (DEX, staking, bridges)
    """
    
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
    
    def detect(self) -> List[Dict]:
        """
        Détecte les paires suspectes de wash trading
        """
        wash_trade_pairs = []
        whitelist = {addr.lower() for addr in getattr(Config, "PROTOCOL_WHITELIST", set())}
        burst_window = getattr(Config, "WASH_TRADE_BURST_WINDOW_SECONDS", 2 * 60 * 60)  # défaut: 2h
        
        # Parcourir toutes les edges
        for from_addr, to_addr, data in self.graph.edges(data=True):
            # Filtrer interactions protocolaires légitimes
            if from_addr.lower() in whitelist or to_addr.lower() in whitelist:
                continue
            
            count = data.get("count", 1)
            weight = data.get("weight", 0.0)
            min_ts = data.get("min_ts", 0) or 0
            max_ts = data.get("max_ts", 0) or 0
            window_seconds = max(0, (max_ts - min_ts))
            
            # Critères de suspicion:
            # 1. Nombre de transactions élevé entre mêmes paires
            # 2. Volume élevé
            # 3. Pattern bidirectionnel (A->B et B->A)
            # 4. Concentration temporelle (burst)
            
            is_suspicious = False
            suspicion_reasons = []
            
            # Critère 1: Plus de 5 transactions entre mêmes adresses
            if count >= 5:
                is_suspicious = True
                suspicion_reasons.append(f"{count} transactions répétées")
            
            # Critère 2: Pattern bidirectionnel avec volume ou fréquence
            is_bidirectional = False
            reverse_count = 0
            reverse_weight = 0.0
            if self.graph.has_edge(to_addr, from_addr):
                reverse_data = self.graph[to_addr][from_addr]
                reverse_count = reverse_data.get("count", 0)
                reverse_weight = reverse_data.get("weight", 0.0)
                if reverse_count >= 3 and count >= 3:
                    is_suspicious = True
                    is_bidirectional = True
                    suspicion_reasons.append("Pattern bidirectionnel suspect")
            
            # Critère 4: Burst temporel (ex: >=3 tx dans une fenêtre courte)
            if count >= 3 and window_seconds > 0 and window_seconds <= burst_window:
                is_suspicious = True
                # Décrire la fenêtre en minutes/heures
                minutes = max(1, int(window_seconds / 60))
                if minutes < 120:
                    suspicion_reasons.append(f"Burst temporel: {count} tx en {minutes} min")
                else:
                    hours = round(window_seconds / 3600, 1)
                    suspicion_reasons.append(f"Burst temporel: {count} tx en {hours} h")
            
            if is_suspicious:
                avg_value = float(weight) / max(count, 1)
                wash_trade_pairs.append({
                    "from": from_addr,
                    "to": to_addr,
                    "transaction_count": count,
                    "total_volume": float(weight),
                    "avg_value": avg_value,
                    "window_seconds": window_seconds,
                    "is_bidirectional": is_bidirectional,
                    "reverse_count": reverse_count,
                    "reverse_total_volume": float(reverse_weight),
                    "suspicion_reasons": suspicion_reasons,
                    "risk_level": "high" if (count >= 10 or (count >= 5 and window_seconds <= burst_window)) else "medium"
                })
        
        return wash_trade_pairs

