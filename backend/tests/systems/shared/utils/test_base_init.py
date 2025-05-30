from backend.systems.shared.database.base import Base
from backend.systems.shared.database.base import Base
"""
Tests for backend.systems.shared.utils.base.__init__

Tests for the base package compatibility layer.
"""

import pytest


def test_base_init_imports(): pass
    """Test that the base package can be imported and provides BaseManager."""
    from backend.systems.shared.utils.base import BaseManager
    
    # Verify BaseManager is available
    assert BaseManager is not None
    
    # Verify it's the same as the canonical import
    from backend.systems.shared.utils.core.base_manager import BaseManager as CanonicalBaseManager
    assert BaseManager is CanonicalBaseManager


def test_base_init_all_exports(): pass
    """Test that __all__ is properly defined."""
    import backend.systems.shared.utils.base as base_module
    
    assert hasattr(base_module, '__all__')
    assert 'BaseManager' in base_module.__all__
    assert len(base_module.__all__) == 1 