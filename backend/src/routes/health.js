import express from 'express';
import axios from 'axios';

const router = express.Router();
const GRAPH_AGENT_URL = process.env.GRAPH_AGENT_URL || 'http://localhost:8000';

// Health check endpoint
router.get('/', async (req, res) => {
    try {
        // Check Graph Agent health
        let graphAgentStatus = 'unknown';
        try {
            const healthResponse = await axios.get(`${GRAPH_AGENT_URL}/health`, { timeout: 5000 });
            graphAgentStatus = healthResponse.data.status === 'healthy' ? 'healthy' : 'unhealthy';
        } catch (e) {
            graphAgentStatus = 'unavailable';
        }

        res.json({
            status: 'ok',
            message: 'BlockStat API is running',
            timestamp: new Date().toISOString(),
            services: {
                backend: 'online',
                graph_agent: graphAgentStatus,
                chatbot: process.env.GROQ_API_KEY ? 'configured' : 'not_configured'
            },
            version: '1.0.0'
        });
    } catch (error) {
        res.status(500).json({
            status: 'error',
            message: 'Health check failed',
            error: error.message
        });
    }
});

export default router;

