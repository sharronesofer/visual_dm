import pytest
from app import create_app, redis_client
from app.services.redis_service import RedisService
from app.utils.cache import cached, invalidate_cache
import time

@pytest.mark.skipif(redis_client is None, reason="Redis not configured")
def test_redis_connection():
    try:
        redis_client.set('test_key', 'test_value')
        value = redis_client.get('test_key')
        assert value == b'test_value'
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")

redis_service = RedisService()

def test_redis_service_set_get():
    assert redis_service.set('foo', 'bar', ex=2)
    assert redis_service.get('foo') == 'bar'
    time.sleep(2)
    assert redis_service.get('foo') is None

def test_redis_service_ttl():
    redis_service.set('ttl_key', 'baz', ex=1)
    assert redis_service.ttl('ttl_key') > 0
    time.sleep(1.1)
    assert redis_service.get('ttl_key') is None

def test_cached_decorator():
    call_count = {'count': 0}
    @cached(ttl=1)
    def add(x, y):
        call_count['count'] += 1
        return x + y
    assert add(1, 2) == 3
    assert add(1, 2) == 3
    assert call_count['count'] == 1
    time.sleep(1.1)
    assert add(1, 2) == 3
    assert call_count['count'] == 2
    invalidate_cache(add, 1, 2)
    assert add(1, 2) == 3
    assert call_count['count'] == 3 