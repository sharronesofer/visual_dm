"""
World Generation Models

Data models and repository interfaces for the world generation system.
"""

from typing import Protocol, Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from backend.systems.region.models import RegionMetadata, ContinentMetadata


@dataclass
class WorldGenerationConfig:
    """Configuration for world generation - business data model"""
    # World sizing - continent-focused
    main_continent_size: tuple[int, int] = (80, 120)  # Number of regions
    island_count: int = 3  # Additional smaller landmasses
    island_size_range: tuple[int, int] = (5, 15)  # Regions per island
    
    # Geographic diversity
    biome_diversity: float = 0.8  # How many different biomes to include
    climate_variation: float = 0.7  # How much climate varies across the world
    elevation_complexity: float = 0.6  # How complex the terrain should be
    
    # Resource and content distribution
    resource_abundance: float = 0.5  # Overall resource richness
    poi_density: float = 0.8  # Points of interest per region
    settlement_density: float = 0.3  # Starting settlements per region
    
    # Gameplay balance
    danger_progression: tuple[float, float, float] = (0.6, 0.3, 0.1)  # safe, moderate, dangerous
    resource_clustering: float = 0.7  # How much resources cluster together
    travel_connectivity: float = 0.8  # How well-connected regions are
    
    # Full generation options
    generate_full_world: bool = True  # If True, generates NPCs, factions, economy
    world_seed: Optional[int] = None  # Specific world seed
    region_size: int = 64  # Size of individual regions for terrain generation
    
    # NPC Generation
    npc_density: float = 0.5  # NPCs per settlement
    faction_density: float = 0.2  # Factions per region
    starting_factions: int = 8  # Number of starting factions
    
    # Economy Generation
    trade_route_density: float = 0.4  # Trade routes between settlements
    market_variance: float = 0.3  # Price variation between markets
    economic_complexity: float = 0.5  # How complex the economy should be


@dataclass
class CreateWorldGenerationData:
    """Data for creating a new world generation request"""
    world_name: str
    template_name: Optional[str] = None
    config: Optional[WorldGenerationConfig] = None
    user_id: Optional[UUID] = None


@dataclass
class WorldGenerationRecord:
    """Persistent record of a world generation session."""
    id: UUID
    world_name: str
    world_seed: int
    template_used: Optional[str]
    generation_config: Dict[str, Any]
    generation_stats: Dict[str, Any]
    generation_time: float
    created_at: datetime
    
    # Generated content references
    main_continent_id: UUID
    island_ids: List[UUID]
    region_count: int
    npc_count: int
    faction_count: int
    trade_route_count: int
    
    # Simulation state
    simulation_active: bool = False
    last_simulation_tick: Optional[datetime] = None


@dataclass
class GeneratedWorldData:
    """Complete world data with all generated content."""
    record: WorldGenerationRecord
    main_continent: ContinentMetadata
    islands: List[ContinentMetadata]
    regions: List[Dict[str, Any]]
    npcs: List[Dict[str, Any]]
    factions: List[Dict[str, Any]]
    trade_routes: List[Dict[str, Any]]


@dataclass
class WorldGenerationResult:
    """Result of world generation process - business result"""
    main_continent: ContinentMetadata
    islands: List[ContinentMetadata]
    all_regions: List[RegionMetadata]
    regions: List[Dict[str, Any]]  # Simplified region data for API
    npcs: List[Dict[str, Any]]  # Generated NPCs
    factions: List[Dict[str, Any]]  # Generated factions
    trade_routes: List[Dict[str, Any]]  # Generated trade routes
    generation_stats: Dict[str, Any]
    generation_time: float
    seed_used: int
    config_used: WorldGenerationConfig


# Repository Protocols (dependency injection interfaces)
class WorldGenerationRepository(Protocol):
    """Repository interface for world generation data persistence."""
    
    def save_world_generation(self, record: WorldGenerationRecord) -> WorldGenerationRecord:
        """Save a world generation record."""
        ...
    
    def get_world_generation(self, world_id: UUID) -> Optional[WorldGenerationRecord]:
        """Get a world generation record by ID."""
        ...
    
    def get_world_generation_by_name(self, world_name: str) -> Optional[WorldGenerationRecord]:
        """Get a world generation record by name."""
        ...
    
    def list_world_generations(self, active_only: bool = False) -> List[WorldGenerationRecord]:
        """List all world generation records."""
        ...
    
    def update_simulation_state(self, world_id: UUID, active: bool, last_tick: Optional[datetime] = None) -> bool:
        """Update the simulation state for a world."""
        ...
    
    def delete_world_generation(self, world_id: UUID) -> bool:
        """Delete a world generation record and all associated data."""
        ...


class WorldContentRepository(Protocol):
    """Repository interface for generated world content (NPCs, factions, etc.)."""
    
    def save_world_content(self, world_id: UUID, content_data: GeneratedWorldData) -> bool:
        """Save all generated world content."""
        ...
    
    def get_world_content(self, world_id: UUID) -> Optional[GeneratedWorldData]:
        """Get all world content for a world."""
        ...
    
    def get_world_npcs(self, world_id: UUID, region_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Get NPCs for a world, optionally filtered by region."""
        ...
    
    def get_world_factions(self, world_id: UUID) -> List[Dict[str, Any]]:
        """Get factions for a world."""
        ...
    
    def get_world_trade_routes(self, world_id: UUID) -> List[Dict[str, Any]]:
        """Get trade routes for a world."""
        ...
    
    def update_npc(self, world_id: UUID, npc_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update an NPC's data."""
        ...
    
    def update_faction(self, world_id: UUID, faction_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update a faction's data."""
        ...


class WorldGenerationConfigService(Protocol):
    """Protocol for world generation configuration services"""
    
    def get_biome_configuration(self, biome_type: str) -> Dict[str, Any]:
        """Get biome configuration data"""
        ...
    
    def get_world_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get world template configuration"""
        ...
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available world templates"""
        ...
    
    def validate_generation_config(self, config: WorldGenerationConfig) -> Dict[str, Any]:
        """Validate and process generation configuration"""
        ...
    
    def get_biome_placement_rules(self) -> Dict[str, Any]:
        """Get biome placement and adjacency rules"""
        ...
    
    def get_population_parameters(self) -> Dict[str, Any]:
        """Get population generation parameters"""
        ...


class WorldGenerationValidationService(Protocol):
    """Protocol for world generation validation"""
    
    def validate_world_generation_data(self, world_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate world generation data"""
        ...
    
    def validate_region_constraints(self, regions: List[RegionMetadata]) -> bool:
        """Validate that generated regions meet constraints"""
        ...
    
    def validate_biome_adjacency(self, biome_map: Dict[Any, str]) -> bool:
        """Validate biome adjacency rules"""
        ...


# Mock implementations for testing
class InMemoryWorldGenerationRepository:
    """In-memory implementation of WorldGenerationRepository for testing."""
    
    def __init__(self):
        self._records: Dict[UUID, WorldGenerationRecord] = {}
    
    def save_world_generation(self, record: WorldGenerationRecord) -> WorldGenerationRecord:
        self._records[record.id] = record
        return record
    
    def get_world_generation(self, world_id: UUID) -> Optional[WorldGenerationRecord]:
        return self._records.get(world_id)
    
    def get_world_generation_by_name(self, world_name: str) -> Optional[WorldGenerationRecord]:
        for record in self._records.values():
            if record.world_name == world_name:
                return record
        return None
    
    def list_world_generations(self, active_only: bool = False) -> List[WorldGenerationRecord]:
        records = list(self._records.values())
        if active_only:
            records = [r for r in records if r.simulation_active]
        return records
    
    def update_simulation_state(self, world_id: UUID, active: bool, last_tick: Optional[datetime] = None) -> bool:
        if world_id in self._records:
            self._records[world_id].simulation_active = active
            self._records[world_id].last_simulation_tick = last_tick
            return True
        return False
    
    def delete_world_generation(self, world_id: UUID) -> bool:
        if world_id in self._records:
            del self._records[world_id]
            return True
        return False


class InMemoryWorldContentRepository:
    """In-memory implementation of WorldContentRepository for testing."""
    
    def __init__(self):
        self._content: Dict[UUID, GeneratedWorldData] = {}
    
    def save_world_content(self, world_id: UUID, content_data: GeneratedWorldData) -> bool:
        self._content[world_id] = content_data
        return True
    
    def get_world_content(self, world_id: UUID) -> Optional[GeneratedWorldData]:
        return self._content.get(world_id)
    
    def get_world_npcs(self, world_id: UUID, region_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        content = self._content.get(world_id)
        if not content:
            return []
        
        npcs = content.npcs
        if region_id:
            npcs = [npc for npc in npcs if npc.get('region_id') == str(region_id)]
        
        return npcs
    
    def get_world_factions(self, world_id: UUID) -> List[Dict[str, Any]]:
        content = self._content.get(world_id)
        return content.factions if content else []
    
    def get_world_trade_routes(self, world_id: UUID) -> List[Dict[str, Any]]:
        content = self._content.get(world_id)
        return content.trade_routes if content else []
    
    def update_npc(self, world_id: UUID, npc_id: UUID, updates: Dict[str, Any]) -> bool:
        content = self._content.get(world_id)
        if not content:
            return False
        
        for npc in content.npcs:
            if npc.get('id') == str(npc_id):
                npc.update(updates)
                return True
        return False
    
    def update_faction(self, world_id: UUID, faction_id: UUID, updates: Dict[str, Any]) -> bool:
        content = self._content.get(world_id)
        if not content:
            return False
        
        for faction in content.factions:
            if faction.get('id') == str(faction_id):
                faction.update(updates)
                return True
        return False 