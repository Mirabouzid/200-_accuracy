import dotenv from 'dotenv';

dotenv.config();

export const config = {
    // Server
    port: process.env.PORT || 5000,
    nodeEnv: process.env.NODE_ENV || 'development',
    
    // Graph Agent
    graphAgentUrl: process.env.GRAPH_AGENT_URL || 'http://localhost:8000',
    
    // Groq AI
    groqApiKey: process.env.GROQ_API_KEY,
    
    // Timeouts
    graphAgentTimeout: 35000, // 35 seconds
    healthCheckTimeout: 5000,  // 5 seconds
};

// Validate required configuration
export function validateConfig() {
    const warnings = [];
    
    if (!config.groqApiKey) {
        warnings.push('⚠️  GROQ_API_KEY not found - Chatbot will not work');
    }
    
    if (warnings.length > 0) {
        console.warn('⚠️  Configuration warnings:');
        warnings.forEach(warning => console.warn(`   - ${warning}`));
        console.warn('   The backend will start, but some features may not work.\n');
    } else {
        console.log('✅ Configuration validated\n');
    }
}

export default config;

