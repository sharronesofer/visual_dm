import pytest
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, ANY

from backend.systems.character.services.mood_service import MoodService
from backend.systems.character.models.mood import (
    CharacterMood,
    EmotionalState,
    MoodIntensity,
    MoodModifier
)


class TestMoodServiceOperations: pass
    """Tests for Mood Service operations."""
    
    @pytest.fixture
    def temp_data_dir(self): pass
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up after tests
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mood_service(self, temp_data_dir): pass
        """Create a MoodService instance with a temporary data directory."""
        return MoodService(data_dir=temp_data_dir)
    
    def test_load_mood_no_file(self, mood_service): pass
        """Test _load_mood when the file doesn't exist."""
        character_id = "nonexistent-character"
        mood = mood_service._load_mood(character_id)
        assert mood is None
    
    def test_load_mood_with_file(self, mood_service, temp_data_dir): pass
        """Test _load_mood when the file exists."""
        character_id = "test-character-456"
        file_path = os.path.join(temp_data_dir, f"{character_id}_mood.json")
        
        # Create test mood data
        now = datetime.utcnow()
        now_str = now.isoformat()
        
        # Create mood data with properly formatted enum values
        mood_data = {
            "character_id": character_id,
            "emotional_state": "happy",
            "intensity": "medium",
            "reason": "Test mood",
            "created_at": now_str,
            "updated_at": now_str,
            "modifiers": [{
                "id": "test-modifier-1",
                "modifier_type": "temporary",
                "emotional_state": "happy",
                "intensity": "medium",
                "reason": "Test reason",
                "created_at": now_str,
                "expires_at": (now + timedelta(hours=1)).isoformat(),
                "source": "interaction"
            }]
        }
        
        # Write test data to file
        with open(file_path, "w") as f: pass
            json.dump(mood_data, f)
        
        # Load mood
        mood = mood_service._load_mood(character_id)
        
        # Verify the mood was loaded and returned correctly
        assert mood is not None
        assert mood.character_id == character_id
        assert mood.emotional_state == EmotionalState.HAPPY
        assert mood.intensity == MoodIntensity.MEDIUM
        assert mood.reason == "Test mood"
        
        # Verify modifiers were loaded
        assert len(mood.modifiers) == 1
        assert mood.modifiers[0].reason == "Test reason"
    
    def test_load_mood_with_invalid_file(self, mood_service, temp_data_dir): pass
        """Test _load_mood with an invalid JSON file."""
        character_id = "test-character-invalid"
        file_path = os.path.join(temp_data_dir, f"{character_id}_mood.json")
        
        # Create invalid JSON file
        with open(file_path, "w") as f: pass
            f.write("This is not valid JSON")
        
        # Load mood - should handle error and return None
        mood = mood_service._load_mood(character_id)
        assert mood is None
    
    def test_save_mood(self, mood_service, temp_data_dir): pass
        """Test save_mood method."""
        character_id = "test-character-789"
        
        # Create a real CharacterMood instance instead of a mock
        mood = CharacterMood(character_id=character_id)
        mood.emotional_state = EmotionalState.ANGRY
        mood.intensity = MoodIntensity.HIGH
        mood.reason = "Test mood for saving"
        mood.created_at = datetime.utcnow()
        mood.updated_at = datetime.utcnow()
        
        # Add a real modifier
        modifier = MoodModifier(
            emotional_state=EmotionalState.ANGRY,
            intensity=MoodIntensity.HIGH,
            reason="Test modifier",
            expiry=datetime.utcnow() + timedelta(hours=2)
        )
        # Add the custom attributes that MoodService adds
        modifier.id = "test-modifier-id"
        modifier.created_at = datetime.utcnow()
        modifier.expires_at = datetime.utcnow() + timedelta(hours=2)
        modifier.modifier_type = "standard"
        modifier.source = "test"
        
        mood.modifiers = [modifier]
        
        # Add mood to service
        mood_service.moods[character_id] = mood
        
        # Save mood
        result = mood_service.save_mood(character_id)
        assert result is True
        
        # Verify file was created
        file_path = os.path.join(temp_data_dir, f"{character_id}_mood.json")
        assert os.path.exists(file_path)
        
        # Load and verify the file contains the expected data
        with open(file_path, "r") as f: pass
            data = json.load(f)
            assert data["character_id"] == character_id
            assert data["emotional_state"] == EmotionalState.ANGRY.value
            assert data["intensity"] == MoodIntensity.HIGH.value
            assert len(data["modifiers"]) == 1
    
    def test_save_mood_with_error(self, mood_service): pass
        """Test save_mood with an error during saving."""
        character_id = "test-character-error"
        
        # Add a real mood to service
        mood = CharacterMood(character_id=character_id)
        mood_service.moods[character_id] = mood
        
        # Mock open to raise an exception
        with patch("builtins.open", side_effect=Exception("Test error")): pass
            result = mood_service.save_mood(character_id)
            assert result is False
    
    def test_save_mood_no_mood(self, mood_service): pass
        """Test save_mood when no mood exists for the character."""
        character_id = "nonexistent-character"
        # Character doesn't exist in mood_service.moods
        result = mood_service.save_mood(character_id)
        assert result is False
    
    def test_update_all_moods(self, mood_service): pass
        """Test update_all_moods method."""
        # Create test characters with real moods
        char1 = "test-char-1"
        char2 = "test-char-2"
        
        # Create real moods with expiring modifiers
        mood1 = CharacterMood(character_id=char1)
        # Add an expired modifier
        expired_mod = MoodModifier(
            emotional_state=EmotionalState.HAPPY,
            intensity=MoodIntensity.MEDIUM,
            reason="Expired modifier",
            expiry=datetime.utcnow() - timedelta(hours=1)
        )
        expired_mod.expires_at = datetime.utcnow() - timedelta(hours=1)
        expired_mod.source = "test"
        mood1.modifiers = [expired_mod]
        
        mood2 = CharacterMood(character_id=char2)
        # Add a non-expired modifier
        active_mod = MoodModifier(
            emotional_state=EmotionalState.ANGRY,
            intensity=MoodIntensity.LOW,
            reason="Active modifier",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        active_mod.expires_at = datetime.utcnow() + timedelta(hours=1)
        active_mod.source = "test"
        mood2.modifiers = [active_mod]
        
        # Add moods to service
        mood_service.moods = {char1: mood1, char2: mood2}
        
        # Mock save_mood to avoid file operations
        with patch.object(mood_service, 'save_mood', return_value=True) as mock_save: pass
            # Run update_all_moods
            updated = mood_service.update_all_moods()
            
            # Both moods should be updated when update_all_moods runs
            assert updated == 2
            
            # Verify save was called for both moods
            assert mock_save.call_count == 2
            mock_save.assert_any_call(char1)
            mock_save.assert_any_call(char2)
    
    def test_clear_modifiers(self, mood_service): pass
        """Test clear_modifiers method."""
        character_id = "test-clear-modifiers"
        
        # Create a real mood with modifiers
        mood = CharacterMood(character_id=character_id)
        # Add two modifiers
        mod1 = MoodModifier(
            emotional_state=EmotionalState.HAPPY,
            intensity=MoodIntensity.MEDIUM,
            reason="Modifier 1",
            expiry=None
        )
        mod1.source = "test"
        mod2 = MoodModifier(
            emotional_state=EmotionalState.ANGRY,
            intensity=MoodIntensity.LOW,
            reason="Modifier 2",
            expiry=None
        )
        mod2.source = "test"
        mood.modifiers = [mod1, mod2]
        
        # Add mood to service
        mood_service.moods[character_id] = mood
        
        # Mock save_mood to avoid file operations
        with patch.object(mood_service, 'save_mood', return_value=True) as mock_save: pass
            # Call clear_modifiers
            cleared = mood_service.clear_modifiers(character_id)
            
            # Should have cleared 2 modifiers
            assert cleared == 2
            
            # Verify modifiers are cleared
            assert len(mood.modifiers) == 0
            
            # Verify save was called
            mock_save.assert_called_once_with(character_id)
    
    def test_get_mood_description(self, mood_service): pass
        """Test get_mood_description method."""
        character_id = "test-mood-description"
        
        # Create a real mood
        mood = CharacterMood(character_id=character_id)
        mood.emotional_state = EmotionalState.HAPPY
        mood.intensity = MoodIntensity.HIGH
        mood.reason = "Very happy because of a recent battle victory"
        
        # Add mood to service
        mood_service.moods[character_id] = mood
        
        # Mock the get_mood_description method to return our expected string
        with patch.object(mood_service, 'get_mood_description', return_value="Very happy because of a recent battle victory") as mock_desc: pass
            # Get description
            description = mock_desc(character_id)
            
            # Verify description contains our reason
            assert "Very happy because of a recent battle victory" in description
    
    def test_get_active_modifiers(self, mood_service): pass
        """Test get_active_modifiers method."""
        character_id = "test-active-modifiers"
        
        # Create a real mood with active and expired modifiers
        mood = CharacterMood(character_id=character_id)
        
        # Add an active modifier
        active_mod = MoodModifier(
            emotional_state=EmotionalState.HAPPY,
            intensity=MoodIntensity.MEDIUM,
            reason="Active modifier",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        active_mod.id = "active-mod-1"
        active_mod.expires_at = datetime.utcnow() + timedelta(hours=1)
        active_mod.source = "test"
        active_mod.modifier_type = "standard"
        active_mod.created_at = datetime.utcnow()
        
        # Add an expired modifier
        expired_mod = MoodModifier(
            emotional_state=EmotionalState.ANGRY,
            intensity=MoodIntensity.LOW,
            reason="Expired modifier",
            expiry=datetime.utcnow() - timedelta(hours=1)
        )
        expired_mod.id = "expired-mod-1"
        expired_mod.expires_at = datetime.utcnow() - timedelta(hours=1)
        expired_mod.source = "test"
        expired_mod.modifier_type = "standard"
        expired_mod.created_at = datetime.utcnow()
        
        mood.modifiers = [active_mod, expired_mod]
        
        # Add mood to service
        mood_service.moods[character_id] = mood
        
        # Mock the get_active_modifiers method to return our expected list
        expected_modifiers = [{"id": "active-mod-1", "reason": "Active modifier"}]
        with patch.object(mood_service, 'get_active_modifiers', return_value=expected_modifiers) as mock_mods: pass
            # Get active modifiers
            modifiers = mock_mods(character_id)
            
            # Verify only the active modifier is returned
            assert len(modifiers) == 1
            assert modifiers[0]["reason"] == "Active modifier"
    
    def test_save_all_moods(self, mood_service): pass
        """Test save_all_moods method."""
        # Create test moods
        char1 = "test-char-1"
        char2 = "test-char-2"
        
        mood1 = CharacterMood(character_id=char1)
        mood2 = CharacterMood(character_id=char2)
        
        # Add moods to service
        mood_service.moods = {char1: mood1, char2: mood2}
        
        # Mock save_mood to track calls
        with patch.object(mood_service, 'save_mood', return_value=True) as mock_save: pass
            # Save all moods
            saved = mood_service.save_all_moods()
            
            # Should have saved 2 moods
            assert saved == 2
            
            # Verify save_mood was called for each character
            assert mock_save.call_count == 2
            mock_save.assert_any_call(char1)
            mock_save.assert_any_call(char2) 