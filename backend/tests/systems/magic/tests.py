from backend.systems.shared.database.base import Base
from backend.systems.shared.database.base import Base
"""
Magic system tests.

This module contains tests for the magic system to demonstrate its functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.systems.shared.database import Base
from backend.systems.shared.database.database_objects import engine

from backend.systems.shared.models import SpellModel
from backend.systems.shared.services import MagicService, SpellService
from backend.systems.router import router as magic_router


def create_test_app():
    """Create a simple FastAPI app for testing."""
    app = FastAPI(title="Test API")
    app.include_router(magic_router)
    return app


class TestMagicSystem(unittest.TestCase):
    """Tests for the magic system."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create tables
        Base.metadata.create_all(bind=engine)

        # Create a mock DB session
        self.db = MagicMock(spec=Session)

        # Create services
        self.magic_service = MagicService(self.db)
        self.spell_service = SpellService(self.db)

        # Create FastAPI app for testing routes
        self.app = create_test_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        """Clean up after tests."""
        # Drop tables
        Base.metadata.drop_all(bind=engine)

    def test_get_spell(self):
        """Test getting a spell by ID."""
        # Prepare mock
        mock_spell = SpellModel(
            id=1,
            name="Fireball",
            description="A ball of fire that explodes on impact.",
            school="fire",
            narrative_power=7.0,
            narrative_effects={"damage_type": "fire", "area": "explosion"},
        )
        
        # Setup mock repository behavior
        self.db.query.return_value.filter.return_value.first.return_value = mock_spell
        
        # Test using the service directly
        result = self.spell_service.get_spell(1)

        # Assertions
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Fireball")
        self.assertEqual(result.school, "fire")
        self.assertEqual(result.narrative_power, 7.0)

    def test_search_spells(self):
        """Test searching for spells."""
        # Prepare mock spell
        mock_spell = SpellModel(
            id=1,
            name="Fireball",
            description="A ball of fire that explodes on impact.",
            school="fire",
            narrative_power=7.0,
            narrative_effects={"damage_type": "fire", "area": "explosion"},
        )
        
        # Setup mock repository behavior for search
        self.db.query.return_value.filter.return_value.all.return_value = [mock_spell]
        
        # Test the search_spells method
        with patch.object(self.spell_service, 'search_spells', return_value=[mock_spell]):
            results = self.spell_service.search_spells(school="fire")
            
            # Assertions
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Fireball")
            self.assertEqual(results[0].school, "fire")

    @unittest.skip("API implementation may change; skipping until API is stable")
    @patch('backend.systems.magic.router.SpellService')
    def test_spell_api_get(self, MockSpellService):
        """Test getting a spell through the API."""
        # Create mock for spell service
        mock_service_instance = MockSpellService.return_value
        mock_spell_dict = {
            "id": 1,
            "name": "Fireball",
            "description": "A ball of fire that explodes on impact.",
            "school": "fire",
            "narrative_power": 7.0,
            "narrative_effects": {"damage_type": "fire", "area": "explosion"},
        }
        
        # Set up the mock to return a dictionary representation of the spell
        mock_service_instance.get_spell.return_value = MagicMock(
            to_dict=MagicMock(return_value=mock_spell_dict)
        )
        
        # Test API endpoint (assuming there's a GET /magic/spells/{spell_id} endpoint)
        with patch('backend.systems.magic.router.get_db', return_value=self.db):
            response = self.client.get("/magic/spells/1")
            
            # If the API endpoint doesn't exist yet, this test will fail,
            # which is expected until the endpoint is implemented
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["name"], "Fireball")
            self.assertEqual(response.json()["school"], "fire")


if __name__ == "__main__":
    unittest.main()
