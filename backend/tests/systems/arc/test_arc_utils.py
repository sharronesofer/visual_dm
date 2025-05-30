from backend.systems.shared.database.base import Base
from backend.systems.shared.database.base import Base
from typing import Type
from dataclasses import field
"""Tests for Arc System Utilities

Comprehensive unit tests for arc utility functions including
complexity calculations, validation, progress tracking, and formatting.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from backend.systems.arc.models import Arc, ArcType, ArcStatus, ArcPriority
from backend.systems.arc.utils.arc_utils import (
    calculate_arc_complexity,
    estimate_arc_duration,
    validate_arc_data,
    calculate_arc_progress_percentage,
    determine_arc_stagnation,
    generate_arc_id_string,
    format_arc_summary,
    calculate_arc_difficulty,
    get_arc_recommendations,
    merge_arc_metadata,
    sanitize_arc_tags
)


class TestArcComplexity: pass
    """Test arc complexity calculation"""
    
    def test_calculate_complexity_global_arc(self): pass
        """Test complexity calculation for global arc"""
        arc = Arc(
            id=uuid4(),
            title="Global Arc",
            description="A global arc",
            arc_type=ArcType.GLOBAL,
            starting_point="Start",
            preferred_ending="End",
            total_steps=15,
            system_hooks=["hook1", "hook2"],
            faction_ids=["faction1", "faction2", "faction3"],
            time_sensitivity=0.9
        )
        
        complexity = calculate_arc_complexity(arc)
        
        # Base: 8.0 (GLOBAL) + 1.0 (>10 steps) + 0.4 (2 hooks) + 0.9 (3 factions) + 1.0 (high time sensitivity)
        expected = 8.0 + 1.0 + 0.4 + 0.9 + 1.0
        assert complexity == expected
    
    def test_calculate_complexity_character_arc(self): pass
        """Test complexity calculation for character arc"""
        arc = Arc(
            id=uuid4(),
            title="Character Arc",
            description="A character arc",
            arc_type=ArcType.CHARACTER,
            starting_point="Start",
            preferred_ending="End",
            total_steps=5,
            system_hooks=[],
            faction_ids=["faction1"],
            time_sensitivity=0.3
        )
        
        complexity = calculate_arc_complexity(arc)
        
        # Base: 4.0 (CHARACTER) + 0.0 (≤10 steps) + 0.0 (no hooks) + 0.3 (1 faction) + 0.0 (low time sensitivity)
        expected = 4.0 + 0.0 + 0.0 + 0.3 + 0.0
        assert complexity == expected
    
    def test_calculate_complexity_bounds(self): pass
        """Test complexity calculation stays within bounds"""
        # Test maximum complexity - should be able to exceed 10.0 for very complex arcs
        arc = Arc(
            id=uuid4(),
            title="Max Complexity Arc",
            description="Maximum complexity",
            arc_type=ArcType.GLOBAL,
            starting_point="Start",
            preferred_ending="End",
            total_steps=25,
            system_hooks=["hook"] * 10,  # 10 hooks
            faction_ids=["faction"] * 20,  # 20 factions
            time_sensitivity=1.0
        )
        
        complexity = calculate_arc_complexity(arc)
        # Should be able to exceed 10.0 for very complex arcs
        # Expected: 8.0 (GLOBAL) + 1.0 (>10 steps) + 2.0 (10 hooks) + 6.0 (20 factions) + 1.0 (high time sensitivity) = 18.0
        assert complexity > 10.0  # Should exceed the old cap
        assert complexity >= 15.0  # Should be quite high for this complex arc
        
        # Test minimum complexity
        arc.arc_type = ArcType.NPC
        arc.total_steps = 1
        arc.system_hooks = []
        arc.faction_ids = []
        arc.time_sensitivity = 0.0
        
        complexity = calculate_arc_complexity(arc)
        assert complexity >= 0.0


class TestArcDuration: pass
    """Test arc duration estimation"""
    
    def test_estimate_duration_global_arc(self): pass
        """Test duration estimation for global arc"""
        arc = Arc(
            id=uuid4(),
            title="Global Arc",
            description="A global arc",
            arc_type=ArcType.GLOBAL,
            starting_point="Start",
            preferred_ending="End",
            total_steps=10,
            priority=ArcPriority.MEDIUM
        )
        
        duration = estimate_arc_duration(arc)
        
        # Base: 30 days * (complexity/5.0) * (steps/5.0) * priority_modifier
        # Complexity for this arc would be around 8.0
        # So: 30 * (8.0/5.0) * (10/5.0) * 1.0 = 30 * 1.6 * 2.0 = 96 days
        assert duration.days >= 90  # Allow some variance
    
    def test_estimate_duration_character_arc(self): pass
        """Test duration estimation for character arc"""
        arc = Arc(
            id=uuid4(),
            title="Character Arc",
            description="A character arc",
            arc_type=ArcType.CHARACTER,
            starting_point="Start",
            preferred_ending="End",
            total_steps=3,
            priority=ArcPriority.HIGH
        )
        
        duration = estimate_arc_duration(arc)
        
        # Base: 7 days * complexity_factor * steps_factor * 0.8 (high priority)
        assert duration.days >= 1  # Should be at least 1 day
        assert duration.days <= 20  # Should be reasonable for character arc
    
    def test_estimate_duration_priority_effects(self): pass
        """Test that priority affects duration estimation"""
        base_arc = Arc(
            id=uuid4(),
            title="Test Arc",
            description="Test",
            arc_type=ArcType.REGIONAL,
            starting_point="Start",
            preferred_ending="End",
            total_steps=5
        )
        
        # High priority should be faster
        base_arc.priority = ArcPriority.HIGH
        high_duration = estimate_arc_duration(base_arc)
        
        # Medium priority baseline
        base_arc.priority = ArcPriority.MEDIUM
        medium_duration = estimate_arc_duration(base_arc)
        
        # Low priority should be slower
        base_arc.priority = ArcPriority.LOW
        low_duration = estimate_arc_duration(base_arc)
        
        assert high_duration < medium_duration < low_duration


class TestArcValidation: pass
    """Test arc data validation"""
    
    def test_validate_arc_data_valid(self): pass
        """Test validation with valid arc data"""
        arc_data = {
            "title": "Valid Arc Title",
            "description": "This is a valid description that is long enough",
            "arc_type": "character",
            "starting_point": "A valid starting point",
            "priority": "medium",
            "status": "pending",
            "time_sensitivity": 0.5
        }
        
        is_valid, errors = validate_arc_data(arc_data)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_arc_data_missing_required(self): pass
        """Test validation with missing required fields"""
        arc_data = {
            "title": "Test Arc"
            # Missing description, arc_type, starting_point
        }
        
        is_valid, errors = validate_arc_data(arc_data)
        
        assert not is_valid
        assert len(errors) == 3
        assert any("description" in error for error in errors)
        assert any("arc_type" in error for error in errors)
        assert any("starting_point" in error for error in errors)
    
    def test_validate_arc_data_title_validation(self): pass
        """Test title validation rules"""
        # Title too short
        arc_data = {
            "title": "Hi",
            "description": "Valid description here",
            "arc_type": "character",
            "starting_point": "Start"
        }
        
        is_valid, errors = validate_arc_data(arc_data)
        assert not is_valid
        assert any("at least 3 characters" in error for error in errors)
        
        # Title too long
        arc_data["title"] = "x" * 201
        is_valid, errors = validate_arc_data(arc_data)
        assert not is_valid
        assert any("less than 200 characters" in error for error in errors)
    
    def test_validate_arc_data_description_validation(self): pass
        """Test description validation rules"""
        # Description too short
        arc_data = {
            "title": "Valid Title",
            "description": "Short",
            "arc_type": "character",
            "starting_point": "Start"
        }
        
        is_valid, errors = validate_arc_data(arc_data)
        assert not is_valid
        assert any("at least 10 characters" in error for error in errors)
        
        # Description too long
        arc_data["description"] = "x" * 2001
        is_valid, errors = validate_arc_data(arc_data)
        assert not is_valid
        assert any("less than 2000 characters" in error for error in errors)
    
    def test_validate_arc_data_enum_validation(self): pass
        """Test enum field validation"""
        arc_data = {
            "title": "Valid Title",
            "description": "Valid description here",
            "arc_type": "invalid_type",
            "starting_point": "Start",
            "priority": "invalid_priority",
            "status": "invalid_status"
        }
        
        is_valid, errors = validate_arc_data(arc_data)
        assert not is_valid
        assert any("Invalid arc type" in error for error in errors)
        assert any("Invalid priority" in error for error in errors)
        assert any("Invalid status" in error for error in errors)
    
    def test_validate_arc_data_time_sensitivity(self): pass
        """Test time sensitivity validation"""
        arc_data = {
            "title": "Valid Title",
            "description": "Valid description here",
            "arc_type": "character",
            "starting_point": "Start",
            "time_sensitivity": 1.5  # Invalid: > 1.0
        }
        
        is_valid, errors = validate_arc_data(arc_data)
        assert not is_valid
        assert any("between 0.0 and 1.0" in error for error in errors)


class TestArcProgress: pass
    """Test arc progress calculations"""
    
    def test_calculate_progress_percentage_normal(self): pass
        """Test normal progress percentage calculation"""
        arc = Arc(
            id=uuid4(),
            title="Test Arc",
            description="Test",
            arc_type=ArcType.CHARACTER,
            starting_point="Start",
            preferred_ending="End",
            total_steps=10
        )
        
        # 0% progress
        assert calculate_arc_progress_percentage(arc, 0) == 0.0
        
        # 50% progress
        assert calculate_arc_progress_percentage(arc, 5) == 50.0
        
        # 100% progress
        assert calculate_arc_progress_percentage(arc, 10) == 100.0
    
    def test_calculate_progress_percentage_edge_cases(self): pass
        """Test progress percentage edge cases"""
        arc = Arc(
            id=uuid4(),
            title="Test Arc",
            description="Test",
            arc_type=ArcType.CHARACTER,
            starting_point="Start",
            preferred_ending="End",
            total_steps=0  # No steps
        )
        
        # No total steps
        assert calculate_arc_progress_percentage(arc, 5) == 0.0
        
        # Negative current step
        arc.total_steps = 10
        assert calculate_arc_progress_percentage(arc, -1) == 0.0
        
        # Current step exceeds total
        assert calculate_arc_progress_percentage(arc, 15) == 100.0


class TestArcStagnation: pass
    """Test arc stagnation detection"""
    
    def test_determine_stagnation_active_arc(self): pass
        """Test stagnation detection for active arc"""
        arc = Arc(
            id=uuid4(),
            title="Test Arc",
            description="Test",
            arc_type=ArcType.CHARACTER,
            starting_point="Start",
            preferred_ending="End",
            status=ArcStatus.ACTIVE
        )
        
        # Recent activity - not stagnant
        recent_activity = datetime.utcnow() - timedelta(days=2)
        assert not determine_arc_stagnation(arc, recent_activity)
        
        # Old activity - stagnant (character arcs stagnate after 7 days)
        old_activity = datetime.utcnow() - timedelta(days=10)
        assert determine_arc_stagnation(arc, old_activity)
    
    def test_determine_stagnation_different_arc_types(self): pass
        """Test stagnation thresholds for different arc types"""
        old_activity = datetime.utcnow() - timedelta(days=15)
        
        # Global arc (21 day threshold) - not stagnant
        global_arc = Arc(
            id=uuid4(),
            title="Global Arc",
            description="Test",
            arc_type=ArcType.GLOBAL,
            starting_point="Start",
            preferred_ending="End",
            status=ArcStatus.ACTIVE
        )
        assert not determine_arc_stagnation(global_arc, old_activity)
        
        # Character arc (7 day threshold) - stagnant
        char_arc = Arc(
            id=uuid4(),
            title="Character Arc",
            description="Test",
            arc_type=ArcType.CHARACTER,
            starting_point="Start",
            preferred_ending="End",
            status=ArcStatus.ACTIVE
        )
        assert determine_arc_stagnation(char_arc, old_activity)
    
    def test_determine_stagnation_inactive_arc(self): pass
        """Test that inactive arcs are not considered stagnant"""
        arc = Arc(
            id=uuid4(),
            title="Test Arc",
            description="Test",
            arc_type=ArcType.CHARACTER,
            starting_point="Start",
            preferred_ending="End",
            status=ArcStatus.COMPLETED  # Not active
        )
        
        old_activity = datetime.utcnow() - timedelta(days=30)
        assert not determine_arc_stagnation(arc, old_activity)


class TestArcIdGeneration: pass
    """Test arc ID generation"""
    
    def test_generate_arc_id_string_format(self): pass
        """Test that generated arc IDs follow expected format"""
        arc_id = generate_arc_id_string()
        
        # Should be in format: Adjective_Noun_Number
        parts = arc_id.split("_")
        assert len(parts) == 3
        
        # First part should be adjective (capitalized)
        assert parts[0][0].isupper()
        
        # Second part should be noun (capitalized)
        assert parts[1][0].isupper()
        
        # Third part should be 3-digit number
        assert parts[2].isdigit()
        assert 100 <= int(parts[2]) <= 999
    
    def test_generate_arc_id_string_uniqueness(self): pass
        """Test that generated IDs are reasonably unique"""
        ids = [generate_arc_id_string() for _ in range(100)]
        
        # Should have high uniqueness (allow some duplicates due to randomness)
        unique_ids = set(ids)
        assert len(unique_ids) > 90  # At least 90% unique


class TestArcFormatting: pass
    """Test arc formatting functions"""
    
    def test_format_arc_summary(self): pass
        """Test arc summary formatting"""
        arc = Arc(
            id=uuid4(),
            title="Test Arc",
            description="A test arc for formatting",
            arc_type=ArcType.CHARACTER,
            starting_point="Start",
            preferred_ending="End",
            status=ArcStatus.ACTIVE,
            priority=ArcPriority.HIGH,
            current_step=3,
            total_steps=10
        )
        
        summary = format_arc_summary(arc)
        
        # Should contain key information
        assert "Test Arc" in summary
        assert "Character" in summary
        assert "High" in summary
        assert "3/10" in summary  # Progress
        assert "🔄" in summary  # Active status emoji
    
    def test_calculate_arc_difficulty(self): pass
        """Test arc difficulty calculation"""
        # Easy arc
        easy_arc = Arc(
            id=uuid4(),
            title="Easy Arc",
            description="Easy",
            arc_type=ArcType.NPC,
            starting_point="Start",
            preferred_ending="End",
            total_steps=2
        )
        
        difficulty = calculate_arc_difficulty(easy_arc)
        assert difficulty in ["Trivial", "Easy", "Moderate", "Hard", "Legendary"]
        
        # Hard arc
        hard_arc = Arc(
            id=uuid4(),
            title="Hard Arc",
            description="Hard",
            arc_type=ArcType.GLOBAL,
            starting_point="Start",
            preferred_ending="End",
            total_steps=25,
            system_hooks=["hook1", "hook2", "hook3"],
            faction_ids=["f1", "f2", "f3", "f4"],
            time_sensitivity=0.9
        )
        
        difficulty = calculate_arc_difficulty(hard_arc)
        assert difficulty in ["Moderate", "Hard", "Legendary"]  # Should be harder


class TestArcRecommendations: pass
    """Test arc recommendation generation"""
    
    def test_get_arc_recommendations(self): pass
        """Test arc recommendation generation"""
        arc = Arc(
            id=uuid4(),
            title="Test Arc",
            description="Test",
            arc_type=ArcType.CHARACTER,
            starting_point="Start",
            preferred_ending="End",
            status=ArcStatus.PENDING,
            priority=ArcPriority.LOW,
            total_steps=0
        )
        
        recommendations = get_arc_recommendations(arc)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should contain relevant recommendations
        rec_text = " ".join(recommendations)
        assert any(keyword in rec_text.lower() for keyword in ["step", "priority", "activate"])


class TestArcMetadata: pass
    """Test arc metadata utilities"""
    
    def test_merge_arc_metadata(self): pass
        """Test metadata merging"""
        original = {
            "theme": "mystery",
            "difficulty": 5,
            "tags": {"important": True}
        }
        
        updates = {
            "difficulty": 7,  # Override
            "new_field": "value",  # Add
            "tags": {"urgent": True}  # Merge nested
        }
        
        merged = merge_arc_metadata(original, updates)
        
        assert merged["theme"] == "mystery"  # Preserved
        assert merged["difficulty"] == 7  # Updated
        assert merged["new_field"] == "value"  # Added
        assert merged["tags"]["important"] is True  # Preserved nested
        assert merged["tags"]["urgent"] is True  # Added nested
    
    def test_sanitize_arc_tags(self): pass
        """Test tag sanitization"""
        tags = {
            "valid_tag": "value",
            "": "empty_key",  # Should be removed
            "null_value": None,  # Should be removed
            "empty_string": "",  # Should be removed
            "whitespace": "  ",  # Should be trimmed
            "normal": "  normal value  "  # Should be trimmed
        }
        
        sanitized = sanitize_arc_tags(tags)
        
        assert "valid_tag" in sanitized
        assert "" not in sanitized
        assert "null_value" not in sanitized
        assert "empty_string" not in sanitized
        assert sanitized["whitespace"] == ""  # Trimmed to empty, might be removed
        assert sanitized["normal"] == "normal value"  # Trimmed 