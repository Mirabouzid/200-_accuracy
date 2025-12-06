import app from './src/app.js';
import dotenv from 'dotenv';

dotenv.config();

const PORT = process.env.PORT || 5000;
const GRAPH_AGENT_URL = process.env.GRAPH_AGENT_URL || 'http://localhost:8000';

// Start server
app.listen(PORT, () => {
    console.log('\n' + '='.repeat(60));
    console.log('🚀 BlockStat Pro Backend Server');
    console.log('='.repeat(60));
    console.log(`📍 Server running on: http://localhost:${PORT}`);
    console.log(`🔗 Graph Agent URL: ${GRAPH_AGENT_URL}`);
    console.log('\n📡 Available Endpoints:');
    console.log(`   GET  /api/health     - Health check`);
    console.log(`   POST /api/chat       - AI Chatbot (SSE)`);
    console.log(`   POST /api/analyze    - Token analysis`);
    console.log(`   GET  /api/token/:addr - Token info`);
    console.log(`   GET  /api/stats      - Statistics`);
    console.log('\n⚠️  Make sure the Graph Agent Python backend is running on port 8000');
    console.log('='.repeat(60) + '\n');
});
