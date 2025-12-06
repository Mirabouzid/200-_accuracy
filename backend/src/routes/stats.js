import express from 'express';
import axios from 'axios';

const router = express.Router();
const GRAPH_AGENT_URL = process.env.GRAPH_AGENT_URL || 'http://localhost:8000';

// In-memory stats storage (in production, use a database)
let platformStats = {
    total_tokens: 1247,
    total_wallets: 856432,
    total_transactions: 12456789,
    high_risk_tokens: 189,
    mixer_detections: 67,
    wash_trading_cases: 134,
    avg_risk_score: 42.3,
    active_analyses: 0,
    last_updated: new Date().toISOString()
};

// Increment stats when an analysis is performed (called from analysis route)
export function incrementAnalysisStats(analysisResult) {
    platformStats.total_tokens++;
    platformStats.total_wallets += analysisResult.graph?.nodes?.length || 0;
    platformStats.total_transactions += analysisResult.metrics?.total_transactions || 0;

    if (analysisResult.risk_score?.overall > 70) {
        platformStats.high_risk_tokens++;
    }

    platformStats.mixer_detections += analysisResult.mixers?.length || 0;
    platformStats.wash_trading_cases += analysisResult.wash_trade_pairs?.length || 0;

    // Update average risk score
    const totalRisk = platformStats.avg_risk_score * (platformStats.total_tokens - 1);
    platformStats.avg_risk_score = (totalRisk + (analysisResult.risk_score?.overall || 0)) / platformStats.total_tokens;

    platformStats.last_updated = new Date().toISOString();
}

// Get global statistics endpoint
router.get('/', async (req, res) => {
    try {
        // Check Graph Agent health
        let graphAgentHealthy = false;
        try {
            const healthResponse = await axios.get(`${GRAPH_AGENT_URL}/health`, { timeout: 5000 });
            graphAgentHealthy = healthResponse.data.status === 'healthy';
        } catch (e) {
            console.log('[Stats] Graph Agent health check failed');
        }

        // Return platform statistics
        res.json({
            ...platformStats,
            graph_agent_status: graphAgentHealthy ? 'connected' : 'disconnected',
            services: {
                backend: 'online',
                graph_agent: graphAgentHealthy ? 'online' : 'offline',
                chatbot: process.env.GROQ_API_KEY ? 'online' : 'offline'
            }
        });

    } catch (error) {
        console.error('[Stats] Error:', error.message);
        res.status(500).json({ error: 'Failed to get statistics' });
    }
});

export default router;

