import express from 'express';
import { Groq } from 'groq-sdk';

const router = express.Router();

// Initialize Groq - will be created on first request
let groq = null;

function getGroqClient() {
    if (!groq && process.env.GROQ_API_KEY) {
        groq = new Groq({
            apiKey: process.env.GROQ_API_KEY
        });
    }
    return groq;
}

// Chat endpoint with streaming
router.post('/', async (req, res) => {
    try {
        // Get or create Groq client
        const groqClient = getGroqClient();

        // Check if Groq is configured
        if (!groqClient) {
            console.error('[Chat] GROQ_API_KEY not found in environment variables');
            console.error('[Chat] Available env keys:', Object.keys(process.env).filter(k => k.includes('GROQ') || k.includes('API')));
            return res.status(503).json({
                error: 'Chatbot service is not configured. Please set GROQ_API_KEY in .env file.',
                debug: {
                    hasKey: !!process.env.GROQ_API_KEY,
                    keyLength: process.env.GROQ_API_KEY?.length || 0
                }
            });
        }

        const { message, conversationHistory = [] } = req.body;

        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }

        // Enhanced system prompt with context awareness and politeness
        const systemPrompt = `You are a polite, respectful, and helpful AI assistant for BlockStat Pro, a blockchain forensic analysis platform. 

IMPORTANT CONTEXT RULES:
1. Always maintain full context awareness - remember and reference previous messages in the conversation
2. If a user mentions something from a previous message (like "and +7 = ?" after "5+5=10"), you must understand the context and continue from where they left off
3. Be extremely polite, respectful, and professional in all responses
4. Respect the user's content, questions, and context - never dismiss or ignore previous conversation elements
5. When answering follow-up questions, explicitly reference the previous context when relevant
6. Help users understand token analysis, risk assessment, and blockchain security
7. Be concise but thorough, and always maintain a friendly, helpful tone

Remember: Context is key. Always consider the full conversation history when responding.`;

        // Include more conversation history for better context (last 20 messages)
        const messages = [
            {
                role: 'system',
                content: systemPrompt
            },
            ...conversationHistory,
            {
                role: 'user',
                content: message
            }
        ];

        // Set up SSE
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');

        const chatCompletion = await groqClient.chat.completions.create({
            messages: messages,
            model: 'openai/gpt-oss-120b',
            temperature: 1,
            max_completion_tokens: 8192,
            top_p: 1,
            stream: true,
            reasoning_effort: 'medium',
            stop: null
        });

        // Stream the response
        for await (const chunk of chatCompletion) {
            const content = chunk.choices[0]?.delta?.content || '';
            if (content) {
                res.write(`data: ${JSON.stringify({ content })}\n\n`);
            }
        }

        res.write('data: [DONE]\n\n');
        res.end();

    } catch (error) {
        console.error('[Chat] Error:', error);
        if (!res.headersSent) {
            res.status(500).json({ error: 'Failed to process chat request' });
        } else {
            res.write(`data: ${JSON.stringify({ error: 'An error occurred' })}\n\n`);
            res.end();
        }
    }
});

export default router;

