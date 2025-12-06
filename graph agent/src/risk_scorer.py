"""
Risk Scorer Module
Calcule le score de risque global basé sur plusieurs facteurs
"""
from typing import Dict, List
from config import Config


class RiskScorer:
    """
    Calcule un score de risque de 0.0 à 1.0
    Basé sur: Gini, Mixers, Wash Trading, Clusters
    """
    
    def __init__(self):
        self.weights = Config.RISK_WEIGHTS
    
    def calculate_risk_score(
        self, 
        analysis_results: Dict, 
        token_data: Dict
    ) -> float:
        """
        Calcule le score de risque global
        """
        metrics = analysis_results.get("metrics", {})
        reasoning: List[str] = []
        
        # 1. Score Gini (centralisation) — NE PAS modifier le calcul
        gini = metrics.get("gini", 0.0)
        gini_score = min(gini, 1.0)  # Normaliser à [0, 1]
        reasoning.append(f"Centralisation (Gini): {gini:.3f}")
        # Flag explicit if dangerously centralized per hackathon phrasing
        if gini > 0.9:
            reasoning.append("Dangerously centralized (Gini > 0.9)")
        
        # 2. Score Mixer (connexions aux mixers)
        mixer_flags = analysis_results.get("mixer_flags", [])
        mixer_score = self._calculate_mixer_score(mixer_flags)
        if mixer_score > 0:
            mixer_count = sum(1 for flag in mixer_flags if flag.get("is_mixer", False))
            reasoning.append(f"Connexions aux mixers: {mixer_count} adresses liées")
        
        # 3. Score Wash Trading (pondération par volume + normalisation diversité)
        wash_trade_pairs = analysis_results.get("wash_trade_pairs", [])
        wash_trade_score, wash_context = self._calculate_wash_trade_score(wash_trade_pairs, token_data)
        if wash_trade_score > 0:
            reasoning.append(wash_context)
        
        # 4. Score Clusters suspects
        suspicious_clusters = analysis_results.get("suspicious_clusters", [])
        cluster_score = self._calculate_cluster_score(suspicious_clusters)
        if cluster_score > 0:
            total_suspicious_wallets = sum(cluster.get("size", 0) for cluster in suspicious_clusters)
            reasoning.append(f"Clusters suspects: {total_suspicious_wallets} wallets impliqués")
        
        # Score final pondéré
        risk_score = (
            self.weights["gini"] * gini_score +
            self.weights["mixer"] * mixer_score +
            self.weights["wash_trade"] * wash_trade_score +
            self.weights["cluster"] * cluster_score
        )
        
        # Mettre à jour les mixer flags et enrichir metrics
        analysis_results["mixer_flags"] = mixer_flags
        metrics["risk_components"] = {
            "gini": gini_score,
            "mixer": mixer_score,
            "wash_trade": wash_trade_score,
            "cluster": cluster_score
        }
        metrics["reasoning"] = reasoning
        metrics["confidence"], metrics["dataQuality"] = self._compute_confidence(token_data)
        analysis_results["metrics"] = metrics
        
        return min(risk_score, 1.0)  # Cap à 1.0
    
    def _calculate_mixer_score(self, mixer_flags: List[Dict]) -> float:
        """Score basé sur le nombre de connexions aux mixers"""
        if not mixer_flags:
            return 0.0
        
        mixer_count = sum(1 for flag in mixer_flags if flag.get("is_mixer", False))
        total_addresses = len(mixer_flags)
        
        if total_addresses == 0:
            return 0.0
        
        # Score proportionnel au nombre de mixers
        return min(mixer_count / max(total_addresses, 1), 1.0)
    
    def _calculate_wash_trade_score(self, wash_trade_pairs: List[Dict], token_data: Dict) -> (float, str):
        """Score pondéré par volume et burst pour wash trading, avec normalisation dynamique.
        Retourne (score, contexte_raisonnement).
        """
        if not wash_trade_pairs:
            return 0.0, ""
        
        # Comptages et volumes suspects
        pair_count = len(wash_trade_pairs)
        total_suspicious_volume = sum(float(p.get("total_volume", 0.0)) for p in wash_trade_pairs)
        high_burst_pairs = sum(1 for p in wash_trade_pairs if p.get("window_seconds", 0) > 0 and p.get("transaction_count", 0) >= 5)
        
        # Contexte global du token pour normalisation
        txs = token_data.get("transactions", []) or []
        total_transferred_volume = sum(float(t.get("value", 0.0)) for t in txs)
        wallet_count = len(token_data.get("all_wallets", []) or [])
        
        # Normalisation du volume: ratio du volume suspect / volume total (ou fallback sur Config)
        normalizer = total_transferred_volume if total_transferred_volume > 0 else max(Config.__dict__.get("WASH_TRADE_VOLUME_NORMALIZER", 100000.0), 1.0)
        volume_component = min(total_suspicious_volume / normalizer, 1.0)
        
        # Normalisation du compte de paires par diversité (plus il y a de wallets, plus le seuil augmente)
        denom_pairs = max(10.0, wallet_count / 50.0)  # ex: 5000 wallets -> denom ≈ 100
        count_component = min(pair_count / denom_pairs, 1.0)
        
        # Bonus limité pour bursts prononcés
        burst_bonus = min(high_burst_pairs / 10.0, 0.3)
        raw_score = min(0.3 * count_component + 0.7 * volume_component + burst_bonus, 1.0)
        
        # Atténuation pour tokens très distribués (évite faux positifs sur large-cap)
        if wallet_count >= 5000:
            diversity_scale = 0.5
        elif wallet_count >= 2000:
            diversity_scale = 0.7
        elif wallet_count >= 1000:
            diversity_scale = 0.85
        else:
            diversity_scale = 1.0
        score = min(raw_score * diversity_scale, 1.0)
        
        # Contexte explicatif
        context = (
            f"Wash trading: {pair_count} paires suspectes, volume susp. ≈ {int(total_suspicious_volume)}" +
            (f" sur {int(total_transferred_volume)} total" if total_transferred_volume > 0 else "") +
            (f", {high_burst_pairs} paires en burst" if high_burst_pairs else "") +
            (f", normalisation diversité (wallets={wallet_count})" if wallet_count else "")
        )
        return score, context
    
    def _calculate_cluster_score(self, suspicious_clusters: List[Dict]) -> float:
        """Score basé sur les clusters suspects"""
        if not suspicious_clusters:
            return 0.0
        
        # Compter les clusters à haut risque
        high_risk_clusters = sum(
            1 for cluster in suspicious_clusters 
            if cluster.get("risk_level") == "high"
        )
        
        # Score basé sur le nombre et la taille des clusters
        total_suspicious_wallets = sum(
            cluster.get("size", 0) for cluster in suspicious_clusters
        )
        
        # Normaliser: 20+ wallets suspects = score 1.0
        return min(total_suspicious_wallets / 20.0, 1.0)
    
    def _compute_confidence(self, token_data: Dict) -> (str, Dict):
        """Calcule niveau de confiance et qualité des données pour transparence."""
        txs = token_data.get("transactions", []) or []
        wallets = token_data.get("all_wallets", []) or []
        
        # Estimer période couverte si timestamps présents
        timestamps = [t.get("timestamp") for t in txs if t.get("timestamp")]
        time_span_days = 0
        if timestamps:
            try:
                time_span_days = max(0, (max(timestamps) - min(timestamps)) / 86400.0)
            except Exception:
                time_span_days = 0
        
        sufficient_data = (len(txs) >= 100 and time_span_days >= 7)
        if len(txs) >= 1000 and time_span_days >= 30:
            confidence = "high"
        elif len(txs) >= 100 and time_span_days >= 7:
            confidence = "medium"
        else:
            confidence = "low"
        
        data_quality = {
            "transactionCount": len(txs),
            "timeSpanDays": round(time_span_days, 1),
            "walletCount": len(wallets),
            "sufficientData": sufficient_data
        }
        return confidence, data_quality

