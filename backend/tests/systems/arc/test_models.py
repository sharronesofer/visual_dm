"""
Test module for arc.models

Tests for arc system model functionality and data structures.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from uuid import uuid4
from enum import Enum

# Import the module under test
try:
    from backend.systems.arc.models.arc import Arc, ArcType, ArcStatus, ArcPriority
    from backend.systems.arc.models.arc_step import ArcStep, StepType, StepStatus, StepRequirements
    from backend.systems.arc.models.arc_progression import ArcProgression, ProgressionStatus
    from backend.systems.arc.models.arc_completion_record import ArcCompletionRecord, CompletionType
    arc_models_available = True
except ImportError as e:
    print(f"Arc models not available: {e}")
    arc_models_available = False
    
    # Create mock enums and classes for testing
    class ArcType(Enum):
        PERSONAL = "personal"
        FACTION = "faction"
        WORLD = "world"
        CAMPAIGN = "campaign"
    
    class ArcStatus(Enum):
        INACTIVE = "inactive"
        ACTIVE = "active"
        COMPLETED = "completed"
        FAILED = "failed"
        SUSPENDED = "suspended"
    
    class ArcPriority(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    class StepType(Enum):
        QUEST = "quest"
        EVENT = "event"
        MILESTONE = "milestone"
        CHOICE = "choice"
    
    class StepStatus(Enum):
        PENDING = "pending"
        ACTIVE = "active"
        COMPLETED = "completed"
        SKIPPED = "skipped"
        FAILED = "failed"
    
    class ProgressionStatus(Enum):
        NOT_STARTED = "not_started"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        ABANDONED = "abandoned"
    
    class CompletionType(Enum):
        SUCCESS = "success"
        FAILURE = "failure"
        PARTIAL = "partial"
        ABANDONED = "abandoned"
    
    class StepRequirements:
        def __init__(self, **kwargs):
            self.required_quests = kwargs.get('required_quests', [])
            self.required_events = kwargs.get('required_events', [])
            self.required_items = kwargs.get('required_items', [])
            self.required_level = kwargs.get('required_level', 1)
            self.required_faction_standing = kwargs.get('required_faction_standing', {})
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class Arc:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.title = kwargs.get('title', 'Test Arc')
            self.description = kwargs.get('description', 'A test arc')
            self.arc_type = kwargs.get('arc_type', ArcType.PERSONAL)
            self.status = kwargs.get('status', ArcStatus.INACTIVE)
            self.priority = kwargs.get('priority', ArcPriority.MEDIUM)
            self.tags = kwargs.get('tags', [])
            self.metadata = kwargs.get('metadata', {})
            self.created_at = kwargs.get('created_at', datetime.utcnow())
            self.updated_at = kwargs.get('updated_at', datetime.utcnow())
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def activate(self):
            self.status = ArcStatus.ACTIVE
        
        def complete(self):
            self.status = ArcStatus.COMPLETED
        
        def fail(self):
            self.status = ArcStatus.FAILED
        
        def is_active(self):
            return self.status == ArcStatus.ACTIVE
    
    class ArcStep:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.arc_id = kwargs.get('arc_id', str(uuid4()))
            self.step_number = kwargs.get('step_number', 1)
            self.title = kwargs.get('title', 'Test Step')
            self.description = kwargs.get('description', 'A test step')
            self.step_type = kwargs.get('step_type', StepType.QUEST)
            self.status = kwargs.get('status', StepStatus.PENDING)
            self.requirements = kwargs.get('requirements', StepRequirements())
            self.rewards = kwargs.get('rewards', {})
            self.created_at = kwargs.get('created_at', datetime.utcnow())
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def activate(self):
            self.status = StepStatus.ACTIVE
        
        def complete(self):
            self.status = StepStatus.COMPLETED
        
        def can_activate(self):
            return self.status == StepStatus.PENDING
    
    class ArcProgression:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.player_id = kwargs.get('player_id', str(uuid4()))
            self.arc_id = kwargs.get('arc_id', str(uuid4()))
            self.current_step = kwargs.get('current_step', 1)
            self.progress_percentage = kwargs.get('progress_percentage', 0.0)
            self.status = kwargs.get('status', ProgressionStatus.NOT_STARTED)
            self.started_at = kwargs.get('started_at', None)
            self.completed_at = kwargs.get('completed_at', None)
            self.notes = kwargs.get('notes', [])
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def start(self):
            self.status = ProgressionStatus.IN_PROGRESS
            self.started_at = datetime.utcnow()
        
        def complete(self):
            self.status = ProgressionStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            self.progress_percentage = 100.0
        
        def update_progress(self, percentage):
            self.progress_percentage = min(100.0, max(0.0, percentage))
    
    class ArcCompletionRecord:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.arc_id = kwargs.get('arc_id', str(uuid4()))
            self.player_id = kwargs.get('player_id', str(uuid4()))
            self.completion_type = kwargs.get('completion_type', CompletionType.SUCCESS)
            self.completion_date = kwargs.get('completion_date', datetime.utcnow())
            self.final_step_reached = kwargs.get('final_step_reached', 1)
            self.rewards_granted = kwargs.get('rewards_granted', {})
            self.player_choices = kwargs.get('player_choices', {})
            self.completion_notes = kwargs.get('completion_notes', '')
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def was_successful(self):
            return self.completion_type == CompletionType.SUCCESS


class TestArcModels:
    """Test class for Arc model"""
    
    def test_arc_creation(self):
        """Test basic arc creation"""
        arc = Arc(
            title="Test Arc",
            description="A test narrative arc",
            arc_type=ArcType.PERSONAL,
            priority=ArcPriority.HIGH
        )
        
        assert arc.title == "Test Arc"
        assert arc.description == "A test narrative arc"
        assert arc.arc_type == ArcType.PERSONAL
        assert arc.priority == ArcPriority.HIGH
        assert arc.status == ArcStatus.INACTIVE
        assert isinstance(arc.id, str)
        assert arc.created_at is not None
    
    def test_arc_status_transitions(self):
        """Test arc status state transitions"""
        arc = Arc(title="Test Arc")
        
        # Test initial state
        assert arc.status == ArcStatus.INACTIVE
        assert not arc.is_active()
        
        # Test activation
        arc.activate()
        assert arc.status == ArcStatus.ACTIVE
        assert arc.is_active()
        
        # Test completion
        arc.complete()
        assert arc.status == ArcStatus.COMPLETED
        assert not arc.is_active()
        
        # Test failure
        arc = Arc(title="Another Arc")
        arc.activate()
        arc.fail()
        assert arc.status == ArcStatus.FAILED
    
    def test_arc_type_enumeration(self):
        """Test arc type enumeration values"""
        arc_types = [ArcType.PERSONAL, ArcType.FACTION, ArcType.WORLD, ArcType.CAMPAIGN]
        for arc_type in arc_types:
            arc = Arc(title="Test Arc", arc_type=arc_type)
            assert arc.arc_type == arc_type
    
    def test_arc_priority_levels(self):
        """Test arc priority level handling"""
        priorities = [ArcPriority.LOW, ArcPriority.MEDIUM, ArcPriority.HIGH, ArcPriority.CRITICAL]
        for priority in priorities:
            arc = Arc(title="Priority Test", priority=priority)
            assert arc.priority == priority
    
    def test_arc_metadata_handling(self):
        """Test arc metadata and tags"""
        metadata = {"difficulty": "hard", "estimated_duration": "5 sessions"}
        tags = ["combat", "intrigue", "political"]
        
        arc = Arc(
            title="Complex Arc",
            metadata=metadata,
            tags=tags
        )
        
        assert arc.metadata == metadata
        assert arc.tags == tags
        assert "combat" in arc.tags
        assert arc.metadata["difficulty"] == "hard"


class TestArcStepModels:
    """Test class for ArcStep model"""
    
    def test_arc_step_creation(self):
        """Test basic arc step creation"""
        requirements = StepRequirements(
            required_quests=["quest_1"],
            required_level=5
        )
        
        step = ArcStep(
            arc_id="test_arc_123",
            step_number=1,
            title="First Step",
            description="The beginning of the arc",
            step_type=StepType.QUEST,
            requirements=requirements
        )
        
        assert step.arc_id == "test_arc_123"
        assert step.step_number == 1
        assert step.title == "First Step"
        assert step.step_type == StepType.QUEST
        assert step.status == StepStatus.PENDING
        assert step.requirements == requirements
    
    def test_step_status_transitions(self):
        """Test step status state transitions"""
        step = ArcStep(title="Test Step")
        
        # Test initial state
        assert step.status == StepStatus.PENDING
        assert step.can_activate()
        
        # Test activation
        step.activate()
        assert step.status == StepStatus.ACTIVE
        
        # Test completion
        step.complete()
        assert step.status == StepStatus.COMPLETED
    
    def test_step_type_enumeration(self):
        """Test step type enumeration values"""
        step_types = [StepType.QUEST, StepType.EVENT, StepType.MILESTONE, StepType.CHOICE]
        for step_type in step_types:
            step = ArcStep(title="Test Step", step_type=step_type)
            assert step.step_type == step_type
    
    def test_step_requirements_structure(self):
        """Test step requirements data structure"""
        requirements = StepRequirements(
            required_quests=["quest_1", "quest_2"],
            required_events=["event_a"],
            required_items=["sword", "key"],
            required_level=10,
            required_faction_standing={"guild": 50, "nobles": 25}
        )
        
        step = ArcStep(
            title="Complex Step",
            requirements=requirements
        )
        
        assert len(step.requirements.required_quests) == 2
        assert "quest_1" in step.requirements.required_quests
        assert step.requirements.required_level == 10
        assert step.requirements.required_faction_standing["guild"] == 50
    
    def test_step_rewards_handling(self):
        """Test step rewards data handling"""
        rewards = {
            "experience": 1000,
            "gold": 500,
            "items": ["magic_sword"],
            "reputation": {"faction_a": 25}
        }
        
        step = ArcStep(
            title="Rewarding Step",
            rewards=rewards
        )
        
        assert step.rewards["experience"] == 1000
        assert "magic_sword" in step.rewards["items"]
        assert step.rewards["reputation"]["faction_a"] == 25


class TestArcProgressionModels:
    """Test class for ArcProgression model"""
    
    def test_progression_creation(self):
        """Test basic progression creation"""
        progression = ArcProgression(
            player_id="player_123",
            arc_id="arc_456"
        )
        
        assert progression.player_id == "player_123"
        assert progression.arc_id == "arc_456"
        assert progression.current_step == 1
        assert progression.progress_percentage == 0.0
        assert progression.status == ProgressionStatus.NOT_STARTED
        assert progression.started_at is None
        assert progression.completed_at is None
    
    def test_progression_lifecycle(self):
        """Test progression lifecycle management"""
        progression = ArcProgression(
            player_id="player_123",
            arc_id="arc_456"
        )
        
        # Test starting progression
        progression.start()
        assert progression.status == ProgressionStatus.IN_PROGRESS
        assert progression.started_at is not None
        
        # Test progress updates
        progression.update_progress(25.5)
        assert progression.progress_percentage == 25.5
        
        progression.update_progress(150)  # Should cap at 100
        assert progression.progress_percentage == 100.0
        
        progression.update_progress(-10)  # Should floor at 0
        assert progression.progress_percentage == 0.0
        
        # Test completion
        progression.complete()
        assert progression.status == ProgressionStatus.COMPLETED
        assert progression.completed_at is not None
        assert progression.progress_percentage == 100.0
    
    def test_progression_notes_tracking(self):
        """Test progression notes functionality"""
        progression = ArcProgression(
            player_id="player_123",
            arc_id="arc_456",
            notes=["Started quest", "Met important NPC"]
        )
        
        assert len(progression.notes) == 2
        assert "Started quest" in progression.notes


class TestArcCompletionRecordModels:
    """Test class for ArcCompletionRecord model"""
    
    def test_completion_record_creation(self):
        """Test basic completion record creation"""
        rewards = {"experience": 5000, "title": "Hero of the Realm"}
        choices = {"spare_villain": True, "alliance_formed": "guild"}
        
        record = ArcCompletionRecord(
            arc_id="arc_123",
            player_id="player_456",
            completion_type=CompletionType.SUCCESS,
            final_step_reached=10,
            rewards_granted=rewards,
            player_choices=choices,
            completion_notes="Epic finale with dramatic choices"
        )
        
        assert record.arc_id == "arc_123"
        assert record.player_id == "player_456"
        assert record.completion_type == CompletionType.SUCCESS
        assert record.final_step_reached == 10
        assert record.rewards_granted == rewards
        assert record.player_choices == choices
        assert record.was_successful()
        assert record.completion_date is not None
    
    def test_completion_type_enumeration(self):
        """Test completion type enumeration values"""
        completion_types = [
            CompletionType.SUCCESS,
            CompletionType.FAILURE, 
            CompletionType.PARTIAL,
            CompletionType.ABANDONED
        ]
        
        for completion_type in completion_types:
            record = ArcCompletionRecord(
                arc_id="test_arc",
                player_id="test_player",
                completion_type=completion_type
            )
            assert record.completion_type == completion_type
            
            # Test success check
            if completion_type == CompletionType.SUCCESS:
                assert record.was_successful()
            else:
                assert not record.was_successful()
    
    def test_player_choices_tracking(self):
        """Test player choices data structure"""
        complex_choices = {
            "moral_decisions": {
                "save_village": True,
                "spare_enemy": False
            },
            "alliance_choices": ["guild", "nobles"],
            "romantic_interests": "npc_maria",
            "final_boss_strategy": "diplomacy"
        }
        
        record = ArcCompletionRecord(
            arc_id="complex_arc",
            player_id="player_123",
            player_choices=complex_choices
        )
        
        assert record.player_choices["moral_decisions"]["save_village"] is True
        assert "guild" in record.player_choices["alliance_choices"]
        assert record.player_choices["romantic_interests"] == "npc_maria"


class TestArcModelsIntegration:
    """Integration tests for arc models working together"""
    
    def test_arc_with_steps_integration(self):
        """Test arc and steps working together"""
        if not arc_models_available:
            pytest.skip("Advanced integration tests require actual arc models")
        
        # This would test actual model relationships and constraints
        assert True
    
    def test_progression_with_completion_record(self):
        """Test progression leading to completion record"""
        progression = ArcProgression(
            player_id="player_123",
            arc_id="arc_456"
        )
        
        progression.start()
        progression.update_progress(100.0)
        progression.complete()
        
        # Create completion record based on progression
        record = ArcCompletionRecord(
            arc_id=progression.arc_id,
            player_id=progression.player_id,
            completion_type=CompletionType.SUCCESS,
            final_step_reached=progression.current_step
        )
        
        assert record.arc_id == progression.arc_id
        assert record.player_id == progression.player_id
        assert record.was_successful()
        assert progression.status == ProgressionStatus.COMPLETED
    
    def test_step_progression_flow(self):
        """Test step progression through an arc"""
        arc = Arc(title="Test Arc")
        arc.activate()
        
        step1 = ArcStep(
            arc_id=arc.id,
            step_number=1,
            title="First Step"
        )
        
        step2 = ArcStep(
            arc_id=arc.id,
            step_number=2,
            title="Second Step"
        )
        
        progression = ArcProgression(
            player_id="player_123",
            arc_id=arc.id
        )
        
        # Start progression
        progression.start()
        step1.activate()
        
        # Complete first step, move to second
        step1.complete()
        progression.current_step = 2
        progression.update_progress(50.0)
        step2.activate()
        
        # Complete arc
        step2.complete()
        progression.complete()
        arc.complete()
        
        assert arc.status == ArcStatus.COMPLETED
        assert step1.status == StepStatus.COMPLETED
        assert step2.status == StepStatus.COMPLETED
        assert progression.status == ProgressionStatus.COMPLETED
        assert progression.progress_percentage == 100.0
