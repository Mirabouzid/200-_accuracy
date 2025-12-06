import express from 'express';
import axios from 'axios';
import { incrementAnalysisStats } from './stats.js';

const router = express.Router();
const GRAPH_AGENT_URL = process.env.GRAPH_AGENT_URL || 'http://localhost:8000';

// Transform Graph Agent response to frontend format
function transformAnalysisResponse(pythonResponse) {
    const { graph_data, risk_score, metrics, mixer_flags, suspicious_clusters, top_holders, wash_trade_pairs } = pythonResponse;

    // Transform risk_score from number to object with metrics
    const riskScoreObj = {
        overall: Math.round(risk_score * 100), // Convert 0-1 to 0-100
        gini: metrics?.gini || 0,
        concentration: metrics?.top_10_percent_holdings || 0,
        clustering: metrics?.clustering_coefficient || 0,
        total_wallets: graph_data?.nodes?.length || 0,
        active_wallets: graph_data?.nodes?.filter(n => n.tx_count > 0)?.length || 0
    };

    // Transform mixer_flags to mixers array
    const mixers = mixer_flags?.map(flag => ({
        address: flag.address || flag.wallet,
        type: 'mixer',
        risk_level: 'critical'
    })) || [];

    // Transform suspicious_clusters to clusters array
    const clusters = suspicious_clusters?.map(cluster => ({
        id: cluster.id || cluster.cluster_id,
        nodes: cluster.nodes || cluster.members || [],
        suspicious: true,
        wash_trading: cluster.wash_trading || false
    })) || [];

    // Transform top_holders to whales array
    const whales = top_holders?.slice(0, 10).map(holder => ({
        address: holder.address || holder.wallet,
        balance: holder.balance || holder.amount || 0,
        percentage: holder.percentage || holder.percent || 0,
        type: 'whale',
        pagerank: holder.pagerank || 0
    })) || [];

    return {
        graph: {
            nodes: graph_data?.nodes || [],
            links: graph_data?.links || []
        },
        risk_score: riskScoreObj,
        mixers: mixers,
        clusters: clusters,
        whales: whales,
        wash_trade_pairs: wash_trade_pairs || [],
        metrics: metrics || {}
    };
}

// Analyze token endpoint - calls Graph Agent Python
router.post('/', async (req, res) => {
    try {
        const { token_address } = req.body;

        if (!token_address) {
            return res.status(400).json({ error: 'token_address is required' });
        }

        console.log(`[Analysis] Analyzing token: ${token_address}`);

        // Call Graph Agent Python API
        const response = await axios.post(`${GRAPH_AGENT_URL}/analyze`, {
            token_address: token_address,
            chain: 'ethereum',
            api_provider: 'auto',
            timeout_seconds: 30
        }, {
            timeout: 35000 // 35s timeout (Graph Agent has 30s max)
        });

        // Transform response to frontend format
        const transformedData = transformAnalysisResponse(response.data);

        console.log(`[Analysis] Complete - Risk Score: ${transformedData.risk_score.overall}%`);

        // Update platform statistics
        incrementAnalysisStats(transformedData);

        res.json(transformedData);

    } catch (error) {
        console.error('[Analysis] Error:', error.message);

        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                error: 'Graph Agent service is not available. Please ensure the Python backend is running on port 8000.'
            });
        }

        if (error.response) {
            // Graph Agent returned an error
            return res.status(error.response.status || 500).json({
                error: error.response.data?.detail || error.response.data?.error || 'Analysis failed'
            });
        }

        if (error.code === 'ECONNABORTED') {
            return res.status(504).json({
                error: 'Analysis timeout. The token analysis took too long.'
            });
        }

        res.status(500).json({
            error: error.message || 'Internal server error during analysis'
        });
    }
});

export default router;

