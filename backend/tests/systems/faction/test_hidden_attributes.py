"""
Tests for Faction Hidden Attributes System

This module tests the implementation of the 6 hidden personality attributes
for factions, ensuring proper generation, validation, and behavior modification.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, Mock

from backend.infrastructure.models.faction.models import (
    FactionEntity,
    CreateFactionRequest,
    UpdateFactionRequest,
    FactionResponse
)
from backend.systems.faction.services.services import FactionService
from backend.infrastructure.utils.faction.faction_utils import (
    generate_faction_hidden_attributes,
    validate_hidden_attributes,
    calculate_faction_behavior_modifiers
)


class TestFactionHiddenAttributes:
    """Test faction hidden attributes generation and validation"""

    def test_generate_faction_hidden_attributes(self):
        """Test that hidden attributes are generated properly"""
        attributes = generate_faction_hidden_attributes()
        
        # Check that all 6 attributes are present
        expected_attributes = [
            'hidden_ambition', 'hidden_integrity', 'hidden_discipline',
            'hidden_impulsivity', 'hidden_pragmatism', 'hidden_resilience'
        ]
        
        for attr in expected_attributes:
            assert attr in attributes
            # Check that values are in valid range (1-10) per Development Bible
            assert 1 <= attributes[attr] <= 10
            assert isinstance(attributes[attr], int)

    def test_generate_faction_hidden_attributes_distribution(self):
        """Test that generated attributes have reasonable distribution"""
        # Generate multiple sets to check distribution
        all_values = {
            'hidden_ambition': [],
            'hidden_integrity': [],
            'hidden_discipline': [],
            'hidden_impulsivity': [],
            'hidden_pragmatism': [],
            'hidden_resilience': []
        }
        
        for _ in range(100):
            attributes = generate_faction_hidden_attributes()
            for attr, value in attributes.items():
                all_values[attr].append(value)
        
        # Check that we get variety in values (not all the same)
        for attr, values in all_values.items():
            unique_values = set(values)
            assert len(unique_values) > 1, f"{attr} should have variety in generated values"
            
            # Check that all values are in valid range
            assert all(1 <= v <= 10 for v in values), f"All {attr} values should be 1-10"

    def test_validate_hidden_attributes_valid(self):
        """Test validation of valid hidden attributes"""
        valid_attributes = {
            'hidden_ambition': 3,
            'hidden_integrity': 5,
            'hidden_discipline': 2,
            'hidden_impulsivity': 1,
            'hidden_pragmatism': 6,
            'hidden_resilience': 4
        }
        
        validated = validate_hidden_attributes(valid_attributes)
        assert validated == valid_attributes

    def test_validate_hidden_attributes_clamps_values(self):
        """Test that validation clamps out-of-range values"""
        invalid_attributes = {
            'hidden_ambition': -1,  # Too low
            'hidden_integrity': 11,   # Too high
            'hidden_discipline': 3,  # Valid
            'hidden_impulsivity': 15, # Too high
            'hidden_pragmatism': -5,  # Too low
            'hidden_resilience': 4    # Valid
        }
        
        validated = validate_hidden_attributes(invalid_attributes)
        
        assert validated['hidden_ambition'] == 1    # Clamped from -1
        assert validated['hidden_integrity'] == 10   # Clamped from 11
        assert validated['hidden_discipline'] == 3  # Unchanged
        assert validated['hidden_impulsivity'] == 10 # Clamped from 15
        assert validated['hidden_pragmatism'] == 1  # Clamped from -5
        assert validated['hidden_resilience'] == 4  # Unchanged

    def test_validate_hidden_attributes_fills_missing(self):
        """Test that validation fills in missing attributes"""
        partial_attributes = {
            'hidden_ambition': 3,
            'hidden_integrity': 2
            # Missing other attributes
        }
        
        validated = validate_hidden_attributes(partial_attributes)
        
        # Should have all 6 attributes
        expected_attributes = [
            'hidden_ambition', 'hidden_integrity', 'hidden_discipline',
            'hidden_impulsivity', 'hidden_pragmatism', 'hidden_resilience'
        ]
        
        for attr in expected_attributes:
            assert attr in validated
            assert 1 <= validated[attr] <= 10

    def test_calculate_faction_behavior_modifiers(self):
        """Test calculation of behavior modifiers from hidden attributes"""
        attributes = {
            'hidden_ambition': 8,     # High ambition
            'hidden_integrity': 3,    # Low integrity
            'hidden_discipline': 6,   # Medium discipline
            'hidden_impulsivity': 2,  # Low impulsivity
            'hidden_pragmatism': 9,   # High pragmatism
            'hidden_resilience': 5    # Medium resilience
        }
        
        modifiers = calculate_faction_behavior_modifiers(attributes)
        
        # Check that all expected modifiers are present
        expected_modifiers = [
            'expansion_tendency', 'territorial_aggression', 'trade_aggression',
            'treaty_reliability', 'alliance_stability', 'diplomatic_trustworthiness',
            'strategic_planning', 'military_organization', 'economic_efficiency',
            'crisis_reaction_speed', 'opportunism', 'rash_decision_making',
            'compromise_willingness', 'principle_flexibility', 'realpolitik_tendency',
            'recovery_speed', 'crisis_handling', 'stability_under_pressure'
        ]
        
        for modifier in expected_modifiers:
            assert modifier in modifiers
            assert isinstance(modifiers[modifier], float)
            # Most modifiers should be between 0.0 and 2.0 (adjusted for 1-10 range)
            assert 0.0 <= modifiers[modifier] <= 2.0

    def test_behavior_modifiers_logical_relationships(self):
        """Test that behavior modifiers have logical relationships to attributes"""
        # High ambition should increase expansion tendency
        high_ambition = {'hidden_ambition': 9, 'hidden_integrity': 5, 'hidden_discipline': 5,
                        'hidden_impulsivity': 5, 'hidden_pragmatism': 5, 'hidden_resilience': 5}
        low_ambition = {'hidden_ambition': 2, 'hidden_integrity': 5, 'hidden_discipline': 5,
                       'hidden_impulsivity': 5, 'hidden_pragmatism': 5, 'hidden_resilience': 5}
        
        high_modifiers = calculate_faction_behavior_modifiers(high_ambition)
        low_modifiers = calculate_faction_behavior_modifiers(low_ambition)
        
        assert high_modifiers['expansion_tendency'] > low_modifiers['expansion_tendency']
        assert high_modifiers['territorial_aggression'] > low_modifiers['territorial_aggression']
        
        # High integrity should increase treaty reliability
        high_integrity = {'hidden_ambition': 5, 'hidden_integrity': 9, 'hidden_discipline': 5,
                         'hidden_impulsivity': 5, 'hidden_pragmatism': 5, 'hidden_resilience': 5}
        low_integrity = {'hidden_ambition': 5, 'hidden_integrity': 2, 'hidden_discipline': 5,
                        'hidden_impulsivity': 5, 'hidden_pragmatism': 5, 'hidden_resilience': 5}
        
        high_int_modifiers = calculate_faction_behavior_modifiers(high_integrity)
        low_int_modifiers = calculate_faction_behavior_modifiers(low_integrity)
        
        assert high_int_modifiers['treaty_reliability'] > low_int_modifiers['treaty_reliability']
        assert high_int_modifiers['diplomatic_trustworthiness'] > low_int_modifiers['diplomatic_trustworthiness']


class TestFactionEntityHiddenAttributes:
    """Test faction entity database model with hidden attributes"""

    def test_faction_entity_creation_with_hidden_attributes(self):
        """Test creating faction entity with hidden attributes"""
        faction = FactionEntity(
            name="Test Faction",
            description="A test faction",
            hidden_ambition=7,
            hidden_integrity=4,
            hidden_discipline=8,
            hidden_impulsivity=3,
            hidden_pragmatism=2,
            hidden_resilience=9
        )
        
        assert faction.hidden_ambition == 7
        assert faction.hidden_integrity == 4
        assert faction.hidden_discipline == 8
        assert faction.hidden_impulsivity == 3
        assert faction.hidden_pragmatism == 2
        assert faction.hidden_resilience == 9

    def test_faction_entity_default_hidden_attributes(self):
        """Test that faction entity has default hidden attributes when not specified"""
        faction = FactionEntity(name="Test Faction")
        
        # Check that all attributes have default values in valid range (1-10)
        assert 1 <= faction.hidden_ambition <= 10
        assert 1 <= faction.hidden_integrity <= 10 
        assert 1 <= faction.hidden_discipline <= 10
        assert 1 <= faction.hidden_impulsivity <= 10
        assert 1 <= faction.hidden_pragmatism <= 10
        assert 1 <= faction.hidden_resilience <= 10
        
        # Typically defaults should be neutral (around 5)
        assert faction.hidden_ambition == 5
        assert faction.hidden_integrity == 5
        assert faction.hidden_discipline == 5
        assert faction.hidden_impulsivity == 5
        assert faction.hidden_pragmatism == 5
        assert faction.hidden_resilience == 5

    def test_faction_entity_get_hidden_attributes(self):
        """Test the get_hidden_attributes method"""
        faction = FactionEntity(
            name="Test Faction",
            hidden_ambition=8,
            hidden_integrity=3,
            hidden_discipline=6,
            hidden_impulsivity=2,
            hidden_pragmatism=9,
            hidden_resilience=4
        )
        
        attributes = faction.get_hidden_attributes()
        
        expected = {
            'hidden_ambition': 8,
            'hidden_integrity': 3,
            'hidden_discipline': 6,
            'hidden_impulsivity': 2,
            'hidden_pragmatism': 9,
            'hidden_resilience': 4
        }
        
        assert attributes == expected

    def test_faction_entity_update_hidden_attributes(self):
        """Test the update_hidden_attributes method"""
        faction = FactionEntity(name="Test Faction")
        
        new_attributes = {
            'hidden_ambition': 8,
            'hidden_integrity': 3,
            'hidden_pragmatism': 7
        }
        
        faction.update_hidden_attributes(new_attributes)
        
        # Updated attributes should change
        assert faction.hidden_ambition == 8
        assert faction.hidden_integrity == 3
        assert faction.hidden_pragmatism == 7
        
        # Non-updated attributes should remain at default (5)
        assert faction.hidden_discipline == 5
        assert faction.hidden_impulsivity == 5
        assert faction.hidden_resilience == 5


@pytest.mark.asyncio
class TestFactionServiceHiddenAttributes:
    """Test faction service integration with hidden attributes"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return Mock()

    @pytest.fixture
    def faction_service(self, mock_db_session):
        """Create faction service with mocked database"""
        # FactionService creates its own business service internally
        return FactionService(mock_db_session)

    async def test_create_faction_with_hidden_attributes(self, faction_service, mock_db_session):
        """Test creating faction with specified hidden attributes"""
        request = CreateFactionRequest(
            name="Test Faction",
            description="A test faction",
            hidden_ambition=8,
            hidden_integrity=3,
            hidden_discipline=6,
            hidden_impulsivity=2,
            hidden_pragmatism=9,
            hidden_resilience=4
        )
        
        # Mock the underlying repository methods
        with patch.object(faction_service.business_service.faction_repository, 'get_faction_by_name', return_value=None), \
             patch.object(faction_service.business_service.faction_repository, 'create_faction') as mock_create:
            
            # Mock the create return value
            mock_faction_data = Mock()
            mock_faction_data.id = uuid4()
            mock_faction_data.name = "Test Faction"
            mock_faction_data.description = "A test faction"
            mock_faction_data.status = "active"
            mock_faction_data.properties = {}
            mock_faction_data.hidden_ambition = 8
            mock_faction_data.hidden_integrity = 3
            mock_faction_data.hidden_discipline = 6
            mock_faction_data.hidden_impulsivity = 2
            mock_faction_data.hidden_pragmatism = 9
            mock_faction_data.hidden_resilience = 4
            mock_faction_data.get_hidden_attributes.return_value = {
                'hidden_ambition': 8, 'hidden_integrity': 3, 'hidden_discipline': 6,
                'hidden_impulsivity': 2, 'hidden_pragmatism': 9, 'hidden_resilience': 4
            }
            mock_create.return_value = mock_faction_data
            
            faction_response = await faction_service.create_faction(request)
            
            # Verify the response has the expected attributes
            assert faction_response.hidden_ambition == 8
            assert faction_response.hidden_integrity == 3

    async def test_create_faction_auto_generates_hidden_attributes(self, faction_service, mock_db_session):
        """Test that hidden attributes are auto-generated when not provided"""
        request = CreateFactionRequest(
            name="Test Faction", 
            description="A test faction"
            # No hidden attributes specified
        )
        
        # Mock the underlying repository methods
        with patch.object(faction_service.business_service.faction_repository, 'get_faction_by_name', return_value=None), \
             patch.object(faction_service.business_service.faction_repository, 'create_faction') as mock_create, \
             patch('backend.infrastructure.utils.faction.faction_utils.generate_faction_hidden_attributes') as mock_generate:
            
            mock_generate.return_value = {
                'hidden_ambition': 7, 'hidden_integrity': 4, 'hidden_discipline': 8,
                'hidden_impulsivity': 3, 'hidden_pragmatism': 2, 'hidden_resilience': 9
            }
            
            # Mock the create return value
            mock_faction_data = Mock()
            mock_faction_data.id = uuid4()
            mock_faction_data.name = "Test Faction"
            mock_faction_data.description = "A test faction"
            mock_faction_data.status = "active"
            mock_faction_data.properties = {}
            mock_faction_data.get_hidden_attributes.return_value = {
                'hidden_ambition': 7, 'hidden_integrity': 4, 'hidden_discipline': 8,
                'hidden_impulsivity': 3, 'hidden_pragmatism': 2, 'hidden_resilience': 9
            }
            mock_create.return_value = mock_faction_data
            
            await faction_service.create_faction(request)
            
            # Verify that generation function was called when no attributes provided
            mock_generate.assert_called_once()

    async def test_update_faction_hidden_attributes(self, faction_service, mock_db_session):
        """Test updating faction with new hidden attributes"""
        faction_id = uuid4()
        
        # Mock existing faction data
        existing_faction_data = Mock()
        existing_faction_data.id = faction_id
        existing_faction_data.name = "Test Faction"
        existing_faction_data.description = "A test faction for updating"
        existing_faction_data.status = "active"
        existing_faction_data.properties = {}
        existing_faction_data.get_hidden_attributes.return_value = {
            'hidden_ambition': 9, 'hidden_integrity': 2, 'hidden_discipline': 8,
            'hidden_impulsivity': 5, 'hidden_pragmatism': 5, 'hidden_resilience': 5
        }
        
        update_request = UpdateFactionRequest(
            hidden_ambition=9,
            hidden_integrity=2,
            hidden_discipline=8
        )
        
        # Mock the repository methods
        with patch.object(faction_service.business_service.faction_repository, 'get_faction_by_id', return_value=existing_faction_data), \
             patch.object(faction_service.business_service.faction_repository, 'update_faction', return_value=existing_faction_data):
            
            faction_response = await faction_service.update_faction(faction_id, update_request)
            
            # Verify the update was attempted
            assert faction_response is not None


class TestFactionHiddenAttributesEdgeCases:
    """Test edge cases and error handling for hidden attributes"""

    def test_validate_hidden_attributes_empty_dict(self):
        """Test validation with empty dictionary"""
        validated = validate_hidden_attributes({})
        
        # Should fill in all attributes with default values
        expected_attributes = [
            'hidden_ambition', 'hidden_integrity', 'hidden_discipline',
            'hidden_impulsivity', 'hidden_pragmatism', 'hidden_resilience'
        ]
        
        for attr in expected_attributes:
            assert attr in validated
            assert 1 <= validated[attr] <= 10

    def test_validate_hidden_attributes_non_integer_values(self):
        """Test validation with non-integer values"""
        invalid_attributes = {
            'hidden_ambition': 3.7,    # Float
            'hidden_integrity': "5",   # String
            'hidden_discipline': None, # None
            'hidden_impulsivity': 2,   # Valid integer
        }
        
        validated = validate_hidden_attributes(invalid_attributes)
        
        # Should convert to integers or use defaults
        assert isinstance(validated['hidden_ambition'], int)
        assert isinstance(validated['hidden_integrity'], int)
        assert isinstance(validated['hidden_discipline'], int)
        assert validated['hidden_impulsivity'] == 2

    def test_calculate_behavior_modifiers_extreme_values(self):
        """Test behavior modifier calculation with extreme attribute values"""
        # All minimum values
        min_attributes = {attr: 1 for attr in ['hidden_ambition', 'hidden_integrity', 
                                             'hidden_discipline', 'hidden_impulsivity',
                                             'hidden_pragmatism', 'hidden_resilience']}
        
        # All maximum values  
        max_attributes = {attr: 10 for attr in ['hidden_ambition', 'hidden_integrity',
                                             'hidden_discipline', 'hidden_impulsivity', 
                                             'hidden_pragmatism', 'hidden_resilience']}
        
        min_modifiers = calculate_faction_behavior_modifiers(min_attributes)
        max_modifiers = calculate_faction_behavior_modifiers(max_attributes)
        
        # Should handle extreme values without errors
        assert isinstance(min_modifiers, dict)
        assert isinstance(max_modifiers, dict)
        
        # All modifiers should be valid numbers
        for modifier_dict in [min_modifiers, max_modifiers]:
            for value in modifier_dict.values():
                assert isinstance(value, float)
                assert not (value != value)  # Check for NaN 