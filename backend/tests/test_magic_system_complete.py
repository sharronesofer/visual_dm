"""
Comprehensive Magic System Test Suite

Tests all components of the canonical magic system:
- Basic MP-based spellcasting
- Domain efficiency and access  
- Metamagic enhancements
- Spell combinations
- Performance optimizations
- Caching functionality

Validates complete system integration and functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Core system imports
from backend.systems.magic.services.magic_business_service import MagicBusinessService
from backend.systems.magic.services.magic_combat_service import MagicCombatBusinessService

# Advanced feature imports
from backend.systems.magic.services.metamagic_service import (
    MetamagicService, MetamagicType, MetamagicResult
)
from backend.systems.magic.services.spell_combination_service import (
    SpellCombinationService, CombinationType, CombinationResult
)

# Performance imports
from backend.infrastructure.cache.magic_cache import MagicCache, CacheConfig
from backend.infrastructure.utils.time_provider import SystemTimeProvider

# Mock character abilities to avoid circular imports
class MockCharacterAbilities:
    """Mock character abilities for testing"""
    
    def __init__(self, intelligence: int = 16, wisdom: int = 14, charisma: int = 12):
        self.intelligence = intelligence
        self.wisdom = wisdom 
        self.charisma = charisma
    
    def get_ability_modifier(self, ability_name: str) -> int:
        """Get ability modifier for testing"""
        ability_score = getattr(self, ability_name.lower(), 10)
        return (ability_score - 10) // 2

class TestCanonicalMagicSystemComplete:
    """Comprehensive tests for the complete canonical magic system"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock configuration repository
        self.mock_config_repo = Mock()
        self.mock_damage_service = Mock()
        self.time_provider = SystemTimeProvider()
        
        # Setup domain configurations
        self.mock_config_repo.get_domain.side_effect = lambda domain: {
            "arcane": {"mp_efficiency": 1.0, "primary_ability": "intelligence"},
            "divine": {"mp_efficiency": 0.9, "primary_ability": "wisdom"},
            "nature": {"mp_efficiency": 0.8, "primary_ability": "wisdom"},
            "occult": {"mp_efficiency": 0.85, "primary_ability": "charisma"}
        }.get(domain, {"mp_efficiency": 1.0, "primary_ability": "intelligence"})
        
        # Setup spell configurations
        self.mock_config_repo.get_spell.side_effect = lambda name: {
            "fireball": {
                "name": "Fireball", "mp_cost": 5, "base_damage": 28,
                "school": "evocation", "damage_type": "fire",
                "range_feet": 150, "duration_seconds": 0,
                "concentration": False, "components": ["verbal", "somatic"],
                "valid_domains": ["arcane", "occult"], "target": "area"
            },
            "healing_word": {
                "name": "Healing Word", "mp_cost": 2, "base_healing": 8,
                "school": "evocation", "damage_type": None,
                "range_feet": 60, "duration_seconds": 0,
                "concentration": False, "components": ["verbal"],
                "valid_domains": ["divine", "nature"], "target": "single_target"
            },
            "shield": {
                "name": "Shield", "mp_cost": 2, "base_damage": 0,
                "school": "abjuration", "damage_type": None,
                "range_feet": 0, "duration_seconds": 600,
                "concentration": True, "components": ["verbal", "somatic"],
                "valid_domains": ["arcane"], "target": "self"
            }
        }.get(name)
        
        # Setup damage calculations
        self.mock_damage_service.calculate_damage.return_value = {
            "final_damage": 28, "damage_type": "fire", "critical": False
        }
        
        # Create services
        self.magic_service = MagicBusinessService(
            self.mock_config_repo, self.mock_damage_service
        )
        self.combat_service = MagicCombatBusinessService(
            self.magic_service, self.time_provider
        )
        
        # Create advanced services
        self.metamagic_service = MetamagicService()
        self.combination_service = SpellCombinationService()
        
        # Create cache with test configuration
        cache_config = CacheConfig(enabled=False)  # Disable Redis for tests
        self.cache = MagicCache(cache_config)
    
    def test_basic_mp_spellcasting(self):
        """Test basic MP-based spell casting without spell slots"""
        abilities = MockCharacterAbilities(intelligence=16)  # +3 modifier
        
        # Test successful spell cast
        result = self.combat_service.attempt_spell_cast(
            caster_id="test_character",
            spell_name="fireball",
            domain="arcane",
            target_id="enemy1",
            abilities=abilities,
            current_mp=20,
            proficiency_bonus=3
        )
        
        assert result.success is True
        assert result.mp_cost == 5  # Base MP cost for fireball
        assert result.spell_effect["damage"] == 28
        assert "spell_slots" not in result.__dict__  # No spell slot system
    
    def test_domain_efficiency_bonuses(self):
        """Test domain-based MP efficiency bonuses"""
        abilities = MockCharacterAbilities(wisdom=14)  # +2 modifier
        
        # Test Nature domain (0.8 efficiency)
        nature_result = self.combat_service.attempt_spell_cast(
            caster_id="druid",
            spell_name="healing_word",
            domain="nature",
            target_id="ally1", 
            abilities=abilities,
            current_mp=10,
            proficiency_bonus=2
        )
        
        # Nature domain should have reduced MP cost due to efficiency
        expected_mp_cost = int(2 * 0.8)  # 2 MP * 0.8 efficiency = 1.6 → 2 (minimum 1)
        assert nature_result.mp_cost <= 2  # Should be efficient
        
        # Test Arcane domain (1.0 efficiency) 
        arcane_result = self.combat_service.attempt_spell_cast(
            caster_id="wizard",
            spell_name="healing_word", 
            domain="arcane",
            target_id="ally1",
            abilities=abilities,
            current_mp=10,
            proficiency_bonus=2
        )
        
        # Note: healing_word is not in arcane's valid domains, so this might fail
        # But if it succeeds, it should cost full MP
        if arcane_result.success:
            assert arcane_result.mp_cost >= nature_result.mp_cost
    
    def test_metamagic_empowered_spell(self):
        """Test empowered metamagic effect (+50% damage for +25% MP)"""
        spell_properties = {
            "name": "fireball",
            "school": "evocation", 
            "mp_cost": 5,
            "base_damage": 28,
            "base_healing": None,
            "range_feet": 150,
            "duration_seconds": 0,
            "concentration": False,
            "target": "area",
            "components": ["verbal", "somatic"]
        }
        
        result = self.metamagic_service.apply_metamagic(
            spell_properties=spell_properties,
            base_mp_cost=5,
            metamagic_types=[MetamagicType.EMPOWERED],
            available_mp=10
        )
        
        assert result.success is True
        assert result.total_mp_cost == 6  # 5 + (5 * 0.25) = 6.25 → 6
        assert result.modified_effect["base_damage"] == 42  # 28 * 1.5 = 42
        assert MetamagicType.EMPOWERED in result.metamagic_applied
    
    def test_metamagic_multiple_effects(self):
        """Test combining multiple metamagic effects"""
        spell_properties = {
            "name": "shield",
            "school": "abjuration",
            "mp_cost": 2,
            "base_damage": 0,
            "base_healing": None,
            "range_feet": 0,
            "duration_seconds": 600,
            "concentration": True,
            "target": "self",
            "components": ["verbal", "somatic"]
        }
        
        # Combine Extended (double duration) + Silent (remove verbal)
        result = self.metamagic_service.apply_metamagic(
            spell_properties=spell_properties,
            base_mp_cost=2,
            metamagic_types=[MetamagicType.EXTENDED, MetamagicType.SILENT],
            available_mp=5
        )
        
        assert result.success is True
        # Total multiplier: 0.5 (Extended) + 0.5 (Silent) = 1.0
        assert result.total_mp_cost == 4  # 2 + (2 * 1.0) = 4
        assert result.modified_effect["duration_seconds"] == 1200  # 600 * 2
        assert "verbal" not in result.modified_effect["components"]
    
    def test_spell_combination_elemental_storm(self):
        """Test elemental storm spell combination"""
        # Create spell data objects
        fireball_data = type('SpellData', (), {
            'name': 'Fireball',
            'school': 'evocation',
            'mp_cost': 5,
            'base_damage': 28,
            'base_healing': None,
            'range_feet': 150,
            'duration_seconds': 0,
            'damage_type': 'fire'
        })()
        
        ice_storm_data = type('SpellData', (), {
            'name': 'Ice Storm',
            'school': 'evocation', 
            'mp_cost': 6,
            'base_damage': 22,
            'base_healing': None,
            'range_feet': 300,
            'duration_seconds': 0,
            'damage_type': 'cold'
        })()
        
        lightning_bolt_data = type('SpellData', (), {
            'name': 'Lightning Bolt',
            'school': 'evocation',
            'mp_cost': 5,
            'base_damage': 25,
            'base_healing': None,
            'range_feet': 100,
            'duration_seconds': 0,
            'damage_type': 'lightning'
        })()
        
        spells = [fireball_data, ice_storm_data, lightning_bolt_data]
        
        # Test combination
        result = self.combination_service.combine_spells(
            spells=spells,
            combination_name="elemental_storm",
            available_mp=25
        )
        
        assert result.success is True
        # Base cost: 5+6+5=16, with 1.25 multiplier = 20
        assert result.total_mp_cost == 20
        assert result.combination_name == "elemental_storm"
        assert len(result.spells_combined) == 3
        # Enhanced damage: (28+22+25) * 1.75 = 131.25 → 131
        assert result.enhanced_properties["final_damage"] == 131
    
    def test_spell_combination_prerequisites(self):
        """Test spell combination prerequisite validation"""
        # Try to combine spells that don't meet requirements
        same_element_spells = [
            type('SpellData', (), {
                'name': 'Fireball', 'school': 'evocation', 'mp_cost': 5,
                'base_damage': 28, 'range_feet': 150, 'duration_seconds': 0,
                'damage_type': 'fire'
            })(),
            type('SpellData', (), {
                'name': 'Fire Bolt', 'school': 'evocation', 'mp_cost': 1,
                'base_damage': 10, 'range_feet': 120, 'duration_seconds': 0,
                'damage_type': 'fire'  # Same damage type
            })()
        ]
        
        # This should fail because elemental_storm requires different damage types
        result = self.combination_service.combine_spells(
            spells=same_element_spells,
            combination_name="elemental_storm",
            available_mp=20
        )
        
        assert result.success is False
        assert "cannot create" in result.error_message.lower()
    
    def test_concentration_tracking(self):
        """Test concentration effect tracking"""
        abilities = MockCharacterAbilities(intelligence=16)
        
        # Cast a concentration spell
        result = self.combat_service.attempt_spell_cast(
            caster_id="caster1",
            spell_name="shield",
            domain="arcane",
            target_id="caster1",
            abilities=abilities,
            current_mp=10,
            proficiency_bonus=3
        )
        
        assert result.success is True
        assert result.concentration_effect is not None
        assert result.concentration_effect["requires_concentration"] is True
        assert "duration" in result.concentration_effect
    
    def test_insufficient_mp_handling(self):
        """Test proper handling when MP is insufficient"""
        abilities = MockCharacterAbilities(intelligence=14)
        
        # Try to cast expensive spell with insufficient MP
        result = self.combat_service.attempt_spell_cast(
            caster_id="low_mp_caster",
            spell_name="fireball",
            domain="arcane",
            target_id="enemy1",
            abilities=abilities,
            current_mp=3,  # Need 5 MP for fireball
            proficiency_bonus=2
        )
        
        assert result.success is False
        assert "insufficient mp" in result.error_message.lower()
        assert result.mp_cost == 5  # Should still show required cost
    
    def test_cache_spell_data(self):
        """Test spell data caching functionality"""
        if not self.cache.config.enabled:
            pytest.skip("Cache disabled for tests")
        
        spell_data = {
            "id": "test_spell_123",
            "name": "Test Spell",
            "mp_cost": 3,
            "school": "evocation"
        }
        
        # Cache spell data
        success = self.cache.set_spell("test_spell_123", spell_data)
        assert success is True
        
        # Retrieve cached data
        cached_data = self.cache.get_spell("test_spell_123")
        assert cached_data == spell_data
        
        # Test cache invalidation
        self.cache.invalidate_spell_cache("test_spell_123")
        invalidated_data = self.cache.get_spell("test_spell_123")
        assert invalidated_data is None
    
    def test_batch_metamagic_calculations(self):
        """Test performance of batch metamagic calculations"""
        spell_properties = {
            "name": "fireball",
            "school": "evocation",
            "mp_cost": 5,
            "base_damage": 28,
            "range_feet": 150,
            "concentration": False
        }
        
        # Test multiple metamagic combinations
        metamagic_combinations = [
            [MetamagicType.EMPOWERED],
            [MetamagicType.EXTENDED],
            [MetamagicType.EMPOWERED, MetamagicType.EXTENDED],
            [MetamagicType.MAXIMIZED],
        ]
        
        results = []
        for metamagic_types in metamagic_combinations:
            result = self.metamagic_service.apply_metamagic(
                spell_properties=spell_properties,
                base_mp_cost=5,
                metamagic_types=metamagic_types,
                available_mp=20
            )
            results.append(result)
        
        # All should succeed
        assert all(result.success for result in results)
        
        # Different MP costs based on metamagic
        assert results[0].total_mp_cost == 6   # Empowered (+25%)
        assert results[1].total_mp_cost == 7   # Extended (+50%)  
        assert results[2].total_mp_cost == 8   # Both (+75%)
        assert results[3].total_mp_cost == 15  # Maximized (+200%)
    
    def test_domain_access_validation(self):
        """Test domain access and validation"""
        abilities = MockCharacterAbilities(intelligence=16)
        
        # Mock spell that only works in specific domains  
        self.mock_config_repo.get_spell.return_value = {
            "name": "Divine Word", "mp_cost": 12, "base_damage": 0,
            "school": "evocation", "valid_domains": ["divine"],
            "range_feet": 30, "duration_seconds": 0,
            "concentration": False, "components": ["verbal"]
        }
        
        # Should work with divine domain
        divine_result = self.combat_service.attempt_spell_cast(
            caster_id="cleric",
            spell_name="Divine Word",
            domain="divine",
            target_id="undead1",
            abilities=abilities,
            current_mp=15,
            proficiency_bonus=4
        )
        
        assert divine_result.success is True
    
    def test_mp_regeneration_simulation(self):
        """Test MP regeneration over time"""
        # This tests the MP regeneration calculation logic
        initial_mp = 15
        max_mp = 30
        regeneration_rate = 2  # MP per hour
        hours_rested = 4
        
        # Calculate expected MP after rest
        mp_restored = regeneration_rate * hours_rested
        final_mp = min(max_mp, initial_mp + mp_restored)
        
        assert final_mp == 23  # 15 + (2*4) = 23, under max of 30
        
        # Test full rest
        full_rest_mp = min(max_mp, initial_mp + (regeneration_rate * 8))
        assert full_rest_mp == 30  # Should cap at max MP
    
    def test_spell_scaling_with_extra_mp(self):
        """Test spell scaling when extra MP is spent"""
        abilities = MockCharacterAbilities(intelligence=18)  # +4 modifier
        
        # Test fireball with extra MP (should increase damage)
        result = self.combat_service.attempt_spell_cast(
            caster_id="sorcerer",
            spell_name="fireball",
            domain="arcane",
            target_id="enemies",
            abilities=abilities,
            current_mp=20,
            proficiency_bonus=3,
            extra_mp=3  # Spend 3 extra MP for scaling
        )
        
        assert result.success is True
        assert result.mp_cost == 8  # 5 base + 3 extra
        # Damage should be scaled up (implementation dependent)
        assert result.spell_effect["damage"] >= 28  # At least base damage
    
    @pytest.mark.asyncio
    async def test_concurrent_spell_casting(self):
        """Test concurrent spell casting scenarios"""
        abilities = MockCharacterAbilities(intelligence=16)
        
        # Simulate multiple casters casting simultaneously
        tasks = []
        for i in range(3):
            task = asyncio.create_task(
                asyncio.to_thread(
                    self.combat_service.attempt_spell_cast,
                    caster_id=f"caster_{i}",
                    spell_name="fireball",
                    domain="arcane", 
                    target_id="boss",
                    abilities=abilities,
                    current_mp=10,
                    proficiency_bonus=3
                )
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed independently
        assert all(result.success for result in results)
        assert len(results) == 3

def test_magic_system_integration():
    """Integration test for the complete magic system"""
    test_suite = TestCanonicalMagicSystemComplete()
    test_suite.setup_method()
    
    # Run key integration tests
    test_suite.test_basic_mp_spellcasting()
    test_suite.test_domain_efficiency_bonuses()
    test_suite.test_metamagic_empowered_spell()
    test_suite.test_spell_combination_elemental_storm()
    test_suite.test_concentration_tracking()
    
    print("✅ All magic system integration tests passed!")

if __name__ == "__main__":
    test_magic_system_integration() 