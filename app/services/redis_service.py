import redis
import logging
from typing import Any, Optional
from app.services import ServiceProvider

class RedisService(ServiceProvider):
    """
    RedisService provides a Redis client with common operations, suitable for dependency injection.
    Register an instance at app startup using register_service('redis', RedisService(...)).
    Retrieve with get_service('redis').
    """
    def __init__(self, url: Optional[str] = None, host: str = 'localhost', port: int = 6379, db: int = 0, password: Optional[str] = None, max_connections: int = 10):
        self.logger = logging.getLogger('RedisService')
        try:
            if url:
                self.client = redis.Redis.from_url(url, decode_responses=True, max_connections=max_connections)
            else:
                self.client = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True, max_connections=max_connections)
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis client: {e}")
            self.client = None

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        try:
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            self.logger.error(f"Redis SET error: {e}")
            return False

    def get(self, key: str) -> Any:
        try:
            return self.client.get(key)
        except Exception as e:
            self.logger.error(f"Redis GET error: {e}")
            return None

    def delete(self, key: str) -> int:
        try:
            return self.client.delete(key)
        except Exception as e:
            self.logger.error(f"Redis DELETE error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        try:
            return self.client.exists(key) == 1
        except Exception as e:
            self.logger.error(f"Redis EXISTS error: {e}")
            return False

    def ttl(self, key: str) -> int:
        try:
            return self.client.ttl(key)
        except Exception as e:
            self.logger.error(f"Redis TTL error: {e}")
            return -2

    def health_check(self) -> bool:
        try:
            return self.client.ping()
        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            return False 