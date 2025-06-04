"""
Test module for Magic System Business Logic (Canonical MP-Based System)

Tests for the canonical magic system as defined by the Development Bible:
- MP-based spellcasting (not spell slots)
- Domain-based efficiency and primary abilities
- Permanent spell learning (no daily preparation)
- Four domains: Nature, Arcane, Eldritch/Occult, Divine
"""

import pytest
from unittest.mock import Mock
from uuid import uuid4

# Import the canonical business logic
from backend.systems.magic.services import (
    MagicBusinessService,
    MagicCombatBusinessService,
    SpellEffect,
    SaveType,
    ConcentrationCheck,
    SpellCastingResult
)


class MockAbilities:
    """Mock abilities for canonical system testing"""
    def __init__(self, intelligence_modifier=3, constitution_modifier=2, wisdom_modifier=1, charisma_modifier=0):
        self.intelligence_modifier = intelligence_modifier
        self.constitution_modifier = constitution_modifier
        self.wisdom_modifier = wisdom_modifier
        self.charisma_modifier = charisma_modifier


class MockConfigRepository:
    """Mock configuration repository that matches canonical JSON structure"""
    
    def get_spell(self, spell_name: str):
        """Return canonical MP-based spell data"""
        spells = {
            "fireball": {
                "mp_cost": 15,
                "school": "evocation",
                "valid_domains": ["arcane", "occult"],
                "base_damage": 28,  # Numeric instead of "8d6"
                "mp_scaling": 2,  # Extra MP adds 2 damage per MP
                "damage_type": "fire",
                "save_type": "reflex",
                "save_for_half": True,
                "concentration": False,
                "duration": "instantaneous",
                "range_feet": 400,
                "area_of_effect": "20ft_radius"
            },
            "heal": {
                "mp_cost": 12,
                "school": "conjuration",
                "valid_domains": ["divine", "nature"],
                "base_healing": 18,  # Numeric instead of "2d8+4"
                "healing_scaling": 1,  # Extra MP adds 1 healing per MP
                "save_type": "none",
                "concentration": False,
                "duration": "instantaneous",
                "range_feet": 30,
                "target": "single_target"
            },
            "charm_person": {
                "mp_cost": 8,
                "school": "enchantment", 
                "valid_domains": ["arcane", "occult"],
                "save_type": "will",
                "save_negates": True,
                "concentration": True,
                "duration": "10_minutes",
                "range_feet": 60,
                "target": "single_humanoid"
            }
        }
        return spells.get(spell_name)
    
    def get_spells(self):
        return {
            "fireball": self.get_spell("fireball"),
            "heal": self.get_spell("heal"),
            "charm_person": self.get_spell("charm_person")
        }
    
    def get_domain(self, domain_name: str):
        """Return canonical domain data matching Bible requirements"""
        domains = {
            "arcane": {
                "primary_ability": "intelligence",
                "mp_efficiency": 1.0,
                "save_bonus": 0,
                "schools_bonus": ["evocation", "transmutation"],
                "schools_penalty": [],
                "description": "Academic study of magical forces"
            },
            "divine": {
                "primary_ability": "wisdom",
                "mp_efficiency": 0.9,
                "save_bonus": 2,
                "schools_bonus": ["abjuration", "conjuration"],
                "schools_penalty": ["necromancy"],
                "description": "Magic granted by higher powers"
            },
            "nature": {
                "primary_ability": "wisdom",
                "mp_efficiency": 0.8,
                "save_bonus": 1,
                "schools_bonus": ["transmutation", "conjuration"],
                "schools_penalty": ["enchantment"],
                "description": "Magic drawn from natural forces"
            },
            "occult": {  # Note: Bible says "Eldritch" but JSON uses "occult"
                "primary_ability": "charisma",
                "mp_efficiency": 1.2,
                "save_bonus": -1,
                "schools_bonus": ["necromancy", "enchantment"],
                "schools_penalty": ["abjuration"],
                "description": "Forbidden knowledge and dark pacts"
            }
        }
        return domains.get(domain_name)
    
    def get_magic_domains(self):
        return {
            "arcane": self.get_domain("arcane"),
            "divine": self.get_domain("divine"),
            "nature": self.get_domain("nature"),
            "occult": self.get_domain("occult")
        }
    
    def get_combat_rules(self):
        return {
            "bypasses_armor_class": ["force"],
            "bypasses_damage_reduction": ["force", "radiant"]
        }
    
    def get_concentration_rules(self):
        return {
            "base_mechanics": {
                "max_concentration_effects": 1,
                "concentration_save_base_dc": 10,
                "damage_concentration_dc_formula": "max(10, damage_taken / 2)",
                "ability_modifier": "constitution"
            }
        }


class MockDamageTypeService:
    """Mock damage type service that validates canonical damage types"""
    
    def validate_damage_type(self, damage_type_id: str):
        valid_types = ["fire", "cold", "lightning", "acid", "force", "necrotic", "radiant", "psychic", "thunder"]
        return damage_type_id in valid_types
    
    def get_environmental_damage_modifier(self, damage_type_id: str, environment: str):
        return 1.0
    
    def calculate_damage_interaction(self, attacker_type: str, defender_type: str):
        return 1.0
    
    def get_damage_resistances(self, damage_type_id: str):
        return []
    
    def get_damage_vulnerabilities(self, damage_type_id: str):
        return []


class TestCanonicalMagicSystem:
    """Test the canonical MP-based magic system business logic"""
    
    def setup_method(self):
        """Set up test fixtures for canonical system"""
        self.mock_config = MockConfigRepository()
        self.mock_damage_service = MockDamageTypeService()
        self.magic_service = MagicBusinessService(self.mock_config, self.mock_damage_service)
        self.abilities = MockAbilities()
    
    def test_mp_cost_calculation_with_domain_efficiency(self):
        """Test MP cost calculation with domain efficiency bonuses (Bible requirement)"""
        # Arcane domain has 1.0 efficiency (no bonus)
        arcane_cost = self.magic_service.calculate_mp_cost("fireball", "arcane")
        assert arcane_cost == 15  # Base cost
        
        # Divine domain has 0.9 efficiency (10% reduction)
        divine_cost = self.magic_service.calculate_mp_cost("heal", "divine")
        assert divine_cost == 11  # 12 * 0.9 = 10.8, rounded up to 11
        
        # Nature domain has 0.8 efficiency (20% reduction)
        nature_cost = self.magic_service.calculate_mp_cost("heal", "nature")
        assert nature_cost == 10  # 12 * 0.8 = 9.6, rounded up to 10
        
        # Occult domain has 1.2 efficiency (20% penalty)
        occult_cost = self.magic_service.calculate_mp_cost("charm_person", "occult")
        assert occult_cost == 10  # 8 * 1.2 = 9.6, rounded up to 10
    
    def test_domain_compatibility_validation(self):
        """Test that spells can only be cast with valid domains (Bible requirement)"""
        # Fireball can be cast with arcane or occult
        assert self.magic_service.can_cast_spell("fireball", "arcane", current_mp=20)
        assert self.magic_service.can_cast_spell("fireball", "occult", current_mp=20)
        
        # Fireball cannot be cast with divine or nature
        assert not self.magic_service.can_cast_spell("fireball", "divine", current_mp=20)
        assert not self.magic_service.can_cast_spell("fireball", "nature", current_mp=20)
        
        # Heal can be cast with divine or nature
        assert self.magic_service.can_cast_spell("heal", "divine", current_mp=20)
        assert self.magic_service.can_cast_spell("heal", "nature", current_mp=20)
        
        # Heal cannot be cast with arcane or occult
        assert not self.magic_service.can_cast_spell("heal", "arcane", current_mp=20)
        assert not self.magic_service.can_cast_spell("heal", "occult", current_mp=20)
    
    def test_mp_requirement_validation(self):
        """Test MP requirement validation (Bible's core difference from D&D)"""
        # Character with sufficient MP can cast
        assert self.magic_service.can_cast_spell("fireball", "arcane", current_mp=15)
        assert self.magic_service.can_cast_spell("fireball", "arcane", current_mp=20)
        
        # Character with insufficient MP cannot cast
        assert not self.magic_service.can_cast_spell("fireball", "arcane", current_mp=14)
        assert not self.magic_service.can_cast_spell("fireball", "arcane", current_mp=5)
    
    def test_spell_save_dc_by_domain_primary_ability(self):
        """Test save DC calculation using domain's primary ability (Bible requirement)"""
        # Arcane domain uses Intelligence
        arcane_dc = self.magic_service.calculate_spell_save_dc("fireball", "arcane", self.abilities, proficiency_bonus=3)
        expected_arcane = 8 + 3 + 3 + 0  # 8 + prof + int_mod + domain_bonus
        assert arcane_dc == expected_arcane
        
        # Divine domain uses Wisdom and has +2 save bonus
        divine_dc = self.magic_service.calculate_spell_save_dc("heal", "divine", self.abilities, proficiency_bonus=3)
        expected_divine = 8 + 3 + 1 + 2  # 8 + prof + wis_mod + domain_bonus
        assert divine_dc == expected_divine
        
        # Occult domain uses Charisma and has -1 save penalty
        occult_dc = self.magic_service.calculate_spell_save_dc("charm_person", "occult", self.abilities, proficiency_bonus=3)
        expected_occult = 8 + 3 + 0 + (-1)  # 8 + prof + cha_mod + domain_penalty
        assert occult_dc == expected_occult
    
    def test_spell_casting_produces_canonical_effects(self):
        """Test that spell casting produces effects consistent with Bible system"""
        spell_effect = self.magic_service.cast_spell("fireball", "arcane", self.abilities, proficiency_bonus=3)
        
        assert isinstance(spell_effect, SpellEffect)
        assert spell_effect.damage is not None
        assert spell_effect.damage == 28  # Base damage from mock
        assert spell_effect.damage_type == "fire"
        assert spell_effect.save_type == SaveType.REFLEX
        assert spell_effect.save_dc == 14  # 8 + 3 + 3 + 0
        assert not spell_effect.concentration_required  # Fireball doesn't require concentration
    
    def test_concentration_check_mechanics(self):
        """Test concentration check mechanics (Bible mentions this needs implementation)"""
        # Test basic concentration check calculation
        check = self.magic_service.check_concentration(damage_taken=10, abilities=self.abilities, proficiency_bonus=3)
        
        assert isinstance(check, ConcentrationCheck)
        assert check.dc == 10  # max(10, 10/2) = max(10, 5) = 10
        assert check.ability_modifier == 2  # Constitution modifier
        assert check.proficiency_bonus == 3
    
    def test_concentration_save_resolution(self):
        """Test concentration save resolution"""
        check = ConcentrationCheck(dc=15, ability_modifier=2, proficiency_bonus=3, additional_bonuses=0)
        
        # The save should be deterministic for testing
        # Mock the dice roll or test the calculation logic
        result = self.magic_service.make_concentration_save(check)
        assert isinstance(result, bool)
    
    def test_extra_mp_scaling(self):
        """Test extra MP spending for enhanced effects (Bible system feature)"""
        # Base cost
        base_cost = self.magic_service.calculate_mp_cost("fireball", "arcane", extra_mp=0)
        assert base_cost == 15
        
        # Enhanced cost
        enhanced_cost = self.magic_service.calculate_mp_cost("fireball", "arcane", extra_mp=10)
        assert enhanced_cost == 25  # 15 + 10
        
        # Should still be able to cast if have enough MP
        assert self.magic_service.can_cast_spell("fireball", "arcane", current_mp=25, extra_mp=10)
        assert not self.magic_service.can_cast_spell("fireball", "arcane", current_mp=24, extra_mp=10)
    
    def test_get_available_spells_for_domain(self):
        """Test getting available spells for a specific domain"""
        arcane_spells = self.magic_service.get_available_spells_for_domain("arcane")
        assert "fireball" in arcane_spells
        assert "charm_person" in arcane_spells
        assert "heal" not in arcane_spells  # Heal is divine/nature only
        
        divine_spells = self.magic_service.get_available_spells_for_domain("divine")
        assert "heal" in divine_spells
        assert "fireball" not in divine_spells  # Fireball is arcane/occult only
    
    def test_unknown_spell_handling(self):
        """Test that unknown spells are handled gracefully"""
        with pytest.raises(ValueError, match="Unknown spell: nonexistent_spell"):
            self.magic_service.calculate_mp_cost("nonexistent_spell", "arcane")
        
        assert not self.magic_service.can_cast_spell("nonexistent_spell", "arcane", current_mp=100)
        
        with pytest.raises(ValueError, match="Unknown spell: nonexistent_spell"):
            self.magic_service.cast_spell("nonexistent_spell", "arcane", self.abilities, proficiency_bonus=3)


class TestCanonicalMagicCombatIntegration:
    """Test magic system integration with combat (canonical system)"""
    
    def setup_method(self):
        """Set up test fixtures for combat integration"""
        self.mock_config = MockConfigRepository()
        self.mock_damage_service = MockDamageTypeService()
        self.magic_service = MagicBusinessService(self.mock_config, self.mock_damage_service)
        
        self.mock_time_provider = Mock()
        from datetime import datetime
        self.mock_time_provider.get_current_time.return_value = datetime.now()
        
        self.combat_service = MagicCombatBusinessService(self.magic_service, self.mock_time_provider)
        self.abilities = MockAbilities()
    
    def test_spell_casting_attempt_success(self):
        """Test successful spell casting attempt in combat"""
        result = self.combat_service.attempt_spell_cast(
            caster_id="player_1",
            spell_name="fireball",
            domain="arcane",
            target_id="enemy_1",
            abilities=self.abilities,
            current_mp=20,
            proficiency_bonus=3
        )
        
        assert isinstance(result, SpellCastingResult)
        assert result.success is True
        assert result.spell_effect is not None
        assert result.mp_cost == 15
        assert result.error_message is None
    
    def test_spell_casting_attempt_insufficient_mp(self):
        """Test spell casting attempt with insufficient MP"""
        result = self.combat_service.attempt_spell_cast(
            caster_id="player_1",
            spell_name="fireball",
            domain="arcane",
            target_id="enemy_1",
            abilities=self.abilities,
            current_mp=10,  # Not enough for fireball (15 MP)
            proficiency_bonus=3
        )
        
        assert isinstance(result, SpellCastingResult)
        assert result.success is False
        assert result.spell_effect is None
        assert result.error_message is not None
    
    def test_spell_casting_attempt_invalid_domain(self):
        """Test spell casting attempt with invalid domain"""
        result = self.combat_service.attempt_spell_cast(
            caster_id="player_1",
            spell_name="fireball",
            domain="divine",  # Fireball not available to divine domain
            target_id="enemy_1",
            abilities=self.abilities,
            current_mp=20,
            proficiency_bonus=3
        )
        
        assert isinstance(result, SpellCastingResult)
        assert result.success is False
        assert result.spell_effect is None
        assert result.error_message is not None
    
    def test_concentration_effect_tracking(self):
        """Test that concentration effects are properly tracked"""
        result = self.combat_service.attempt_spell_cast(
            caster_id="player_1",
            spell_name="charm_person",  # Requires concentration
            domain="arcane",
            target_id="enemy_1",
            abilities=self.abilities,
            current_mp=20,
            proficiency_bonus=3
        )
        
        assert result.success is True
        assert result.concentration_effect is not None
        assert result.concentration_effect.caster_id == "player_1"
        # ActiveConcentration object should have these attributes based on the error output
        assert hasattr(result.concentration_effect, 'spell_name')
        assert result.concentration_effect.spell_name == "charm_person"
        assert hasattr(result.concentration_effect, 'target_id')
        assert result.concentration_effect.target_id == "enemy_1"


if __name__ == "__main__":
    pytest.main([__file__]) 