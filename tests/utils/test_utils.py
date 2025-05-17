import os
import pytest
import asyncio
from typing import Any, Dict, Optional, Type, TypeVar, Generic
from unittest.mock import MagicMock, patch
from contextlib import contextmanager
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import tempfile
import gzip
import json
import hashlib
import importlib.util
import sys

# Type variable for generic database model
T = TypeVar('T')

# Dynamically import db_health.py for isolated testing
spec = importlib.util.spec_from_file_location("db_health", os.path.abspath("backend/app/utils/db_health.py"))
db_health = importlib.util.module_from_spec(spec)
sys.modules["db_health"] = db_health
spec.loader.exec_module(db_health)

class TestUtils:
    """Base test utilities class with common helper methods."""
    
    @staticmethod
    def get_test_file_path(filename: str) -> str:
        """Get the absolute path of a test file in the test_data directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '..', 'test_data', filename)

    @staticmethod
    def load_json_fixture(filename: str) -> Dict[str, Any]:
        """Load a JSON fixture file from the test_data directory."""
        import json
        file_path = TestUtils.get_test_file_path(filename)
        with open(file_path, 'r') as f:
            return json.load(f)

    @staticmethod
    @contextmanager
    def mock_env(**env_vars):
        """Temporarily mock environment variables."""
        original = dict(os.environ)
        os.environ.update(env_vars)
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(original)

    @staticmethod
    def create_mock_response(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> MagicMock:
        """Create a mock response object for testing HTTP clients."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.ok = 200 <= status_code < 300
        mock_response.json.return_value = json_data or {}
        mock_response.text = text or ''
        mock_response.headers = headers or {}
        return mock_response

    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC datetime for consistent testing."""
        return datetime.now(timezone.utc)

    @staticmethod
    def mock_datetime(target_datetime: datetime):
        """Mock the datetime.now() and datetime.utcnow() methods."""
        class MockDateTime:
            @classmethod
            def now(cls, tz=None):
                if tz:
                    return target_datetime.astimezone(tz)
                return target_datetime

            @classmethod
            def utcnow(cls):
                return target_datetime.astimezone(timezone.utc)

        return patch('datetime.datetime', MockDateTime)

class AsyncTestUtils:
    """Utilities for testing async code."""

    @staticmethod
    async def mock_async_context_manager(return_value: Any = None):
        """Create a mock async context manager."""
        class AsyncContextManager:
            async def __aenter__(self):
                return return_value

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        return AsyncContextManager()

    @staticmethod
    def async_return(result: Any):
        """Create a coroutine function that returns the given result."""
        async def mock_coroutine(*args, **kwargs):
            return result
        return mock_coroutine

    @staticmethod
    def async_exception(exception: Exception):
        """Create a coroutine function that raises the given exception."""
        async def mock_coroutine(*args, **kwargs):
            raise exception
        return mock_coroutine

    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
        """Wait for a condition to be true with timeout."""
        start_time = asyncio.get_event_loop().time()
        while not condition_func():
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("Condition not met within timeout")
            await asyncio.sleep(interval)

class DBTestUtils:
    """Utilities for database testing."""

    @staticmethod
    def create_test_model(model_class: Type[T], **kwargs) -> T:
        """Create a test instance of a database model."""
        instance = model_class()
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance

    @staticmethod
    def mock_db_session() -> MagicMock:
        """Create a mock database session."""
        session = MagicMock(spec=Session)
        session.commit = MagicMock()
        session.rollback = MagicMock()
        session.close = MagicMock()
        session.add = MagicMock()
        session.delete = MagicMock()
        session.query = MagicMock(return_value=session)
        session.filter = MagicMock(return_value=session)
        session.first = MagicMock()
        session.all = MagicMock()
        return session

    @staticmethod
    @contextmanager
    def mock_transaction():
        """Mock a database transaction context."""
        try:
            yield
        finally:
            pass  # In a real transaction, this would be rollback

    @staticmethod
    def create_test_models(model_class: Type[T], count: int, **base_kwargs) -> list[T]:
        """Create multiple test instances of a database model."""
        models = []
        for i in range(count):
            kwargs = {**base_kwargs}
            # Add an index to any string values to make them unique
            for key, value in kwargs.items():
                if isinstance(value, str):
                    kwargs[key] = f"{value}_{i}"
            models.append(DBTestUtils.create_test_model(model_class, **kwargs))
        return models

    @staticmethod
    def assert_model_equal(model1: Any, model2: Any, exclude_fields: Optional[list[str]] = None):
        """Assert that two model instances are equal, optionally excluding certain fields."""
        exclude_fields = exclude_fields or []
        exclude_fields.extend(['_sa_instance_state', 'created_at', 'updated_at'])
        
        for field in [f for f in dir(model1) if not f.startswith('_') and f not in exclude_fields]:
            if not callable(getattr(model1, field)):
                assert getattr(model1, field) == getattr(model2, field), \
                    f"Field '{field}' differs: {getattr(model1, field)} != {getattr(model2, field)}"

# Pytest fixtures
@pytest.fixture
def mock_env():
    """Fixture to mock environment variables."""
    return TestUtils.mock_env

@pytest.fixture
def mock_response():
    """Fixture to create mock HTTP responses."""
    return TestUtils.create_mock_response

@pytest.fixture
def event_loop():
    """Fixture to get event loop for async tests."""
    return AsyncTestUtils.get_event_loop()

@pytest.fixture
def mock_db():
    """Fixture to mock database session."""
    return DBTestUtils.mock_db_session

@pytest.fixture
def utc_now():
    """Fixture to get consistent UTC datetime."""
    return TestUtils.utc_now()

@pytest.fixture
def temp_backup_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test backup data")
        yield f.name
    os.remove(f.name)

@pytest.fixture
def temp_manifest_file(temp_backup_file):
    hash_val = db_health.hash_file(temp_backup_file)
    manifest = {"hash": hash_val}
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
        json.dump(manifest, f)
        f.flush()
        os.fsync(f.fileno())
        fname = f.name
    yield fname
    os.remove(fname)

def test_hash_file(temp_backup_file):
    h = db_health.hash_file(temp_backup_file)
    assert isinstance(h, str) and len(h) == 64

def test_verify_manifest_success(temp_backup_file, temp_manifest_file):
    assert db_health.verify_manifest(temp_backup_file, temp_manifest_file)

def test_verify_manifest_hash_mismatch(temp_backup_file):
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
        json.dump({"hash": "bad" * 16}, f)
        manifest_path = f.name
    assert not db_health.verify_manifest(temp_backup_file, manifest_path)
    os.remove(manifest_path)

def test_verify_manifest_missing():
    assert db_health.verify_manifest("nofile", "missing_manifest.json")

def test_decompress_file(tmp_path):
    src = tmp_path / "test.gz"
    dst = tmp_path / "out.txt"
    with gzip.open(src, 'wb') as f:
        f.write(b"hello world")
    db_health.decompress_file(str(src), str(dst))
    with open(dst, 'rb') as f:
        assert f.read() == b"hello world"

def test_decrypt_file(monkeypatch, tmp_path):
    src = tmp_path / "enc.bin"
    dst = tmp_path / "dec.txt"
    key = b"0" * 32
    class DummyFernet:
        def __init__(self, k): pass
        def decrypt(self, data): return b"decrypted"
    monkeypatch.setattr(db_health, "Fernet", DummyFernet)
    with open(src, 'wb') as f:
        f.write(b"encrypted")
    db_health.decrypt_file(str(src), str(dst), key)
    with open(dst, 'rb') as f:
        assert f.read() == b"decrypted"

def test_verify_backup_success(monkeypatch, temp_backup_file, temp_manifest_file):
    monkeypatch.setattr(db_health, "ENCRYPTION_KEY", None)
    assert db_health.verify_backup(temp_backup_file, temp_manifest_file)

def test_verify_backup_hash_mismatch(monkeypatch, temp_backup_file):
    monkeypatch.setattr(db_health, "ENCRYPTION_KEY", None)
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
        json.dump({"hash": "bad" * 16}, f)
        manifest_path = f.name
    assert not db_health.verify_backup(temp_backup_file, manifest_path)
    os.remove(manifest_path)

def test_verify_backup_error(monkeypatch):
    monkeypatch.setattr(db_health, "ENCRYPTION_KEY", None)
    assert not db_health.verify_backup("/nonexistent/file", None) 