// EmotionApiAdapter.js
// Adapter for legacy systems to interact with the new unified emotion API
// Usage: const adapter = new EmotionApiAdapter(baseUrl)

/**
 * @class EmotionApiAdapter
 * Provides methods for legacy systems to interact with the new emotion API.
 */
class EmotionApiAdapter {
    /**
     * @param {string} baseUrl - Base URL of the new emotion API (e.g., 'http://localhost:3000/api')
     */
    constructor(baseUrl) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }

    /**
     * Get all emotions
     * @returns {Promise<Array>} List of emotions
     */
    async getEmotions() {
        const res = await fetch(`${this.baseUrl}/emotions`);
        if (!res.ok) throw new Error('Failed to fetch emotions');
        const data = await res.json();
        return data.emotions;
    }

    /**
     * Get a specific emotion by name
     * @param {string} name
     * @returns {Promise<Object>} Emotion object
     */
    async getEmotion(name) {
        const res = await fetch(`${this.baseUrl}/emotions/${encodeURIComponent(name)}`);
        if (!res.ok) throw new Error('Emotion not found');
        return res.json();
    }

    /**
     * Create or update an emotion
     * @param {Object} emotion - { name, intensity, ... }
     * @returns {Promise<Object>} Updated emotion
     */
    async upsertEmotion(emotion) {
        const res = await fetch(`${this.baseUrl}/emotions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(emotion)
        });
        if (!res.ok) throw new Error('Failed to upsert emotion');
        return res.json();
    }

    /**
     * Delete an emotion by name
     * @param {string} name
     * @returns {Promise<Object>} Deletion result
     */
    async deleteEmotion(name) {
        const res = await fetch(`${this.baseUrl}/emotions/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error('Failed to delete emotion');
        return res.json();
    }
}

module.exports = EmotionApiAdapter;

/**
 * Example usage:
 * const adapter = new EmotionApiAdapter('http://localhost:3000/api');
 * adapter.getEmotions().then(console.log);
 */ 