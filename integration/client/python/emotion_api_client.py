"""
Python client for the unified emotion API.
Usage:
    from emotion_api_client import EmotionApiClient
    client = EmotionApiClient('http://localhost:3000/api')
    emotions = client.get_emotions()
"""
import requests

class EmotionApiClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def get_emotions(self):
        """Get all emotions."""
        r = requests.get(f'{self.base_url}/emotions')
        r.raise_for_status()
        return r.json().get('emotions', [])

    def get_emotion(self, name):
        """Get a specific emotion by name."""
        r = requests.get(f'{self.base_url}/emotions/{name}')
        r.raise_for_status()
        return r.json()

    def upsert_emotion(self, emotion):
        """Create or update an emotion. Expects a dict with at least 'name' and 'intensity'."""
        r = requests.post(f'{self.base_url}/emotions', json=emotion)
        r.raise_for_status()
        return r.json()

    def delete_emotion(self, name):
        """Delete an emotion by name."""
        r = requests.delete(f'{self.base_url}/emotions/{name}')
        r.raise_for_status()
        return r.json()

# Example usage
if __name__ == '__main__':
    client = EmotionApiClient('http://localhost:3000/api')
    print(client.get_emotions()) 