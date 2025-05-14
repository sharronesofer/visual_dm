import requests
from typing import Dict, Any, Optional
from .config import ENDPOINTS, REQUEST_TIMEOUT, MAX_RETRIES

def make_request(endpoint: str, data: Dict[str, Any], method: str = 'POST') -> Optional[Dict[str, Any]]:
    """
    Make a request to the backend with retry logic and proper error handling.
    
    Args:
        endpoint: The endpoint key from the ENDPOINTS configuration
        data: The data to send in the request
        method: HTTP method to use (default: POST)
    
    Returns:
        Optional[Dict[str, Any]]: Response data if successful, None if failed
    """
    url = ENDPOINTS.get(endpoint)
    if not url:
        print(f"Error: Unknown endpoint '{endpoint}'")
        return None
        
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"Connection error. Retrying... ({retries + 1}/{MAX_RETRIES})")
        except requests.exceptions.Timeout:
            print(f"Request timed out. Retrying... ({retries + 1}/{MAX_RETRIES})")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
        retries += 1
    
    print("Max retries reached. Could not connect to backend.")
    return None

def post_character_to_backend(character_data: Dict[str, Any]) -> bool:
    """Post character data to the backend."""
    response = make_request('character_create', character_data)
    return response is not None

def load_character_from_backend(character_id: str) -> Optional[Dict[str, Any]]:
    """Load character data from the backend."""
    return make_request('character_load', {'character_id': character_id})

def generate_region(region_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Generate a new region."""
    return make_request('region_generate', region_data)

def generate_world(world_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Generate a new world."""
    return make_request('world_generate', world_data)
