"""
Test module for motif.models

Tests the motif models according to Development_Bible.md requirements:
- Motif scopes: GLOBAL, REGIONAL, LOCAL, PLAYER_CHARACTER
- Lifecycle states: EMERGING, STABLE, WANING, DORMANT, CONCLUDED  
- All required fields and validation rules
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from uuid import uuid4

# Import the models under test
from backend.infrastructure.systems.motif.models import (
    Motif, MotifCreate, MotifUpdate, MotifFilter,
    MotifScope, MotifLifecycle, MotifCategory, 
    MotifEffect, MotifEffectTarget, LocationInfo
)


class TestMotifModels:
    """Test class for motif models compliance with Development Bible"""
    
    def test_motif_scope_enum_compliance(self):
        """Test that MotifScope enum matches Bible requirements"""
        # Bible specifies: GLOBAL, REGIONAL, LOCAL, ENTITY-SPECIFIC
        # Code implements PLAYER_CHARACTER as specialization of ENTITY-SPECIFIC
        assert MotifScope.GLOBAL == "global"
        assert MotifScope.REGIONAL == "regional" 
        assert MotifScope.LOCAL == "local"
        assert MotifScope.PLAYER_CHARACTER == "player_character"
        
    def test_motif_lifecycle_enum_compliance(self):
        """Test that MotifLifecycle enum matches Bible requirements"""
        # Bible specifies lifecycle management
        assert MotifLifecycle.EMERGING == "emerging"
        assert MotifLifecycle.STABLE == "stable"
        assert MotifLifecycle.WANING == "waning"
        assert MotifLifecycle.DORMANT == "dormant"
        assert MotifLifecycle.CONCLUDED == "concluded"
        
    def test_motif_category_enum_has_required_categories(self):
        """Test that MotifCategory includes Bible-specified categories"""
        # Bible mentions categories like betrayal, chaos, hope, etc.
        required_categories = ["betrayal", "chaos", "hope", "power", "redemption"]
        available_categories = [cat.value for cat in MotifCategory]
        
        for category in required_categories:
            assert category in available_categories, f"Missing required category: {category}"
            
    def test_motif_model_core_fields(self):
        """Test that Motif model has all required core fields per Bible"""
        motif = Motif(
            name="Test Motif",
            description="Test description", 
            category=MotifCategory.HOPE,
            scope=MotifScope.GLOBAL
        )
        
        # Core fields as specified in Bible
        assert hasattr(motif, 'id')
        assert hasattr(motif, 'name')
        assert hasattr(motif, 'description')
        assert hasattr(motif, 'category')
        assert hasattr(motif, 'scope')
        assert hasattr(motif, 'intensity')
        assert hasattr(motif, 'lifecycle')
        
        # Default values
        assert motif.intensity == 5  # Default intensity
        assert motif.lifecycle == MotifLifecycle.EMERGING
        
    def test_motif_intensity_validation(self):
        """Test that motif intensity validation matches Bible requirements"""
        # Bible specifies 1-10 scale
        with pytest.raises(ValueError):
            Motif(
                name="Test",
                description="Test", 
                category=MotifCategory.HOPE,
                scope=MotifScope.GLOBAL,
                intensity=0  # Below minimum
            )
            
        with pytest.raises(ValueError):
            Motif(
                name="Test",
                description="Test",
                category=MotifCategory.HOPE, 
                scope=MotifScope.GLOBAL,
                intensity=11  # Above maximum
            )
            
        # Valid intensity should work
        motif = Motif(
            name="Test",
            description="Test",
            category=MotifCategory.HOPE,
            scope=MotifScope.GLOBAL, 
            intensity=7
        )
        assert motif.intensity == 7
        
    def test_location_info_for_regional_local_motifs(self):
        """Test LocationInfo for regional/local motifs per Bible requirements"""
        location = LocationInfo(
            region_id="test_region",
            x=100.0,
            y=200.0,
            radius=50.0
        )
        
        motif = Motif(
            name="Regional Test",
            description="Test regional motif",
            category=MotifCategory.PEACE,
            scope=MotifScope.REGIONAL,
            location=location
        )
        
        assert motif.location.region_id == "test_region"
        assert motif.location.x == 100.0
        assert motif.location.y == 200.0
        assert motif.location.radius == 50.0
        
    def test_motif_effects_system_integration(self):
        """Test MotifEffect for system integration per Bible requirements"""
        # Bible specifies integration with NPC, Event, Quest, Faction systems
        npc_effect = MotifEffect(
            target=MotifEffectTarget.NPC,
            intensity=7,
            description="Affects NPC behavior and dialogue"
        )
        
        quest_effect = MotifEffect(
            target=MotifEffectTarget.QUEST,
            intensity=5,
            description="Influences quest generation"
        )
        
        motif = Motif(
            name="Integration Test",
            description="Test system integration",
            category=MotifCategory.BETRAYAL,
            scope=MotifScope.GLOBAL,
            effects=[npc_effect, quest_effect]
        )
        
        assert len(motif.effects) == 2
        assert motif.effects[0].target == MotifEffectTarget.NPC
        assert motif.effects[1].target == MotifEffectTarget.QUEST
        
    def test_motif_create_schema_completeness(self):
        """Test MotifCreate schema has all necessary fields"""
        create_data = MotifCreate(
            name="New Motif",
            description="New motif description",
            category=MotifCategory.ASCENSION,
            scope=MotifScope.LOCAL,
            intensity=8,
            duration_days=30
        )
        
        assert create_data.name == "New Motif"
        assert create_data.category == MotifCategory.ASCENSION
        assert create_data.scope == MotifScope.LOCAL
        assert create_data.intensity == 8
        assert create_data.duration_days == 30
        
    def test_motif_filter_capabilities(self):
        """Test MotifFilter supports all Bible-specified filtering"""
        filter_params = MotifFilter(
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            lifecycle=MotifLifecycle.STABLE,
            min_intensity=5,
            max_intensity=10,
            region_id="test_region"
        )
        
        assert filter_params.category == MotifCategory.CHAOS
        assert filter_params.scope == MotifScope.REGIONAL
        assert filter_params.lifecycle == MotifLifecycle.STABLE
        assert filter_params.min_intensity == 5
        assert filter_params.max_intensity == 10
        assert filter_params.region_id == "test_region"
