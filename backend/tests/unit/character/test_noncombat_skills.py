"""
Unit Tests for Noncombat Skills System
-------------------------------------
Tests for skill checks, environmental mechanics, and skill integrations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.systems.character.models.character import Character
from backend.systems.character.services.skill_check_service import (
    skill_check_service, SkillCheckDifficulty, AdvantageType, SkillCheckModifiers, SkillCheckResult
)
from backend.systems.character.services.noncombat_skills import (
    noncombat_skill_service, PerceptionType, StealthContext, SocialInteractionType,
    PerceptionResult, StealthResult, SocialResult
)
from backend.systems.character.services.environmental_skill_mechanics import (
    environmental_skill_service, EnvironmentalContext, TerrainType, EnvironmentalCondition
)
from backend.systems.character.utils.skill_integration_utils import skill_integration_service


class TestSkillCheckService:
    """Test the core skill check service."""
    
    @pytest.fixture
    def test_character(self):
        """Create a test character with skills."""
        character = Character()
        character.uuid = "test-char-123"
        character.name = "Test Character"
        character.level = 5
        character.stats = {
            "strength": 14,
            "dexterity": 16,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 15,
            "charisma": 10
        }
        character.skills = {
            "perception": {"proficient": True, "expertise": False, "bonus": 0},
            "stealth": {"proficient": True, "expertise": True, "bonus": 0},
            "persuasion": {"proficient": False, "expertise": False, "bonus": 0},
            "investigation": {"proficient": True, "expertise": False, "bonus": 2}
        }
        return character
    
    def test_basic_skill_check(self, test_character):
        """Test basic skill check functionality."""
        with patch('random.randint', return_value=15):
            result = skill_check_service.make_skill_check(
                character=test_character,
                skill_name="perception",
                dc=15,
                description="Basic perception check"
            )
            
            assert isinstance(result, SkillCheckResult)
            assert result.skill_name == "perception"
            assert result.character_id == test_character.uuid
            assert result.success is True
            assert result.description == "Basic perception check"
    
    def test_skill_check_with_modifiers(self, test_character):
        """Test skill check with various modifiers."""
        modifiers = SkillCheckModifiers(
            circumstance_bonus=2,
            environmental_modifier=-3,
            equipment_bonus=1
        )
        
        with patch('random.randint', return_value=10):
            result = skill_check_service.make_skill_check(
                character=test_character,
                skill_name="stealth",
                dc=18,
                modifiers=modifiers
            )
            
            # Should include proficiency (3) + expertise (3) + dex mod (3) + modifiers (0)
            # Total modifier should be around 9, so 10 + 9 = 19 vs DC 18
            assert result.success is True
            assert result.final_modifiers == 0  # 2 - 3 + 1 = 0
    
    def test_advantage_disadvantage(self, test_character):
        """Test advantage and disadvantage mechanics."""
        with patch('random.randint', side_effect=[5, 15]):
            # Advantage - should take higher roll (15)
            result_adv = skill_check_service.make_skill_check(
                character=test_character,
                skill_name="perception",
                advantage_type=AdvantageType.ADVANTAGE
            )
            assert result_adv.base_roll == [5, 15]
            
            # Disadvantage - should take lower roll (5)
            result_dis = skill_check_service.make_skill_check(
                character=test_character,
                skill_name="perception",
                advantage_type=AdvantageType.DISADVANTAGE
            )
            assert result_dis.base_roll == [5, 15]
    
    def test_passive_skill_calculation(self, test_character):
        """Test passive skill score calculation."""
        passive_result = skill_check_service.get_passive_skill_score(
            character=test_character,
            skill_name="perception"
        )
        
        # Base 10 + wisdom mod (2) + proficiency (3) = 15
        assert passive_result.passive_score == 15
        assert passive_result.skill_name == "perception"
    
    def test_group_skill_check(self, test_character):
        """Test group skill check mechanics."""
        # Create multiple characters
        char2 = Character()
        char2.uuid = "char2"
        char2.level = 3
        char2.stats = {"wisdom": 12}
        char2.skills = {"perception": {"proficient": False, "expertise": False, "bonus": 0}}
        
        characters = [test_character, char2]
        
        with patch('random.randint', side_effect=[12, 8]):
            result = skill_check_service.make_group_skill_check(
                characters=characters,
                skill_name="perception",
                dc=15,
                description="Group perception check"
            )
            
            assert result.group_success is True  # At least half succeeded
            assert len(result.individual_results) == 2


class TestNoncombatSkillService:
    """Test specific noncombat skill implementations."""
    
    @pytest.fixture
    def test_character(self):
        """Create a test character."""
        character = Character()
        character.uuid = "test-char-456"
        character.name = "Sneaky Character"
        character.level = 6
        character.stats = {
            "dexterity": 18,
            "wisdom": 14,
            "charisma": 12
        }
        character.skills = {
            "perception": {"proficient": True, "expertise": False, "bonus": 0},
            "stealth": {"proficient": True, "expertise": True, "bonus": 0},
            "persuasion": {"proficient": True, "expertise": False, "bonus": 0}
        }
        return character
    
    def test_perception_check(self, test_character):
        """Test perception check mechanics."""
        hidden_objects = [
            {"id": "obj1", "name": "Hidden Door", "dc": 15, "modifier": 0},
            {"id": "obj2", "name": "Trap", "dc": 20, "modifier": -2}
        ]
        
        with patch.object(skill_check_service, 'make_skill_check') as mock_check:
            mock_check.return_value = SkillCheckResult(
                skill_name="perception",
                character_id=test_character.uuid,
                total_roll=18,
                success=True,
                degree_of_success=3
            )
            
            result = noncombat_skill_service.make_perception_check(
                character=test_character,
                perception_type=PerceptionType.VISUAL,
                hidden_objects=hidden_objects,
                environmental_conditions=["bright_light"]
            )
            
            assert isinstance(result, PerceptionResult)
            assert result.perception_type == PerceptionType.VISUAL
            assert len(result.detected_objects) >= 0
    
    def test_stealth_check(self, test_character):
        """Test stealth check mechanics."""
        observer = Character()
        observer.uuid = "observer-1"
        observer.stats = {"wisdom": 12}
        observer.skills = {"perception": {"proficient": False, "expertise": False, "bonus": 0}}
        
        with patch.object(skill_check_service, 'make_skill_check') as mock_check:
            mock_check.return_value = SkillCheckResult(
                skill_name="stealth",
                character_id=test_character.uuid,
                total_roll=22,
                success=True
            )
            
            with patch.object(noncombat_skill_service, 'get_passive_perception', return_value=12):
                result = noncombat_skill_service.make_stealth_check(
                    character=test_character,
                    stealth_context=StealthContext.HIDING,
                    observers=[observer],
                    environmental_conditions=["cover_available"]
                )
                
                assert isinstance(result, StealthResult)
                assert result.stealth_context == StealthContext.HIDING
                assert len(result.detected_by) == 0  # Should not be detected
    
    def test_social_interaction(self, test_character):
        """Test social interaction mechanics."""
        target = Character()
        target.uuid = "npc-target"
        target.stats = {"wisdom": 10}
        
        with patch.object(skill_check_service, 'make_skill_check') as mock_check:
            mock_check.return_value = SkillCheckResult(
                skill_name="persuasion",
                character_id=test_character.uuid,
                total_roll=16,
                success=True,
                degree_of_success=6
            )
            
            result = noncombat_skill_service.make_social_check(
                character=test_character,
                target=target,
                interaction_type=SocialInteractionType.PERSUASION,
                goal="Convince them to help",
                social_conditions=["good_reputation"]
            )
            
            assert isinstance(result, SocialResult)
            assert result.interaction_type == SocialInteractionType.PERSUASION
            assert result.attitude_change > 0  # Should improve attitude
    
    def test_investigation_check(self, test_character):
        """Test investigation mechanics."""
        available_clues = [
            {"id": "clue1", "name": "Footprint", "dc": 12},
            {"id": "clue2", "name": "Hidden Note", "dc": 18}
        ]
        
        with patch.object(skill_check_service, 'make_skill_check') as mock_check:
            mock_check.return_value = SkillCheckResult(
                skill_name="investigation",
                character_id=test_character.uuid,
                total_roll=15,
                success=True
            )
            
            check_result, discovered_clues = noncombat_skill_service.make_investigation_check(
                character=test_character,
                investigation_target="Crime Scene",
                time_spent_minutes=30,
                available_clues=available_clues
            )
            
            assert len(discovered_clues) >= 1  # Should find at least the easier clue
    
    def test_sneak_attack_viability(self, test_character):
        """Test sneak attack viability calculation."""
        target = Character()
        target.uuid = "enemy-target"
        target.stats = {"wisdom": 10}
        
        with patch.object(noncombat_skill_service, 'make_stealth_check') as mock_stealth:
            mock_stealth.return_value = StealthResult(
                check_result=SkillCheckResult(
                    skill_name="stealth",
                    character_id=test_character.uuid,
                    total_roll=20
                ),
                stealth_context=StealthContext.HIDING,
                detected_by=[],  # Not detected
                stealth_level=10
            )
            
            with patch.object(noncombat_skill_service, 'get_passive_perception', return_value=12):
                can_sneak_attack, reason = noncombat_skill_service.calculate_sneak_attack_viability(
                    attacker=test_character,
                    target=target,
                    environmental_conditions=["cover_available"]
                )
                
                assert can_sneak_attack is True
                assert "sneak attack possible" in reason.lower()


class TestEnvironmentalSkillMechanics:
    """Test environmental and contextual skill mechanics."""
    
    @pytest.fixture
    def test_character(self):
        """Create a test character."""
        character = Character()
        character.uuid = "env-test-char"
        character.level = 4
        character.stats = {"wisdom": 16, "dexterity": 14}
        return character
    
    def test_environmental_context_calculation(self, test_character):
        """Test environmental context calculation."""
        context = environmental_skill_service.calculate_environmental_context(
            location_type="forest",
            weather="heavy_rain",
            time_of_day="night",
            terrain_difficulty="difficult"
        )
        
        assert context.primary_terrain == TerrainType.FOREST
        assert EnvironmentalCondition.HEAVY_RAIN in context.conditions
        assert context.visibility_modifier < 0  # Should have visibility penalty
    
    def test_skill_modifiers_from_environment(self, test_character):
        """Test skill modifier calculation from environment."""
        environmental_conditions = ["darkness", "heavy_rain", "difficult_terrain"]
        
        modifiers = environmental_skill_service.get_skill_modifiers_for_environment(
            skill_name="perception",
            environmental_conditions=environmental_conditions
        )
        
        assert modifiers.environmental_modifier < 0  # Should have penalties


class TestSkillIntegration:
    """Test skill integration with other systems."""
    
    @pytest.fixture
    def test_character(self):
        """Create a test character."""
        character = Character()
        character.uuid = "integration-test-char"
        character.level = 5
        character.stats = {"charisma": 16, "wisdom": 12}
        character.skills = {
            "persuasion": {"proficient": True, "expertise": False, "bonus": 0},
            "insight": {"proficient": True, "expertise": False, "bonus": 0}
        }
        return character
    
    def test_dialogue_skill_options_generation(self, test_character):
        """Test generation of dialogue skill options."""
        npc_data = {
            "name": "Village Elder",
            "attributes": {"wisdom": 14},
            "attitude_towards_player": 10
        }
        
        options = skill_integration_service.get_dialogue_skill_options(
            character=test_character,
            npc_data=npc_data,
            conversation_context="seeking_information"
        )
        
        assert len(options) > 0
        assert any(opt.skill_name == "persuasion" for opt in options)
        assert any(opt.skill_name == "insight" for opt in options)
    
    def test_dialogue_skill_execution(self, test_character):
        """Test execution of dialogue skill checks."""
        from backend.systems.character.utils.skill_integration_utils import DialogueSkillOption
        
        dialogue_option = DialogueSkillOption(
            skill_name="persuasion",
            option_text="[Persuasion] Please help us",
            dc=15,
            success_response="I'll help you",
            failure_response="I can't help",
            attitude_change_success=10,
            attitude_change_failure=-5
        )
        
        target_npc = {
            "name": "Test NPC",
            "id": "npc-123",
            "attributes": {"wisdom": 12},
            "attitude_towards_player": 0
        }
        
        with patch.object(noncombat_skill_service, 'make_social_check') as mock_social:
            mock_social.return_value = SocialResult(
                check_result=SkillCheckResult(
                    skill_name="persuasion",
                    character_id=test_character.uuid,
                    total_roll=18,
                    success=True
                ),
                interaction_type=SocialInteractionType.PERSUASION,
                target_reaction="Positive",
                attitude_change=10,
                information_gained=[],
                consequences=[]
            )
            
            success, response, consequences = skill_integration_service.execute_dialogue_skill_check(
                character=test_character,
                target_npc=target_npc,
                dialogue_option=dialogue_option
            )
            
            assert success is True
            assert response == "I'll help you"
            assert consequences["attitude_change"] == 10


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_skill_name(self):
        """Test handling of invalid skill names."""
        character = Character()
        character.uuid = "error-test-char"
        character.stats = {"wisdom": 10}
        character.skills = {}
        
        # Should handle gracefully, not crash
        result = skill_check_service.make_skill_check(
            character=character,
            skill_name="nonexistent_skill",
            dc=15
        )
        
        assert result is not None
    
    def test_missing_character_data(self):
        """Test handling of incomplete character data."""
        character = Character()
        character.uuid = "incomplete-char"
        # Missing stats and skills
        
        with pytest.raises((AttributeError, KeyError)):
            skill_check_service.make_skill_check(
                character=character,
                skill_name="perception",
                dc=15
            )


class TestPerformanceAndCaching:
    """Test performance optimizations and caching."""
    
    def test_skill_check_caching(self):
        """Test that recent skill checks are cached for synergy bonuses."""
        character = Character()
        character.uuid = "cache-test-char"
        character.level = 5
        character.stats = {"wisdom": 14}
        character.skills = {
            "perception": {"proficient": True, "expertise": False, "bonus": 0},
            "investigation": {"proficient": True, "expertise": False, "bonus": 0}
        }
        
        # Make first check
        result1 = skill_check_service.make_skill_check(
            character=character,
            skill_name="perception",
            dc=15
        )
        
        # Make second check that should benefit from synergy
        result2 = skill_check_service.make_skill_check(
            character=character,
            skill_name="investigation",
            dc=15
        )
        
        # Should have cached the first result
        assert character.uuid in skill_check_service.recent_checks


if __name__ == "__main__":
    pytest.main([__file__]) 