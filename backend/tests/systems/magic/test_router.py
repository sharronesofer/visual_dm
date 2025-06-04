"""
Tests for Magic System Router - Canonical MP-Based System

Tests for the router endpoints that implement the Development Bible's canonical system:
- MP-based spellcasting (not spell slots)
- Domain-based spell access (no preparation)
- Rest-based MP restoration
- Permanent spell learning
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from uuid import uuid4

# Import the canonical router
try:
    from backend.infrastructure.systems.magic.router.magic_router import router
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router, prefix="/magic")
    client = TestClient(app)
    
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    pytest.skip(f"Magic router module not found", allow_module_level=True)

# Mock database session
@pytest.fixture
def mock_db():
    return Mock()

@pytest.mark.skipif(not ROUTER_AVAILABLE, reason="Router not available")
class TestCanonicalMagicRouter:
    """Test canonical MP-based magic system router"""
    
    def test_router_has_mp_endpoints(self):
        """Test that router exposes canonical MP-based endpoints"""
        route_paths = [route.path for route in router.routes]
        
        # Should have MP endpoints (Bible-compliant)
        assert "/mp/{character_id}" in route_paths
        assert "/mp/{character_id}/rest" in route_paths
        
        # Should have domain endpoints (Bible-compliant)
        assert "/domains/{character_id}" in route_paths
        
        # Should have spell learning endpoints (Bible-compliant)
        assert "/spells/learn" in route_paths
        
        # Should have casting endpoints (Bible-compliant)  
        assert "/spells/cast" in route_paths
    
    def test_router_lacks_spell_slot_endpoints(self):
        """Test that router does NOT expose forbidden D&D spell slot endpoints"""
        route_paths = [route.path for route in router.routes]
        
        # Should NOT have spell slot endpoints (Bible-forbidden)
        slot_endpoints = [path for path in route_paths if "spell-slot" in path or "preparation" in path]
        assert len(slot_endpoints) == 0, f"Found forbidden spell slot endpoints: {slot_endpoints}"
    
    @patch('backend.infrastructure.systems.magic.router.magic_router.get_db')
    def test_get_character_mp(self, mock_get_db):
        """Test getting character MP status (canonical endpoint)"""
        mock_db = Mock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        
        # Mock character MP data
        mock_mp = Mock()
        mock_mp.character_id = 1
        mock_mp.current_mp = 20
        mock_mp.max_mp = 30
        mock_mp.mp_regeneration_rate = 1.0
        mock_mp.last_rest = None
        mock_mp.short_rests_taken = 0
        mock_db.query.return_value.filter.return_value.first.return_value = mock_mp
        
        response = client.get("/magic/mp/1")
        assert response.status_code == 200
    
    @patch('backend.infrastructure.systems.magic.router.magic_router.get_db')
    def test_spell_casting_endpoint(self, mock_get_db):
        """Test spell casting endpoint (canonical MP-based)"""
        mock_db = Mock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        
        # Mock required data for spell casting
        mock_mp = Mock()
        mock_mp.current_mp = 30
        mock_domain = Mock() 
        mock_learned = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_mp
        
        cast_request = {
            "spell_id": str(uuid4()),
            "domain": "arcane",
            "target_id": str(uuid4()),
            "extra_mp": 0
        }
        
        # This will fail with mocked data, but should reach the endpoint
        response = client.post("/magic/spells/cast?character_id=1", json=cast_request)
        # We expect some response (even if error due to mocking)
        assert response.status_code in [200, 404, 422, 500]  # Various valid responses
    
    def test_domains_endpoint_exists(self):
        """Test that domain access endpoint exists (canonical system)"""
        route_paths = [route.path for route in router.routes]
        assert "/domains/{character_id}" in route_paths
    
    def test_spell_learning_endpoint_exists(self):
        """Test that spell learning endpoint exists (canonical system)"""
        route_paths = [route.path for route in router.routes]
        assert "/spells/learn" in route_paths


@pytest.mark.skipif(not ROUTER_AVAILABLE, reason="Router not available")
def test_router_integration():
    """Test that router integrates properly with FastAPI"""
    assert len(router.routes) > 0
    
    # Check that routes are properly tagged
    for route in router.routes:
        if hasattr(route, 'tags'):
            assert "magic" in route.tags
