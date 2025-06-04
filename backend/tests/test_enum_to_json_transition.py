"""
Test suite for enum-to-JSON configuration transition.
Tests core functionality without complex dependencies.
"""

import pytest
from backend.infrastructure.data.json_config_loader import (
    get_config_loader,
    FactionType,
    DamageType,
    ResourceType,
    BiomeType,
    RegionType,
    ConfigurationType,
    validate_config_id
)


class TestJSONConfigurationLoader:
    """Test the JSON configuration loader functionality"""
    
    def test_loader_singleton(self):
        """Test that loader is properly implemented as singleton"""
        loader1 = get_config_loader()
        loader2 = get_config_loader()
        assert loader1 is loader2
    
    def test_all_configuration_types_loaded(self):
        """Test that all configuration types are loaded"""
        loader = get_config_loader()
        
        # Test each configuration type has data
        assert len(loader.get_faction_type_ids()) > 0
        assert len(loader.get_damage_type_ids()) > 0
        assert len(loader.get_settlement_type_ids()) > 0
        assert len(loader.get_resource_type_ids()) > 0
        assert len(loader.get_region_type_ids()) > 0
        assert len(loader.get_biome_type_ids()) > 0
        assert len(loader.get_chaos_level_ids()) > 0
    
    def test_configuration_data_retrieval(self):
        """Test that configuration data can be retrieved"""
        loader = get_config_loader()
        
        # Test faction data
        faction_ids = loader.get_faction_type_ids()
        if faction_ids:
            faction_data = loader.get_faction_type(faction_ids[0])
            assert faction_data is not None
            assert isinstance(faction_data, dict)
        
        # Test damage data
        damage_ids = loader.get_damage_type_ids()
        if damage_ids:
            damage_data = loader.get_damage_type(damage_ids[0])
            assert damage_data is not None
            assert isinstance(damage_data, dict)
    
    def test_validation_functions(self):
        """Test configuration validation functions"""
        loader = get_config_loader()
        
        # Test faction validation
        faction_ids = loader.get_faction_type_ids()
        if faction_ids:
            valid_id = faction_ids[0]
            assert validate_config_id(valid_id, ConfigurationType.FACTION_TYPE)
            assert not validate_config_id("invalid_id", ConfigurationType.FACTION_TYPE)
        
        # Test resource validation
        resource_ids = loader.get_resource_type_ids()
        if resource_ids:
            valid_id = resource_ids[0]
            assert validate_config_id(valid_id, ConfigurationType.RESOURCE_TYPE)
            assert not validate_config_id("invalid_id", ConfigurationType.RESOURCE_TYPE)


class TestBackwardsCompatibilityEnums:
    """Test backwards compatibility enum replacements"""
    
    def test_faction_type_enum_compatibility(self):
        """Test FactionType backwards compatibility"""
        loader = get_config_loader()
        faction_ids = loader.get_faction_type_ids()
        
        # Test that we can iterate over FactionType
        for faction_id in FactionType:
            assert faction_id in faction_ids
        
        # Test that we can check membership
        if faction_ids:
            assert faction_ids[0] in FactionType
    
    def test_damage_type_enum_compatibility(self):
        """Test DamageType backwards compatibility"""
        loader = get_config_loader()
        damage_ids = loader.get_damage_type_ids()
        
        # Test that we can iterate over DamageType
        for damage_id in DamageType:
            assert damage_id in damage_ids
        
        # Test that we can check membership
        if damage_ids:
            assert damage_ids[0] in DamageType
    
    def test_resource_type_enum_compatibility(self):
        """Test ResourceType backwards compatibility"""
        loader = get_config_loader()
        resource_ids = loader.get_resource_type_ids()
        
        # Test that we can iterate over ResourceType
        for resource_id in ResourceType:
            assert resource_id in resource_ids
        
        # Test that we can check membership
        if resource_ids:
            assert resource_ids[0] in ResourceType


class TestRegionSystemIntegration:
    """Test region system integration with JSON configs"""
    
    def test_region_helper_functions(self):
        """Test region system helper functions"""
        from backend.systems.region.models import (
            get_valid_region_types,
            get_valid_biome_types,
            get_valid_resource_types,
            validate_region_type,
            validate_biome_type,
            validate_resource_type
        )
        
        # Test getter functions
        region_types = get_valid_region_types()
        biome_types = get_valid_biome_types()
        resource_types = get_valid_resource_types()
        
        assert len(region_types) > 0
        assert len(biome_types) > 0
        assert len(resource_types) > 0
        
        # Test validation functions
        if region_types:
            assert validate_region_type(region_types[0])
            assert not validate_region_type("invalid_type")
        
        if biome_types:
            assert validate_biome_type(biome_types[0])
            assert not validate_biome_type("invalid_type")
        
        if resource_types:
            assert validate_resource_type(resource_types[0])
            assert not validate_resource_type("invalid_type")
    
    def test_resource_node_creation(self):
        """Test resource node creation with JSON configurations"""
        from backend.systems.region.models import ResourceNode, get_valid_resource_types
        
        resource_types = get_valid_resource_types()
        if resource_types:
            # Test valid resource node creation
            node = ResourceNode(
                resource_type=resource_types[0],
                abundance=0.8,
                quality=0.7,
                accessibility=0.6
            )
            
            assert node.resource_type == resource_types[0]
            assert node.abundance == 0.8
            assert node.quality == 0.7
            assert node.accessibility == 0.6
            
            # Test value calculation
            value = node.calculate_value()
            assert isinstance(value, float)
            assert value >= 0.0
        
        # Test invalid resource node creation
        with pytest.raises(ValueError):
            ResourceNode(
                resource_type="invalid_resource",
                abundance=0.5,
                quality=0.5,
                accessibility=0.5
            )


class TestFactionSystemIntegration:
    """Test faction system integration with JSON configs"""
    
    def test_faction_helper_functions(self):
        """Test faction system helper functions"""
        from backend.infrastructure.schemas.faction.faction_types import (
            get_valid_faction_types,
            get_valid_faction_alignments,
            get_valid_diplomatic_stances,
            validate_faction_type,
            validate_faction_alignment,
            validate_diplomatic_stance
        )
        
        # Test getter functions
        faction_types = get_valid_faction_types()
        alignments = get_valid_faction_alignments()
        stances = get_valid_diplomatic_stances()
        
        assert len(faction_types) > 0
        assert len(alignments) > 0
        assert len(stances) > 0
        
        # Test validation functions
        if faction_types:
            assert validate_faction_type(faction_types[0])
            assert not validate_faction_type("invalid_type")
        
        if alignments:
            assert validate_faction_alignment(alignments[0])
            assert not validate_faction_alignment("invalid_alignment")
        
        if stances:
            assert validate_diplomatic_stance(stances[0])
            assert not validate_diplomatic_stance("invalid_stance")


class TestConfigurationIntegrity:
    """Test overall configuration integrity"""
    
    def test_all_configurations_have_required_structure(self):
        """Test that all configurations have the required structure"""
        loader = get_config_loader()
        
        # Test faction configuration structure
        faction_types = loader.get_all_faction_types()
        for faction_id, faction_data in faction_types.items():
            assert isinstance(faction_data, dict)
            assert 'name' in faction_data
            assert 'description' in faction_data
        
        # Test damage configuration structure
        damage_types = loader.get_all_damage_types()
        for damage_id, damage_data in damage_types.items():
            assert isinstance(damage_data, dict)
            assert 'name' in damage_data
            assert 'description' in damage_data
    
    def test_configuration_cross_references(self):
        """Test that configuration cross-references are valid"""
        loader = get_config_loader()
        
        # This test ensures that any references between configurations are valid
        # For example, if biome configurations reference climate zones, 
        # those climate zones should exist
        
        # Test biome interactions if they exist
        biome_interactions = loader.get_biome_interactions()
        if biome_interactions:
            assert isinstance(biome_interactions, dict)
        
        # Test faction alignment compatibility
        faction_types = loader.get_all_faction_types()
        faction_alignments = loader.get_all_faction_alignments()
        
        for faction_id, faction_data in faction_types.items():
            if 'default_alignment' in faction_data:
                default_alignment = faction_data['default_alignment']
                assert default_alignment in faction_alignments


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 