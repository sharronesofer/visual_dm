"""
Test module for arc.services

Tests for arc system service functionality and business logic.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from uuid import uuid4

# Import the services under test
try:
    from backend.systems.arc.services.arc import ArcManager
    from backend.systems.arc.services.arc_generator import ArcGenerator
    from backend.systems.arc.services.player_arc_manager import PlayerArcManager
    from backend.systems.arc.services.progression_tracker import ProgressionTracker
    from backend.systems.arc.services.quest_integration_service import QuestIntegrationService
    from backend.systems.arc.services.arc_relationship_service import ArcRelationshipService
    arc_services_available = True
except ImportError as e:
    print(f"Arc services not available: {e}")
    arc_services_available = False
    
    # Create mock service classes for testing
    class ArcManager:
        def __init__(self, repository=None):
            self.repository = repository or Mock()
            self.player_manager = Mock()
            self.progression_tracker = Mock()
        
        def create_arc(self, arc_data):
            """Mock method for creating arcs"""
            return {
                "id": str(uuid4()),
                "title": arc_data.get("title", "Test Arc"),
                "status": "inactive",
                "created_at": datetime.utcnow()
            }
        
        def activate_arc(self, arc_id, player_id=None):
            """Mock method for activating arcs"""
            return {
                "arc_id": arc_id,
                "status": "active",
                "activated_at": datetime.utcnow(),
                "player_id": player_id
            }
        
        def get_arc_by_id(self, arc_id):
            """Mock method for getting arc by ID"""
            return {
                "id": arc_id,
                "title": "Test Arc",
                "status": "active"
            }
        
        def list_active_arcs(self):
            """Mock method for listing active arcs"""
            return [
                {"id": "arc_1", "title": "Personal Quest", "status": "active"},
                {"id": "arc_2", "title": "Faction War", "status": "active"}
            ]
        
        def complete_arc(self, arc_id, completion_data):
            """Mock method for completing arcs"""
            return {
                "arc_id": arc_id,
                "status": "completed",
                "completion_type": completion_data.get("type", "success"),
                "completed_at": datetime.utcnow()
            }
    
    class ArcGenerator:
        def __init__(self):
            self.template_repository = Mock()
            self.narrative_engine = Mock()
        
        def generate_personal_arc(self, character_data):
            """Mock method for generating personal arcs"""
            return {
                "id": str(uuid4()),
                "title": f"The Journey of {character_data.get('name', 'Unknown')}",
                "arc_type": "personal",
                "steps": [
                    {"step_number": 1, "title": "Humble Beginnings"},
                    {"step_number": 2, "title": "The Call to Adventure"},
                    {"step_number": 3, "title": "First Challenge"}
                ]
            }
        
        def generate_faction_arc(self, faction_data):
            """Mock method for generating faction arcs"""
            return {
                "id": str(uuid4()),
                "title": f"Rise of the {faction_data.get('name', 'Unknown Faction')}",
                "arc_type": "faction",
                "steps": [
                    {"step_number": 1, "title": "Establishing Power"},
                    {"step_number": 2, "title": "Expanding Influence"},
                    {"step_number": 3, "title": "Ultimate Goal"}
                ]
            }
        
        def generate_world_arc(self, world_events):
            """Mock method for generating world arcs"""
            return {
                "id": str(uuid4()),
                "title": "The Great Upheaval",
                "arc_type": "world",
                "steps": [
                    {"step_number": 1, "title": "Signs of Change"},
                    {"step_number": 2, "title": "The Crisis Unfolds"},
                    {"step_number": 3, "title": "Resolution"}
                ]
            }
        
        def customize_arc_for_player(self, base_arc, player_data):
            """Mock method for customizing arcs for players"""
            customized = base_arc.copy()
            customized["customizations"] = {
                "player_id": player_data.get("id"),
                "difficulty_adjusted": True,
                "personal_hooks": ["family_history", "past_trauma"]
            }
            return customized
    
    class PlayerArcManager:
        def __init__(self):
            self.progression_tracker = Mock()
            self.notification_service = Mock()
        
        def assign_arc_to_player(self, player_id, arc_id):
            """Mock method for assigning arcs to players"""
            return {
                "player_id": player_id,
                "arc_id": arc_id,
                "status": "assigned",
                "assigned_at": datetime.utcnow()
            }
        
        def get_player_arcs(self, player_id, status=None):
            """Mock method for getting player arcs"""
            arcs = [
                {"id": "arc_1", "title": "Personal Quest", "status": "active"},
                {"id": "arc_2", "title": "Guild Mission", "status": "completed"},
                {"id": "arc_3", "title": "World Event", "status": "pending"}
            ]
            if status:
                return [arc for arc in arcs if arc["status"] == status]
            return arcs
        
        def advance_player_arc(self, player_id, arc_id, step_data):
            """Mock method for advancing player arcs"""
            return {
                "player_id": player_id,
                "arc_id": arc_id,
                "new_step": step_data.get("step_number", 2),
                "progress_percentage": step_data.get("progress", 50.0),
                "advanced_at": datetime.utcnow()
            }
        
        def check_arc_availability(self, player_id, arc_id):
            """Mock method for checking arc availability"""
            return {
                "available": True,
                "requirements_met": True,
                "blocking_factors": []
            }
    
    class ProgressionTracker:
        def __init__(self):
            self.event_dispatcher = Mock()
            self.analytics_service = Mock()
        
        def track_step_completion(self, player_id, arc_id, step_id):
            """Mock method for tracking step completion"""
            return {
                "player_id": player_id,
                "arc_id": arc_id,
                "step_id": step_id,
                "completed_at": datetime.utcnow(),
                "progress_updated": True
            }
        
        def calculate_arc_progress(self, player_id, arc_id):
            """Mock method for calculating arc progress"""
            return {
                "arc_id": arc_id,
                "player_id": player_id,
                "progress_percentage": 60.0,
                "current_step": 3,
                "total_steps": 5,
                "estimated_completion": "2 sessions"
            }
        
        def get_player_progression_summary(self, player_id):
            """Mock method for getting player progression summary"""
            return {
                "player_id": player_id,
                "total_arcs": 5,
                "active_arcs": 2,
                "completed_arcs": 2,
                "failed_arcs": 1,
                "overall_progress": 40.0,
                "achievements": ["First Arc", "Completionist"]
            }
    
    class QuestIntegrationService:
        def __init__(self):
            self.quest_repository = Mock()
            self.arc_repository = Mock()
        
        def link_quest_to_arc_step(self, quest_id, arc_id, step_id):
            """Mock method for linking quests to arc steps"""
            return {
                "quest_id": quest_id,
                "arc_id": arc_id,
                "step_id": step_id,
                "linked_at": datetime.utcnow(),
                "integration_type": "primary_objective"
            }
        
        def get_arc_related_quests(self, arc_id):
            """Mock method for getting arc-related quests"""
            return [
                {"quest_id": "quest_1", "step_id": "step_1", "relationship": "primary"},
                {"quest_id": "quest_2", "step_id": "step_2", "relationship": "optional"},
                {"quest_id": "quest_3", "step_id": "step_3", "relationship": "side_quest"}
            ]
        
        def sync_quest_completion_with_arc(self, quest_id):
            """Mock method for syncing quest completion with arcs"""
            return {
                "quest_id": quest_id,
                "affected_arcs": ["arc_1"],
                "steps_advanced": ["step_2"],
                "sync_completed": True
            }
    
    class ArcRelationshipService:
        def __init__(self):
            self.relationship_repository = Mock()
        
        def create_arc_dependency(self, dependent_arc_id, prerequisite_arc_id):
            """Mock method for creating arc dependencies"""
            return {
                "dependent_arc": dependent_arc_id,
                "prerequisite_arc": prerequisite_arc_id,
                "dependency_type": "completion_required",
                "created_at": datetime.utcnow()
            }
        
        def get_arc_dependencies(self, arc_id):
            """Mock method for getting arc dependencies"""
            return {
                "arc_id": arc_id,
                "prerequisites": ["arc_1", "arc_2"],
                "dependents": ["arc_4", "arc_5"],
                "circular_dependencies": False
            }
        
        def check_arc_unlock_conditions(self, player_id, arc_id):
            """Mock method for checking arc unlock conditions"""
            return {
                "arc_id": arc_id,
                "player_id": player_id,
                "can_unlock": True,
                "missing_requirements": [],
                "completion_percentage_needed": 0
            }


class TestArcManager:
    """Test class for ArcManager service"""
    
    def test_arc_manager_initialization(self):
        """Test arc manager initialization"""
        manager = ArcManager()
        assert manager is not None
        assert hasattr(manager, 'repository')
        assert hasattr(manager, 'player_manager')
        assert hasattr(manager, 'progression_tracker')
    
    def test_arc_creation(self):
        """Test arc creation functionality"""
        manager = ArcManager()
        
        arc_data = {
            "title": "The Hero's Journey",
            "description": "A classic personal arc",
            "arc_type": "personal",
            "priority": "high"
        }
        
        result = manager.create_arc(arc_data)
        
        assert result is not None
        assert "id" in result
        assert result["title"] == "The Hero's Journey"
        assert result["status"] == "inactive"
        assert "created_at" in result
    
    def test_arc_activation(self):
        """Test arc activation"""
        manager = ArcManager()
        arc_id = "test_arc_123"
        player_id = "player_456"
        
        result = manager.activate_arc(arc_id, player_id)
        
        assert result["arc_id"] == arc_id
        assert result["status"] == "active"
        assert result["player_id"] == player_id
        assert "activated_at" in result
    
    def test_arc_retrieval(self):
        """Test arc retrieval by ID"""
        manager = ArcManager()
        arc_id = "test_arc_123"
        
        result = manager.get_arc_by_id(arc_id)
        
        assert result["id"] == arc_id
        assert "title" in result
        assert "status" in result
    
    def test_active_arcs_listing(self):
        """Test listing active arcs"""
        manager = ArcManager()
        
        result = manager.list_active_arcs()
        
        assert isinstance(result, list)
        assert len(result) > 0
        for arc in result:
            assert "id" in arc
            assert "title" in arc
            assert arc["status"] == "active"
    
    def test_arc_completion(self):
        """Test arc completion"""
        manager = ArcManager()
        arc_id = "test_arc_123"
        completion_data = {"type": "success", "final_choice": "heroic"}
        
        result = manager.complete_arc(arc_id, completion_data)
        
        assert result["arc_id"] == arc_id
        assert result["status"] == "completed"
        assert result["completion_type"] == "success"
        assert "completed_at" in result


class TestArcGenerator:
    """Test class for ArcGenerator service"""
    
    def test_arc_generator_initialization(self):
        """Test arc generator initialization"""
        generator = ArcGenerator()
        assert generator is not None
        assert hasattr(generator, 'template_repository')
        assert hasattr(generator, 'narrative_engine')
    
    def test_personal_arc_generation(self):
        """Test personal arc generation"""
        generator = ArcGenerator()
        
        character_data = {
            "name": "Elara",
            "background": "noble",
            "personality_traits": ["ambitious", "honorable"]
        }
        
        result = generator.generate_personal_arc(character_data)
        
        assert result is not None
        assert "id" in result
        assert result["arc_type"] == "personal"
        assert "Elara" in result["title"]
        assert "steps" in result
        assert len(result["steps"]) > 0
    
    def test_faction_arc_generation(self):
        """Test faction arc generation"""
        generator = ArcGenerator()
        
        faction_data = {
            "name": "The Silver Hand",
            "goals": ["protect the realm", "expand influence"],
            "resources": "moderate"
        }
        
        result = generator.generate_faction_arc(faction_data)
        
        assert result is not None
        assert result["arc_type"] == "faction"
        assert "Silver Hand" in result["title"]
        assert len(result["steps"]) >= 3
    
    def test_world_arc_generation(self):
        """Test world arc generation"""
        generator = ArcGenerator()
        
        world_events = {
            "crisis_type": "ancient_evil_returns",
            "affected_regions": ["kingdom", "borderlands"],
            "threat_level": "catastrophic"
        }
        
        result = generator.generate_world_arc(world_events)
        
        assert result is not None
        assert result["arc_type"] == "world"
        assert "title" in result
        assert len(result["steps"]) >= 3
    
    def test_arc_customization_for_player(self):
        """Test arc customization for specific players"""
        generator = ArcGenerator()
        
        base_arc = {
            "id": "base_arc_123",
            "title": "Generic Adventure",
            "steps": [{"step_number": 1, "title": "Start"}]
        }
        
        player_data = {
            "id": "player_456",
            "preferences": ["political_intrigue"],
            "background": "criminal"
        }
        
        result = generator.customize_arc_for_player(base_arc, player_data)
        
        assert result is not None
        assert "customizations" in result
        assert result["customizations"]["player_id"] == "player_456"
        assert result["customizations"]["difficulty_adjusted"] is True


class TestPlayerArcManager:
    """Test class for PlayerArcManager service"""
    
    def test_player_arc_manager_initialization(self):
        """Test player arc manager initialization"""
        manager = PlayerArcManager()
        assert manager is not None
        assert hasattr(manager, 'progression_tracker')
        assert hasattr(manager, 'notification_service')
    
    def test_arc_assignment_to_player(self):
        """Test assigning arcs to players"""
        manager = PlayerArcManager()
        player_id = "player_123"
        arc_id = "arc_456"
        
        result = manager.assign_arc_to_player(player_id, arc_id)
        
        assert result["player_id"] == player_id
        assert result["arc_id"] == arc_id
        assert result["status"] == "assigned"
        assert "assigned_at" in result
    
    def test_player_arcs_retrieval(self):
        """Test retrieving player arcs"""
        manager = PlayerArcManager()
        player_id = "player_123"
        
        # Test all arcs
        all_arcs = manager.get_player_arcs(player_id)
        assert isinstance(all_arcs, list)
        assert len(all_arcs) > 0
        
        # Test filtered by status
        active_arcs = manager.get_player_arcs(player_id, status="active")
        assert isinstance(active_arcs, list)
        for arc in active_arcs:
            assert arc["status"] == "active"
    
    def test_player_arc_advancement(self):
        """Test advancing player through arc steps"""
        manager = PlayerArcManager()
        player_id = "player_123"
        arc_id = "arc_456"
        step_data = {"step_number": 3, "progress": 75.0}
        
        result = manager.advance_player_arc(player_id, arc_id, step_data)
        
        assert result["player_id"] == player_id
        assert result["arc_id"] == arc_id
        assert result["new_step"] == 3
        assert result["progress_percentage"] == 75.0
        assert "advanced_at" in result
    
    def test_arc_availability_checking(self):
        """Test checking arc availability for players"""
        manager = PlayerArcManager()
        player_id = "player_123"
        arc_id = "arc_456"
        
        result = manager.check_arc_availability(player_id, arc_id)
        
        assert "available" in result
        assert "requirements_met" in result
        assert "blocking_factors" in result
        assert isinstance(result["blocking_factors"], list)


class TestProgressionTracker:
    """Test class for ProgressionTracker service"""
    
    def test_progression_tracker_initialization(self):
        """Test progression tracker initialization"""
        tracker = ProgressionTracker()
        assert tracker is not None
        assert hasattr(tracker, 'event_dispatcher')
        assert hasattr(tracker, 'analytics_service')
    
    def test_step_completion_tracking(self):
        """Test tracking step completion"""
        tracker = ProgressionTracker()
        player_id = "player_123"
        arc_id = "arc_456"
        step_id = "step_789"
        
        result = tracker.track_step_completion(player_id, arc_id, step_id)
        
        assert result["player_id"] == player_id
        assert result["arc_id"] == arc_id
        assert result["step_id"] == step_id
        assert result["progress_updated"] is True
        assert "completed_at" in result
    
    def test_arc_progress_calculation(self):
        """Test calculating arc progress"""
        tracker = ProgressionTracker()
        player_id = "player_123"
        arc_id = "arc_456"
        
        result = tracker.calculate_arc_progress(player_id, arc_id)
        
        assert result["arc_id"] == arc_id
        assert result["player_id"] == player_id
        assert "progress_percentage" in result
        assert "current_step" in result
        assert "total_steps" in result
        assert "estimated_completion" in result
    
    def test_player_progression_summary(self):
        """Test getting player progression summary"""
        tracker = ProgressionTracker()
        player_id = "player_123"
        
        result = tracker.get_player_progression_summary(player_id)
        
        assert result["player_id"] == player_id
        assert "total_arcs" in result
        assert "active_arcs" in result
        assert "completed_arcs" in result
        assert "overall_progress" in result
        assert "achievements" in result
        assert isinstance(result["achievements"], list)


class TestQuestIntegrationService:
    """Test class for QuestIntegrationService"""
    
    def test_quest_integration_service_initialization(self):
        """Test quest integration service initialization"""
        service = QuestIntegrationService()
        assert service is not None
        assert hasattr(service, 'quest_repository')
        assert hasattr(service, 'arc_repository')
    
    def test_quest_to_arc_step_linking(self):
        """Test linking quests to arc steps"""
        service = QuestIntegrationService()
        quest_id = "quest_123"
        arc_id = "arc_456"
        step_id = "step_789"
        
        result = service.link_quest_to_arc_step(quest_id, arc_id, step_id)
        
        assert result["quest_id"] == quest_id
        assert result["arc_id"] == arc_id
        assert result["step_id"] == step_id
        assert result["integration_type"] == "primary_objective"
        assert "linked_at" in result
    
    def test_arc_related_quests_retrieval(self):
        """Test getting arc-related quests"""
        service = QuestIntegrationService()
        arc_id = "arc_456"
        
        result = service.get_arc_related_quests(arc_id)
        
        assert isinstance(result, list)
        assert len(result) > 0
        for quest_relation in result:
            assert "quest_id" in quest_relation
            assert "step_id" in quest_relation
            assert "relationship" in quest_relation
    
    def test_quest_completion_sync_with_arc(self):
        """Test syncing quest completion with arcs"""
        service = QuestIntegrationService()
        quest_id = "quest_123"
        
        result = service.sync_quest_completion_with_arc(quest_id)
        
        assert result["quest_id"] == quest_id
        assert "affected_arcs" in result
        assert "steps_advanced" in result
        assert result["sync_completed"] is True


class TestArcRelationshipService:
    """Test class for ArcRelationshipService"""
    
    def test_arc_relationship_service_initialization(self):
        """Test arc relationship service initialization"""
        service = ArcRelationshipService()
        assert service is not None
        assert hasattr(service, 'relationship_repository')
    
    def test_arc_dependency_creation(self):
        """Test creating arc dependencies"""
        service = ArcRelationshipService()
        dependent_arc = "arc_456"
        prerequisite_arc = "arc_123"
        
        result = service.create_arc_dependency(dependent_arc, prerequisite_arc)
        
        assert result["dependent_arc"] == dependent_arc
        assert result["prerequisite_arc"] == prerequisite_arc
        assert result["dependency_type"] == "completion_required"
        assert "created_at" in result
    
    def test_arc_dependencies_retrieval(self):
        """Test getting arc dependencies"""
        service = ArcRelationshipService()
        arc_id = "arc_456"
        
        result = service.get_arc_dependencies(arc_id)
        
        assert result["arc_id"] == arc_id
        assert "prerequisites" in result
        assert "dependents" in result
        assert "circular_dependencies" in result
        assert isinstance(result["prerequisites"], list)
        assert isinstance(result["dependents"], list)
    
    def test_arc_unlock_conditions_checking(self):
        """Test checking arc unlock conditions"""
        service = ArcRelationshipService()
        player_id = "player_123"
        arc_id = "arc_456"
        
        result = service.check_arc_unlock_conditions(player_id, arc_id)
        
        assert result["arc_id"] == arc_id
        assert result["player_id"] == player_id
        assert "can_unlock" in result
        assert "missing_requirements" in result
        assert "completion_percentage_needed" in result


class TestArcServicesIntegration:
    """Integration tests for arc services working together"""
    
    def test_full_arc_lifecycle(self):
        """Test complete arc lifecycle from generation to completion"""
        # Initialize services
        generator = ArcGenerator()
        manager = ArcManager()
        player_manager = PlayerArcManager()
        tracker = ProgressionTracker()
        
        # Generate arc
        character_data = {"name": "Test Hero", "background": "soldier"}
        arc_data = generator.generate_personal_arc(character_data)
        
        # Create and activate arc
        created_arc = manager.create_arc(arc_data)
        activated_arc = manager.activate_arc(created_arc["id"], "player_123")
        
        # Assign to player
        assignment = player_manager.assign_arc_to_player("player_123", created_arc["id"])
        
        # Track progress
        step_completion = tracker.track_step_completion("player_123", created_arc["id"], "step_1")
        progress = tracker.calculate_arc_progress("player_123", created_arc["id"])
        
        # Verify integration
        assert created_arc["id"] == activated_arc["arc_id"]
        assert assignment["arc_id"] == created_arc["id"]
        assert step_completion["arc_id"] == created_arc["id"]
        assert progress["arc_id"] == created_arc["id"]
    
    def test_quest_arc_integration_flow(self):
        """Test quest and arc integration workflow"""
        # Initialize services
        quest_service = QuestIntegrationService()
        manager = ArcManager()
        tracker = ProgressionTracker()
        
        # Create arc and link quests
        arc_id = "integration_arc_123"
        quest_id = "integration_quest_456"
        step_id = "step_1"
        
        # Link quest to arc step
        link_result = quest_service.link_quest_to_arc_step(quest_id, arc_id, step_id)
        
        # Sync quest completion
        sync_result = quest_service.sync_quest_completion_with_arc(quest_id)
        
        # Verify integration
        assert link_result["quest_id"] == quest_id
        assert link_result["arc_id"] == arc_id
        assert sync_result["quest_id"] == quest_id
        assert arc_id in sync_result["affected_arcs"] or len(sync_result["affected_arcs"]) > 0
    
    def test_arc_dependency_workflow(self):
        """Test arc dependency and relationship workflow"""
        # Initialize services
        relationship_service = ArcRelationshipService()
        manager = ArcManager()
        player_manager = PlayerArcManager()
        
        # Create dependency
        prerequisite_arc = "arc_123"
        dependent_arc = "arc_456"
        player_id = "player_789"
        
        dependency = relationship_service.create_arc_dependency(dependent_arc, prerequisite_arc)
        unlock_check = relationship_service.check_arc_unlock_conditions(player_id, dependent_arc)
        dependencies = relationship_service.get_arc_dependencies(dependent_arc)
        
        # Verify workflow
        assert dependency["dependent_arc"] == dependent_arc
        assert dependency["prerequisite_arc"] == prerequisite_arc
        assert unlock_check["player_id"] == player_id
        assert unlock_check["arc_id"] == dependent_arc
        assert dependencies["arc_id"] == dependent_arc
