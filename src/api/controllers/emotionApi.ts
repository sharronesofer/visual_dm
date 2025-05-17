import { EmotionRegistry, BasicEmotion } from '../../models/EmotionDefinition';

// In-memory event bus for emotion events
const emotionEventBus = {
    subscribers: new Set<Function>(),
    publish(event: any) {
        for (const sub of this.subscribers) {
            try { sub(event); } catch (e) { /* ignore */ }
        }
    },
    subscribe(fn: Function) {
        this.subscribers.add(fn);
        return () => this.subscribers.delete(fn);
    }
};

export { emotionEventBus };

export function registerEmotionRoutes(app) {
    // List all emotions
    app.get('/api/emotions', (req, res) => {
        try {
            const emotions = EmotionRegistry.instance.getAllEmotions().map(e => e.toJSON());
            res.json({ emotions });
        } catch (err) {
            res.status(500).json({ error: 'Failed to list emotions', details: (err instanceof Error ? err.message : String(err)) });
        }
    });

    // Get a specific emotion by name
    app.get('/api/emotions/:name', (req, res) => {
        try {
            const emotion = EmotionRegistry.instance.getEmotionByName(req.params.name);
            if (!emotion) return res.status(404).json({ error: 'Emotion not found' });
            res.json({ emotion: emotion.toJSON() });
        } catch (err) {
            res.status(500).json({ error: 'Failed to get emotion', details: (err instanceof Error ? err.message : String(err)) });
        }
    });

    // Create or update an emotion
    app.post('/api/emotions', (req, res) => {
        try {
            const { name, intensity, valence, arousal, metadata } = req.body;
            if (!name || typeof intensity !== 'number' || typeof valence !== 'number' || typeof arousal !== 'number') {
                return res.status(400).json({ error: 'Missing required emotion fields' });
            }
            const emotion = new BasicEmotion(name, intensity, valence, arousal, metadata || {});
            EmotionRegistry.instance.registerEmotion(emotion);
            // Publish event
            emotionEventBus.publish({ type: 'emotion.updated', emotion: emotion.toJSON(), timestamp: Date.now() });
            res.status(201).json({ emotion: emotion.toJSON() });
        } catch (err) {
            res.status(500).json({ error: 'Failed to create/update emotion', details: (err instanceof Error ? err.message : String(err)) });
        }
    });

    // Delete an emotion
    app.delete('/api/emotions/:name', (req, res) => {
        try {
            const registry = EmotionRegistry.instance;
            const deleted = registry.deleteEmotionByName(req.params.name);
            if (!deleted) return res.status(404).json({ error: 'Emotion not found' });
            // Publish event
            emotionEventBus.publish({ type: 'emotion.deleted', name: req.params.name, timestamp: Date.now() });
            res.json({ deleted: req.params.name });
        } catch (err) {
            res.status(500).json({ error: 'Failed to delete emotion', details: (err instanceof Error ? err.message : String(err)) });
        }
    });

    // Stub for real-time subscription (to be implemented with WebSockets or SSE)
    app.get('/api/emotions/subscribe', (req, res) => {
        res.status(501).json({ error: 'Subscription endpoint not implemented yet' });
    });

    /**
     * @openapi
     * /api/emotions/gpt-context:
     *   get:
     *     summary: Get all current emotions in a format optimized for GPT prompt consumption
     *     description: Returns a list of emotions with name, intensity, and description for use in LLM prompt templates and AI integrations.
     *     tags:
     *       - Emotions
     *     responses:
     *       200:
     *         description: List of current emotions for GPT context
     *         content:
     *           application/json:
     *             schema:
     *               type: object
     *               properties:
     *                 emotions:
     *                   type: array
     *                   items:
     *                     type: object
     *                     properties:
     *                       name:
     *                         type: string
     *                       intensity:
     *                         type: number
     *                       description:
     *                         type: string
     */
    app.get('/api/emotions/gpt-context', (req, res) => {
        try {
            const emotions = EmotionRegistry.instance.getAllEmotions().map(e => ({
                name: e.name,
                intensity: e.intensity ?? 1.0,
                description: e.metadata?.description ?? ''
            }));
            res.json({ emotions });
        } catch (err) {
            res.status(500).json({ error: 'Failed to get GPT context', details: (err instanceof Error ? err.message : String(err)) });
        }
    });
}

/**
 * Helper for GPT prompt injection: returns emotion context as a string for LLMs.
 */
export function getEmotionContextForGPT(): string {
    const emotions = EmotionRegistry.instance.getAllEmotions();
    if (!emotions.length) return 'No emotions are currently active.';
    return 'Current emotions: ' + emotions.map(e => `${e.name} (intensity: ${e.intensity ?? 1.0})`).join(', ');
} 