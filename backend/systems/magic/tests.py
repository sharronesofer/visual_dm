"""
Magic system tests.

This module contains tests for the magic system to demonstrate its functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.core.app import create_app

from .models import MagicModel, SpellModel
from .repositories import MagicRepository, SpellRepository
from .services import MagicService, SpellService
from .router import router as magic_router


class TestMagicSystem(unittest.TestCase):
    """Tests for the magic system."""
    
    def setUp(self):
        """Set up the test database and dependencies."""
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Create a mock DB session
        self.db = MagicMock(spec=Session)
        
        # Create repositories
        self.magic_repo = MagicRepository(self.db)
        self.spell_repo = SpellRepository(self.db)
        
        # Create services
        self.magic_service = MagicService(self.db)
        self.spell_service = SpellService(self.db)
        
        # Create FastAPI app for testing routes
        self.app = create_app()
        self.app.include_router(magic_router)
        self.client = TestClient(self.app)
    
    def tearDown(self):
        """Clean up after tests."""
        # Drop tables
        Base.metadata.drop_all(bind=engine)
    
    def test_create_spell(self):
        """Test creating a spell."""
        # Prepare mock
        mock_spell = SpellModel(
            id=1,
            name="Fireball",
            level=3,
            school="fire",
            description="A ball of fire that explodes on impact.",
            casting_time="1 action",
            range="150 feet",
            components=["V", "S", "M"],
            duration="Instantaneous",
            damage_type="fire",
            damage_dice="8d6"
        )
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = None
        self.db.query.return_value.filter.return_value.first.return_value = mock_spell
        
        # Test service
        spell_data = {
            "name": "Fireball",
            "level": 3,
            "school": "fire",
            "description": "A ball of fire that explodes on impact.",
            "casting_time": "1 action",
            "range": "150 feet",
            "components": ["V", "S", "M"],
            "duration": "Instantaneous",
            "damage_type": "fire",
            "damage_dice": "8d6"
        }
        
        result = self.spell_repo.create(spell_data)
        
        # Assertions
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()
    
    def test_get_spell(self):
        """Test getting a spell by ID."""
        # Prepare mock
        mock_spell = SpellModel(
            id=1,
            name="Fireball",
            level=3,
            school="fire",
            description="A ball of fire that explodes on impact.",
            casting_time="1 action",
            range="150 feet",
            components=["V", "S", "M"],
            duration="Instantaneous",
            damage_type="fire",
            damage_dice="8d6"
        )
        self.db.query.return_value.filter.return_value.first.return_value = mock_spell
        
        # Test repository
        result = self.spell_repo.get_by_id(1)
        
        # Assertions
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Fireball")
        self.assertEqual(result.level, 3)
        self.assertEqual(result.school, "fire")
    
    def test_spell_api_create(self):
        """Test creating a spell through the API."""
        # Patch the service
        with patch('backend.systems.magic.services.SpellService.create_spell') as mock_create:
            mock_create.return_value = {
                "id": 1,
                "name": "Fireball",
                "level": 3,
                "school": "fire",
                "description": "A ball of fire that explodes on impact.",
                "casting_time": "1 action",
                "range": "150 feet",
                "components": ["V", "S", "M"],
                "duration": "Instantaneous",
                "damage_type": "fire",
                "damage_dice": "8d6"
            }
            
            # Test API endpoint
            response = self.client.post(
                "/magic/spells",
                json={
                    "name": "Fireball",
                    "level": 3,
                    "school": "fire",
                    "description": "A ball of fire that explodes on impact.",
                    "casting_time": "1 action",
                    "range": "150 feet",
                    "components": ["V", "S", "M"],
                    "duration": "Instantaneous",
                    "damage_type": "fire",
                    "damage_dice": "8d6"
                }
            )
            
            # Assertions
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json()["name"], "Fireball")
            self.assertEqual(response.json()["level"], 3)
            self.assertEqual(response.json()["school"], "fire")


if __name__ == "__main__":
    unittest.main() 