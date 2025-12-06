"""
BlockStat - Forensic Graph Agent Backend
Optimized for <30s response time (Hackathon MVP)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from typing import Optional, Dict, List
import uvicorn

import os
os.environ.setdefault("NX_CUGRAPH_AUTOCONFIG", "True")

from config import Config
from src.data_fetcher import DataFetcher
from src.graph_builder import GraphBuilder
from src.analyzer import GraphAnalyzer
from src.risk_scorer import RiskScorer
from src.wash_trade_detector import WashTradeDetector
from src.utils import check_mixer_flags
from src.agents.chat_agent import get_chat_agent, extract_cypher, run_cypher

# Valider la configuration au démarrage
Config.validate()

app = FastAPI(
    title="BlockStat Forensic Graph Agent",
    version="1.0.0",
    description="Backend pour analyse de tokens blockchain avec détection de fraude (<30s)"
)

# CORS pour permettre le frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier le domaine du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenAnalysisRequest(BaseModel):
    token_address: str
    chain: Optional[str] = "ethereum"  # ethereum, polygon, bsc, etc.
    api_provider: Optional[str] = "auto"  # auto, bitquery, etherscan, alchemy
    max_transactions: Optional[int] = None  # Override MAX_TRANSACTIONS_TO_FETCH
    timeout_seconds: Optional[int] = None  # Override TIMEOUT_SECONDS (None = disabled)
    community_mode: Optional[str] = "auto"  # "auto" | "leiden" | "louvain"

class TokenAnalysisResponse(BaseModel):
    token_address: str
    analysis_time_seconds: float
    risk_score: float
    top_holders: List[Dict]
    suspicious_clusters: List[Dict]
    mixer_flags: List[Dict]
    wash_trade_pairs: List[Dict]
    graph_data: Dict  # Format pour React Force Graph
    metrics: Dict  # PageRank, Gini, etc.


@app.get("/")
async def root():
    return {
        "message": "BlockStat Forensic Graph Agent API",
        "version": "1.0.0",
        "max_response_time": "30s",
        "status": "ready"
    }


@app.post("/analyze", response_model=TokenAnalysisResponse)
async def analyze_token(request: TokenAnalysisRequest):
    """
    Endpoint principal : analyse un token et retourne le graphe + flags suspects
    CONTRAINTE CRITIQUE : < 30 secondes
    """
    start_time = time.time()
    
    # Override config avec valeurs de la requête si fournies
    max_transactions = request.max_transactions if request.max_transactions else Config.MAX_TRANSACTIONS_TO_FETCH
    timeout_seconds = request.timeout_seconds if request.timeout_seconds is not None else Config.TIMEOUT_SECONDS
    timeout_enabled = request.timeout_seconds is not None
    
    try:
        # Vérification timeout avant de commencer (seulement si activé)
        if timeout_enabled and time.time() - start_time > timeout_seconds:
            raise HTTPException(
                status_code=408,
                detail=f"Timeout avant même de commencer l'analyse"
            )
        
        # 1. FETCH DATA (optimisé : seulement top holders + transactions clés)
        print(f"[{time.time() - start_time:.2f}s] 📥 Fetching data for {request.token_address}")
        print(f"  🔧 API Provider: {request.api_provider}")
        print(f"  📊 Max Transactions: {max_transactions}")
        print(f"  ⏱️ Timeout: {'Enabled (' + str(timeout_seconds) + 's)' if timeout_enabled else 'Disabled'}")
        
        # Override temporairement la config pour cette requête
        original_max = Config.MAX_TRANSACTIONS_TO_FETCH
        Config.MAX_TRANSACTIONS_TO_FETCH = max_transactions
        
        fetcher = DataFetcher(chain=request.chain, preferred_provider=request.api_provider)
        token_data = await fetcher.fetch_token_data(request.token_address)
        # Inject provider used into metrics for frontend visibility
        if "metrics" not in token_data:
            token_data["metrics"] = {}
        token_data["metrics"]["provider_used"] = fetcher.last_provider_used or request.api_provider
        
        # Restaurer la config originale
        Config.MAX_TRANSACTIONS_TO_FETCH = original_max
        
        # Vérification timeout après fetch (seulement si activé)
        elapsed = time.time() - start_time
        if timeout_enabled and elapsed > timeout_seconds:
            print(f"  ⚠️ WARNING: Fetch took {elapsed:.2f}s (exceeds {timeout_seconds}s timeout)")
            print(f"  💡 Suggestion: Reduce max_transactions or use faster API (Alchemy)")
            raise HTTPException(
                status_code=408,
                detail=f"Timeout après fetch ({elapsed:.2f}s > {timeout_seconds}s). "
                       f"BitQuery peut être lent. Essayez: 1) Réduire max_transactions, "
                       f"2) Utiliser Alchemy API, ou 3) Désactiver le timeout dans l'interface."
            )
        
        # 2. BUILD GRAPH (rapide : seulement top holders)
        print(f"[{time.time() - start_time:.2f}s] 🕸️ Building graph")
        builder = GraphBuilder()
        graph = builder.build_graph(token_data)
        
        # 3. ANALYZE (algorithms optimisés)
        print(f"[{time.time() - start_time:.2f}s] 🧠 Running analysis")
        analyzer = GraphAnalyzer(graph)
        analysis_results = analyzer.analyze(community_mode=request.community_mode or "auto")
        # Ensure provider_used is available in response metrics
        analysis_results.setdefault("metrics", {})
        analysis_results["metrics"]["provider_used"] = fetcher.last_provider_used or request.api_provider
        
        # 3.5. WASH TRADE DETECTION
        print(f"[{time.time() - start_time:.2f}s] 🔍 Detecting wash trades")
        wash_detector = WashTradeDetector(graph)
        wash_trade_pairs = wash_detector.detect()
        analysis_results["wash_trade_pairs"] = wash_trade_pairs
        
        # 3.6. MIXER FLAGS
        print(f"[{time.time() - start_time:.2f}s] 🚨 Checking mixer flags")
        holder_addresses = [h.get("address", "") for h in token_data.get("top_holders", [])]
        mixer_flags = check_mixer_flags(holder_addresses)
        analysis_results["mixer_flags"] = mixer_flags
        
        # 4. RISK SCORING
        print(f"[{time.time() - start_time:.2f}s] ⚠️ Calculating risk scores")
        scorer = RiskScorer()
        risk_score = scorer.calculate_risk_score(
            analysis_results, 
            token_data
        )
        
        # 5. FORMAT FOR FRONTEND (React Force Graph format)
        print(f"[{time.time() - start_time:.2f}s] 📊 Formatting for frontend")
        graph_data = builder.format_for_react_force_graph(graph, analysis_results)
        
        elapsed_time = time.time() - start_time
        
        # VÉRIFICATION CONTRAINTE 30s (désactivée)
        if elapsed_time > 30:
            print(f"[{elapsed_time:.2f}s] ⏱️ Warning: analysis exceeded 30s but returning results")
        
        print(f"[{elapsed_time:.2f}s] ✅ Analysis complete - Risk Score: {risk_score:.2f}")
        
        return TokenAnalysisResponse(
            token_address=request.token_address,
            analysis_time_seconds=round(elapsed_time, 2),
            risk_score=round(risk_score, 3),
            top_holders=analysis_results["top_holders"],
            suspicious_clusters=analysis_results["suspicious_clusters"],
            mixer_flags=analysis_results["mixer_flags"],
            wash_trade_pairs=analysis_results["wash_trade_pairs"],
            graph_data=graph_data,
            metrics=analysis_results["metrics"]
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        # Erreur de configuration API
        elapsed_time = time.time() - start_time
        print(f"[{elapsed_time:.2f}s] ❌ Configuration Error: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"API Configuration Error: {str(e)}\n\n💡 Solution: Add the required API key to your .env file or use 'auto' mode to use available APIs."
        )
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"[{elapsed_time:.2f}s] ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "max_response_time": "30s",
        "config": {
            "max_holders": Config.MAX_HOLDERS,
            "max_transactions": Config.MAX_TRANSACTIONS_TO_FETCH,
            "timeout_seconds": Config.TIMEOUT_SECONDS
        }
    }


class ChatRequest(BaseModel):
    message: str
    execute: Optional[bool] = True  # Execute Cypher if present
    params: Optional[Dict] = None   # Optional Cypher parameters

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with an AI agent that can generate Cypher and query Neo4j.
    - If the model returns a Cypher block, optionally execute it and include results.
    - Returns: agent response, extracted cypher (if any), and query results (if executed).
    """
    agent = get_chat_agent()
    run = agent.run(request.message)
    content = str(getattr(run, "content", ""))

    cypher = extract_cypher(content)
    execution = None
    if cypher and (request.execute is None or request.execute):
        try:
            execution = {
                "query": cypher,
                "params": request.params or {},
                "rows": run_cypher(cypher, request.params or {}),
            }
        except Exception as e:
            execution = {"error": str(e), "query": cypher}

    return {
        "response": content,
        "cypher": cypher,
        "execution": execution,
    }


if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)

