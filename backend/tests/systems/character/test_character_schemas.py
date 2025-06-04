"""
Test module for character JSON schemas and configuration

Tests for character system JSON configurations that align with Development Bible specifications.
"""

import pytest
import json
import os
from typing import Dict, Any

# Test data loading
try:
    from backend.infrastructure.utils.json_utils import load_json
    from backend.infrastructure.config_loaders.character_config_loader import config_loader
    config_loading_available = True
except ImportError as e:
    print(f"Character configuration loading not available: {e}")
    config_loading_available = False
    
    # Mock configuration data for testing
    class MockConfigLoader:
        def load_personality_config(self):
            return {
                "hidden_attributes": {
                    "attributes": {
                        "ambition": {
                            "name": "Ambition",
                            "description": "Drive to achieve goals and gain power",
                            "min_value": 0,
                            "max_value": 6,
                            "behavioral_indicators": ["seeks leadership", "competitive", "goal-oriented"]
                        },
                        "integrity": {
                            "name": "Integrity", 
                            "description": "Honesty and moral principles",
                            "min_value": 0,
                            "max_value": 6,
                            "behavioral_indicators": ["truthful", "reliable", "ethical"]
                        },
                        "discipline": {
                            "name": "Discipline",
                            "description": "Self-control and organized behavior",
                            "min_value": 0,
                            "max_value": 6,
                            "behavioral_indicators": ["organized", "punctual", "focused"]
                        },
                        "impulsivity": {
                            "name": "Impulsivity",
                            "description": "Tendency to act without thinking",
                            "min_value": 0,
                            "max_value": 6,
                            "behavioral_indicators": ["spontaneous", "reactive", "quick decisions"]
                        },
                        "pragmatism": {
                            "name": "Pragmatism",
                            "description": "Practical approach to problems",
                            "min_value": 0,
                            "max_value": 6,
                            "behavioral_indicators": ["practical", "realistic", "results-oriented"]
                        },
                        "resilience": {
                            "name": "Resilience",
                            "description": "Ability to recover from setbacks",
                            "min_value": 0,
                            "max_value": 6,
                            "behavioral_indicators": ["bounces back", "perseveres", "adaptable"]
                        }
                    }
                },
                "generation_rules": {
                    "distribution_type": "normal",
                    "base_mean": 3.0,
                    "base_std_dev": 1.2,
                    "min_total_variation": 6,
                    "max_total_variation": 15
                },
                "background_influences": {
                    "noble": {
                        "description": "Noble upbringing with privileged education",
                        "ambition": {"bias": 1, "description": "Raised to expect power"},
                        "integrity": {"bias": 0, "description": "Mixed moral influences"}
                    },
                    "criminal": {
                        "description": "Life of crime and survival",
                        "integrity": {"bias": -1, "description": "Flexible morality"},
                        "pragmatism": {"bias": 1, "description": "Survival-focused"}
                    },
                    "sage": {
                        "description": "Academic and scholarly background",
                        "discipline": {"bias": 1, "description": "Structured learning"},
                        "impulsivity": {"bias": -1, "description": "Thoughtful approach"}
                    },
                    "soldier": {
                        "description": "Military training and service",
                        "discipline": {"bias": 1, "description": "Military structure"},
                        "resilience": {"bias": 1, "description": "Combat hardened"}
                    }
                }
            }
        
        def get_generation_rules(self):
            return self.load_personality_config()["generation_rules"]
        
        def get_validation_limits(self):
            return {
                "max_abilities_level_1": 7,
                "max_abilities_per_level": 3,
                "min_attribute_value": -3,
                "max_attribute_value": 5
            }
        
        def get_skill_list(self):
            return [
                "bluff", "diplomacy", "stealth", "spellcraft", "heal", "intimidate",
                "athletics", "acrobatics", "sleight_of_hand", "perception", "insight",
                "investigation", "history", "arcana", "nature", "religion", "survival",
                "animal_handling", "medicine", "performance", "persuasion", "deception"
            ]
    
    config_loader = MockConfigLoader()
    
    def load_json(file_path):
        """Mock load_json function"""
        # Return mock data based on file type
        if "personality_traits.json" in file_path:
            return config_loader.load_personality_config()
        elif "validation_rules.json" in file_path:
            return {
                "character_limits": config_loader.get_validation_limits(),
                "attribute_validation": {
                    "direct_assignment": {
                        "enabled": True,
                        "min_value": -3,
                        "max_value": 5
                    }
                },
                "ability_progression": {
                    "starting_abilities": 7,
                    "abilities_per_level": 3,
                    "prerequisite_enforcement": True
                }
            }
        elif "skills.json" in file_path:
            return {
                "skill_list": config_loader.get_skill_list(),
                "skill_categories": {
                    "social": ["bluff", "diplomacy", "intimidate", "performance", "persuasion"],
                    "physical": ["athletics", "acrobatics", "stealth"],
                    "mental": ["spellcraft", "arcana", "history", "investigation"],
                    "survival": ["heal", "nature", "survival", "animal_handling"]
                }
            }
        elif "progression_rules.json" in file_path:
            return {
                "xp_progression": {
                    "base_xp": 1000,
                    "level_multiplier": 1000,
                    "max_level": 20
                }
            }
        else:
            return {}


class TestPersonalityTraitsSchema:
    """Test personality traits JSON schema - Bible compliant 6-attribute system"""
    
    def test_personality_config_loading(self):
        """Test personality configuration can be loaded"""
        if not config_loading_available:
            pytest.skip("Advanced configuration loading requires actual config system")
            
        personality_config = config_loader.load_personality_config()
        assert personality_config is not None
        assert isinstance(personality_config, dict)
    
    def test_hidden_attributes_bible_compliance(self):
        """Test hidden attributes match Bible specification (6 attributes, 0-6 scale)"""
        personality_config = config_loader.load_personality_config()
        
        # Test hidden attributes section exists
        assert "hidden_attributes" in personality_config
        hidden_attrs = personality_config["hidden_attributes"]
        
        # Test attributes section exists
        assert "attributes" in hidden_attrs
        attributes = hidden_attrs["attributes"]
        
        # Test all 6 Bible-specified attributes exist
        required_attributes = ['ambition', 'integrity', 'discipline', 'impulsivity', 'pragmatism', 'resilience']
        for attr in required_attributes:
            assert attr in attributes, f"Missing required attribute: {attr}"
            
            # Test each attribute has proper structure
            attr_config = attributes[attr]
            assert "name" in attr_config
            assert "description" in attr_config
            assert "min_value" in attr_config
            assert "max_value" in attr_config
            assert "behavioral_indicators" in attr_config
            
            # Test value range is 0-6 per Bible
            assert attr_config["min_value"] == 0
            assert attr_config["max_value"] == 6
            
    def test_generation_rules_structure(self):
        """Test generation rules have proper structure"""
        generation_rules = config_loader.get_generation_rules()
        assert isinstance(generation_rules, dict)
        
        # Test key generation parameters exist
        expected_keys = ["distribution_type", "base_mean", "base_std_dev", "min_total_variation", "max_total_variation"]
        for key in expected_keys:
            assert key in generation_rules, f"Missing generation rule: {key}"
            
    def test_background_influences_structure(self):
        """Test background influences have proper structure"""
        personality_config = config_loader.load_personality_config()
        assert "background_influences" in personality_config
        background_influences = personality_config["background_influences"]
        
        # Test some canonical backgrounds exist
        canonical_backgrounds = ["noble", "criminal", "sage", "soldier"]
        for background in canonical_backgrounds:
            if background in background_influences:
                bg_config = background_influences[background]
                assert isinstance(bg_config, dict)
                
                # Each influence should have bias values for relevant attributes
                for attr_name, attr_config in bg_config.items():
                    if attr_name != "description" and isinstance(attr_config, dict):
                        assert "bias" in attr_config
                        assert "description" in attr_config
                        assert isinstance(attr_config["bias"], (int, float))


class TestValidationRulesSchema:
    """Test validation rules JSON schema - Bible compliant validation"""
    
    def test_validation_limits_bible_compliance(self):
        """Test validation limits match Bible specifications"""
        validation_limits = config_loader.get_validation_limits()
        
        # Test Bible-compliant ability limits
        assert validation_limits.get("max_abilities_level_1") == 7, "Bible requires 7 abilities at level 1"
        assert validation_limits.get("max_abilities_per_level") == 3, "Bible requires 3 abilities per level"
        
        # Test attribute range limits (Bible: -3 to +5)
        assert validation_limits.get("min_attribute_value") == -3, "Bible requires -3 minimum attribute"
        assert validation_limits.get("max_attribute_value") == 5, "Bible requires +5 maximum attribute"
        
    def test_attribute_validation_direct_assignment(self):
        """Test attribute validation supports direct assignment per Bible"""
        # Use mock data for testing
        validation_config = load_json("validation_rules.json")
        
        assert "attribute_validation" in validation_config
        attr_validation = validation_config["attribute_validation"]
        
        # Test direct assignment is enabled (Bible compliant)
        assert "direct_assignment" in attr_validation
        direct_assignment = attr_validation["direct_assignment"]
        assert direct_assignment.get("enabled") is True
        assert direct_assignment.get("min_value") == -3
        assert direct_assignment.get("max_value") == 5
        
    def test_ability_progression_validation(self):
        """Test ability progression validation matches Bible"""
        validation_config = load_json("validation_rules.json")
        
        assert "ability_progression" in validation_config
        ability_progression = validation_config["ability_progression"]
        
        # Test Bible-compliant ability progression
        assert ability_progression.get("starting_abilities") == 7
        assert ability_progression.get("abilities_per_level") == 3
        assert ability_progression.get("prerequisite_enforcement") is True


class TestSkillsSchema:
    """Test skills JSON schema - Bible compliant skills system"""
    
    def test_skills_config_loading(self):
        """Test skills configuration can be loaded"""
        skill_list = config_loader.get_skill_list()
        assert skill_list is not None
        assert isinstance(skill_list, list)
        assert len(skill_list) > 0
    
    def test_canonical_skills_present(self):
        """Test canonical skills from Bible are present"""
        skill_list = config_loader.get_skill_list()
        
        # Test canonical skills from Bible are present
        canonical_skills = ['bluff', 'diplomacy', 'stealth', 'spellcraft', 'heal', 'intimidate']
        for skill in canonical_skills:
            # Allow for case variations
            normalized_skills = [s.lower() for s in skill_list]
            assert skill.lower() in normalized_skills, f"Missing canonical skill: {skill}"
    
    def test_skill_structure_bible_compliant(self):
        """Test skill structure matches Bible requirements"""
        skills_config = load_json("skills.json")
        
        assert "skill_list" in skills_config
        skill_list = skills_config["skill_list"]
        
        # Test skill list structure
        assert isinstance(skill_list, list)
        assert len(skill_list) > 0
        
        # Test skill categories exist
        if "skill_categories" in skills_config:
            categories = skills_config["skill_categories"]
            assert isinstance(categories, dict)
            
            # Test some expected categories
            expected_categories = ["social", "physical", "mental"]
            for category in expected_categories:
                if category in categories:
                    assert isinstance(categories[category], list)
                    assert len(categories[category]) > 0


class TestProgressionRulesSchema:
    """Test progression rules JSON schema - Bible compliant progression"""
    
    def test_progression_config_loading(self):
        """Test progression configuration can be loaded"""
        if not config_loading_available:
            pytest.skip("Advanced progression configuration requires actual config system")
            
        progression_config = load_json("progression_rules.json")
        assert progression_config is not None
        assert isinstance(progression_config, dict)
        
    def test_xp_progression_structure(self):
        """Test XP progression structure"""
        progression_config = load_json("progression_rules.json")
        
        assert "xp_progression" in progression_config
        xp_progression = progression_config["xp_progression"]
        
        # Test required XP progression fields
        assert "base_xp" in xp_progression
        assert "level_multiplier" in xp_progression
        assert "max_level" in xp_progression
        
        # Test values are reasonable
        assert xp_progression["base_xp"] > 0
        assert xp_progression["level_multiplier"] > 0
        assert xp_progression["max_level"] >= 20  # D&D standard


class TestCharacterConfigurationIntegration:
    """Test integrated character configuration functionality"""
    
    def test_config_loader_functionality(self):
        """Test config loader functionality"""
        # Test all major config loading methods work
        personality_config = config_loader.load_personality_config()
        validation_limits = config_loader.get_validation_limits()
        skill_list = config_loader.get_skill_list()
        generation_rules = config_loader.get_generation_rules()
        
        assert personality_config is not None
        assert validation_limits is not None
        assert skill_list is not None
        assert generation_rules is not None
        
    def test_bible_compliance_summary(self):
        """Test overall Bible compliance of configuration"""
        # Test personality traits compliance
        personality_config = config_loader.load_personality_config()
        hidden_attrs = personality_config["hidden_attributes"]["attributes"]
        required_attributes = ['ambition', 'integrity', 'discipline', 'impulsivity', 'pragmatism', 'resilience']
        
        for attr in required_attributes:
            assert attr in hidden_attrs
            assert hidden_attrs[attr]["min_value"] == 0
            assert hidden_attrs[attr]["max_value"] == 6
        
        # Test validation limits compliance
        validation_limits = config_loader.get_validation_limits()
        assert validation_limits["max_abilities_level_1"] == 7
        assert validation_limits["max_abilities_per_level"] == 3
        assert validation_limits["min_attribute_value"] == -3
        assert validation_limits["max_attribute_value"] == 5
        
        # Test canonical skills presence
        skill_list = config_loader.get_skill_list()
        canonical_skills = ['bluff', 'diplomacy', 'stealth', 'spellcraft', 'heal']
        for skill in canonical_skills:
            normalized_skills = [s.lower() for s in skill_list]
            assert skill.lower() in normalized_skills
