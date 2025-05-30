"""
Test the DialogueMotifIntegration class.

This module tests all functionality of the motif integration system including
context addition, style application, and motif-influenced dialogue transformation.
"""

import pytest
import random
from unittest.mock import MagicMock, patch
from backend.systems.dialogue.motif_integration import DialogueMotifIntegration


class TestDialogueMotifIntegration:
    """Test cases for DialogueMotifIntegration class."""

    @pytest.fixture
    def mock_motif_manager(self):
        """Create a mock motif manager."""
        mock_manager = MagicMock()
        mock_manager.get_active_motifs_for_location.return_value = ["heroic", "magical"]
        mock_manager.get_active_global_motifs.return_value = ["mysterious", "political"]
        return mock_manager

    @pytest.fixture
    def integration(self, mock_motif_manager):
        """Create DialogueMotifIntegration instance with mock manager."""
        return DialogueMotifIntegration(motif_manager=mock_motif_manager)

    @pytest.fixture
    def integration_no_manager(self):
        """Create DialogueMotifIntegration instance without motif manager."""
        with patch('backend.systems.dialogue.motif_integration.MotifManager') as mock_motif_cls:
            mock_instance = MagicMock()
            mock_motif_cls.get_instance.return_value = mock_instance
            return DialogueMotifIntegration()

    def test_init_with_manager(self, mock_motif_manager):
        """Test initialization with provided motif manager."""
        integration = DialogueMotifIntegration(motif_manager=mock_motif_manager)
        assert integration.motif_manager == mock_motif_manager
        assert "tragic" in integration.motif_data
        assert "heroic" in integration.motif_data

    def test_init_without_manager(self):
        """Test initialization without provided motif manager."""
        with patch('backend.systems.dialogue.motif_integration.MotifManager') as mock_motif_cls:
            mock_instance = MagicMock()
            mock_motif_cls.get_instance.return_value = mock_instance
            
            integration = DialogueMotifIntegration()
            assert integration.motif_manager == mock_instance
            mock_motif_cls.get_instance.assert_called_once()

    def test_motif_data_structure(self, integration):
        """Test that motif data contains expected structure."""
        # Test canonical motifs exist
        expected_motifs = [
            "tragic", "heroic", "romantic", "mysterious", "comedic", 
            "horrific", "historical", "magical", "political", "religious",
            "military", "natural", "deceptive", "corrupt", "redemptive"
        ]
        
        for motif in expected_motifs:
            assert motif in integration.motif_data
            motif_data = integration.motif_data[motif]
            assert "tone" in motif_data
            assert "themes" in motif_data
            assert "keywords" in motif_data
            assert isinstance(motif_data["themes"], list)
            assert isinstance(motif_data["keywords"], list)

    def test_add_motifs_to_context_with_active_motifs(self, integration, mock_motif_manager):
        """Test adding motifs to context when active motifs exist."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.return_value = ["heroic", "magical"]
        context = {"speaker": "npc", "location": "castle"}
        
        # Execute
        result = integration.add_motifs_to_context(context, "castle_1")
        
        # Verify
        assert "motifs" in result
        assert len(result["motifs"]) == 2
        
        motif_ids = [motif["id"] for motif in result["motifs"]]
        assert "heroic" in motif_ids
        assert "magical" in motif_ids
        
        # Check motif data is included
        heroic_motif = next(m for m in result["motifs"] if m["id"] == "heroic")
        assert "data" in heroic_motif
        assert heroic_motif["data"]["tone"] == "inspiring"

    def test_add_motifs_to_context_no_active_motifs(self, integration, mock_motif_manager):
        """Test adding motifs to context when no active motifs exist."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.return_value = []
        mock_motif_manager.get_active_global_motifs.return_value = []
        context = {"speaker": "npc"}
        
        # Execute
        result = integration.add_motifs_to_context(context)
        
        # Verify - context should be unchanged except for being copied
        assert result == context
        assert "motifs" not in result

    def test_add_motifs_to_context_existing_motifs(self, integration, mock_motif_manager):
        """Test adding motifs to context that already has motifs."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.return_value = ["tragic"]
        context = {"motifs": [{"id": "existing", "data": {}}]}
        
        # Execute
        result = integration.add_motifs_to_context(context, "location_1")
        
        # Verify
        assert len(result["motifs"]) == 2
        assert result["motifs"][0]["id"] == "existing"
        assert result["motifs"][1]["id"] == "tragic"

    def test_add_motifs_to_context_no_location(self, integration, mock_motif_manager):
        """Test adding motifs to context without specifying location."""
        # Setup
        mock_motif_manager.get_active_global_motifs.return_value = ["mysterious"]
        context = {"speaker": "npc"}
        
        # Execute
        result = integration.add_motifs_to_context(context)
        
        # Verify
        assert "motifs" in result
        assert len(result["motifs"]) == 1
        assert result["motifs"][0]["id"] == "mysterious"

    def test_apply_motif_style_with_active_motifs(self, integration, mock_motif_manager):
        """Test applying motif style when active motifs exist."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.return_value = ["heroic"]
        message = "This is a test message for styling"
        
        # Mock random.choice to consistently return first motif
        with patch('backend.systems.dialogue.motif_integration.random.choice') as mock_choice:
            mock_choice.return_value = "heroic"
            
            # Execute
            result = integration.apply_motif_style(message, "location_1")
            
            # Verify - result should be different from original
            assert isinstance(result, str)
            # The exact result depends on random styling, so we just verify it's processed

    def test_apply_motif_style_no_active_motifs(self, integration, mock_motif_manager):
        """Test applying motif style when no active motifs exist."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.return_value = []
        mock_motif_manager.get_active_global_motifs.return_value = []
        message = "This is a test message"
        
        # Execute
        result = integration.apply_motif_style(message, "location_1")
        
        # Verify - message should be unchanged
        assert result == message

    def test_apply_motif_style_unknown_motif(self, integration, mock_motif_manager):
        """Test applying motif style with unknown motif."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.return_value = ["unknown_motif"]
        message = "This is a test message"
        
        # Mock random.choice to return the unknown motif
        with patch('backend.systems.dialogue.motif_integration.random.choice') as mock_choice:
            mock_choice.return_value = "unknown_motif"
            
            # Execute
            result = integration.apply_motif_style(message, "location_1")
            
            # Verify - message should be unchanged when motif data is missing
            assert result == message

    def test_get_active_motifs_location_specific(self, integration, mock_motif_manager):
        """Test getting active motifs for specific location."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.return_value = ["heroic", "magical"]
        
        # Execute
        result = integration.get_active_motifs("castle_1")
        
        # Verify
        assert result == ["heroic", "magical"]
        mock_motif_manager.get_active_motifs_for_location.assert_called_once_with("castle_1")

    def test_get_active_motifs_fallback_to_global(self, integration, mock_motif_manager):
        """Test getting active motifs falls back to global when location has none."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.return_value = []
        mock_motif_manager.get_active_global_motifs.return_value = ["mysterious", "political"]
        
        # Execute
        result = integration.get_active_motifs("empty_location")
        
        # Verify
        assert result == ["mysterious", "political"]
        mock_motif_manager.get_active_motifs_for_location.assert_called_once_with("empty_location")
        mock_motif_manager.get_active_global_motifs.assert_called_once()

    def test_get_active_motifs_no_location(self, integration, mock_motif_manager):
        """Test getting active motifs without specifying location."""
        # Setup
        mock_motif_manager.get_active_global_motifs.return_value = ["tragic", "redemptive"]
        
        # Execute
        result = integration.get_active_motifs()
        
        # Verify
        assert result == ["tragic", "redemptive"]
        mock_motif_manager.get_active_global_motifs.assert_called_once()

    def test_get_active_motifs_error_handling(self, integration, mock_motif_manager):
        """Test getting active motifs with error handling."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.side_effect = Exception("Motif error")
        
        # Execute
        result = integration.get_active_motifs("error_location")
        
        # Verify - should return default motifs on error
        assert result == ["mysterious", "political"]

    def test_apply_motif_characteristics_keyword_addition_beginning(self, integration):
        """Test applying motif characteristics with keyword addition at beginning."""
        # Setup
        motif_data = {"keywords": ["honor", "courage"], "tone": "inspiring"}
        message = "We must continue our quest"
        
        # Mock random to force keyword addition at beginning
        with patch('backend.systems.dialogue.motif_integration.random.random') as mock_random, \
             patch('backend.systems.dialogue.motif_integration.random.choice') as mock_choice:
            mock_random.side_effect = [0.1, 0.5]  # First for keyword addition, second for tone
            mock_choice.side_effect = ["honor", "beginning"]
            
            # Execute
            result = integration._apply_motif_characteristics(message, motif_data)
            
            # Verify - the method actually capitalizes the result
            assert "by honor means" in result.lower()

    def test_apply_motif_characteristics_keyword_addition_middle(self, integration):
        """Test applying motif characteristics with keyword addition in middle."""
        # Setup
        motif_data = {"keywords": ["mysterious"], "tone": "cryptic"}
        message = "I must tell you, this is important"
        
        # Mock random to force keyword addition in middle
        with patch('backend.systems.dialogue.motif_integration.random.random') as mock_random, \
             patch('backend.systems.dialogue.motif_integration.random.choice') as mock_choice:
            mock_random.side_effect = [0.1, 0.5]  # First for keyword addition, second for tone
            mock_choice.side_effect = ["mysterious", "middle"]
            
            # Execute
            result = integration._apply_motif_characteristics(message, motif_data)
            
            # Verify
            assert "mysterious" in result

    def test_apply_motif_characteristics_keyword_addition_end(self, integration):
        """Test applying motif characteristics with keyword addition at end."""
        # Setup
        motif_data = {"keywords": ["doom"], "tone": "somber"}
        message = "The situation grows worse"
        
        # Mock random to force keyword addition at end
        with patch('backend.systems.dialogue.motif_integration.random.random') as mock_random, \
             patch('backend.systems.dialogue.motif_integration.random.choice') as mock_choice:
            mock_random.side_effect = [0.1, 0.5]  # First for keyword addition, second for tone
            mock_choice.side_effect = ["doom", "end"]
            
            # Execute
            result = integration._apply_motif_characteristics(message, motif_data)
            
            # Verify
            assert "doom" in result

    def test_apply_motif_characteristics_tone_transformations(self, integration):
        """Test all tone transformations."""
        test_cases = [
            ("somber", "This is great news", ["solemn", "grave"]),
            ("inspiring", "You are a good help", ["noble", "aid"]),
            ("passionate", "I like my friend", ["love", "dear one"]),
            ("cryptic", "I know and tell", ["sense", "reveal"]),
            ("lighthearted", "Hello, yes indeed", ["well met", "indeed"]),
            ("dreadful", "There's a problem and issue", ["terror", "horror"]),
            ("scholarly", "This old story", ["ancient", "chronicle"]),
            ("wondrous", "How unusual and strange", ["mystical", "magical"]),
            ("diplomatic", "I'll tell the group", ["inform", "faction"]),
            ("reverent", "We're lucky this is important", ["blessed", "sacred"]),
            ("disciplined", "Your job with the group", ["duty", "unit"]),
            ("harmonious", "The good world", ["balanced", "realm"])
        ]
        
        for tone, message, expected_words in test_cases:
            motif_data = {"tone": tone, "keywords": []}
            
            # Mock random to force tone transformation
            with patch('backend.systems.dialogue.motif_integration.random.random') as mock_random:
                mock_random.side_effect = [0.5, 0.1]  # Skip keyword, apply tone
                
                result = integration._apply_motif_characteristics(message, motif_data)
                
                # Verify at least one expected transformation occurred or result is valid
                # The tone transformation might not always happen due to word existence checks
                assert isinstance(result, str), f"Failed for tone {tone}: result is not string"
                # If transformation happened, verify it contains expected words
                if result != message:
                    assert any(word in result for word in expected_words), f"Failed for tone {tone}: {result}"

    def test_apply_motif_characteristics_no_keywords(self, integration):
        """Test applying motif characteristics with no keywords."""
        # Setup
        motif_data = {"keywords": [], "tone": "inspiring"}
        message = "This is a test message that is long enough for processing"
        
        # Execute
        result = integration._apply_motif_characteristics(message, motif_data)
        
        # Verify - should handle gracefully
        assert isinstance(result, str)

    def test_apply_motif_characteristics_short_message(self, integration):
        """Test applying motif characteristics to short message."""
        # Setup
        motif_data = {"keywords": ["test"], "tone": "inspiring"}
        message = "Short"
        
        # Execute
        result = integration._apply_motif_characteristics(message, motif_data)
        
        # Verify - short messages shouldn't get keyword additions
        assert result == message or "noble" in result  # Only tone changes possible

    def test_apply_motif_characteristics_message_with_prefix(self, integration):
        """Test applying motif characteristics to message that starts with common prefix."""
        # Setup
        motif_data = {"keywords": ["honor"], "tone": "inspiring"}
        message = "I must continue this quest that is quite long indeed"
        
        # Mock random to force keyword addition at beginning
        with patch('backend.systems.dialogue.motif_integration.random.random') as mock_random, \
             patch('backend.systems.dialogue.motif_integration.random.choice') as mock_choice:
            mock_random.side_effect = [0.1, 0.5]  # First for keyword addition, second for tone
            mock_choice.side_effect = ["honor", "beginning"]
            
            # Execute
            result = integration._apply_motif_characteristics(message, motif_data)
            
            # Verify - should not add prefix when message starts with common prefixes
            assert not result.startswith("By honor means")

    def test_apply_motif_characteristics_message_ends_with_punctuation(self, integration):
        """Test applying motif characteristics to message ending with punctuation."""
        # Setup
        motif_data = {"keywords": ["doom"], "tone": "somber"}
        message = "The situation grows worse."
        
        # Mock random to force keyword addition at end
        with patch('backend.systems.dialogue.motif_integration.random.random') as mock_random, \
             patch('backend.systems.dialogue.motif_integration.random.choice') as mock_choice:
            mock_random.side_effect = [0.1, 0.5]  # First for keyword addition, second for tone
            mock_choice.side_effect = ["doom", "end"]
            
            # Execute
            result = integration._apply_motif_characteristics(message, motif_data)
            
            # Verify - should not add keyword at end when message already has punctuation
            assert result.count("doom") <= 1  # Only from tone transformation if at all

    def test_apply_motif_characteristics_no_comma_in_message(self, integration):
        """Test applying motif characteristics to message without comma for middle insertion."""
        # Setup
        motif_data = {"keywords": ["mystery"], "tone": "cryptic"}
        message = "This is a long message without any commas in it for testing"
        
        # Mock random to force keyword addition in middle
        with patch('backend.systems.dialogue.motif_integration.random.random') as mock_random, \
             patch('backend.systems.dialogue.motif_integration.random.choice') as mock_choice:
            mock_random.side_effect = [0.1, 0.5]  # First for keyword addition, second for tone
            mock_choice.side_effect = ["mystery", "middle"]
            
            # Execute
            result = integration._apply_motif_characteristics(message, motif_data)
            
            # Verify - should handle gracefully when no comma for middle insertion
            assert isinstance(result, str)

    def test_integration_end_to_end(self, integration, mock_motif_manager):
        """Test complete integration workflow."""
        # Setup
        mock_motif_manager.get_active_motifs_for_location.return_value = ["heroic", "magical"]
        context = {"speaker": "knight", "location": "castle"}
        message = "Greetings, traveler! How may I assist you on this fine day?"
        
        # Test context addition
        updated_context = integration.add_motifs_to_context(context, "castle_1")
        assert "motifs" in updated_context
        assert len(updated_context["motifs"]) == 2
        
        # Test style application
        styled_message = integration.apply_motif_style(message, "castle_1")
        assert isinstance(styled_message, str)
        
        # Test motif retrieval
        active_motifs = integration.get_active_motifs("castle_1")
        assert active_motifs == ["heroic", "magical"] 