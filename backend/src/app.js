import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

// Import routes
import healthRoutes from './routes/health.js';
import chatRoutes from './routes/chat.js';
import analysisRoutes from './routes/analysis.js';
import tokenRoutes from './routes/token.js';
import statsRoutes from './routes/stats.js';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const GRAPH_AGENT_URL = process.env.GRAPH_AGENT_URL || 'http://localhost:8000';

// Middleware
app.use(cors());
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
    next();
});

// Routes
app.use('/api/health', healthRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/analyze', analysisRoutes);
app.use('/api/token', tokenRoutes);
app.use('/api/stats', statsRoutes);

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'BlockStat Pro API',
        version: '1.0.0',
        endpoints: {
            health: '/api/health',
            chat: '/api/chat (POST)',
            analyze: '/api/analyze (POST)',
            token: '/api/token/:address (GET)',
            stats: '/api/stats (GET)'
        },
        graph_agent_url: GRAPH_AGENT_URL
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('[Error]', err);
    res.status(err.status || 500).json({
        error: err.message || 'Internal server error',
        path: req.path
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Endpoint not found',
        path: req.path,
        available_endpoints: [
            'GET /',
            'GET /api/health',
            'POST /api/chat',
            'POST /api/analyze',
            'GET /api/token/:address',
            'GET /api/stats'
        ]
    });
});

export default app;

