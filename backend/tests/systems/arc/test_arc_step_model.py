from typing import Any
from typing import Type
from typing import Dict
from dataclasses import field
"""Tests for ArcStep Model

Comprehensive tests for ArcStep model including all methods and edge cases.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Dict, Any

from backend.systems.arc.models.arc_step import (
    ArcStep, ArcStepTag, ArcStepStatus, ArcStepType
)


class TestArcStepTag: pass
    """Test cases for ArcStepTag model"""
    
    def test_tag_creation_minimal(self): pass
        """Test creating a tag with minimal fields"""
        tag = ArcStepTag(key="location", value="forest")
        
        assert tag.key == "location"
        assert tag.value == "forest"
        assert tag.weight == 1.0  # default
        assert tag.required is False  # default
    
    def test_tag_creation_full(self): pass
        """Test creating a tag with all fields"""
        tag = ArcStepTag(
            key="npc",
            value="merchant_guild_leader",
            weight=0.8,
            required=True
        )
        
        assert tag.key == "npc"
        assert tag.value == "merchant_guild_leader"
        assert tag.weight == 0.8
        assert tag.required is True
    
    def test_tag_weight_boundaries(self): pass
        """Test tag weight with boundary values"""
        # Test minimum weight
        tag_min = ArcStepTag(key="skill", value="stealth", weight=0.0)
        assert tag_min.weight == 0.0
        
        # Test maximum weight
        tag_max = ArcStepTag(key="skill", value="combat", weight=1.0)
        assert tag_max.weight == 1.0
        
        # Test above maximum (should be allowed but not recommended)
        tag_high = ArcStepTag(key="faction", value="empire", weight=1.5)
        assert tag_high.weight == 1.5
    
    def test_tag_various_value_types(self): pass
        """Test tag with different value types"""
        # String value
        tag_str = ArcStepTag(key="location", value="dungeon_entrance")
        assert isinstance(tag_str.value, str)
        
        # Integer value
        tag_int = ArcStepTag(key="level_requirement", value=5)
        assert isinstance(tag_int.value, int)
        
        # List value
        tag_list = ArcStepTag(key="required_items", value=["key", "torch"])
        assert isinstance(tag_list.value, list)
        
        # Dict value
        tag_dict = ArcStepTag(key="coordinates", value={"x": 100, "y": 200})
        assert isinstance(tag_dict.value, dict)


class TestArcStep: pass
    """Test cases for ArcStep model"""
    
    @pytest.fixture
    def sample_step(self): pass
        """Sample arc step for testing"""
        return ArcStep(
            arc_id=uuid4(),
            step_index=1,
            title="Investigate Mysterious Disappearances",
            description="Look into the recent vanishings in the village",
            narrative_text="The villagers speak in hushed tones about missing people...",
            step_type=ArcStepType.DISCOVERY,
            completion_criteria={"clues_found": 3, "witnesses_interviewed": 2},
            quest_probability=0.7
        )
    
    def test_arc_step_creation_minimal(self, sample_step): pass
        """Test creating an arc step with minimal required fields"""
        step = ArcStep(
            arc_id=uuid4(),
            step_index=2,
            title="Simple Step",
            description="A simple test step",
            narrative_text="Simple narrative",
            step_type=ArcStepType.NARRATIVE
        )
        
        assert step.title == "Simple Step"
        assert step.step_index == 2
        assert step.status == ArcStepStatus.PENDING  # default
        assert step.quest_probability == 0.3  # default
        assert len(step.tags) == 0  # default
        assert step.attempts == 0  # default
    
    def test_arc_step_creation_full(self, sample_step): pass
        """Test creating an arc step with all fields"""
        assert sample_step.title == "Investigate Mysterious Disappearances"
        assert sample_step.step_type == ArcStepType.DISCOVERY
        assert sample_step.completion_criteria["clues_found"] == 3
        assert sample_step.quest_probability == 0.7
        assert sample_step.status == ArcStepStatus.PENDING
    
    def test_arc_step_enums(self): pass
        """Test all arc step enum values"""
        # Test all step statuses
        for status in ArcStepStatus: pass
            step = ArcStep(
                arc_id=uuid4(),
                step_index=1,
                title="Test Step",
                description="Test",
                narrative_text="Test",
                step_type=ArcStepType.NARRATIVE,
                status=status
            )
            assert step.status == status
        
        # Test all step types
        for step_type in ArcStepType: pass
            step = ArcStep(
                arc_id=uuid4(),
                step_index=1,
                title="Test Step",
                description="Test",
                narrative_text="Test",
                step_type=step_type
            )
            assert step.step_type == step_type
    
    def test_update_timestamp(self, sample_step): pass
        """Test updating timestamp"""
        original_time = sample_step.updated_at
        sample_step.update_timestamp()
        assert sample_step.updated_at > original_time
    
    def test_add_tag(self, sample_step): pass
        """Test adding tags to step"""
        # Add tag with all parameters
        sample_step.add_tag("location", "dark_forest", weight=0.9, required=True)
        
        assert len(sample_step.tags) == 1
        tag = sample_step.tags[0]
        assert tag.key == "location"
        assert tag.value == "dark_forest"
        assert tag.weight == 0.9
        assert tag.required is True
        
        # Add tag with defaults
        sample_step.add_tag("npc", "village_elder")
        
        assert len(sample_step.tags) == 2
        tag2 = sample_step.tags[1]
        assert tag2.key == "npc"
        assert tag2.value == "village_elder"
        assert tag2.weight == 1.0  # default
        assert tag2.required is False  # default
    
    def test_get_tag_value(self, sample_step): pass
        """Test getting tag values"""
        # Add some tags
        sample_step.add_tag("location", "haunted_mansion")
        sample_step.add_tag("faction", "investigators_guild")
        sample_step.add_tag("skill", "investigation", weight=0.8)
        
        # Test getting existing tag values
        assert sample_step.get_tag_value("location") == "haunted_mansion"
        assert sample_step.get_tag_value("faction") == "investigators_guild"
        assert sample_step.get_tag_value("skill") == "investigation"
        
        # Test getting non-existent tag
        assert sample_step.get_tag_value("nonexistent") is None
        assert sample_step.get_tag_value("weapon") is None
    
    def test_get_required_tags(self, sample_step): pass
        """Test getting required tags"""
        # Add mix of required and optional tags
        sample_step.add_tag("location", "crystal_caverns", required=True)
        sample_step.add_tag("npc", "cave_hermit", required=False)
        sample_step.add_tag("item", "magic_crystal", required=True)
        sample_step.add_tag("skill", "spelunking", required=False)
        
        required_tags = sample_step.get_required_tags()
        
        assert len(required_tags) == 2
        required_keys = [tag.key for tag in required_tags]
        assert "location" in required_keys
        assert "item" in required_keys
        assert "npc" not in required_keys
        assert "skill" not in required_keys
    
    def test_get_required_tags_empty(self, sample_step): pass
        """Test getting required tags when none exist"""
        # Add only optional tags
        sample_step.add_tag("location", "anywhere", required=False)
        sample_step.add_tag("npc", "anyone", required=False)
        
        required_tags = sample_step.get_required_tags()
        assert len(required_tags) == 0
    
    def test_is_ready_for_activation(self, sample_step): pass
        """Test checking if step is ready for activation"""
        # Test with PENDING status and no prerequisites
        sample_step.status = ArcStepStatus.PENDING
        sample_step.prerequisite_steps = []
        assert sample_step.is_ready_for_activation() is True
        
        # Test with AVAILABLE status and no prerequisites
        sample_step.status = ArcStepStatus.AVAILABLE
        assert sample_step.is_ready_for_activation() is True
        
        # Test with PENDING status but has prerequisites
        sample_step.status = ArcStepStatus.PENDING
        sample_step.prerequisite_steps = [1, 2]
        assert sample_step.is_ready_for_activation() is False
        
        # Test with wrong status
        sample_step.status = ArcStepStatus.ACTIVE
        sample_step.prerequisite_steps = []
        assert sample_step.is_ready_for_activation() is False
        
        sample_step.status = ArcStepStatus.COMPLETED
        assert sample_step.is_ready_for_activation() is False
    
    def test_start_attempt(self, sample_step): pass
        """Test starting step attempt"""
        # Set step to AVAILABLE status
        sample_step.status = ArcStepStatus.AVAILABLE
        original_attempts = sample_step.attempts
        
        sample_step.start_attempt()
        
        assert sample_step.status == ArcStepStatus.ACTIVE
        assert sample_step.attempts == original_attempts + 1
        assert sample_step.first_attempted is not None
        
        # Test multiple attempts
        sample_step.status = ArcStepStatus.AVAILABLE  # Reset for another attempt
        first_attempt_time = sample_step.first_attempted
        
        sample_step.start_attempt()
        
        assert sample_step.attempts == original_attempts + 2
        assert sample_step.first_attempted == first_attempt_time  # Should not change
    
    def test_start_attempt_wrong_status(self, sample_step): pass
        """Test starting attempt when step is not available"""
        # Test with PENDING status
        sample_step.status = ArcStepStatus.PENDING
        original_attempts = sample_step.attempts
        
        sample_step.start_attempt()
        
        # Should not change anything
        assert sample_step.status == ArcStepStatus.PENDING
        assert sample_step.attempts == original_attempts
        assert sample_step.first_attempted is None
        
        # Test with COMPLETED status
        sample_step.status = ArcStepStatus.COMPLETED
        sample_step.start_attempt()
        
        assert sample_step.status == ArcStepStatus.COMPLETED
        assert sample_step.attempts == original_attempts
    
    def test_complete_step(self, sample_step): pass
        """Test completing step"""
        sample_step.complete_step()
        
        assert sample_step.status == ArcStepStatus.COMPLETED
        assert sample_step.completed_at is not None
        assert isinstance(sample_step.completed_at, datetime)
    
    def test_fail_step(self, sample_step): pass
        """Test failing step"""
        sample_step.fail_step()
        
        assert sample_step.status == ArcStepStatus.FAILED
        assert sample_step.failed_at is not None
        assert isinstance(sample_step.failed_at, datetime)
    
    def test_calculate_tag_match_score_perfect_match(self, sample_step): pass
        """Test tag match score calculation with perfect match"""
        # Add tags with different weights
        sample_step.add_tag("location", "forest", weight=0.8)
        sample_step.add_tag("npc", "ranger", weight=0.6)
        sample_step.add_tag("faction", "nature_guardians", weight=0.4)
        
        context = {
            "location": "forest",
            "npc": "ranger",
            "faction": "nature_guardians"
        }
        
        score = sample_step.calculate_tag_match_score(context)
        assert score == 1.0  # Perfect match
    
    def test_calculate_tag_match_score_partial_match(self, sample_step): pass
        """Test tag match score calculation with partial match"""
        # Add tags with equal weights for easier calculation
        sample_step.add_tag("location", "forest", weight=1.0)
        sample_step.add_tag("npc", "ranger", weight=1.0)
        sample_step.add_tag("faction", "nature_guardians", weight=1.0)
        
        context = {
            "location": "forest",    # Matches
            "npc": "bandit",        # Doesn't match
            "faction": "nature_guardians"  # Matches
        }
        
        score = sample_step.calculate_tag_match_score(context)
        assert abs(score - 0.667) < 0.01  # 2 out of 3 matches
    
    def test_calculate_tag_match_score_no_match(self, sample_step): pass
        """Test tag match score calculation with no match"""
        sample_step.add_tag("location", "forest")
        sample_step.add_tag("npc", "ranger")
        
        context = {
            "location": "desert",
            "npc": "merchant"
        }
        
        score = sample_step.calculate_tag_match_score(context)
        assert score == 0.0  # No matches
    
    def test_calculate_tag_match_score_no_tags(self, sample_step): pass
        """Test tag match score calculation with no tags"""
        # Don't add any tags
        context = {"location": "anywhere", "npc": "anyone"}
        
        score = sample_step.calculate_tag_match_score(context)
        assert score == 0.0  # No tags to match
    
    def test_calculate_tag_match_score_weighted(self, sample_step): pass
        """Test tag match score calculation with different weights"""
        # Add tags with different weights
        sample_step.add_tag("location", "city", weight=0.9)     # High weight
        sample_step.add_tag("npc", "guard", weight=0.3)        # Low weight
        sample_step.add_tag("skill", "persuasion", weight=0.6) # Medium weight
        
        # Only match the high-weight tag
        context = {
            "location": "city",       # Matches (weight 0.9)
            "npc": "merchant",       # Doesn't match (weight 0.3)
            "skill": "intimidation"  # Doesn't match (weight 0.6)
        }
        
        score = sample_step.calculate_tag_match_score(context)
        expected_score = 0.9 / (0.9 + 0.3 + 0.6)  # 0.9 / 1.8 = 0.5
        assert abs(score - expected_score) < 0.01
    
    def test_calculate_tag_match_score_empty_context(self, sample_step): pass
        """Test tag match score calculation with empty context"""
        sample_step.add_tag("location", "forest")
        sample_step.add_tag("npc", "ranger")
        
        score = sample_step.calculate_tag_match_score({})
        assert score == 0.0  # No context to match against
    
    def test_step_timing_and_constraints(self, sample_step): pass
        """Test step timing and constraint fields"""
        # Test estimated duration
        sample_step.estimated_duration = 7  # 7 days
        assert sample_step.estimated_duration == 7
        
        # Test time limit
        deadline = datetime.utcnow() + timedelta(days=14)
        sample_step.time_limit = deadline
        assert sample_step.time_limit == deadline
        
        # Test timing fields with None values
        step = ArcStep(
            arc_id=uuid4(),
            step_index=1,
            title="Timed Step",
            description="Test timing",
            narrative_text="Test",
            step_type=ArcStepType.NARRATIVE
        )
        assert step.estimated_duration is None
        assert step.time_limit is None
    
    def test_step_dependencies_and_branching(self, sample_step): pass
        """Test step dependencies and branching logic"""
        # Test prerequisite steps
        sample_step.prerequisite_steps = [1, 2, 3]
        assert len(sample_step.prerequisite_steps) == 3
        assert 2 in sample_step.prerequisite_steps
        
        # Test next step options
        sample_step.next_step_options = [4, 5]
        assert len(sample_step.next_step_options) == 2
        assert 4 in sample_step.next_step_options
        
        # Test branching condition
        sample_step.branching_condition = "player_choice == 'help_villagers'"
        assert sample_step.branching_condition == "player_choice == 'help_villagers'"
    
    def test_step_ai_generation_data(self, sample_step): pass
        """Test AI generation data fields"""
        # Test GPT generation prompt
        prompt = "Generate a mystery investigation step involving missing villagers"
        sample_step.gpt_generation_prompt = prompt
        assert sample_step.gpt_generation_prompt == prompt
        
        # Test generation options
        options = [
            {"approach": "stealth", "difficulty": "medium"},
            {"approach": "direct", "difficulty": "easy"}
        ]
        sample_step.generation_options = options
        assert len(sample_step.generation_options) == 2
        assert sample_step.generation_options[0]["approach"] == "stealth"
    
    def test_step_completion_tracking(self, sample_step): pass
        """Test completion tracking fields"""
        # Initially no tracking data
        assert sample_step.attempts == 0
        assert sample_step.first_attempted is None
        assert sample_step.completed_at is None
        assert sample_step.failed_at is None
        
        # Test attempt tracking
        sample_step.attempts = 3
        attempt_time = datetime.utcnow()
        sample_step.first_attempted = attempt_time
        
        assert sample_step.attempts == 3
        assert sample_step.first_attempted == attempt_time
    
    def test_step_complex_completion_criteria(self, sample_step): pass
        """Test complex completion criteria"""
        complex_criteria = {
            "primary_objective": "find_missing_person",
            "secondary_objectives": ["gather_clues", "interview_witnesses"],
            "required_items": ["investigation_permit", "magnifying_glass"],
            "skill_checks": {
                "investigation": {"difficulty": 15, "required": True},
                "persuasion": {"difficulty": 12, "required": False}
            },
            "location_requirements": ["visit_last_seen_location", "search_nearby_areas"],
            "time_constraints": {"max_days": 5, "preferred_time": "daylight"}
        }
        
        sample_step.completion_criteria = complex_criteria
        
        assert sample_step.completion_criteria["primary_objective"] == "find_missing_person"
        assert len(sample_step.completion_criteria["secondary_objectives"]) == 2
        assert sample_step.completion_criteria["skill_checks"]["investigation"]["difficulty"] == 15
    
    def test_step_success_and_failure_conditions(self, sample_step): pass
        """Test success and failure conditions"""
        # Test success conditions
        success_conditions = [
            "clues_found >= 3",
            "witnesses_interviewed >= 2",
            "evidence_collected == 'sufficient'"
        ]
        sample_step.success_conditions = success_conditions
        
        assert len(sample_step.success_conditions) == 3
        assert "clues_found >= 3" in sample_step.success_conditions
        
        # Test failure conditions
        failure_conditions = [
            "time_limit_exceeded",
            "cover_blown",
            "critical_evidence_destroyed"
        ]
        sample_step.failure_conditions = failure_conditions
        
        assert len(sample_step.failure_conditions) == 3
        assert "cover_blown" in sample_step.failure_conditions


class TestArcStepEnums: pass
    """Test cases for arc step enums"""
    
    def test_arc_step_status_values(self): pass
        """Test all arc step status enum values"""
        assert ArcStepStatus.PENDING == "pending"
        assert ArcStepStatus.AVAILABLE == "available"
        assert ArcStepStatus.ACTIVE == "active"
        assert ArcStepStatus.COMPLETED == "completed"
        assert ArcStepStatus.FAILED == "failed"
        assert ArcStepStatus.SKIPPED == "skipped"
    
    def test_arc_step_type_values(self): pass
        """Test all arc step type enum values"""
        assert ArcStepType.NARRATIVE == "narrative"
        assert ArcStepType.CHALLENGE == "challenge"
        assert ArcStepType.DISCOVERY == "discovery"
        assert ArcStepType.INTERACTION == "interaction"
        assert ArcStepType.EXPLORATION == "exploration"
        assert ArcStepType.DECISION == "decision"
    
    def test_enum_iteration(self): pass
        """Test that we can iterate over enums"""
        status_values = [status.value for status in ArcStepStatus]
        assert len(status_values) == 6
        assert "pending" in status_values
        assert "completed" in status_values
        
        type_values = [step_type.value for step_type in ArcStepType]
        assert len(type_values) == 6
        assert "discovery" in type_values
        assert "decision" in type_values


class TestArcStepEdgeCases: pass
    """Test edge cases and error conditions for arc step models"""
    
    def test_step_with_extreme_values(self): pass
        """Test step with extreme field values"""
        step = ArcStep(
            arc_id=uuid4(),
            step_index=999999,  # Very high step index
            title="Extreme Step",
            description="A" * 10000,  # Very long description
            narrative_text="B" * 5000,  # Very long narrative
            step_type=ArcStepType.CHALLENGE,
            quest_probability=0.0,  # Minimum probability
            estimated_duration=365  # One year duration
        )
        
        assert step.step_index == 999999
        assert len(step.description) == 10000
        assert step.quest_probability == 0.0
        assert step.estimated_duration == 365
    
    def test_step_with_maximum_probability(self): pass
        """Test step with maximum quest probability"""
        step = ArcStep(
            arc_id=uuid4(),
            step_index=1,
            title="Guaranteed Quest Step",
            description="This step always generates a quest",
            narrative_text="Quest guaranteed",
            step_type=ArcStepType.CHALLENGE,
            quest_probability=1.0
        )
        
        assert step.quest_probability == 1.0
    
    def test_step_with_many_tags(self): pass
        """Test step with many tags"""
        step = ArcStep(
            arc_id=uuid4(),
            step_index=1,
            title="Multi-Tagged Step",
            description="Step with many tags",
            narrative_text="Many requirements",
            step_type=ArcStepType.EXPLORATION
        )
        
        # Add many tags
        tag_keys = ["location", "npc", "faction", "skill", "item", "weather", "time", "mood"]
        for i, key in enumerate(tag_keys): pass
            step.add_tag(key, f"value_{i}", weight=0.1 * (i + 1), required=(i % 2 == 0))
        
        assert len(step.tags) == 8
        assert len(step.get_required_tags()) == 4  # Every other tag is required
        
        # Test tag match with many tags
        context = {key: f"value_{i}" for i, key in enumerate(tag_keys[:4])}  # Match first 4
        score = step.calculate_tag_match_score(context)
        assert score > 0.0  # Should have some matches
    
    def test_step_state_transitions(self): pass
        """Test step going through all state transitions"""
        step = ArcStep(
            arc_id=uuid4(),
            step_index=1,
            title="State Transition Step",
            description="Testing state changes",
            narrative_text="State changes",
            step_type=ArcStepType.NARRATIVE
        )
        
        # Start in PENDING
        assert step.status == ArcStepStatus.PENDING
        
        # Move to AVAILABLE (simulated)
        step.status = ArcStepStatus.AVAILABLE
        assert step.is_ready_for_activation() is True
        
        # Start attempt -> ACTIVE
        step.start_attempt()
        assert step.status == ArcStepStatus.ACTIVE
        assert step.attempts == 1
        
        # Complete -> COMPLETED
        step.complete_step()
        assert step.status == ArcStepStatus.COMPLETED
        assert step.completed_at is not None
        
        # Reset and test failure path
        step.status = ArcStepStatus.AVAILABLE
        step.start_attempt()
        step.fail_step()
        assert step.status == ArcStepStatus.FAILED
        assert step.failed_at is not None
    
    def test_step_timing_edge_cases(self): pass
        """Test edge cases with timing"""
        step = ArcStep(
            arc_id=uuid4(),
            step_index=1,
            title="Timing Test",
            description="Testing timing edge cases",
            narrative_text="Time test",
            step_type=ArcStepType.CHALLENGE
        )
        
        # Test zero duration
        step.estimated_duration = 0
        assert step.estimated_duration == 0
        
        # Test past deadline
        past_deadline = datetime.utcnow() - timedelta(days=1)
        step.time_limit = past_deadline
        assert step.time_limit < datetime.utcnow()
        
        # Test far future deadline
        future_deadline = datetime.utcnow() + timedelta(days=365 * 100)  # 100 years
        step.time_limit = future_deadline
        assert step.time_limit > datetime.utcnow() 