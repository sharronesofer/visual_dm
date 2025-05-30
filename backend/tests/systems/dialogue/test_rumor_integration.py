from backend.systems.shared.database.base import Base
from backend.systems.shared.database.base import Base
"""
Test the DialogueRumorIntegration class.

This module tests all functionality of the rumor integration system including
rumor creation from dialogue, adding rumors to context, relevance calculation,
and rumor spreading through dialogue.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.systems.dialogue.rumor_integration import DialogueRumorIntegration


class TestDialogueRumorIntegration: pass
    """Test cases for DialogueRumorIntegration class."""

    @pytest.fixture
    def mock_rumor_service(self): pass
        """Create a mock rumor service."""
        mock_service = AsyncMock()
        mock_service.create_rumor = AsyncMock(return_value="rumor_123")
        mock_service.get_character_known_rumors = AsyncMock(return_value=[])
        mock_service.spread_rumor = AsyncMock(return_value=True)
        return mock_service

    @pytest.fixture
    def integration(self, mock_rumor_service): pass
        """Create a DialogueRumorIntegration instance with mocked dependencies."""
        return DialogueRumorIntegration(rumor_manager=mock_rumor_service)

    @pytest.fixture
    def sample_rumor(self): pass
        """Sample rumor for testing."""
        return {
            "id": "rumor_123",
            "content": "There's a secret passage behind the tavern",
            "origin_location_id": "location_1",
            "mentions_character_id": "char_2",
            "created_at": "2023-01-01T00:00:00Z",
            "veracity": 0.7
        }

    @pytest.fixture
    def sample_context(self): pass
        """Sample dialogue context for testing."""
        return {
            "location_id": "location_1",
            "target_id": "char_1",
            "recent_messages": [
                {
                    "content": "Did you hear about the mysterious passage?",
                    "speaker_id": "char_1"
                }
            ],
            "location": {
                "name": "The Red Dragon Tavern",
                "type": "tavern"
            }
        }

    def test_init_default(self): pass
        """Test initialization with default rumor service."""
        with patch('backend.systems.dialogue.rumor_integration.RumorService') as mock_service_class: pass
            mock_instance = MagicMock()
            mock_service_class.get_instance.return_value = mock_instance
            
            integration = DialogueRumorIntegration()
            
            assert integration.rumor_service is mock_instance
            assert integration.rumor_threshold == 0.7

    def test_init_with_rumor_manager(self, mock_rumor_service): pass
        """Test initialization with provided rumor manager."""
        integration = DialogueRumorIntegration(rumor_manager=mock_rumor_service)
        
        assert integration.rumor_service is mock_rumor_service
        assert integration.rumor_threshold == 0.7

    @pytest.mark.asyncio
    async def test_generate_rumor_from_dialogue_success(self, integration, mock_rumor_service): pass
        """Test successful rumor generation from dialogue."""
        message = "I heard that there's a secret treasure hidden in the old castle"
        
        # Mock the private methods to return values that will trigger rumor creation
        integration._evaluate_rumor_potential = MagicMock(return_value=0.8)
        integration._extract_rumor_content = MagicMock(return_value="there's a secret treasure hidden in the old castle")
        integration._determine_veracity = MagicMock(return_value=0.6)
        
        result = await integration.generate_rumor_from_dialogue(
            speaker_id="char_1",
            message=message,
            location_id="location_1",
            metadata={"test": "data"}
        )
        
        assert result == "rumor_123"
        integration._evaluate_rumor_potential.assert_called_once_with(message)
        integration._extract_rumor_content.assert_called_once_with(message)
        integration._determine_veracity.assert_called_once_with(message)
        mock_rumor_service.create_rumor.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_rumor_from_dialogue_low_potential(self, integration): pass
        """Test rumor generation with low potential message."""
        message = "Hello, how are you today?"
        
        integration._evaluate_rumor_potential = MagicMock(return_value=0.5)  # Below threshold
        
        result = await integration.generate_rumor_from_dialogue(
            speaker_id="char_1",
            message=message
        )
        
        assert result is None
        integration._evaluate_rumor_potential.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_generate_rumor_from_dialogue_no_content(self, integration): pass
        """Test rumor generation when no rumor content can be extracted."""
        message = "I heard that something happened"
        
        integration._evaluate_rumor_potential = MagicMock(return_value=0.8)
        integration._extract_rumor_content = MagicMock(return_value=None)
        
        result = await integration.generate_rumor_from_dialogue(
            speaker_id="char_1",
            message=message
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_rumor_from_dialogue_service_error(self, integration, mock_rumor_service): pass
        """Test rumor generation when rumor service throws an error."""
        message = "I heard that there's a secret passage"
        
        integration._evaluate_rumor_potential = MagicMock(return_value=0.8)
        integration._extract_rumor_content = MagicMock(return_value="there's a secret passage")
        integration._determine_veracity = MagicMock(return_value=0.6)
        mock_rumor_service.create_rumor.side_effect = Exception("Service error")
        
        result = await integration.generate_rumor_from_dialogue(
            speaker_id="char_1",
            message=message
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_add_rumors_to_context_with_rumors(self, integration, sample_context, sample_rumor): pass
        """Test adding rumors to context when rumors are available."""
        integration.get_relevant_rumors = AsyncMock(return_value=[sample_rumor])
        
        result = await integration.add_rumors_to_context(
            character_id="char_1",
            context=sample_context,
            limit=3
        )
        
        assert "rumors" in result
        assert len(result["rumors"]) == 1
        assert result["rumors"][0] == sample_rumor
        # Original context should not be modified
        assert "rumors" not in sample_context

    @pytest.mark.asyncio
    async def test_add_rumors_to_context_no_rumors(self, integration, sample_context): pass
        """Test adding rumors to context when no rumors are available."""
        integration.get_relevant_rumors = AsyncMock(return_value=[])
        
        result = await integration.add_rumors_to_context(
            character_id="char_1",
            context=sample_context,
            limit=3
        )
        
        assert result == sample_context  # Should be unchanged

    @pytest.mark.asyncio
    async def test_add_rumors_to_context_existing_rumors(self, integration, sample_rumor): pass
        """Test adding rumors to context that already has rumors."""
        existing_rumor = {"id": "existing", "content": "Existing rumor"}
        context_with_rumors = {
            "target_id": "char_1",
            "rumors": [existing_rumor]
        }
        
        integration.get_relevant_rumors = AsyncMock(return_value=[sample_rumor])
        
        result = await integration.add_rumors_to_context(
            character_id="char_1",
            context=context_with_rumors,
            limit=3
        )
        
        assert len(result["rumors"]) == 2
        assert existing_rumor in result["rumors"]
        assert sample_rumor in result["rumors"]

    @pytest.mark.asyncio
    async def test_get_relevant_rumors_no_known_rumors(self, integration, mock_rumor_service, sample_context): pass
        """Test getting relevant rumors when character knows no rumors."""
        mock_rumor_service.get_character_known_rumors.return_value = []
        
        result = await integration.get_relevant_rumors(
            character_id="char_1",
            context=sample_context,
            limit=3
        )
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_relevant_rumors_with_filtering(self, integration, mock_rumor_service, sample_context): pass
        """Test getting relevant rumors with relevance filtering."""
        rumors = [
            {"id": "rumor_1", "content": "About passage", "relevance_score": 0.9},
            {"id": "rumor_2", "content": "About dragon", "relevance_score": 0.3},
            {"id": "rumor_3", "content": "About tavern", "relevance_score": 0.7},
        ]
        mock_rumor_service.get_character_known_rumors.return_value = rumors
        
        integration._extract_topics_from_context = MagicMock(return_value={"passage", "tavern"})
        integration._calculate_rumor_relevance = MagicMock(side_effect=[0.9, 0.3, 0.7])
        
        result = await integration.get_relevant_rumors(
            character_id="char_1",
            context=sample_context,
            limit=2
        )
        
        # Should return top 2 most relevant rumors
        assert len(result) == 2
        assert result[0]["id"] == "rumor_1"  # Highest relevance
        assert result[1]["id"] == "rumor_3"  # Second highest

    @pytest.mark.asyncio
    async def test_spread_rumor_via_dialogue_success(self, integration, mock_rumor_service): pass
        """Test successful rumor spreading via dialogue."""
        result = await integration.spread_rumor_via_dialogue(
            rumor_id="rumor_123",
            speaker_id="char_1",
            listener_id="char_2",
            belief_modifier=0.1
        )
        
        assert result is True
        mock_rumor_service.spread_rumor.assert_called_once_with(
            rumor_id="rumor_123",
            from_character_id="char_1",
            to_character_id="char_2",
            spread_method="dialogue",
            belief_modifier=0.1
        )

    @pytest.mark.asyncio
    async def test_spread_rumor_via_dialogue_failure(self, integration, mock_rumor_service): pass
        """Test rumor spreading failure."""
        mock_rumor_service.spread_rumor.return_value = False
        
        result = await integration.spread_rumor_via_dialogue(
            rumor_id="rumor_123",
            speaker_id="char_1",
            listener_id="char_2"
        )
        
        assert result is False

    @pytest.mark.asyncio
    async def test_spread_rumor_via_dialogue_exception(self, integration, mock_rumor_service): pass
        """Test rumor spreading when service throws exception."""
        mock_rumor_service.spread_rumor.side_effect = Exception("Service error")
        
        result = await integration.spread_rumor_via_dialogue(
            rumor_id="rumor_123",
            speaker_id="char_1",
            listener_id="char_2"
        )
        
        assert result is False

    def test_evaluate_rumor_potential_high(self, integration): pass
        """Test rumor potential evaluation for high-potential message."""
        message = "I heard a secret rumor about a mysterious hidden treasure supposedly discovered by suspicious strangers"
        
        result = integration._evaluate_rumor_potential(message)
        
        assert result > 0.7  # Should be high due to multiple keywords

    def test_evaluate_rumor_potential_low(self, integration): pass
        """Test rumor potential evaluation for low-potential message."""
        message = "Hello, how are you?"
        
        result = integration._evaluate_rumor_potential(message)
        
        assert result < 0.5  # Should be low due to no keywords and short length

    def test_evaluate_rumor_potential_medium(self, integration): pass
        """Test rumor potential evaluation for medium-potential message."""
        message = "I heard something interesting happened at the market yesterday, though I'm not sure what exactly"
        
        result = integration._evaluate_rumor_potential(message)
        
        assert 0.3 <= result <= 0.8  # Should be medium

    def test_extract_rumor_content_with_starter(self, integration): pass
        """Test rumor content extraction with rumor starter phrase."""
        message = "I heard that there's a dragon living in the mountains."
        
        result = integration._extract_rumor_content(message)
        
        assert result == "there's a dragon living in the mountains"

    def test_extract_rumor_content_multiple_starters(self, integration): pass
        """Test rumor content extraction with multiple starter phrases."""
        message = "They say that rumor has it there's treasure buried here."
        
        result = integration._extract_rumor_content(message)
        
        # Should extract from the first found starter
        assert "there's treasure buried here" in result or "rumor has it there's treasure buried here" in result

    def test_extract_rumor_content_no_starter(self, integration): pass
        """Test rumor content extraction without starter phrase."""
        message = "The weather is nice today."
        
        result = integration._extract_rumor_content(message)
        
        assert result is None

    def test_extract_rumor_content_too_short(self, integration): pass
        """Test rumor content extraction with content too short."""
        message = "I heard that no."
        
        result = integration._extract_rumor_content(message)
        
        assert result is None  # Content "no" is too short

    def test_determine_veracity_with_certainty_keywords(self, integration): pass
        """Test determining veracity with certainty keywords."""
        content_certain = "I am absolutely certain that dragons exist in the mountains."
        content_uncertain = "I heard rumors that dragons might exist in the mountains."
        
        result_certain = integration._determine_veracity(content_certain)
        result_uncertain = integration._determine_veracity(content_uncertain)
        
        # Both should return valid veracity scores between 0 and 1
        assert 0 <= result_certain <= 1
        assert 0 <= result_uncertain <= 1
        # The difference should be measurable, even if small
        assert abs(result_certain - result_uncertain) > 0.01

    def test_determine_veracity_no_keywords(self, integration): pass
        """Test veracity determination without special keywords."""
        message = "There was something in the forest"
        
        # Run multiple times to test randomization
        results = [integration._determine_veracity(message) for _ in range(10)]
        
        # All results should be in valid range
        assert all(0.0 <= result <= 1.0 for result in results)
        # Should have some variation due to randomization
        assert len(set(results)) > 1

    def test_extract_topics_from_context_recent_messages(self, integration): pass
        """Test topic extraction from recent messages."""
        context = {
            "recent_messages": [
                {"content": "The ancient dragon sleeps in the mountain cave"},
                {"content": "Treasure hunters seek the golden crown"}
            ]
        }
        
        result = integration._extract_topics_from_context(context)
        
        assert "ancient" in result
        assert "dragon" in result
        assert "mountain" in result
        assert "treasure" in result
        assert "hunters" in result
        assert "golden" in result
        assert "crown" in result
        # Short words should be filtered out
        assert "the" not in result
        assert "in" not in result

    def test_extract_topics_from_context_location(self, integration): pass
        """Test topic extraction from location context."""
        context = {
            "location": {
                "name": "Dragon's Lair",
                "type": "dungeon"
            }
        }
        
        result = integration._extract_topics_from_context(context)
        
        assert "dragon's lair" in result
        assert "dungeon" in result

    def test_extract_topics_from_context_target(self, integration): pass
        """Test topic extraction from target character."""
        context = {
            "target_id": "mysterious_wizard"
        }
        
        result = integration._extract_topics_from_context(context)
        
        assert "mysterious_wizard" in result

    def test_extract_topics_from_context_empty(self, integration): pass
        """Test topic extraction from empty context."""
        context = {}
        
        result = integration._extract_topics_from_context(context)
        
        assert result == set()

    def test_calculate_rumor_relevance_high(self, integration, sample_rumor): pass
        """Test rumor relevance calculation with high relevance."""
        topics = {"secret", "passage", "tavern"}
        context = {
            "location_id": "location_1",
            "target_id": "char_2"
        }
        
        result = integration._calculate_rumor_relevance(sample_rumor, topics, context)
        
        # Should have high relevance due to: pass
        # - Content topic matches
        # - Location match
        # - Character mention match
        assert result > 0.5

    def test_calculate_rumor_relevance_low(self, integration, sample_rumor): pass
        """Test rumor relevance calculation with low relevance."""
        topics = {"unrelated", "different"}
        context = {
            "location_id": "different_location",
            "target_id": "different_char"
        }
        
        result = integration._calculate_rumor_relevance(sample_rumor, topics, context)
        
        # Should have low relevance due to no matches
        assert result <= 0.5

    def test_calculate_rumor_relevance_location_match(self, integration, sample_rumor): pass
        """Test rumor relevance calculation with location match."""
        topics = set()
        context = {
            "location_id": "location_1"  # Matches rumor origin_location_id
        }
        
        result = integration._calculate_rumor_relevance(sample_rumor, topics, context)
        
        # Should get location bonus
        assert result >= 0.4  # Base 0.2 + location bonus 0.2

    def test_calculate_rumor_relevance_character_match(self, integration, sample_rumor): pass
        """Test rumor relevance calculation with character mention match."""
        topics = set()
        context = {
            "target_id": "char_2"  # Matches rumor mentions_character_id
        }
        
        result = integration._calculate_rumor_relevance(sample_rumor, topics, context)
        
        # Should get character mention bonus
        assert result >= 0.5  # Base 0.2 + character bonus 0.3

    def test_calculate_rumor_relevance_capped(self, integration): pass
        """Test rumor relevance calculation is capped at 1.0."""
        rumor = {
            "content": "secret passage tavern dragon treasure",
            "origin_location_id": "location_1",
            "mentions_character_id": "char_2",
            "created_at": "2023-01-01T00:00:00Z"
        }
        topics = {"secret", "passage", "tavern", "dragon", "treasure"}
        context = {
            "location_id": "location_1",
            "target_id": "char_2"
        }
        
        result = integration._calculate_rumor_relevance(rumor, topics, context)
        
        assert result <= 1.0

    def test_calculate_rumor_relevance_minimal_rumor(self, integration): pass
        """Test rumor relevance calculation with minimal rumor data."""
        rumor = {"content": ""}
        topics = set()
        context = {}
        
        result = integration._calculate_rumor_relevance(rumor, topics, context)
        
        assert result == 0.2  # Should get base relevance only 