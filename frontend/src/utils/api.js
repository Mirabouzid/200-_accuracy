import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
    baseURL: API_URL,
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
    },
    (error) => {
        if (error.response) {
            console.error(`API Error: ${error.response.status}`, error.response.data);
        } else if (error.request) {
            // Network error - backend not running
            if (error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') {
                console.error('❌ Backend server is not running!');
                console.error('💡 Please start the backend: cd backend && npm run dev');
                // Add helpful error message to error object
                error.userMessage = 'Backend server is not running. Please start it on port 5000.';
            } else {
                console.error('API Error: No response received', error.request);
            }
        } else {
            console.error('API Error:', error.message);
        }
        return Promise.reject(error);
    }
);

// API Methods
export const healthCheck = async () => {
    try {
        const response = await api.get('/api/health');
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const analyzeToken = async (tokenAddress) => {
    try {
        const response = await api.post('/api/analyze', {
            token_address: tokenAddress,
        });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getTokenInfo = async (tokenAddress) => {
    try {
        const response = await api.get(`/api/token/${tokenAddress}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getStats = async () => {
    try {
        const response = await api.get('/api/stats');
        return response.data;
    } catch (error) {
        throw error;
    }
};

export default api;