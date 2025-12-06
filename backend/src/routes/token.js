import express from 'express';

const router = express.Router();

// Get token info endpoint
router.get('/:address', async (req, res) => {
    try {
        const { address } = req.params;

        if (!address) {
            return res.status(400).json({ error: 'Token address is required' });
        }

        // For now, we can return basic info
        // In the future, this could cache token metadata or call Graph Agent
        res.json({
            address: address,
            message: 'Token info endpoint',
            note: 'Full token metadata can be retrieved from the analysis endpoint'
        });

    } catch (error) {
        console.error('[Token] Error:', error.message);
        res.status(500).json({ error: 'Failed to get token info' });
    }
});

export default router;

