import functools
import hashlib
import pickle
from typing import Callable, Any, Optional
from app.services.redis_service import RedisService

redis_service = RedisService()

def make_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    key_data = (func.__module__, func.__name__, args, frozenset(kwargs.items()))
    raw = pickle.dumps(key_data)
    return hashlib.sha256(raw).hexdigest()

def cached(ttl: Optional[int] = None):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = make_cache_key(func, args, kwargs)
            cached_result = redis_service.get(cache_key)
            if cached_result is not None:
                return pickle.loads(bytes.fromhex(cached_result))
            result = func(*args, **kwargs)
            redis_service.set(cache_key, pickle.dumps(result).hex(), ex=ttl)
            return result
        return wrapper
    return decorator

def invalidate_cache(func: Callable, *args, **kwargs):
    cache_key = make_cache_key(func, args, kwargs)
    redis_service.delete(cache_key) 