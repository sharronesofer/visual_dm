"""
World Generation Facade Service - API Compatibility Layer

This module provides a facade service that adapts the world generation business service
to API expectations, similar to the faction system pattern.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from backend.systems.world_generation.models import (
    CreateWorldGenerationData, WorldGenerationConfig, WorldGenerationResult,
    WorldGenerationRecord, GeneratedWorldData
)
from backend.systems.world_generation.services.world_generator import (
    WorldGenerationBusinessService, create_world_generation_business_service
)


class WorldGenerationService:
    """Facade service for world generation operations - adapts business service to API expectations"""
    
    def __init__(self, db_session=None):
        """Initialize with database session (for compatibility with existing tests/router)"""
        self.db_session = db_session
        
        # Initialize the repository and business service
        from backend.infrastructure.repositories.world_generation_repository import SQLAlchemyWorldGenerationRepository, SQLAlchemyWorldContentRepository
        from backend.infrastructure.services.world_generation_config_service import DefaultWorldGenerationConfigService
        from backend.infrastructure.services.world_generation_validation_service import DefaultWorldGenerationValidationService
        
        self.world_repository = SQLAlchemyWorldGenerationRepository(db_session)
        self.content_repository = SQLAlchemyWorldContentRepository(db_session)
        self.config_service = DefaultWorldGenerationConfigService()
        self.validation_service = DefaultWorldGenerationValidationService()
        
        self.business_service = create_world_generation_business_service(
            self.world_repository,
            self.content_repository,
            self.config_service,
            self.validation_service
        )
    
    async def generate_world(self, 
                            world_name: str,
                            template_name: Optional[str] = None,
                            config_dict: Optional[Dict[str, Any]] = None,
                            user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Generate a new world - API endpoint method"""
        try:
            # Convert API input to business data
            config = None
            if config_dict:
                config = WorldGenerationConfig(**config_dict)
            
            create_data = CreateWorldGenerationData(
                world_name=world_name,
                template_name=template_name,
                config=config,
                user_id=user_id
            )
            
            # Generate via business service
            result = self.business_service.generate_world(create_data)
            
            # Convert back to API response format
            return {
                'world_id': str(result.main_continent.id),
                'world_name': world_name,
                'main_continent': {
                    'id': str(result.main_continent.id),
                    'name': result.main_continent.name,
                    'region_count': len(result.main_continent.regions)
                },
                'islands': [
                    {
                        'id': str(island.id),
                        'name': island.name,
                        'region_count': len(island.regions)
                    }
                    for island in result.islands
                ],
                'regions': result.regions,
                'npcs': result.npcs,
                'factions': result.factions,
                'trade_routes': result.trade_routes,
                'generation_stats': result.generation_stats,
                'generation_time': result.generation_time,
                'seed_used': result.seed_used
            }
            
        except ValueError as e:
            raise ValueError(f"World generation failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during world generation: {str(e)}")
    
    async def create_single_region(self,
                                  name: str,
                                  biome_type: Optional[str] = None,
                                  climate_type: Optional[str] = None,
                                  config_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a single region - API endpoint method"""
        try:
            from backend.systems.region.models import BiomeType, ClimateType
            
            # Convert string parameters to enums if provided
            biome_enum = None
            if biome_type:
                try:
                    biome_enum = BiomeType(biome_type)
                except ValueError:
                    raise ValueError(f"Invalid biome type: {biome_type}")
            
            climate_enum = None
            if climate_type:
                try:
                    climate_enum = ClimateType(climate_type)
                except ValueError:
                    raise ValueError(f"Invalid climate type: {climate_type}")
            
            config = None
            if config_dict:
                config = WorldGenerationConfig(**config_dict)
            
            # Create via business service
            region = self.business_service.create_single_region(
                name=name,
                biome_type=biome_enum,
                climate_type=climate_enum,
                config=config
            )
            
            # Convert to API response format
            return {
                'id': str(region.id),
                'name': region.name,
                'description': region.description,
                'biome': region.profile.dominant_biome.value,
                'climate': region.profile.climate.value,
                'danger_level': region.danger_level.value,
                'population': region.estimated_population,
                'area_km2': region.area_square_km,
                'coordinates': [
                    {'q': coord.q, 'r': coord.r, 's': coord.s} 
                    for coord in region.hex_coordinates
                ],
                'resources': [
                    {
                        'type': res.resource_type.value,
                        'quantity': res.quantity,
                        'quality': res.quality
                    }
                    for res in region.resource_nodes
                ]
            }
            
        except ValueError as e:
            raise ValueError(f"Region creation failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during region creation: {str(e)}")
    
    async def get_world_by_id(self, world_id: UUID) -> Optional[Dict[str, Any]]:
        """Get world generation record by ID"""
        record = self.business_service.get_world_generation_by_id(world_id)
        if not record:
            return None
        
        return {
            'id': str(record.id),
            'world_name': record.world_name,
            'world_seed': record.world_seed,
            'template_used': record.template_used,
            'region_count': record.region_count,
            'npc_count': record.npc_count,
            'faction_count': record.faction_count,
            'trade_route_count': record.trade_route_count,
            'generation_time': record.generation_time,
            'created_at': record.created_at.isoformat(),
            'simulation_active': record.simulation_active
        }
    
    async def get_world_content(self, world_id: UUID) -> Optional[Dict[str, Any]]:
        """Get complete world content by ID"""
        content = self.business_service.get_world_content(world_id)
        if not content:
            return None
        
        return {
            'world_id': str(world_id),
            'main_continent': {
                'id': str(content.main_continent.id),
                'name': content.main_continent.name,
                'regions': [
                    {
                        'id': str(region.id),
                        'name': region.name,
                        'biome': region.profile.dominant_biome.value
                    }
                    for region in content.main_continent.regions
                ]
            },
            'islands': [
                {
                    'id': str(island.id),
                    'name': island.name,
                    'regions': [
                        {
                            'id': str(region.id),
                            'name': region.name,
                            'biome': region.profile.dominant_biome.value
                        }
                        for region in island.regions
                    ]
                }
                for island in content.islands
            ],
            'regions': content.regions,
            'npcs': content.npcs,
            'factions': content.factions,
            'trade_routes': content.trade_routes
        }
    
    async def list_worlds(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """List world generation records"""
        records = self.business_service.list_world_generations(active_only)
        
        return [
            {
                'id': str(record.id),
                'world_name': record.world_name,
                'region_count': record.region_count,
                'created_at': record.created_at.isoformat(),
                'simulation_active': record.simulation_active
            }
            for record in records
        ]
    
    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available world generation templates"""
        return self.business_service.get_available_templates()
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """Get current generation statistics"""
        return self.business_service.get_generation_statistics()
    
    # Legacy compatibility methods for existing tests
    def generate_world_sync(self, 
                           config: Optional[WorldGenerationConfig] = None,
                           world_name: str = "New World",
                           template_name: Optional[str] = None) -> WorldGenerationResult:
        """Synchronous world generation for backward compatibility"""
        create_data = CreateWorldGenerationData(
            world_name=world_name,
            template_name=template_name,
            config=config
        )
        return self.business_service.generate_world(create_data)
    
    def create_single_region_sync(self, 
                                 name: str,
                                 biome_type=None,
                                 climate_type=None,
                                 hex_coordinates=None,
                                 config=None):
        """Synchronous region creation for backward compatibility"""
        return self.business_service.create_single_region(
            name=name,
            biome_type=biome_type,
            climate_type=climate_type,
            hex_coordinates=hex_coordinates,
            config=config
        )
    
    def get_available_templates_sync(self) -> List[Dict[str, Any]]:
        """Synchronous template listing for backward compatibility"""
        return self.business_service.get_available_templates()


# Factory function for service creation
def create_world_generation_service(db_session=None) -> WorldGenerationService:
    """Factory function to create world generation service"""
    return WorldGenerationService(db_session) 