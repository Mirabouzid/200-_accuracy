// Test script to check if .env is loaded correctly
import dotenv from 'dotenv';

console.log('\n=== Testing .env Configuration ===\n');

// Load .env
const result = dotenv.config();

if (result.error) {
    console.error('❌ Error loading .env:', result.error);
} else {
    console.log('✅ .env file loaded successfully');
}

console.log('\n--- Environment Variables ---');
console.log('PORT:', process.env.PORT || 'NOT SET');
console.log('NODE_ENV:', process.env.NODE_ENV || 'NOT SET');
console.log('GRAPH_AGENT_URL:', process.env.GRAPH_AGENT_URL || 'NOT SET');

// Check GROQ_API_KEY
if (process.env.GROQ_API_KEY) {
    const key = process.env.GROQ_API_KEY;
    console.log('GROQ_API_KEY: ✅ SET');
    console.log('  - Length:', key.length);
    console.log('  - Starts with:', key.substring(0, 10) + '...');
    console.log('  - Ends with:', '...' + key.substring(key.length - 10));
} else {
    console.log('GROQ_API_KEY: ❌ NOT SET');
}

console.log('\n--- All Environment Variables ---');
const envKeys = Object.keys(process.env).filter(k =>
    k.includes('GROQ') ||
    k.includes('API') ||
    k.includes('PORT') ||
    k.includes('NODE')
);
console.log('Relevant keys:', envKeys.join(', '));

console.log('\n=== Test Complete ===\n');
