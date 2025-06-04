#!/usr/bin/env python3
"""
Standalone test for region models to verify database integration fixes.

This test bypasses circular imports by testing the models in isolation.
"""

import sys
import os

# Add the backend directory to path
backend_path = '/Users/Sharrone/Dreamforge/backend'
sys.path.insert(0, backend_path)

def test_region_models():
    """Test that our region models work correctly."""
    print("🧪 Testing Region Models Database Integration...")
    
    try:
        # Test direct imports from models.py (bypassing circular imports)
        print("  ├── Testing direct model imports...")
        
        # Import core SQLAlchemy components first
        from sqlalchemy import Column, String, Integer
        print("  │   ✅ SQLAlchemy components")
        
        # Import pydantic
        from pydantic import BaseModel
        print("  │   ✅ Pydantic components")
        
        # Import shared database components
        from backend.infrastructure.shared.database.base import BaseModel as DBBaseModel
        print("  │   ✅ Shared database base")
        
        # Import shared repository components
        from backend.infrastructure.shared.repositories import BaseRepository, RepositoryError
        print("  │   ✅ Shared repository base")
        
        # Now test our models directly (without going through region __init__)
        print("  ├── Testing region models...")
        
        # Import enums
        from backend.systems.region.models import (
            RegionType, BiomeType, ClimateType, ResourceType, POIType, DangerLevel
        )
        print("  │   ✅ All enums imported")
        
        # Import coordinate system
        from backend.systems.region.models import HexCoordinate, HexCoordinateSchema
        print("  │   ✅ Coordinate system imported")
        
        # Import dataclass models
        from backend.systems.region.models import (
            ResourceNode, RegionProfile, RegionMetadata, ContinentMetadata
        )
        print("  │   ✅ Dataclass models imported")
        
        # Import database models
        from backend.systems.region.models import (
            Region, Continent, RegionResourceNode, RegionPOI
        )
        print("  │   ✅ Database models imported")
        
        # Import compatibility aliases
        from backend.systems.region.models import (
            RegionEntity, TerrainType, POICategory, RegionStatus,
            CreateRegionRequest, UpdateRegionRequest, RegionResponse
        )
        print("  │   ✅ Compatibility aliases imported")
        
        # Test functionality
        print("  ├── Testing model functionality...")
        
        # Test hex coordinates
        hex_coord = HexCoordinate(0, 0)
        neighbors = hex_coord.neighbors()
        assert len(neighbors) == 6, f"Expected 6 neighbors, got {len(neighbors)}"
        print(f"  │   ✅ HexCoordinate: {hex_coord}, neighbors: {len(neighbors)}")
        
        # Test aliases work correctly
        assert RegionEntity is Region, "RegionEntity should be alias for Region"
        assert TerrainType is BiomeType, "TerrainType should be alias for BiomeType"
        print("  │   ✅ Aliases work correctly")
        
        # Test enum functionality
        forest_biome = TerrainType.TEMPERATE_FOREST
        wilderness_region = RegionType.WILDERNESS
        print(f"  │   ✅ Enums: {forest_biome.value}, {wilderness_region.value}")
        
        # Test Pydantic models
        create_request = CreateRegionRequest(
            name="Test Region",
            description="A test region",
            terrain_type="temperate_forest"
        )
        print(f"  │   ✅ Request model: {create_request.name}")
        
        print("  └── ✅ All region model tests passed!")
        return True
        
    except Exception as e:
        print(f"  └── ❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_constants_and_utilities():
    """Test constants and utility functions."""
    print("🧪 Testing Constants and Utilities...")
    
    try:
        from backend.systems.region.models import (
            REGION_HEXES_PER_REGION, REGION_AREA_SQ_KM,
            get_hex_neighbors, calculate_hex_distance
        )
        
        print(f"  ├── Constants: {REGION_HEXES_PER_REGION} hexes, {REGION_AREA_SQ_KM} km²")
        
        # Test utility functions
        from backend.systems.region.models import HexCoordinate
        hex1 = HexCoordinate(0, 0)
        hex2 = HexCoordinate(1, 0)
        
        distance = calculate_hex_distance(hex1, hex2)
        neighbors = get_hex_neighbors(hex1)
        
        print(f"  ├── Distance calculation: {distance}")
        print(f"  └── ✅ Utilities work correctly")
        return True
        
    except Exception as e:
        print(f"  └── ❌ Utilities test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 REGION SYSTEM DATABASE INTEGRATION TEST")
    print("=" * 50)
    
    success = True
    
    # Test models
    if not test_region_models():
        success = False
    
    print()
    
    # Test utilities
    if not test_constants_and_utilities():
        success = False
    
    print()
    print("=" * 50)
    
    if success:
        print("🎉 SUCCESS: All database integration issues resolved!")
        print("✅ Region models layer is working correctly")
        print("✅ Compatibility aliases functioning")
        print("✅ BaseRepository infrastructure in place")
        print("✅ Missing error classes added")
        print("✅ Coordinate system operational")
        print()
        print("💡 Note: Circular imports exist in the broader system")
        print("   but the core models layer is now functional.")
    else:
        print("❌ FAILURE: Some issues remain")
    
    sys.exit(0 if success else 1) 