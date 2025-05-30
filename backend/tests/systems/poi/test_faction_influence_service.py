from backend.systems.poi.models import PointOfInterest
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.events.dispatcher import EventDispatcher
from typing import Any
from typing import Type
from typing import List

# Import EventBase and EventDispatcher with fallbacks
try: pass
    from backend.systems.events import EventBase, EventDispatcher
except ImportError: pass
    # Fallback for tests or when events system isn't available
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    class EventDispatcher: pass
        @classmethod
        def get_instance(cls): pass
            return cls()
        
        def dispatch(self, event): pass
            pass
        
        def publish(self, event): pass
            pass
        
        def emit(self, event): pass
            pass

"""
Tests for backend.systems.poi.services.faction_influence_service

This module contains tests for POI faction influence functionality.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from backend.systems.poi.services.faction_influence_service import FactionInfluenceService
from backend.systems.poi.models import PointOfInterest, POIType, POIState


class TestFactionInfluenceService: pass
    """Tests for POI faction influence service."""

    @pytest.fixture
    def sample_poi(self): pass
        """Create a sample POI for testing."""
        poi = Mock(spec=PointOfInterest)
        poi.id = "poi_1"
        poi.name = "Test Village"
        poi.poi_type = POIType.VILLAGE
        poi.faction_id = None
        poi.faction_influences = {}
        poi.position = {"x": 0, "y": 0}
        return poi

    @pytest.fixture
    def controlled_poi(self): pass
        """Create a POI controlled by a faction."""
        poi = Mock(spec=PointOfInterest)
        poi.id = "poi_controlled"
        poi.name = "Controlled Settlement"
        poi.poi_type = POIType.TOWN
        poi.faction_id = "faction_a"
        poi.faction_influences = {"faction_a": 0.8, "faction_b": 0.2}
        poi.position = {"x": 5, "y": 5}
        poi.population = 1000  # Add population attribute
        return poi

    @pytest.fixture
    def contested_poi(self): pass
        """Create a POI with contested influence."""
        poi = Mock(spec=PointOfInterest)
        poi.id = "poi_contested"
        poi.name = "Contested City"
        poi.poi_type = POIType.CITY
        poi.faction_id = "faction_a"
        poi.faction_influences = {"faction_a": 0.45, "faction_b": 0.35, "faction_c": 0.2}
        poi.position = {"x": 10, "y": 10}
        return poi

    def test_control_threshold_constant(self): pass
        """Test that control threshold is properly defined."""
        assert FactionInfluenceService.CONTROL_THRESHOLD == 0.5

    def test_significant_influence_constant(self): pass
        """Test that significant influence threshold is properly defined."""
        assert FactionInfluenceService.SIGNIFICANT_INFLUENCE == 0.25

    def test_calculate_regional_influence_empty_list(self): pass
        """Test regional influence calculation with empty POI list."""
        result = FactionInfluenceService.calculate_regional_influence([], "faction_a")
        
        expected = {
            "controlled_poi_count": 0,
            "influenced_poi_count": 0,
            "total_poi_count": 0,
            "control_percentage": 0.0,
            "influence_percentage": 0.0,
            "average_influence": 0.0,
            "controlled_pois": [],
            "influenced_pois": [],
        }
        
        assert result == expected

    def test_calculate_regional_influence_single_controlled_poi(self, controlled_poi): pass
        """Test regional influence calculation with single controlled POI."""
        pois = [controlled_poi]
        result = FactionInfluenceService.calculate_regional_influence(pois, "faction_a")
        
        assert result["controlled_poi_count"] == 1
        assert result["influenced_poi_count"] == 0
        assert result["total_poi_count"] == 1
        assert result["control_percentage"] == 1.0
        assert result["influence_percentage"] == 1.0
        assert result["average_influence"] == 0.8
        assert len(result["controlled_pois"]) == 1
        assert result["controlled_pois"][0]["id"] == "poi_controlled"

    def test_calculate_regional_influence_mixed_pois(self, controlled_poi, contested_poi, sample_poi): pass
        """Test regional influence calculation with mixed POI types."""
        pois = [controlled_poi, contested_poi, sample_poi]
        result = FactionInfluenceService.calculate_regional_influence(pois, "faction_a")
        
        assert result["controlled_poi_count"] == 2  # controlled_poi and contested_poi
        assert result["influenced_poi_count"] == 0
        assert result["total_poi_count"] == 3
        assert result["control_percentage"] == 2/3
        assert result["influence_percentage"] == 2/3

    def test_calculate_regional_influence_influenced_poi(self): pass
        """Test regional influence calculation with influenced but not controlled POI."""
        # Create POI with significant influence but not control
        influenced_poi = Mock(spec=PointOfInterest)
        influenced_poi.id = "poi_influenced"
        influenced_poi.name = "Influenced Settlement"
        influenced_poi.faction_id = "faction_b"  # Controlled by different faction
        influenced_poi.faction_influences = {"faction_a": 0.3, "faction_b": 0.7}  # faction_a has significant influence
        influenced_poi.position = {"x": 15, "y": 15}
        
        pois = [influenced_poi]
        result = FactionInfluenceService.calculate_regional_influence(pois, "faction_a")
        
        assert result["controlled_poi_count"] == 0
        assert result["influenced_poi_count"] == 1
        assert result["total_poi_count"] == 1
        assert result["control_percentage"] == 0.0
        assert result["influence_percentage"] == 1.0
        assert len(result["influenced_pois"]) == 1
        assert result["influenced_pois"][0]["controlling_faction"] == "faction_b"

    @patch('backend.systems.events.EventDispatcher.get_instance')
    def test_add_faction_influence_to_poi_basic(self, mock_get_instance, sample_poi): pass
        """Test basic faction influence addition."""
        # Mock event dispatcher
        mock_dispatcher = Mock()
        mock_get_instance.return_value = mock_dispatcher
        
        updated_poi = FactionInfluenceService.add_faction_influence_to_poi(
            sample_poi, "faction_a", 0.3, "conquest"
        )
        
        assert updated_poi.faction_influences["faction_a"] == 0.3
        # Should emit influence changed event
        assert mock_dispatcher.publish.called

    @patch('backend.systems.events.EventDispatcher.get_instance')
    def test_add_faction_influence_control_threshold(self, mock_get_instance, sample_poi): pass
        """Test faction influence reaching control threshold."""
        mock_dispatcher = Mock()
        mock_get_instance.return_value = mock_dispatcher
        
        # Add enough influence to reach control threshold
        updated_poi = FactionInfluenceService.add_faction_influence_to_poi(
            sample_poi, "faction_a", 0.6, "conquest"
        )
        
        assert updated_poi.faction_influences["faction_a"] == 0.6
        assert updated_poi.faction_id == "faction_a"
        # Should emit both influence changed and control changed events
        assert mock_dispatcher.publish.call_count == 2

    @patch('backend.systems.events.EventDispatcher.get_instance')
    def test_add_faction_influence_negative_amount(self, mock_get_instance, controlled_poi): pass
        """Test reducing faction influence."""
        mock_dispatcher = Mock()
        mock_get_instance.return_value = mock_dispatcher
        
        # Reduce influence
        updated_poi = FactionInfluenceService.add_faction_influence_to_poi(
            controlled_poi, "faction_a", -0.3, "resistance"
        )
        
        assert updated_poi.faction_influences["faction_a"] == 0.5  # 0.8 - 0.3
        # Should emit influence changed event
        assert mock_dispatcher.publish.called

    def test_add_faction_influence_invalid_faction_id(self, sample_poi): pass
        """Test adding influence with invalid faction ID."""
        # Test with None faction ID
        updated_poi = FactionInfluenceService.add_faction_influence_to_poi(
            sample_poi, None, 0.3, "test"
        )
        assert updated_poi == sample_poi  # No changes
        
        # Test with empty string faction ID
        updated_poi = FactionInfluenceService.add_faction_influence_to_poi(
            sample_poi, "", 0.3, "test"
        )
        assert updated_poi == sample_poi  # No changes

    def test_add_faction_influence_clamping(self, sample_poi): pass
        """Test that influence values are properly clamped between 0 and 1."""
        with patch('backend.systems.events.EventDispatcher.get_instance'): pass
            # Test upper bound clamping
            updated_poi = FactionInfluenceService.add_faction_influence_to_poi(
                sample_poi, "faction_a", 1.5, "test"
            )
            assert updated_poi.faction_influences["faction_a"] == 1.0
            
            # Test lower bound clamping
            updated_poi = FactionInfluenceService.add_faction_influence_to_poi(
                updated_poi, "faction_a", -2.0, "test"
            )
            assert updated_poi.faction_influences["faction_a"] == 0.0

    def test_add_faction_influence_no_change(self, sample_poi): pass
        """Test that tiny influence changes are ignored."""
        with patch('backend.systems.events.EventDispatcher.get_instance') as mock_get_instance: pass
            mock_dispatcher = Mock()
            mock_get_instance.return_value = mock_dispatcher
            
            # Add some initial influence
            FactionInfluenceService.add_faction_influence_to_poi(
                sample_poi, "faction_a", 0.5, "initial"
            )
            
            # Reset mock
            mock_dispatcher.reset_mock()
            
            # Add tiny amount that should be ignored
            updated_poi = FactionInfluenceService.add_faction_influence_to_poi(
                sample_poi, "faction_a", 0.0005, "tiny change"
            )
            
            # Should not emit events for tiny changes
            assert not mock_dispatcher.publish.called

    def test_simulate_influence_contest(self): pass
        """Test faction influence contest simulation."""
        # Create test POIs
        poi1 = Mock(spec=PointOfInterest)
        poi1.id = "poi_1"
        poi1.faction_id = None
        poi1.faction_influences = {"faction_a": 0.3, "faction_b": 0.2}
        
        poi2 = Mock(spec=PointOfInterest)
        poi2.id = "poi_2"
        poi2.faction_id = None
        poi2.faction_influences = {"faction_a": 0.6, "faction_c": 0.1}
        
        pois = [poi1, poi2]
        contesting_factions = {"faction_a": 0.1, "faction_b": 0.05, "faction_c": 0.08}
        
        with patch('backend.systems.events.EventDispatcher.get_instance'): pass
            updated_pois = FactionInfluenceService.simulate_influence_contest(
                pois, contesting_factions
            )
        
        assert isinstance(updated_pois, list)
        assert len(updated_pois) == 2

    def test_calculate_faction_influence_spread(self, controlled_poi): pass
        """Test faction influence spread calculation."""
        # Create target POIs
        target1 = Mock(spec=PointOfInterest)
        target1.id = "target_1"
        target1.position = {"x": 6, "y": 6}
        target1.faction_influences = {}
        
        target2 = Mock(spec=PointOfInterest)
        target2.id = "target_2" 
        target2.position = {"x": 10, "y": 10}
        target2.faction_influences = {}
        
        target_pois = [target1, target2]
        
        # Mock tilemap service to return actual float values
        mock_tilemap_service = Mock()
        mock_tilemap_service.calculate_distance_between_positions.return_value = 5.0
        
        result = FactionInfluenceService.calculate_faction_influence_spread(
            controlled_poi, target_pois, mock_tilemap_service
        )
        
        assert isinstance(result, dict)

    def test_apply_natural_influence_spread(self): pass
        """Test natural influence spread application."""
        # Create test POIs with proper id attributes
        poi1 = Mock(spec=PointOfInterest)
        poi1.id = "poi_1"
        poi1.faction_influences = {"faction_a": 0.8}
        poi1.position = {"x": 0, "y": 0}
        
        poi2 = Mock(spec=PointOfInterest)
        poi2.id = "poi_2"
        poi2.faction_influences = {"faction_b": 0.6}
        poi2.position = {"x": 5, "y": 5}
        
        pois = [poi1, poi2]
        
        # Mock tilemap service
        mock_tilemap_service = Mock()
        mock_tilemap_service.calculate_distance_between_positions.return_value = 3.0
        
        with patch('backend.systems.events.EventDispatcher.get_instance'): pass
            updated_pois = FactionInfluenceService.apply_natural_influence_spread(
                pois, mock_tilemap_service
            )
        
        assert isinstance(updated_pois, list)
        assert len(updated_pois) == 2

    def test_poi_without_faction_influences_attribute(self): pass
        """Test handling POI without faction_influences attribute."""
        poi_no_influences = Mock(spec=PointOfInterest)
        poi_no_influences.id = "poi_no_influences"
        poi_no_influences.name = "No Influences POI"
        poi_no_influences.faction_id = None
        poi_no_influences.position = {"x": 0, "y": 0}
        # Deliberately not setting faction_influences attribute
        
        result = FactionInfluenceService.calculate_regional_influence(
            [poi_no_influences], "faction_a"
        )
        
        assert result["controlled_poi_count"] == 0
        assert result["influenced_poi_count"] == 0
        assert result["total_poi_count"] == 1
        assert result["average_influence"] == 0.0

    def test_edge_cases_influence_calculation(self): pass
        """Test edge cases in influence calculations."""
        # POI with invalid faction_influences (not a dict)
        invalid_poi = Mock(spec=PointOfInterest)
        invalid_poi.id = "invalid_poi"
        invalid_poi.faction_influences = "not_a_dict"
        invalid_poi.faction_id = None
        invalid_poi.position = {"x": 0, "y": 0}
        
        result = FactionInfluenceService.calculate_regional_influence(
            [invalid_poi], "faction_a"
        )
        
        assert result["controlled_poi_count"] == 0
        assert result["influenced_poi_count"] == 0
        assert result["average_influence"] == 0.0

    def test_influence_initialization(self, sample_poi): pass
        """Test that faction influences dict is properly initialized."""
        # Remove faction_influences attribute to test initialization
        if hasattr(sample_poi, 'faction_influences'): pass
            delattr(sample_poi, 'faction_influences')
        
        with patch('backend.systems.events.EventDispatcher.get_instance'): pass
            updated_poi = FactionInfluenceService.add_faction_influence_to_poi(
                sample_poi, "faction_a", 0.3, "test"
            )
        
        assert hasattr(updated_poi, 'faction_influences')
        assert isinstance(updated_poi.faction_influences, dict)
        assert updated_poi.faction_influences["faction_a"] == 0.3 