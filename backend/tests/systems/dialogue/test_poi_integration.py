"""
Test the DialoguePOIIntegration class.

This module tests all functionality of the POI integration system including
context addition, location state retrieval, settlement information, and POI descriptions.
"""

import pytest
from unittest.mock import MagicMock, patch
from backend.systems.dialogue.poi_integration import DialoguePOIIntegration, POIServiceWrapper


class TestPOIServiceWrapper: pass
    """Test cases for POIServiceWrapper class."""

    @pytest.fixture
    def wrapper(self): pass
        """Create POIServiceWrapper instance."""
        return POIServiceWrapper()

    def test_init(self, wrapper): pass
        """Test POIServiceWrapper initialization."""
        assert wrapper.poi_service is not None

    def test_get_poi(self, wrapper): pass
        """Test getting a POI by ID."""
        result = wrapper.get_poi("test_poi_1")
        
        assert result["id"] == "test_poi_1"
        assert "name" in result
        assert "state" in result
        assert "type" in result
        assert "description" in result
        assert "population" in result
        assert "region" in result

    def test_query_pois(self, wrapper): pass
        """Test querying POIs."""
        result = wrapper.query_pois({"type": "settlement"})
        assert isinstance(result, list)

    def test_get_nearby_pois(self, wrapper): pass
        """Test getting nearby POIs."""
        result = wrapper.get_nearby_pois(location="test", radius=5.0)
        assert isinstance(result, list)

    def test_get_settlement(self, wrapper): pass
        """Test getting settlement information."""
        result = wrapper.get_settlement("test_settlement")
        
        assert result["id"] == "test_settlement"
        assert "name" in result
        assert "type" in result
        assert "state" in result
        assert "population" in result
        assert "region" in result
        assert "description" in result
        assert "notable_features" in result
        assert "prosperity" in result
        assert "primary_industry" in result
        assert "faction_control" in result

    def test_get_settlement_pois(self, wrapper): pass
        """Test getting POIs within a settlement."""
        result = wrapper.get_settlement_pois("test_settlement")
        assert isinstance(result, list)


class TestDialoguePOIIntegration: pass
    """Test cases for DialoguePOIIntegration class."""

    @pytest.fixture
    def mock_poi_service(self): pass
        """Create a mock POI service."""
        mock_service = MagicMock()
        
        # Mock POI data
        mock_service.get_poi.return_value = {
            "id": "location_1",
            "name": "Test Location",
            "state": "normal",
            "type": "village",
            "description": "A peaceful village",
            "population": 150,
            "region": "north",
            "state_duration": 0,
            "state_severity": 0,
            "local_knowledge": "Known for its markets",
            "history": "Founded 200 years ago",
            "expert_knowledge": "Built on ancient ruins"
        }
        
        # Mock settlement data
        mock_service.get_settlement.return_value = {
            "id": "settlement_1",
            "name": "Test Settlement",
            "type": "town",
            "state": "prospering",
            "population": 500,
            "region": "central",
            "description": "A thriving trade town",
            "notable_features": ["market", "inn", "temple"],
            "prosperity": "high",
            "primary_industry": "trade",
            "faction_control": "merchants_guild"
        }
        
        # Mock nearby locations
        mock_service.get_nearby_pois.return_value = [
            {
                "id": "nearby_1",
                "name": "Nearby Place",
                "state": "normal",
                "type": "landmark"
            }
        ]
        
        # Mock settlement POIs
        mock_service.get_settlement_pois.return_value = [
            {
                "id": "poi_1",
                "name": "Market Square",
                "type": "marketplace"
            },
            {
                "id": "poi_2", 
                "name": "The Inn",
                "type": "inn"
            }
        ]
        
        # Mock POI query
        mock_service.query_pois.return_value = [
            {
                "id": "relevant_poi",
                "name": "Relevant Place",
                "type": "shop",
                "state": "normal",
                "relevance_reason": "Character works here"
            }
        ]
        
        return mock_service

    @pytest.fixture
    def integration(self, mock_poi_service): pass
        """Create DialoguePOIIntegration instance with mock service."""
        return DialoguePOIIntegration(poi_service=mock_poi_service)

    @pytest.fixture
    def integration_default(self): pass
        """Create DialoguePOIIntegration instance with default service."""
        return DialoguePOIIntegration()

    def test_init_with_service(self, mock_poi_service): pass
        """Test initialization with provided POI service."""
        integration = DialoguePOIIntegration(poi_service=mock_poi_service)
        assert integration.poi_service == mock_poi_service

    def test_init_without_service(self, integration_default): pass
        """Test initialization without provided POI service."""
        assert isinstance(integration_default.poi_service, POIServiceWrapper)

    def test_add_poi_context_to_dialogue_full(self, integration, mock_poi_service): pass
        """Test adding POI context with all options enabled."""
        context = {"existing_key": "existing_value"}
        
        result = integration.add_poi_context_to_dialogue(
            context=context,
            location_id="location_1",
            include_nearby=True,
            nearby_radius=15.0,
            include_details=True
        )
        
        # Verify original context preserved
        assert result["existing_key"] == "existing_value"
        
        # Verify locations context added
        assert "locations" in result
        assert "current" in result["locations"]
        assert "current_state" in result["locations"]
        assert "state_description" in result["locations"]
        assert "nearby" in result["locations"]
        
        # Verify current location info
        current = result["locations"]["current"]
        assert current["id"] == "location_1"
        assert current["name"] == "Test Location"
        assert current["state"] == "normal"

    def test_add_poi_context_to_dialogue_minimal(self, integration, mock_poi_service): pass
        """Test adding POI context with minimal options."""
        context = {}
        
        result = integration.add_poi_context_to_dialogue(
            context=context,
            location_id="location_1",
            include_nearby=False,
            include_details=False
        )
        
        assert "locations" in result
        assert "current" in result["locations"]
        assert "nearby" not in result["locations"]

    def test_add_poi_context_to_dialogue_existing_locations(self, integration, mock_poi_service): pass
        """Test adding POI context when locations already exist in context."""
        context = {"locations": {"existing": "data"}}
        
        result = integration.add_poi_context_to_dialogue(
            context=context,
            location_id="location_1"
        )
        
        assert result["locations"]["existing"] == "data"
        assert "current" in result["locations"]

    def test_add_poi_context_to_dialogue_no_location_found(self, integration, mock_poi_service): pass
        """Test adding POI context when location is not found."""
        mock_poi_service.get_poi.return_value = None
        context = {}
        
        result = integration.add_poi_context_to_dialogue(
            context=context,
            location_id="nonexistent"
        )
        
        assert "locations" in result
        assert "current" not in result["locations"]

    def test_get_location_state_for_dialogue_success(self, integration, mock_poi_service): pass
        """Test successful location state retrieval."""
        result = integration.get_location_state_for_dialogue("location_1")
        
        assert result["state"] == "normal"
        assert "description" in result
        assert "visible_effects" in result
        assert "duration" in result
        assert "severity" in result

    def test_get_location_state_for_dialogue_not_found(self, integration, mock_poi_service): pass
        """Test location state retrieval when location not found."""
        mock_poi_service.get_poi.return_value = None
        
        result = integration.get_location_state_for_dialogue("nonexistent")
        assert result == {}

    def test_get_location_state_for_dialogue_exception(self, integration, mock_poi_service): pass
        """Test location state retrieval with exception."""
        mock_poi_service.get_poi.side_effect = Exception("Service error")
        
        result = integration.get_location_state_for_dialogue("location_1")
        assert result == {"state": "unknown"}

    def test_get_settlement_dialogue_context_full(self, integration, mock_poi_service): pass
        """Test getting full settlement dialogue context."""
        result = integration.get_settlement_dialogue_context(
            settlement_id="settlement_1",
            include_details=True
        )
        
        # Basic info
        assert result["id"] == "settlement_1"
        assert result["name"] == "Test Settlement"
        assert result["type"] == "town"
        assert result["state"] == "prospering"
        assert result["population"] == 500
        assert result["region"] == "central"
        
        # Detailed info
        assert "description" in result
        assert "notable_features" in result
        assert "prosperity" in result
        assert "primary_industry" in result
        assert "faction_control" in result
        assert "state_description" in result
        assert "points_of_interest" in result
        
        # POIs
        assert len(result["points_of_interest"]) == 2
        assert result["points_of_interest"][0]["name"] == "Market Square"

    def test_get_settlement_dialogue_context_minimal(self, integration, mock_poi_service): pass
        """Test getting minimal settlement dialogue context."""
        result = integration.get_settlement_dialogue_context(
            settlement_id="settlement_1",
            include_details=False
        )
        
        # Should have basic info
        assert "id" in result
        assert "name" in result
        assert "type" in result
        
        # Should not have detailed info
        assert "description" not in result
        assert "notable_features" not in result
        assert "points_of_interest" not in result

    def test_get_settlement_dialogue_context_not_found(self, integration, mock_poi_service): pass
        """Test getting settlement context when settlement not found."""
        mock_poi_service.get_settlement.return_value = None
        
        result = integration.get_settlement_dialogue_context("nonexistent")
        assert result == {}

    def test_get_settlement_dialogue_context_exception(self, integration, mock_poi_service): pass
        """Test getting settlement context with exception."""
        mock_poi_service.get_settlement.side_effect = Exception("Service error")
        
        result = integration.get_settlement_dialogue_context("settlement_1")
        assert result == {}

    def test_get_poi_description_for_dialogue_visitor(self, integration, mock_poi_service): pass
        """Test getting POI description from visitor perspective."""
        result = integration.get_poi_description_for_dialogue(
            poi_id="location_1",
            perspective="visitor",
            time_of_day="morning"
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "peaceful village" in result.lower()

    def test_get_poi_description_for_dialogue_local(self, integration, mock_poi_service): pass
        """Test getting POI description from local perspective."""
        result = integration.get_poi_description_for_dialogue(
            poi_id="location_1",
            perspective="local"
        )
        
        assert isinstance(result, str)
        assert "markets" in result.lower()

    def test_get_poi_description_for_dialogue_expert(self, integration, mock_poi_service): pass
        """Test getting POI description from expert perspective."""
        result = integration.get_poi_description_for_dialogue(
            poi_id="location_1",
            perspective="expert"
        )
        
        assert isinstance(result, str)
        assert "200 years ago" in result

    def test_get_poi_description_for_dialogue_not_found(self, integration, mock_poi_service): pass
        """Test getting POI description when POI not found."""
        mock_poi_service.get_poi.return_value = None
        
        result = integration.get_poi_description_for_dialogue("nonexistent")
        assert result == "This location is unknown."

    def test_get_poi_description_for_dialogue_exception(self, integration, mock_poi_service): pass
        """Test getting POI description with exception."""
        mock_poi_service.get_poi.side_effect = Exception("Service error")
        
        result = integration.get_poi_description_for_dialogue("location_1")
        assert result == "Information about this location is unavailable."

    def test_get_relevant_pois_for_dialogue_success(self, integration, mock_poi_service): pass
        """Test getting relevant POIs for dialogue."""
        with patch.object(integration, '_get_character_info') as mock_char_info: pass
            mock_char_info.return_value = {
                "home_location": "home_1",
                "occupation": "merchant",
                "interests": ["trade", "travel"],
                "faction": "merchants_guild"
            }
            
            result = integration.get_relevant_pois_for_dialogue(
                character_id="char_1",
                topic="trade",
                limit=5
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert result[0]["name"] == "Relevant Place"
            assert "relevance_reason" in result[0]

    def test_get_relevant_pois_for_dialogue_exception(self, integration, mock_poi_service): pass
        """Test getting relevant POIs with exception."""
        with patch.object(integration, '_get_character_info') as mock_char_info: pass
            mock_char_info.side_effect = Exception("Character service error")
            
            result = integration.get_relevant_pois_for_dialogue("char_1")
            assert result == []

    def test_get_location_info_success(self, integration, mock_poi_service): pass
        """Test getting location info successfully."""
        result = integration._get_location_info("location_1", include_details=True)
        
        assert result["id"] == "location_1"
        assert result["name"] == "Test Location"
        assert result["state"] == "normal"

    def test_get_location_info_minimal(self, integration, mock_poi_service): pass
        """Test getting minimal location info."""
        result = integration._get_location_info("location_1", include_details=False)
        
        assert "id" in result
        assert "name" in result
        assert "state" in result

    def test_get_location_info_not_found(self, integration, mock_poi_service): pass
        """Test getting location info when location not found."""
        mock_poi_service.get_poi.return_value = None
        
        result = integration._get_location_info("nonexistent")
        assert result == {}

    def test_get_location_info_exception(self, integration, mock_poi_service): pass
        """Test getting location info with exception."""
        mock_poi_service.get_poi.side_effect = Exception("Service error")
        
        result = integration._get_location_info("location_1")
        assert result == {}

    def test_get_nearby_locations_success(self, integration, mock_poi_service): pass
        """Test getting nearby locations successfully."""
        result = integration._get_nearby_locations(
            location_id="location_1",
            radius=10.0,
            include_details=True
        )
        
        assert isinstance(result, list)
        mock_poi_service.get_nearby_pois.assert_called_once()

    def test_get_nearby_locations_exception(self, integration, mock_poi_service): pass
        """Test getting nearby locations with exception."""
        mock_poi_service.get_nearby_pois.side_effect = Exception("Service error")
        
        result = integration._get_nearby_locations("location_1")
        assert result == []

    def test_get_state_description(self): pass
        """Test the _get_state_description private method."""
        integration = DialoguePOIIntegration()
        
        # Test normal state
        result = integration._get_state_description("normal")
        expected_phrase = "usual state with normal activity"
        assert expected_phrase in result.lower()
        
        # Test declining state
        result = integration._get_state_description("declining")
        expected_phrase = "decline"
        assert expected_phrase in result.lower()
        
        # Test unknown state
        result = integration._get_state_description("unknown_state")
        expected_phrase = "unclear"
        assert expected_phrase in result.lower()

    def test_get_state_visible_effects(self, integration): pass
        """Test getting visible effects for all states."""
        test_cases = [
            "normal", "declining", "abandoned", "prospering", 
            "recovering", "unknown_state"
        ]
        
        for state in test_cases: pass
            result = integration._get_state_visible_effects(state)
            assert isinstance(result, list)

    def test_get_state_narrative(self, integration): pass
        """Test getting state narratives for all states."""
        test_cases = [
            "normal", "declining", "abandoned", "prospering", 
            "recovering", "unknown_state"
        ]
        
        for state in test_cases: pass
            result = integration._get_state_narrative(state)
            assert isinstance(result, str)

    def test_get_time_based_poi_description(self, integration): pass
        """Test getting time-based POI descriptions."""
        test_times = ["morning", "afternoon", "evening", "night", "dawn", "dusk", "unknown_time"]
        
        for time_of_day in test_times: pass
            result = integration._get_time_based_poi_description("location_1", time_of_day)
            assert isinstance(result, str)

    def test_get_character_info(self, integration): pass
        """Test getting character information (stub implementation)."""
        result = integration._get_character_info("char_1")
        
        assert isinstance(result, dict)
        assert "home_location" in result
        assert "occupation" in result
        assert "interests" in result
        assert "faction" in result 