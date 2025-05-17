// usage_monitor.js
// Monitors emotion API usage and adoption metrics
// Usage: node usage_monitor.js http://localhost:3000/api

const fetch = require('node-fetch');

if (process.argv.length < 3) {
    console.error('Usage: node usage_monitor.js <api_base_url>');
    process.exit(1);
}

const apiBaseUrl = process.argv[2].replace(/\/$/, '');

async function monitor() {
    try {
        const res = await fetch(`${apiBaseUrl}/emotions`);
        if (!res.ok) throw new Error('Failed to fetch emotions');
        const data = await res.json();
        const count = Array.isArray(data.emotions) ? data.emotions.length : 0;
        console.log(`[${new Date().toISOString()}] Emotion API: ${count} emotions registered.`);
        // Optionally, add more metrics (e.g., recent changes, top emotions)
    } catch (err) {
        console.error(`[${new Date().toISOString()}] Error:`, err.message);
    }
}

monitor(); 