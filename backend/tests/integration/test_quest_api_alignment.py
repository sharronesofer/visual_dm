"""
Integration tests for Quest API with new schema validation and enum alignment.
Tests verify that API endpoints work correctly with aligned business logic values.
"""

import pytest
import json
from uuid import uuid4
from typing import Dict, Any
from fastapi.testclient import TestClient
from datetime import datetime

# Assuming these imports based on project structure
from backend.main import app
from backend.infrastructure.schemas.quest.quest_schemas import (
    CreateQuestSchema, UpdateQuestSchema, QuestResponseSchema
)

client = TestClient(app)

class TestQuestAPIAlignment:
    """Test suite for quest API alignment with business logic"""
    
    @pytest.fixture
    def valid_quest_data(self) -> Dict[str, Any]:
        """Valid quest data aligned with business logic enums"""
        return {
            "title": "Test Integration Quest",
            "description": "A quest to test API integration with aligned schemas",
            "difficulty": "medium",  # Business logic enum value
            "theme": "mystery",      # Business logic enum value
            "npc_id": str(uuid4()),
            "location_id": str(uuid4()),
            "level": 5,
            "steps": [
                {
                    "id": 1,
                    "description": "Investigate the scene",
                    "type": "investigate",
                    "completed": False,
                    "target_location_id": str(uuid4()),
                    "data": {"clues": []}
                }
            ],
            "rewards": {
                "gold": 100,
                "experience": 250,
                "reputation": {},
                "items": []
            },
            "is_main_quest": False,
            "tags": ["mystery", "investigation"]
        }
    
    def test_create_quest_with_aligned_enums(self, valid_quest_data):
        """Test creating quest with business logic aligned enum values"""
        response = client.post("/quests", json=valid_quest_data)
        
        assert response.status_code == 201, f"Failed to create quest: {response.text}"
        
        quest_data = response.json()
        
        # Verify response contains aligned enum values
        assert quest_data["difficulty"] == "medium"
        assert quest_data["theme"] == "mystery"
        assert "status" in quest_data  # Should have status field
        
        # Verify response structure matches business logic
        assert "npc_id" in quest_data
        assert "level" in quest_data
        assert "steps" in quest_data
        assert "rewards" in quest_data
        
        return quest_data["id"]
    
    def test_create_quest_validates_status_enum(self, valid_quest_data):
        """Test that API rejects invalid status values"""
        # Try to create quest with old enum value
        invalid_data = valid_quest_data.copy()
        
        response = client.post("/quests", json=invalid_data)
        
        # Should succeed with valid data first
        assert response.status_code == 201
        
        # Now test updating with invalid status
        quest_id = response.json()["id"]
        update_data = {"status": "available"}  # Old enum value
        
        response = client.patch(f"/quests/{quest_id}", json=update_data)
        assert response.status_code == 422  # Validation error
        
        # Verify error message mentions valid status values
        error_detail = response.json()["detail"]
        assert any("pending" in str(error) for error in error_detail)
    
    def test_create_quest_validates_difficulty_enum(self, valid_quest_data):
        """Test that API rejects invalid difficulty values"""
        invalid_data = valid_quest_data.copy()
        invalid_data["difficulty"] = "gathering"  # Old invalid value
        
        response = client.post("/quests", json=invalid_data)
        assert response.status_code == 422
        
        # Verify error mentions valid difficulty values
        error_detail = response.json()["detail"]
        assert any("easy" in str(error) and "medium" in str(error) for error in error_detail)
    
    def test_create_quest_validates_theme_enum(self, valid_quest_data):
        """Test that API rejects invalid theme values"""
        invalid_data = valid_quest_data.copy()
        invalid_data["theme"] = "gathering"  # Old invalid value
        
        response = client.post("/quests", json=invalid_data)
        assert response.status_code == 422
        
        # Verify error mentions valid theme values including 'general'
        error_detail = response.json()["detail"]
        assert any("general" in str(error) for error in error_detail)
    
    def test_list_quests_returns_aligned_data(self):
        """Test that listing quests returns data with aligned field names"""
        response = client.get("/quests")
        assert response.status_code == 200
        
        quest_list = response.json()
        
        # Verify response structure
        assert "items" in quest_list
        assert "total" in quest_list
        assert "page" in quest_list
        
        # If quests exist, verify they have aligned fields
        if quest_list["items"]:
            quest = quest_list["items"][0]
            
            # Check for new field names (not old ones)
            assert "status" in quest
            assert "difficulty" in quest
            assert "theme" in quest
            assert "npc_id" in quest or quest.get("npc_id") is None
            
            # Should not have old field names
            assert "quest_status" not in quest
            assert "giver_id" not in quest
    
    def test_get_quest_by_id_returns_aligned_data(self, valid_quest_data):
        """Test that getting individual quest returns aligned data"""
        # Create a quest first
        create_response = client.post("/quests", json=valid_quest_data)
        assert create_response.status_code == 201
        quest_id = create_response.json()["id"]
        
        # Get the quest
        response = client.get(f"/quests/{quest_id}")
        assert response.status_code == 200
        
        quest = response.json()
        
        # Verify aligned field structure
        assert quest["difficulty"] in ["easy", "medium", "hard", "epic"]
        assert quest["theme"] in [
            "combat", "exploration", "social", "mystery", 
            "crafting", "trade", "aid", "knowledge", "general"
        ]
        
        # Verify step structure alignment
        if quest["steps"]:
            step = quest["steps"][0]
            assert "id" in step
            assert "description" in step
            assert "completed" in step
    
    def test_update_quest_with_aligned_enums(self, valid_quest_data):
        """Test updating quest with new aligned enum values"""
        # Create quest
        create_response = client.post("/quests", json=valid_quest_data)
        assert create_response.status_code == 201
        quest_id = create_response.json()["id"]
        
        # Update with valid aligned enum values
        update_data = {
            "status": "active",        # Business logic value
            "difficulty": "hard",      # Business logic value
            "theme": "combat"          # Business logic value
        }
        
        response = client.patch(f"/quests/{quest_id}", json=update_data)
        assert response.status_code == 200
        
        updated_quest = response.json()
        assert updated_quest["status"] == "active"
        assert updated_quest["difficulty"] == "hard"
        assert updated_quest["theme"] == "combat"
    
    def test_quest_action_endpoints_with_new_status(self, valid_quest_data):
        """Test quest action endpoints work with new status values"""
        # Create quest
        create_response = client.post("/quests", json=valid_quest_data)
        assert create_response.status_code == 201
        quest_id = create_response.json()["id"]
        player_id = str(uuid4())
        
        # Test accept quest action
        action_data = {
            "quest_id": quest_id,
            "player_id": player_id,
            "action": "accept"
        }
        
        response = client.post("/quests/actions", json=action_data)
        assert response.status_code == 200
        
        # Verify quest status changed to 'active' (not 'in-progress')
        get_response = client.get(f"/quests/{quest_id}")
        quest = get_response.json()
        assert quest["status"] == "active"  # Business logic status
    
    def test_quest_step_updates_with_new_structure(self, valid_quest_data):
        """Test quest step updates work with new step structure"""
        # Create quest with steps
        create_response = client.post("/quests", json=valid_quest_data)
        assert create_response.status_code == 201
        quest_id = create_response.json()["id"]
        player_id = str(uuid4())
        
        # Update step completion
        step_update_data = {
            "quest_id": quest_id,
            "step_id": 1,  # Using integer ID from business logic
            "completed": True,
            "player_id": player_id
        }
        
        response = client.post("/quests/steps/update", json=step_update_data)
        assert response.status_code == 200
        
        # Verify step was updated
        get_response = client.get(f"/quests/{quest_id}")
        quest = get_response.json()
        
        completed_step = next(
            (step for step in quest["steps"] if step["id"] == 1), 
            None
        )
        assert completed_step is not None
        assert completed_step["completed"] is True
    
    def test_quest_filtering_by_aligned_enums(self):
        """Test quest filtering works with new enum values"""
        # Test filtering by status
        response = client.get("/quests?status=pending")
        assert response.status_code == 200
        
        quest_list = response.json()
        if quest_list["items"]:
            for quest in quest_list["items"]:
                assert quest["status"] == "pending"
        
        # Test filtering by difficulty
        response = client.get("/quests?difficulty=medium")
        assert response.status_code == 200
        
        # Test filtering by theme
        response = client.get("/quests?theme=mystery")
        assert response.status_code == 200
    
    def test_quest_search_works_with_new_structure(self):
        """Test quest search functionality with aligned data"""
        response = client.get("/quests?search=test")
        assert response.status_code == 200
        
        quest_list = response.json()
        # Verify search returns properly structured quests
        if quest_list["items"]:
            quest = quest_list["items"][0]
            assert "status" in quest
            assert "difficulty" in quest
            assert "theme" in quest
    
    def test_quest_statistics_endpoint(self):
        """Test quest statistics endpoint returns data with new enum values"""
        response = client.get("/quests/statistics")
        
        if response.status_code == 200:
            stats = response.json()
            
            # Verify statistics use new enum values
            if "by_status" in stats:
                valid_statuses = {"pending", "active", "completed", "failed", "abandoned", "expired"}
                for status in stats["by_status"].keys():
                    assert status in valid_statuses
            
            if "by_difficulty" in stats:
                valid_difficulties = {"easy", "medium", "hard", "epic"}
                for difficulty in stats["by_difficulty"].keys():
                    assert difficulty in valid_difficulties
    
    def test_quest_export_import_alignment(self, valid_quest_data):
        """Test quest export/import maintains data alignment"""
        # Create quest
        create_response = client.post("/quests", json=valid_quest_data)
        assert create_response.status_code == 201
        quest_id = create_response.json()["id"]
        
        # Export quest (if endpoint exists)
        export_response = client.get(f"/quests/{quest_id}/export")
        
        if export_response.status_code == 200:
            exported_data = export_response.json()
            
            # Verify exported data has aligned structure
            assert exported_data["difficulty"] in ["easy", "medium", "hard", "epic"]
            assert exported_data["theme"] in [
                "combat", "exploration", "social", "mystery", 
                "crafting", "trade", "aid", "knowledge", "general"
            ]
            
            # Verify no old field names
            assert "quest_status" not in exported_data
            assert "giver_id" not in exported_data


@pytest.mark.asyncio
class TestQuestAPIValidation:
    """Additional validation tests for quest API alignment"""
    
    def test_schema_validation_rejects_old_enum_values(self):
        """Test that schema validation properly rejects old enum values"""
        # Test CreateQuestSchema validation
        with pytest.raises(ValueError):
            CreateQuestSchema(
                title="Test",
                description="Test",
                difficulty="gathering",  # Invalid value
                theme="mystery",
                level=1,
                steps=[],
                rewards={"gold": 0, "experience": 0}
            )
    
    def test_schema_validation_accepts_new_enum_values(self):
        """Test that schema validation accepts all new enum values"""
        # Test all valid status values
        valid_statuses = ["pending", "active", "completed", "failed", "abandoned", "expired"]
        for status in valid_statuses:
            update_schema = UpdateQuestSchema(status=status)
            assert update_schema.status == status
        
        # Test all valid difficulty values
        valid_difficulties = ["easy", "medium", "hard", "epic"]
        for difficulty in valid_difficulties:
            create_schema = CreateQuestSchema(
                title="Test",
                description="Test", 
                difficulty=difficulty,
                theme="general",
                level=1,
                steps=[],
                rewards={"gold": 0, "experience": 0}
            )
            assert create_schema.difficulty == difficulty
        
        # Test all valid theme values
        valid_themes = [
            "combat", "exploration", "social", "mystery",
            "crafting", "trade", "aid", "knowledge", "general"
        ]
        for theme in valid_themes:
            create_schema = CreateQuestSchema(
                title="Test",
                description="Test",
                difficulty="medium",
                theme=theme,
                level=1,
                steps=[],
                rewards={"gold": 0, "experience": 0}
            )
            assert create_schema.theme == theme


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"]) 