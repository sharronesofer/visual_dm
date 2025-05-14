import sys
import os
import types
import pytest
from unittest.mock import MagicMock

# Dynamically import the DI registry and ServiceProvider from app/services/__init__.py
import importlib.util
services_path = os.path.join(os.path.dirname(__file__), '../app/services/__init__.py')
spec = importlib.util.spec_from_file_location('services', services_path)
services = importlib.util.module_from_spec(spec)
spec.loader.exec_module(services)

# Dynamically import RedisService from app/services/redis_service.py
redis_service_path = os.path.join(os.path.dirname(__file__), '../app/services/redis_service.py')
redis_spec = importlib.util.spec_from_file_location('redis_service', redis_service_path)
redis_service_mod = importlib.util.module_from_spec(redis_spec)
redis_spec.loader.exec_module(redis_service_mod)
RedisService = redis_service_mod.RedisService

class DummyService(services.ServiceProvider):
    def __init__(self, value):
        self.value = value
    def health_check(self):
        return True
    def get_value(self):
        return self.value

def test_register_and_get_service():
    dummy = DummyService(42)
    services.register_service('dummy', dummy)
    retrieved = services.get_service('dummy')
    assert retrieved is dummy
    assert retrieved.get_value() == 42
    assert retrieved.health_check() is True

def test_get_service_not_registered():
    with pytest.raises(ValueError):
        services.get_service('not_registered')

def test_redis_service_health_check():
    service = RedisService()
    service.client = MagicMock()
    service.client.ping.return_value = True
    assert service.health_check() is True
    service.client.ping.side_effect = Exception('fail')
    assert service.health_check() is False 