"""
Tests for backend.systems.memory.cognitive_frames

Comprehensive tests for cognitive frame functionality.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Set

# Import the module being tested
from backend.systems.memory.cognitive_frames import (
    CognitiveFrame,
    CognitiveFrameMetadata,
    detect_cognitive_frames,
    apply_cognitive_frame,
    get_memory_emotional_impact,
)


class TestCognitiveFrame:
    """Test class for CognitiveFrame enum"""
    
    def test_cognitive_frame_values(self):
        """Test that cognitive frame enum has expected values"""
        assert CognitiveFrame.VICTIM == "victim"
        assert CognitiveFrame.HERO == "hero"
        assert CognitiveFrame.OPTIMISTIC == "optimistic"
        assert CognitiveFrame.PESSIMISTIC == "pessimistic"

    def test_cognitive_frame_enum_properties(self):
        """Test that cognitive frames are proper enum instances"""
        assert isinstance(CognitiveFrame.VICTIM, CognitiveFrame)
        assert isinstance(CognitiveFrame.HERO, CognitiveFrame)
        assert isinstance(CognitiveFrame.OPTIMISTIC, CognitiveFrame)
        assert isinstance(CognitiveFrame.PESSIMISTIC, CognitiveFrame)


class TestCognitiveFrameMetadata:
    """Test class for CognitiveFrameMetadata"""
    
    def test_get_metadata_victim(self):
        """Test getting metadata for victim frame"""
        metadata = CognitiveFrameMetadata.get_metadata(CognitiveFrame.VICTIM)
        
        assert isinstance(metadata, dict)
        assert "display_name" in metadata
        assert "description" in metadata
        assert metadata["display_name"] == "Victim Frame"
        assert "wronged" in metadata["description"].lower()

    def test_get_metadata_hero(self):
        """Test getting metadata for hero frame"""
        metadata = CognitiveFrameMetadata.get_metadata(CognitiveFrame.HERO)
        
        assert metadata["display_name"] == "Hero Frame"
        assert "savior" in metadata["description"].lower()

    def test_get_metadata_optimistic(self):
        """Test getting metadata for optimistic frame"""
        metadata = CognitiveFrameMetadata.get_metadata(CognitiveFrame.OPTIMISTIC)
        
        assert metadata["display_name"] == "Optimistic Frame"
        assert "positive" in metadata["description"].lower()

    def test_get_metadata_pessimistic(self):
        """Test getting metadata for pessimistic frame"""
        metadata = CognitiveFrameMetadata.get_metadata(CognitiveFrame.PESSIMISTIC)
        
        assert metadata["display_name"] == "Pessimistic Frame"
        assert "negative" in metadata["description"].lower()

    def test_get_metadata_returns_copy(self):
        """Test that get_metadata returns a copy, not the original"""
        metadata1 = CognitiveFrameMetadata.get_metadata(CognitiveFrame.VICTIM)
        metadata2 = CognitiveFrameMetadata.get_metadata(CognitiveFrame.VICTIM)
        
        # Should be equal but not the same object
        assert metadata1 == metadata2
        assert metadata1 is not metadata2
        
        # Modifying one shouldn't affect the other
        metadata1["test"] = "value"
        assert "test" not in metadata2

    def test_get_metadata_unknown_frame(self):
        """Test getting metadata for an unknown frame"""
        # Create a mock frame that's not in the metadata
        class MockFrame:
            name = "UNKNOWN_FRAME"
            value = "unknown"
        
        mock_frame = MockFrame()
        metadata = CognitiveFrameMetadata.get_metadata(mock_frame)
        
        assert metadata["display_name"] == "Unknown Frame"
        assert metadata["description"] == "General cognitive frame"


class TestDetectCognitiveFrames:
    """Test class for detect_cognitive_frames function"""
    
    def test_detect_victim_frame(self):
        """Test detection of victim frame"""
        test_cases = [
            "I was wronged by the merchant",
            "They attacked me unfairly",
            "I'm a victim of their schemes",
            "I was hurt by their actions"
        ]
        
        for content in test_cases:
            frames = detect_cognitive_frames(content)
            assert CognitiveFrame.VICTIM in frames

    def test_detect_hero_frame(self):
        """Test detection of hero frame"""
        test_cases = [
            "I saved the village from bandits",
            "I protected the innocent",
            "I rescued the princess",
            "I helped them escape",
            "I was their hero"
        ]
        
        for content in test_cases:
            frames = detect_cognitive_frames(content)
            assert CognitiveFrame.HERO in frames

    def test_detect_optimistic_frame(self):
        """Test detection of optimistic frame"""
        test_cases = [
            "I'm hopeful about the future",
            "This is a great opportunity",
            "I see a bright future ahead",
            "This is very positive news",
            "There's a good chance this will work"
        ]
        
        for content in test_cases:
            frames = detect_cognitive_frames(content)
            assert CognitiveFrame.OPTIMISTIC in frames

    def test_detect_pessimistic_frame(self):
        """Test detection of pessimistic frame"""
        test_cases = [
            "I feel hopeless about this",
            "We're all doomed",
            "This is inevitable failure",
            "It's pointless to try",
            "This will never work"
        ]
        
        for content in test_cases:
            frames = detect_cognitive_frames(content)
            assert CognitiveFrame.PESSIMISTIC in frames

    def test_detect_multiple_frames(self):
        """Test detection of multiple frames in one memory"""
        content = "I saved the village but I was wronged by the mayor"
        frames = detect_cognitive_frames(content)
        
        assert CognitiveFrame.HERO in frames
        assert CognitiveFrame.VICTIM in frames
        assert len(frames) == 2

    def test_detect_no_frames(self):
        """Test detection with neutral content"""
        content = "I walked to the market and bought some bread"
        frames = detect_cognitive_frames(content)
        
        assert len(frames) == 0

    def test_detect_case_insensitive(self):
        """Test that detection is case insensitive"""
        content = "I WAS WRONGED BY THE MERCHANT"
        frames = detect_cognitive_frames(content)
        
        assert CognitiveFrame.VICTIM in frames

    def test_detect_returns_set(self):
        """Test that detect_cognitive_frames returns a set"""
        content = "I was wronged"
        frames = detect_cognitive_frames(content)
        
        assert isinstance(frames, set)


class TestApplyCognitiveFrame:
    """Test class for apply_cognitive_frame function"""
    
    @patch('builtins.__import__')
    def test_apply_cognitive_frame_success(self, mock_import):
        """Test successful application of cognitive frame"""
        # Mock OpenAI module and response
        mock_openai = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Reinterpreted memory content"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # Mock the import to return our mock openai
        def side_effect(name, *args, **kwargs):
            if name == 'openai':
                return mock_openai
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = side_effect
        
        original_content = "I met a merchant in the market"
        result = apply_cognitive_frame(original_content, CognitiveFrame.VICTIM)
        
        assert result == "Reinterpreted memory content"
        mock_openai.ChatCompletion.create.assert_called_once()

    @patch('builtins.__import__')
    def test_apply_cognitive_frame_with_different_frames(self, mock_import):
        """Test applying different cognitive frames"""
        mock_openai = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Frame-specific interpretation"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        def side_effect(name, *args, **kwargs):
            if name == 'openai':
                return mock_openai
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = side_effect
        
        original_content = "I had a conversation with the king"
        
        # Test each frame
        for frame in [CognitiveFrame.VICTIM, CognitiveFrame.HERO, 
                     CognitiveFrame.OPTIMISTIC, CognitiveFrame.PESSIMISTIC]:
            result = apply_cognitive_frame(original_content, frame)
            assert result == "Frame-specific interpretation"

    @patch('builtins.__import__')
    def test_apply_cognitive_frame_error_handling(self, mock_import):
        """Test error handling in apply_cognitive_frame"""
        # Mock OpenAI to raise an exception
        mock_openai = Mock()
        mock_openai.ChatCompletion.create.side_effect = Exception("API Error")
        
        def side_effect(name, *args, **kwargs):
            if name == 'openai':
                return mock_openai
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = side_effect
        
        original_content = "I met a merchant"
        result = apply_cognitive_frame(original_content, CognitiveFrame.VICTIM)
        
        # Should return original content on error
        assert result == original_content

    @patch('builtins.__import__')
    def test_apply_cognitive_frame_prompt_construction(self, mock_import):
        """Test that the prompt is constructed correctly"""
        mock_openai = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Reinterpreted content"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        def side_effect(name, *args, **kwargs):
            if name == 'openai':
                return mock_openai
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = side_effect
        
        original_content = "Test memory content"
        apply_cognitive_frame(original_content, CognitiveFrame.HERO)
        
        # Check that the call was made with correct parameters
        call_args = mock_openai.ChatCompletion.create.call_args
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["temperature"] == 0.7
        assert len(call_args[1]["messages"]) == 2
        
        # Check prompt contains the frame and original content
        user_message = call_args[1]["messages"][1]["content"]
        assert "hero" in user_message.lower()
        assert original_content in user_message


class TestGetMemoryEmotionalImpact:
    """Test class for get_memory_emotional_impact function"""
    
    def test_emotional_impact_joy(self):
        """Test detection of joy emotions"""
        test_cases = [
            ("I was so happy to see them", "joy", 0.8),
            ("It brought me great joy", "joy", 0.8),
            ("I was delighted by the news", "joy", 0.8),
            ("I felt pleased with the result", "joy", 0.8),
            ("I was excited about the opportunity", "joy", 0.8),
            ("It was a good day", "joy", 0.5),
            ("That was nice to hear", "joy", 0.5),
            ("I was satisfied with the outcome", "joy", 0.5)
        ]
        
        for content, emotion, expected_intensity in test_cases:
            emotions = get_memory_emotional_impact(content)
            assert emotions[emotion] == expected_intensity

    def test_emotional_impact_fear(self):
        """Test detection of fear emotions"""
        test_cases = [
            ("I was terrified by the monster", "fear", 0.8),
            ("The horror of that night haunts me", "fear", 0.8),
            ("I felt panic rising in my chest", "fear", 0.8),
            ("I was afraid of the dark", "fear", 0.5),
            ("I felt scared and alone", "fear", 0.5),
            ("I was worried about the outcome", "fear", 0.5)
        ]
        
        for content, emotion, expected_intensity in test_cases:
            emotions = get_memory_emotional_impact(content)
            assert emotions[emotion] == expected_intensity

    def test_emotional_impact_anger(self):
        """Test detection of anger emotions"""
        test_cases = [
            ("I was furious at their betrayal", "anger", 0.8),
            ("I felt enraged by their actions", "anger", 0.8),
            ("I hate what they did to me", "anger", 0.8),
            ("I was angry about the decision", "anger", 0.5),
            ("I felt annoyed by their behavior", "anger", 0.5),
            ("I was irritated by the delay", "anger", 0.5)
        ]
        
        for content, emotion, expected_intensity in test_cases:
            emotions = get_memory_emotional_impact(content)
            assert emotions[emotion] == expected_intensity

    def test_emotional_impact_sadness(self):
        """Test detection of sadness emotions"""
        test_cases = [
            ("I felt grief at their passing", "sadness", 0.8),
            ("I was devastated by the news", "sadness", 0.8),
            ("I felt miserable and alone", "sadness", 0.8),
            ("I was sad to see them go", "sadness", 0.5),
            ("I felt unhappy about the situation", "sadness", 0.5),
            ("I was disappointed by the result", "sadness", 0.5)
        ]
        
        for content, emotion, expected_intensity in test_cases:
            emotions = get_memory_emotional_impact(content)
            assert emotions[emotion] == expected_intensity

    def test_emotional_impact_neutral(self):
        """Test neutral content with no strong emotions"""
        content = "I walked to the market and bought some bread"
        emotions = get_memory_emotional_impact(content)
        
        # All emotions should be 0.0 for neutral content
        for emotion, intensity in emotions.items():
            assert intensity == 0.0

    def test_emotional_impact_multiple_emotions(self):
        """Test content with multiple emotions"""
        content = "I was happy to see them but sad they were leaving"
        emotions = get_memory_emotional_impact(content)
        
        assert emotions["joy"] > 0.0
        assert emotions["sadness"] > 0.0

    def test_emotional_impact_case_insensitive(self):
        """Test that emotion detection is case insensitive"""
        content = "I WAS HAPPY TO SEE THEM"
        emotions = get_memory_emotional_impact(content)
        
        assert emotions["joy"] > 0.0

    def test_emotional_impact_returns_all_emotions(self):
        """Test that all emotion categories are returned"""
        content = "Neutral content"
        emotions = get_memory_emotional_impact(content)
        
        expected_emotions = {
            "joy", "fear", "anger", "sadness", 
            "surprise", "disgust", "trust", "anticipation"
        }
        
        assert set(emotions.keys()) == expected_emotions

    def test_emotional_impact_intensity_range(self):
        """Test that emotion intensities are in valid range"""
        content = "I was extremely happy and terrified at the same time"
        emotions = get_memory_emotional_impact(content)
        
        for emotion, intensity in emotions.items():
            assert 0.0 <= intensity <= 1.0
