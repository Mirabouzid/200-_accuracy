"""
Configuration centralisée pour BlockStat Backend
Optimisé pour contrainte <30s
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration de l'application"""
    
    # API Keys
    ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY", "")
    BITQUERY_ACCESS_TOKEN = os.getenv("BITQUERY_ACCESS_TOKEN", "")  # Access Token (pas API Key)
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")  # Pour récupérer les transactions
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Performance Limits (pour respecter <30s)
    MAX_HOLDERS = int(os.getenv("MAX_HOLDERS", 50))  # Top 50 seulement (pour output)
    # Support both MAX_TRANSACTIONS_TO_FETCH and legacy MAX_TRANSACTIONS from .env
    MAX_TRANSACTIONS_TO_FETCH = int(os.getenv("MAX_TRANSACTIONS_TO_FETCH", os.getenv("MAX_TRANSACTIONS", 10000)))  # 10k transactions selon hackathon
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 25))  # Fail-fast à 25s
    # Concurrence et Rate Limit (nouveaux paramètres)
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 8))
    REQUESTS_PER_SECOND = int(os.getenv("REQUESTS_PER_SECOND", 4))
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 10))
    # Cache in-memory (TTL et taille)
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 300))  # 5 minutes
    MAX_CACHE_ITEMS = int(os.getenv("MAX_CACHE_ITEMS", 100))
    
    # Etherscan API
    ETHERSCAN_API_URL = "https://api.etherscan.io/v2/api"
    
    # Alchemy API Endpoints
    ALCHEMY_BASE_URL = "https://eth-mainnet.g.alchemy.com/v2"
    
    # BitQuery API
    BITQUERY_ENDPOINT = "https://graphql.bitquery.io"
    
    # Graph Database Storage (Optional - for local visualization)
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")
    
    MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
    MEMGRAPH_USER = os.getenv("MEMGRAPH_USER", "")
    MEMGRAPH_PASSWORD = os.getenv("MEMGRAPH_PASSWORD", "")
    
    # Known Mixer Addresses (Tornado Cash, etc.)
    KNOWN_MIXERS = {
        "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc",  # Tornado Cash 0.1 ETH
        "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936",  # Tornado Cash 1 ETH
        "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf",  # Tornado Cash 10 ETH
        "0xa160cdab225685da1d56aa342ad8841c3b53f291",  # Tornado Cash 100 ETH
    }
    
    # Protocol Whitelist (adresses connues de DEX routers, staking, bridges, trésoreries)
    PROTOCOL_WHITELIST = {
        # Uniswap V2 Router
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
        # Uniswap V3 Router
        "0xe592427a0aece92de3edee1f18e0157c05861564",
        # Uniswap Universal Router
        "0xef1c6e67703c7bd7107f31af8ee2b014445c8c73",
        # SushiSwap Router
        "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",
        # 1inch Router v5
        "0x1111111254fb6c44bac0bed2854e76f90643097d",
        # ParaSwap Augustus
        "0xdef171fe48cf0115b1d80b88dc8eab59176fee57",
        # Uniswap Permit2
        "0x000000000022d473030f116ddee9f6b43ac78ba3",
        # Balancer V2 Vault
        "0xba12222222228d8ba445958a75a0704d566bf2c8",
        # Exchange / CEX deposit (reconnus, atténuer faux positifs)
        "0x28c6c06298d514db089934071355e0e4dc0bff89",  # Binance 14
        "0x21a31ee1afc51d94c2efccaa2092ab7cbf6fd64",  # Binance 8
        "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be",  # Binance (hot wallet)
        "0x503828976d22510aad0201ac7ec88293211d23da",  # Coinbase (hot wallet)
    }
    
    # Wash trading heuristics
    WASH_TRADE_BURST_WINDOW_SECONDS = int(os.getenv("WASH_TRADE_BURST_WINDOW_SECONDS", 2 * 60 * 60))  # 2h par défaut
    WASH_TRADE_VOLUME_NORMALIZER = float(os.getenv("WASH_TRADE_VOLUME_NORMALIZER", 100000.0))  # normalisation volume
    
    # Risk Score Weights
    RISK_WEIGHTS = {
        "gini": 0.3,           # Centralisation
        "mixer": 0.25,          # Connexions mixers
        "wash_trade": 0.25,     # Wash trading
        "cluster": 0.2,         # Clusters suspects
    }
    
    @classmethod
    def validate(cls):
        """Valide que les clés API sont configurées"""
        # Etherscan est optionnel mais recommandé pour récupérer les transactions
        if not cls.ALCHEMY_API_KEY and not cls.BITQUERY_ACCESS_TOKEN and not cls.ETHERSCAN_API_KEY:
            raise ValueError(
                "Au moins une clé API doit être configurée (ALCHEMY_API_KEY, BITQUERY_ACCESS_TOKEN, ou ETHERSCAN_API_KEY)"
            )
        return True

