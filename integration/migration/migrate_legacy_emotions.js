// migrate_legacy_emotions.js
// Migration script: Transfers legacy emotion data to the new unified emotion API
// Usage: node migrate_legacy_emotions.js legacy_emotions.json http://localhost:3000/api

const fs = require('fs');
const path = require('path');
const EmotionApiAdapter = require('../legacy/EmotionApiAdapter');

if (process.argv.length < 4) {
    console.error('Usage: node migrate_legacy_emotions.js <legacy_emotions.json> <api_base_url>');
    process.exit(1);
}

const legacyFile = process.argv[2];
const apiBaseUrl = process.argv[3];
const adapter = new EmotionApiAdapter(apiBaseUrl);

// Assumption: legacy_emotions.json is an array of objects with at least { name, value } or { name, intensity }
function transformLegacyEmotion(legacy) {
    // Map legacy fields to new format
    return {
        name: legacy.name,
        intensity: legacy.intensity ?? legacy.value ?? 1.0,
        // Add more mappings as needed
    };
}

async function migrate() {
    const raw = fs.readFileSync(path.resolve(legacyFile), 'utf-8');
    const legacyEmotions = JSON.parse(raw);
    let success = 0, failed = 0;
    for (const legacy of legacyEmotions) {
        const emotion = transformLegacyEmotion(legacy);
        try {
            await adapter.upsertEmotion(emotion);
            console.log(`Migrated: ${emotion.name}`);
            success++;
        } catch (err) {
            console.error(`Failed to migrate ${emotion.name}:`, err.message);
            failed++;
        }
    }
    console.log(`\nMigration complete. Success: ${success}, Failed: ${failed}`);
}

migrate(); 