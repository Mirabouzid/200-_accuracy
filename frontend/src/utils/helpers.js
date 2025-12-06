/**
 * Shorten blockchain address
 * @param {string} address - Full address
 * @param {number} start - Characters to show at start
 * @param {number} end - Characters to show at end
 * @returns {string} Shortened address
 */
export const shortenAddress = (address, start = 6, end = 4) => {
    if (!address) return '';
    if (address.length <= start + end) return address;
    return `${address.slice(0, start)}...${address.slice(-end)}`;
};

/**
 * Format number with commas
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export const formatNumber = (num) => {
    if (num === undefined || num === null) return '0';
    return num.toLocaleString('en-US', {
        maximumFractionDigits: 2,
    });
};

/**
 * Format large numbers with K, M, B suffixes
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export const formatLargeNumber = (num) => {
    if (num === undefined || num === null) return '0';

    const absNum = Math.abs(num);

    if (absNum >= 1e9) {
        return (num / 1e9).toFixed(2) + 'B';
    }
    if (absNum >= 1e6) {
        return (num / 1e6).toFixed(2) + 'M';
    }
    if (absNum >= 1e3) {
        return (num / 1e3).toFixed(2) + 'K';
    }
    return num.toFixed(2);
};

/**
 * Get risk level text and color
 * @param {number} score - Risk score 0-100
 * @returns {object} Risk level info
 */
export const getRiskLevel = (score) => {
    if (score >= 80) {
        return {
            level: 'CRITICAL',
            color: 'red',
            bgColor: 'bg-red-500/10',
            textColor: 'text-red-400',
            borderColor: 'border-red-500/30',
        };
    }
    if (score >= 50) {
        return {
            level: 'HIGH',
            color: 'orange',
            bgColor: 'bg-orange-500/10',
            textColor: 'text-orange-400',
            borderColor: 'border-orange-500/30',
        };
    }
    if (score >= 30) {
        return {
            level: 'MEDIUM',
            color: 'yellow',
            bgColor: 'bg-yellow-500/10',
            textColor: 'text-yellow-400',
            borderColor: 'border-yellow-500/30',
        };
    }
    return {
        level: 'LOW',
        color: 'green',
        bgColor: 'bg-green-500/10',
        textColor: 'text-green-400',
        borderColor: 'border-green-500/30',
    };
};

/**
 * Get node type color
 * @param {string} type - Node type
 * @returns {string} Color hex
 */
export const getNodeColor = (type) => {
    const colors = {
        deployer: '#8b5cf6', // Purple
        mixer: '#ef4444',    // Red
        wash_trading: '#f97316', // Orange
        whale: '#3b82f6',    // Blue
        normal: '#10b981',   // Green
    };
    return colors[type] || colors.normal;
};

/**
 * Calculate node size based on balance
 * @param {object} node - Node data
 * @returns {number} Node size
 */
export const calculateNodeSize = (node) => {
    const baseSize = Math.sqrt(Math.abs(node.balance || 0)) / 100;

    if (node.type === 'deployer') return Math.max(15, baseSize);
    if (node.type === 'mixer') return Math.max(10, baseSize * 0.8);
    if (node.type === 'whale') return Math.max(12, baseSize * 0.9);
    if (node.type === 'wash_trading') return Math.max(7, baseSize * 0.6);
    return Math.max(4, baseSize * 0.5);
};

/**
 * Validate Ethereum address
 * @param {string} address - Address to validate
 * @returns {boolean} Is valid
 */
export const isValidAddress = (address) => {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
};

/**
 * Format timestamp
 * @param {string} timestamp - ISO timestamp
 * @returns {string} Formatted date
 */
export const formatDate = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
};

/**
 * Calculate percentage
 * @param {number} value - Value
 * @param {number} total - Total
 * @returns {number} Percentage
 */
export const calculatePercentage = (value, total) => {
    if (!total || total === 0) return 0;
    return ((value / total) * 100).toFixed(2);
};

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

/**
 * Copy to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success
 */
export const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Failed to copy:', err);
        return false;
    }
};

/**
 * Download JSON file
 * @param {object} data - Data to download
 * @param {string} filename - File name
 */
export const downloadJSON = (data, filename) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
export const generateId = () => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Sleep function
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise} Promise that resolves after ms
 */
export const sleep = (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms));
};