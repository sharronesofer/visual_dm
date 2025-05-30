"""
Test configuration and fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add backend to Python path
backend_root = Path(__file__).parents[3]  # Adjust based on depth
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        "id": 1,
        "name": "test_item",
        "value": 100
    }

@pytest.fixture
def mock_config():
    """Provide mock configuration."""
    return {
        "test_mode": True,
        "debug": True
    }
