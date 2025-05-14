"""
Cache warming utilities.
Provides functionality to proactively warm up caches for critical endpoints.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import threading
import time
import logging
from flask import Flask, current_app
import requests
from app.core.utils.cache import RedisCache

logger = logging.getLogger(__name__)

class CacheWarmer:
    """Manages cache warming for critical endpoints."""
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize the cache warmer."""
        self.app = app
        self.warming_thread = None
        self.stop_warming = False
        self.critical_endpoints = {
            # Character endpoints
            '/character/': {'method': 'GET', 'params': {'page': 1, 'per_page': 25}},
            '/character/{id}': {'method': 'GET', 'ids': range(1, 11)},  # Warm first 10 characters
            
            # World endpoints
            '/regions/': {'method': 'GET', 'params': {'page': 1, 'per_page': 25}},
            '/locations/': {'method': 'GET', 'params': {'page': 1, 'per_page': 25}},
            
            # Social endpoints
            '/relationships/': {'method': 'GET', 'params': {'page': 1, 'per_page': 25}},
            '/interactions/': {'method': 'GET', 'params': {'page': 1, 'per_page': 25}}
        }
        self.warm_interval = timedelta(minutes=4)  # Warm up 1 minute before 5-minute cache expires
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize with Flask application."""
        self.app = app
        self.base_url = app.config.get('BASE_URL', 'http://localhost:5000')
        self.warm_interval = timedelta(minutes=app.config.get('CACHE_WARM_INTERVAL_MINUTES', 4))
        
        # Start warming thread
        self.start_warming()
    
    def warm_endpoint(self, endpoint: str, config: Dict[str, Any]):
        """Warm up a specific endpoint."""
        try:
            method = config['method']
            url = f"{self.base_url}{endpoint}"
            
            if '{id}' in endpoint:
                # Handle parameterized endpoints
                for id in config.get('ids', []):
                    specific_url = url.format(id=id)
                    response = requests.request(method, specific_url)
                    if response.status_code == 200:
                        logger.debug(f"Warmed cache for {specific_url}")
                    else:
                        logger.warning(f"Failed to warm cache for {specific_url}: {response.status_code}")
            else:
                # Handle regular endpoints
                params = config.get('params', {})
                response = requests.request(method, url, params=params)
                if response.status_code == 200:
                    logger.debug(f"Warmed cache for {url}")
                else:
                    logger.warning(f"Failed to warm cache for {url}: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error warming cache for {endpoint}: {str(e)}")
    
    def warm_all_endpoints(self):
        """Warm up all critical endpoints."""
        logger.info("Starting cache warm-up cycle")
        for endpoint, config in self.critical_endpoints.items():
            if self.stop_warming:
                break
            self.warm_endpoint(endpoint, config)
        logger.info("Completed cache warm-up cycle")
    
    def warming_loop(self):
        """Main cache warming loop."""
        while not self.stop_warming:
            with self.app.app_context():
                self.warm_all_endpoints()
            
            # Sleep until next warm-up cycle
            for _ in range(int(self.warm_interval.total_seconds())):
                if self.stop_warming:
                    break
                time.sleep(1)
    
    def start_warming(self):
        """Start the cache warming thread."""
        if self.warming_thread is None or not self.warming_thread.is_alive():
            self.stop_warming = False
            self.warming_thread = threading.Thread(target=self.warming_loop)
            self.warming_thread.daemon = True
            self.warming_thread.start()
            logger.info("Cache warming thread started")
    
    def stop(self):
        """Stop the cache warming thread."""
        self.stop_warming = True
        if self.warming_thread:
            self.warming_thread.join()
            logger.info("Cache warming thread stopped")

# Initialize cache warmer
cache_warmer = CacheWarmer()

def init_cache_warmer(app: Flask):
    """Initialize cache warmer for the application."""
    cache_warmer.init_app(app) 