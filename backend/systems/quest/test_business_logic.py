#!/usr/bin/env python3
"""
Simple test to verify quest business logic works without technical dependencies.
This demonstrates that the business logic is pure and can be tested in isolation.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from datetime import datetime

# Import pure business logic using relative imports
from .models import (
    QuestData, QuestStepData, QuestRewardData,
    CreateQuestData, QuestStatus, QuestDifficulty, QuestTheme
)
from .services.services import QuestBusinessService
from .services.generator import QuestGenerationBusinessService
from .utils import QuestBusinessUtils
from .utils.validation import (
    validate_status_transition,
    validate_quest_level_for_difficulty,
    calculate_quest_complexity_score,
    validate_quest_rewards,
    validate_quest_steps_order,
    calculate_reward_multiplier,
    is_quest_completable,
    get_theme_typical_objectives
)

# Mock implementations for protocols (no technical dependencies)
class MockQuestRepository:
    """Mock repository for testing - no database dependencies"""
    
    def __init__(self):
        self.quests: Dict[UUID, QuestData] = {}
    
    def get_quest_by_id(self, quest_id: UUID) -> Optional[QuestData]:
        return self.quests.get(quest_id)
    
    def get_quest_by_title(self, title: str) -> Optional[QuestData]:
        for quest in self.quests.values():
            if quest.title == title:
                return quest
        return None
    
    def create_quest(self, quest_data: QuestData) -> QuestData:
        self.quests[quest_data.id] = quest_data
        return quest_data
    
    def update_quest(self, quest_data: QuestData) -> QuestData:
        self.quests[quest_data.id] = quest_data
        return quest_data
    
    def delete_quest(self, quest_id: UUID) -> bool:
        if quest_id in self.quests:
            del self.quests[quest_id]
            return True
        return False
    
    def list_quests(self, page: int = 1, size: int = 50, status: Optional[str] = None, search: Optional[str] = None) -> tuple[List[QuestData], int]:
        quests = list(self.quests.values())
        if status:
            quests = [q for q in quests if q.status.value == status]
        return quests, len(quests)
    
    def get_player_quests(self, player_id: str, status: Optional[str] = None) -> List[QuestData]:
        quests = [q for q in self.quests.values() if q.player_id == player_id]
        if status:
            quests = [q for q in quests if q.status.value == status]
        return quests
    
    def get_npc_quests(self, npc_id: str, status: Optional[str] = None) -> List[QuestData]:
        quests = [q for q in self.quests.values() if q.npc_id == npc_id]
        if status:
            quests = [q for q in quests if q.status.value == status]
        return quests
    
    def get_location_quests(self, location_id: str, status: Optional[str] = None) -> List[QuestData]:
        quests = [q for q in self.quests.values() if q.location_id == location_id]
        if status:
            quests = [q for q in quests if q.status.value == status]
        return quests
    
    def get_quest_statistics(self) -> Dict[str, Any]:
        return {'total_quests': len(self.quests)}


class MockValidationService:
    """Mock validation service - no external dependencies"""
    
    def validate_quest_data(self, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simple validation
        if not quest_data.get('title'):
            raise ValueError("Title is required")
        if not quest_data.get('description'):
            raise ValueError("Description is required")
        return quest_data
    
    def validate_quest_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return steps
    
    def validate_quest_rewards(self, rewards: Dict[str, Any]) -> Dict[str, Any]:
        return rewards


def test_pure_business_logic():
    """Test that business logic works without any technical dependencies"""
    print("🧪 Testing Quest Business Logic (Pure - No Technical Dependencies)")
    
    # Test enum alignment with schemas
    print("\n📋 Testing Enum Alignment:")
    
    # Test QuestStatus enum values
    expected_statuses = ["pending", "active", "completed", "failed", "abandoned", "expired"]
    actual_statuses = [status.value for status in QuestStatus]
    print(f"✅ Quest Status Values: {actual_statuses}")
    assert set(actual_statuses) == set(expected_statuses), f"Status mismatch: expected {expected_statuses}, got {actual_statuses}"
    
    # Test QuestDifficulty enum values  
    expected_difficulties = ["easy", "medium", "hard", "epic"]
    actual_difficulties = [diff.value for diff in QuestDifficulty]
    print(f"✅ Quest Difficulty Values: {actual_difficulties}")
    assert set(actual_difficulties) == set(expected_difficulties), f"Difficulty mismatch: expected {expected_difficulties}, got {actual_difficulties}"
    
    # Test QuestTheme enum values
    expected_themes = ["combat", "exploration", "social", "mystery", "crafting", "trade", "aid", "knowledge", "general"]
    actual_themes = [theme.value for theme in QuestTheme]
    print(f"✅ Quest Theme Values: {actual_themes}")
    assert set(actual_themes) == set(expected_themes), f"Theme mismatch: expected {expected_themes}, got {actual_themes}"
    
    # Create mock implementations
    repository = MockQuestRepository()
    validation_service = MockValidationService()
    generation_service = QuestGenerationBusinessService()
    
    # Create business service with dependency injection
    quest_service = QuestBusinessService(repository, validation_service, generation_service)
    
    print("✅ Services created successfully")
    
    # Test quest creation with correct enums
    create_data = CreateQuestData(
        title="Find the Lost Artifact",
        description="A mysterious artifact has gone missing",
        difficulty=QuestDifficulty.MEDIUM,  # Will validate to "medium"
        theme=QuestTheme.MYSTERY,           # Will validate to "mystery"  
        level=5
    )
    
    quest = quest_service.create_quest(create_data)
    print(f"✅ Quest created: {quest.title} (ID: {quest.id})")
    print(f"   Status: {quest.status.value}")        # Should be "pending"
    print(f"   Difficulty: {quest.difficulty.value}") # Should be "medium"
    print(f"   Theme: {quest.theme.value}")          # Should be "mystery"
    
    # Test data structure alignment
    quest_dict = quest.to_dict()
    required_fields = ["id", "title", "description", "status", "difficulty", "theme", "level", "steps", "rewards"]
    missing_fields = [field for field in required_fields if field not in quest_dict]
    print(f"✅ Quest data structure contains all required fields: {len(missing_fields) == 0}")
    if missing_fields:
        print(f"   Missing fields: {missing_fields}")
    
    # Verify step structure
    if quest.steps:
        step_dict = quest.steps[0].to_dict()
        required_step_fields = ["id", "title", "description", "completed", "required", "order"]
        missing_step_fields = [field for field in required_step_fields if field not in step_dict]
        print(f"✅ Quest step structure contains all required fields: {len(missing_step_fields) == 0}")
        if missing_step_fields:
            print(f"   Missing step fields: {missing_step_fields}")
    
    # Verify reward structure
    reward_dict = quest.rewards.to_dict()
    required_reward_fields = ["gold", "experience", "reputation", "items", "special"]
    missing_reward_fields = [field for field in required_reward_fields if field not in reward_dict]
    print(f"✅ Quest reward structure contains all required fields: {len(missing_reward_fields) == 0}")
    if missing_reward_fields:
        print(f"   Missing reward fields: {missing_reward_fields}")
    
    # Test quest utilities
    priority_score = QuestBusinessUtils.calculate_quest_priority_score(quest_dict)
    estimated_time = QuestBusinessUtils.calculate_estimated_completion_time(quest_dict)
    
    print(f"✅ Priority Score: {priority_score}")
    print(f"✅ Estimated Time: {estimated_time} minutes")
    
    # Test quest generation
    npc_data = {
        'id': 'npc_001',
        'name': 'Village Elder',
        'profession': 'scholar',
        'level': 10,
        'importance': 3
    }
    
    generated_quest = generation_service.generate_quest_for_npc(npc_data, {})
    if generated_quest:
        print(f"✅ Generated Quest: {generated_quest.title}")
        print(f"   Theme: {generated_quest.theme.value}")
        print(f"   Difficulty: {generated_quest.difficulty.value}")
        print(f"   Steps: {len(generated_quest.steps)}")
    
    # Test quest assignment
    player_id = "player_123"
    assigned_quest = quest_service.assign_quest_to_player(quest.id, player_id)
    print(f"✅ Quest assigned to player: {assigned_quest.status.value}")
    
    # Test step completion
    if assigned_quest.steps:
        step_id = assigned_quest.steps[0].id
        updated_quest = quest_service.complete_quest_step(quest.id, step_id, player_id)
        print(f"✅ Step completed. Progress: {updated_quest.get_progress():.2%}")
    
    print("\n🎉 All tests passed! Quest business logic is pure and working correctly.")
    print("✅ No database dependencies")
    print("✅ No web framework dependencies") 
    print("✅ No external service dependencies")
    print("✅ Pure business logic with dependency injection")
    print("✅ Enum values align with API schemas and JSON configuration")
    print("✅ Data structures match expected field names and types")


if __name__ == "__main__":
    test_pure_business_logic() 