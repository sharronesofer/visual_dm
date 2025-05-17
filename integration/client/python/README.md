# Python Client: Unified Emotion API

This module provides a Python client for interacting with the unified emotion API.

## Installation

Requires Python 3.7+ and the `requests` library:

```sh
pip install requests
```

## Usage Example

```python
from emotion_api_client import EmotionApiClient
client = EmotionApiClient('http://localhost:3000/api')

# Get all emotions
emotions = client.get_emotions()
print(emotions)

# Get a specific emotion
joy = client.get_emotion('joy')
print(joy)

# Create or update an emotion
client.upsert_emotion({'name': 'joy', 'intensity': 0.8})

# Delete an emotion
client.delete_emotion('joy')
```

## Integration Notes
- Use this client in Python-based systems to read/write emotion data via the REST API.
- For batch operations, wrap calls in your own scripts or use the migration utilities.
- See backend OpenAPI docs for full API details. 