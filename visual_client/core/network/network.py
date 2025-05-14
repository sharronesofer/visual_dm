import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future
import queue
import time
import requests
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)

class NetworkError(Exception):
    pass

class APIError(Exception):
    pass

class AuthError(Exception):
    pass

class NetworkClient:
    """
    Handles communication with the backend REST API, with support for concurrent requests and queuing.
    """
    def __init__(self, base_url: str, auth_token: Optional[str] = None, timeout: int = 10, max_retries: int = 3, backoff_factor: float = 0.5, max_workers: int = 5, rate_limit: int = 10):
        """
        Initialize the NetworkClient.
        
        Args:
            base_url: Base URL for the API endpoints.
            auth_token: Optional authentication token for API requests.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for transient errors.
            backoff_factor: Factor to increase wait time between retries.
            max_workers: Maximum number of concurrent requests.
            rate_limit: Maximum number of requests per second.
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._futures: List[Future] = []
        self._lock = threading.Lock()
        self._last_request_time = 0.0
        self._rate_limit = rate_limit  # max requests per second
        self._rate_lock = threading.Lock()

    def _rate_limited(self):
        with self._rate_lock:
            now = time.time()
            elapsed = now - self._last_request_time
            min_interval = 1.0 / self._rate_limit
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            self._last_request_time = time.time()

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        self._rate_limited()
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        retries = 0
        while retries <= self.max_retries:
            try:
                logger.info(f"Request: {method} {url} | Data: {data}")
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
                logger.info(f"Response: {response.status_code} {response.text}")
                if response.status_code == 401:
                    logger.error("Authentication failed.")
                    raise AuthError("Authentication failed.")
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on {method} {url}, retry {retries+1}/{self.max_retries}")
                if retries == self.max_retries:
                    logger.error(f"Request timed out after {self.max_retries} retries.")
                    raise NetworkError(f"Request timed out after {self.max_retries} retries.")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on {method} {url}, retry {retries+1}/{self.max_retries}")
                if retries == self.max_retries:
                    logger.error(f"Connection error after {self.max_retries} retries.")
                    raise NetworkError(f"Connection error after {self.max_retries} retries.")
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                if 500 <= response.status_code < 600 and retries < self.max_retries:
                    pass  # Retry on server errors
                else:
                    raise APIError(f"HTTP error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise NetworkError(f"Unexpected error: {e}")
            retries += 1
            time.sleep(self.backoff_factor * (2 ** (retries - 1)))
        logger.error("Max retries reached. Could not complete request.")
        raise NetworkError("Max retries reached. Could not complete request.")

    def submit_request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None, callback: Optional[Callable[[Any], None]] = None) -> Future:
        future = self.executor.submit(self._request, method, path, data)
        if callback:
            def _cb(fut):
                try:
                    result = fut.result()
                    callback(result)
                except Exception as e:
                    callback(e)
            future.add_done_callback(_cb)
        with self._lock:
            self._futures.append(future)
        return future

    def cancel_pending_requests(self):
        with self._lock:
            for future in self._futures:
                if not future.done():
                    future.cancel()
            self._futures = [f for f in self._futures if not f.cancelled()]

    def get_game_state(self) -> Dict[str, Any]:
        """
        Fetch the current game state from the backend.
        Returns:
            Dictionary representing the game state.
        """
        return self._request("GET", "/game/state")

    def update_game_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the game state on the backend.
        Args:
            state: Dictionary representing the new game state.
        Returns:
            Dictionary with the update result.
        """
        return self._request("POST", "/game/state", data=state)

    def get_regions(self) -> List[Dict[str, Any]]:
        """
        Fetch all regions from the backend.
        Returns:
            List of dictionaries, each representing a region.
        """
        return self._request("GET", "/regions")

    def get_items(self) -> List[Dict[str, Any]]:
        """
        Fetch all items from the backend.
        Returns:
            List of dictionaries, each representing an item.
        """
        return self._request("GET", "/items")

    def get_characters(self) -> List[Dict[str, Any]]:
        """
        Fetch all characters from the backend.
        Returns:
            List of dictionaries, each representing a character.
        """
        return self._request("GET", "/characters")

class MockNetworkClient(NetworkClient):
    """
    Mock version of NetworkClient for development and testing.
    Returns predefined mock responses instead of making real HTTP requests.
    """
    def __init__(self):
        super().__init__(base_url="http://mock.api", auth_token=None)

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        logger.info(f"[MOCK] Request: {method} {path} | Data: {data}")
        # Return mock data based on endpoint
        if path == "/game/state" and method == "GET":
            return {"state": "mock_game_state"}
        if path == "/game/state" and method == "POST":
            return {"result": "mock_update_success"}
        if path == "/regions" and method == "GET":
            return [{"id": 1, "name": "Mock Region"}]
        if path == "/items" and method == "GET":
            return [{"id": 1, "name": "Mock Item"}]
        if path == "/characters" and method == "GET":
            return [{"id": 1, "name": "Mock Character"}]
        return {"mock": True}

# Config flag to switch between real and mock client
USE_MOCK_CLIENT = False

def get_network_client() -> NetworkClient:
    if USE_MOCK_CLIENT:
        return MockNetworkClient()
    return NetworkClient(base_url="http://localhost:5000")

# Unit test stubs
if __name__ == "__main__":
    import unittest

    class TestNetworkClient(unittest.TestCase):
        def setUp(self):
            self.client = MockNetworkClient()

        def test_get_game_state(self):
            result = self.client.get_game_state()
            self.assertIn("state", result)

        def test_update_game_state(self):
            result = self.client.update_game_state({"foo": "bar"})
            self.assertIn("result", result)

        def test_get_regions(self):
            result = self.client.get_regions()
            self.assertIsInstance(result, list)

        def test_get_items(self):
            result = self.client.get_items()
            self.assertIsInstance(result, list)

        def test_get_characters(self):
            result = self.client.get_characters()
            self.assertIsInstance(result, list)

    unittest.main() 