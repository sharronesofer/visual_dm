# Legacy System Integration: EmotionApiAdapter

This directory provides adapters and utilities for integrating legacy systems with the new unified emotion API.

## EmotionApiAdapter.js

A JavaScript adapter for legacy systems to interact with the new RESTful emotion API. Supports querying, updating, and deleting emotions, and translates between legacy and new data formats.

### Usage Example

```js
const EmotionApiAdapter = require('./EmotionApiAdapter');
const adapter = new EmotionApiAdapter('http://localhost:3000/api');

// Get all emotions
adapter.getEmotions().then(console.log);

// Get a specific emotion
adapter.getEmotion('joy').then(console.log);

// Create or update an emotion
adapter.upsertEmotion({ name: 'joy', intensity: 0.8 }).then(console.log);

// Delete an emotion
adapter.deleteEmotion('joy').then(console.log);
```

## Migration Notes
- Replace legacy emotion API calls with EmotionApiAdapter methods.
- Ensure data formats match the new API (see backend OpenAPI docs).
- For batch migration, see migration scripts (to be provided).

## Roadmap
- Add Python and other language adapters
- Provide migration scripts for bulk data transfer
- Add offline fallback and caching utilities 