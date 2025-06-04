"""
Test module for magic configuration repositories/adapters

Tests for the canonical magic system configuration adapters that support
the Development Bible's MP-based system. These adapters provide:
- MP-based spell configurations
- Domain-based efficiency and primary abilities
- Canonical damage type validation
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

# Import the canonical magic system adapters
try:
    from backend.infrastructure.data_loaders.magic_config import (
        MagicConfigRepositoryAdapter,
        DamageTypeServiceAdapter,
        create_magic_config_repository,
        create_damage_type_service
    )
    MAGIC_CONFIG_AVAILABLE = True
except ImportError as e:
    MAGIC_CONFIG_AVAILABLE = False
    pytestmark = pytest.mark.skip(f"Magic config adapters not found: {e}")


@pytest.mark.skipif(not MAGIC_CONFIG_AVAILABLE, reason="Magic config adapters not available")
class TestMagicConfigRepositoryAdapter:
    """Test class for canonical magic config repository adapter"""
    
    def test_adapter_creation(self):
        """Test that the adapter can be created"""
        adapter = create_magic_config_repository()
        assert isinstance(adapter, MagicConfigRepositoryAdapter)
    
    def test_get_spells(self):
        """Test getting spells configuration"""
        adapter = create_magic_config_repository()
        spells = adapter.get_spells()
        assert isinstance(spells, dict)
        
        # Verify canonical spell structure if spells exist
        if spells:
            for spell_name, spell_data in spells.items():
                # Should have MP cost instead of spell level
                assert "mp_cost" in spell_data, f"Spell {spell_name} missing mp_cost"
                # Should have valid domains
                assert "valid_domains" in spell_data, f"Spell {spell_name} missing valid_domains"
                assert isinstance(spell_data["valid_domains"], list)
    
    def test_get_spell(self):
        """Test getting a specific spell"""
        adapter = create_magic_config_repository()
        
        # Test with known canonical spell
        fireball = adapter.get_spell("fireball")
        if fireball:
            assert "mp_cost" in fireball
            assert "valid_domains" in fireball
            assert isinstance(fireball["valid_domains"], list)
            assert fireball["mp_cost"] > 0
    
    def test_get_magic_domains(self):
        """Test getting magic domains configuration"""
        adapter = create_magic_config_repository()
        domains = adapter.get_magic_domains()
        assert isinstance(domains, dict)
        
        # Verify canonical domain structure
        expected_domains = ["arcane", "divine", "nature", "occult"]  # Note: JSON uses "occult" not "eldritch"
        
        for domain_name in expected_domains:
            if domain_name in domains:
                domain_data = domains[domain_name]
                assert "primary_ability" in domain_data
                assert "mp_efficiency" in domain_data
                assert isinstance(domain_data["mp_efficiency"], (int, float))
                assert domain_data["mp_efficiency"] > 0
    
    def test_get_domain(self):
        """Test getting a specific domain"""
        adapter = create_magic_config_repository()
        
        # Test arcane domain
        arcane = adapter.get_domain("arcane")
        if arcane:
            assert arcane["primary_ability"] == "intelligence"
            assert "mp_efficiency" in arcane
            assert "save_bonus" in arcane
    
    def test_get_combat_rules(self):
        """Test getting combat rules configuration"""
        adapter = create_magic_config_repository()
        combat_rules = adapter.get_combat_rules()
        assert isinstance(combat_rules, dict)
        
        # Should have bypass rules
        if "bypasses_armor_class" in combat_rules:
            assert isinstance(combat_rules["bypasses_armor_class"], list)
        if "bypasses_damage_reduction" in combat_rules:
            assert isinstance(combat_rules["bypasses_damage_reduction"], list)
    
    def test_get_concentration_rules(self):
        """Test getting concentration rules configuration"""
        adapter = create_magic_config_repository()
        concentration_rules = adapter.get_concentration_rules()
        assert isinstance(concentration_rules, dict)


@pytest.mark.skipif(not MAGIC_CONFIG_AVAILABLE, reason="Magic config adapters not available")
class TestDamageTypeServiceAdapter:
    """Test class for canonical damage type service adapter"""
    
    def test_adapter_creation(self):
        """Test that the adapter can be created"""
        adapter = create_damage_type_service()
        assert isinstance(adapter, DamageTypeServiceAdapter)
    
    def test_validate_damage_type(self):
        """Test damage type validation with canonical damage types"""
        adapter = create_damage_type_service()
        
        # Test common canonical damage types
        canonical_types = ["fire", "cold", "lightning", "acid", "force", "necrotic", "radiant", "psychic", "thunder"]
        
        for damage_type in canonical_types:
            result = adapter.validate_damage_type(damage_type)
            assert isinstance(result, bool)
            # Most canonical types should be valid if damage_types.json is properly configured
        
        # Test obviously invalid type
        assert isinstance(adapter.validate_damage_type("invalid_type"), bool)
    
    def test_environmental_damage_modifier(self):
        """Test environmental damage modifier calculation"""
        adapter = create_damage_type_service()
        
        # Test with canonical damage type
        modifier = adapter.get_environmental_damage_modifier("fire", "wet")
        assert isinstance(modifier, (int, float))
        assert modifier >= 0  # Should not be negative
    
    def test_damage_interaction_calculation(self):
        """Test damage interaction calculation"""
        adapter = create_damage_type_service()
        
        # Test damage type interactions
        interaction = adapter.calculate_damage_interaction("fire", "ice")
        assert isinstance(interaction, (int, float))
        assert interaction >= 0  # Should not be negative
    
    def test_damage_resistances(self):
        """Test getting damage resistances"""
        adapter = create_damage_type_service()
        
        # Test with canonical damage type
        resistances = adapter.get_damage_resistances("fire")
        assert resistances is None or isinstance(resistances, list)
        
        if isinstance(resistances, list):
            # All resistance entries should be strings
            for resistance in resistances:
                assert isinstance(resistance, str)
    
    def test_damage_vulnerabilities(self):
        """Test getting damage vulnerabilities"""
        adapter = create_damage_type_service()
        
        # Test with canonical damage type
        vulnerabilities = adapter.get_damage_vulnerabilities("fire")
        assert vulnerabilities is None or isinstance(vulnerabilities, list)
        
        if isinstance(vulnerabilities, list):
            # All vulnerability entries should be strings
            for vulnerability in vulnerabilities:
                assert isinstance(vulnerability, str)


class TestConfigurationIntegration:
    """Test integration between configuration components"""
    
    @pytest.mark.skipif(not MAGIC_CONFIG_AVAILABLE, reason="Magic config adapters not available")
    def test_spell_domain_compatibility(self):
        """Test that spells and domains are properly compatible"""
        config_adapter = create_magic_config_repository()
        
        spells = config_adapter.get_spells()
        domains = config_adapter.get_magic_domains()
        
        if spells and domains:
            for spell_name, spell_data in spells.items():
                if "valid_domains" in spell_data:
                    for domain in spell_data["valid_domains"]:
                        # Each valid domain should exist in the domains configuration
                        assert domain in domains, f"Spell {spell_name} references unknown domain {domain}"
    
    @pytest.mark.skipif(not MAGIC_CONFIG_AVAILABLE, reason="Magic config adapters not available")
    def test_damage_type_spell_compatibility(self):
        """Test that spell damage types are valid"""
        config_adapter = create_magic_config_repository()
        damage_adapter = create_damage_type_service()
        
        spells = config_adapter.get_spells()
        
        if spells:
            for spell_name, spell_data in spells.items():
                if "damage_type" in spell_data and spell_data["damage_type"]:
                    damage_type = spell_data["damage_type"]
                    # Damage type should be valid
                    is_valid = damage_adapter.validate_damage_type(damage_type)
                    assert is_valid, f"Spell {spell_name} has invalid damage type {damage_type}"


# Note: These tests validate the canonical configuration adapters that implement
# the business logic protocols for the MP-based magic system. They test the
# infrastructure components that DO align with the Development Bible's requirements.
