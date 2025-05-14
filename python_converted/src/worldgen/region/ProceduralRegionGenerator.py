"""
ProceduralRegionGenerator - Procedural terrain generation implementation

This module provides the ProceduralRegionGenerator class responsible for
generating regions using procedural algorithms.
"""
from typing import Dict, List, Any, Tuple, Optional
import math
import time

from python_converted.src.worldgen.core.IWorldGenerator import (
    IProceduralRegionGenerator, GeneratorType, Region, Cell,
    RegionGeneratorOptions, PointOfInterest, Resource
)
from python_converted.src.worldgen.core.simple_test import DeterministicRNG
from python_converted.src.worldgen.region.BaseRegionGenerator import BaseRegionGenerator

class ProceduralRegionGenerator(BaseRegionGenerator, IProceduralRegionGenerator):
    """
    Procedural region generator that creates terrain using algorithms.
    
    This generator creates regions using procedural generation techniques for
    terrain, biomes, resources, and points of interest without relying on
    pre-defined templates.
    
    Attributes:
        terrain_params (Dict[str, Any]): Parameters for terrain generation
        resource_params (Dict[str, Any]): Parameters for resource generation
        poi_params (Dict[str, Any]): Parameters for point of interest generation
    """
    
    def __init__(self):
        """Initialize the procedural region generator with default parameters"""
        super().__init__()
        
        # Default parameters for the different generation aspects
        self.terrain_params: Dict[str, Any] = {
            "scale": 20.0,
            "octaves": 4,
            "persistence": 0.5,
            "lacunarity": 2.0,
            "height_multiplier": 1.0,
            "water_level": 0.3
        }
        
        self.resource_params: Dict[str, Any] = {
            "density": 0.05,
            "clustering": 0.7,
            "variety": 0.8
        }
        
        self.poi_params: Dict[str, Any] = {
            "density": 0.02,
            "min_separation": 5,
            "variety": 0.7
        }
    
    def get_type(self) -> GeneratorType:
        """Get the type of this generator"""
        return GeneratorType.PROCEDURAL
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this generator"""
        return {
            "variable_terrain": True,
            "complex_biomes": True,
            "customizable_params": True,
            "supports_custom_size": True,
            "resource_generation": True,
            "poi_generation": True
        }
    
    def set_terrain_parameters(self, params: Dict[str, Any]) -> None:
        """
        Set parameters for terrain generation.
        
        Args:
            params (Dict[str, Any]): Parameters for terrain generation
        """
        # Update terrain parameters with new values, keeping defaults for any not specified
        self.terrain_params.update(params)
    
    def set_resource_parameters(self, params: Dict[str, Any]) -> None:
        """
        Set parameters for resource generation.
        
        Args:
            params (Dict[str, Any]): Parameters for resource generation
        """
        # Update resource parameters with new values, keeping defaults for any not specified
        self.resource_params.update(params)
    
    def set_poi_parameters(self, params: Dict[str, Any]) -> None:
        """
        Set parameters for point of interest generation.
        
        Args:
            params (Dict[str, Any]): Parameters for POI generation
        """
        # Update POI parameters with new values, keeping defaults for any not specified
        self.poi_params.update(params)
    
    def _generate_region(self, options: RegionGeneratorOptions, 
                        rng: DeterministicRNG) -> Region:
        """
        Generate a region using procedural algorithms.
        
        Args:
            options (RegionGeneratorOptions): The generation options
            rng (DeterministicRNG): The random number generator
            
        Returns:
            Region: The generated region
        """
        # Create the base region object
        region = Region(
            id=self._generate_region_id(options, rng),
            name=self._generate_region_name(options, rng),
            width=options.width,
            height=options.height
        )
        
        # Apply any modifications based on options
        terrain_complexity = options.terrain_complexity
        resource_abundance = options.resource_abundance
        poi_density = options.poi_density
        
        # Apply option-specific modifiers
        if options.is_coastal:
            self.terrain_params["water_level"] = 0.4
        if options.is_mountainous:
            self.terrain_params["height_multiplier"] = 1.5
        if options.is_arid:
            # Adjust for arid regions
            pass
        
        # Generate terrain with derived seed for deterministic generation
        terrain_rng = self._derive_child_rng(rng, "terrain")
        region.cells = self._generate_terrain_grid(
            options.width, options.height, 
            terrain_complexity, terrain_rng
        )
        
        # Generate resources with derived seed
        resource_rng = self._derive_child_rng(rng, "resources")
        region.resources = self._generate_resources(
            region, resource_abundance, resource_rng
        )
        
        # Generate points of interest with derived seed
        poi_rng = self._derive_child_rng(rng, "poi")
        region.points_of_interest = self._generate_points_of_interest(
            region, poi_density, poi_rng
        )
        
        # Add generation metadata
        region.metadata = {
            "generator": "procedural",
            "generation_time": time.time(),
            "seed": options.seed,
            "terrain_complexity": terrain_complexity,
            "resource_abundance": resource_abundance,
            "poi_density": poi_density
        }
        
        return region
    
    def _derive_child_rng(self, parent_rng: DeterministicRNG, purpose: str) -> DeterministicRNG:
        """
        Create a derived RNG for a specific purpose.
        
        Args:
            parent_rng (DeterministicRNG): The parent RNG
            purpose (str): The purpose of this RNG (e.g., 'terrain', 'resources')
            
        Returns:
            DeterministicRNG: A new deterministic RNG
        """
        if hasattr(parent_rng, 'create_child'):
            # If the RNG supports child derivation directly
            return parent_rng.create_child(purpose)
        else:
            # Otherwise, derive a new seed and create a new RNG
            seed_value = self.seed_manager.derive_seed(
                f"{purpose}_seed", 
                parent_name=parent_rng.config.name
            )
            return DeterministicRNG({
                "seed": seed_value,
                "name": f"{parent_rng.config.name}_{purpose}"
            })
    
    def _generate_terrain_grid(self, width: int, height: int, 
                              complexity: float, rng: DeterministicRNG) -> List[Cell]:
        """
        Generate the terrain grid for the region.
        
        Args:
            width (int): The width of the region
            height (int): The height of the region
            complexity (float): The terrain complexity factor (0.0-1.0)
            rng (DeterministicRNG): The random number generator
            
        Returns:
            List[Cell]: The list of cells in the region
        """
        cells = []
        
        # Adjust parameters based on complexity
        octaves = max(1, int(self.terrain_params["octaves"] * complexity))
        scale = self.terrain_params["scale"] * (1.0 + complexity)
        
        # Generate heightmap using simplex noise approximation
        # (In a real implementation, we'd use a proper noise library)
        for y in range(height):
            for x in range(width):
                # Generate height using multiple RNG calls as a simple noise approximation
                elevation = 0
                amplitude = 1.0
                frequency = 1.0
                max_value = 0
                
                for i in range(octaves):
                    # Sample noise at different scales
                    nx = x / scale * frequency
                    ny = y / scale * frequency
                    
                    # Simple hash for deterministic "noise"
                    sample = rng.normal(0, 1, hash=f"{nx}_{ny}_{i}")
                    sample = (sample + 1) / 2  # Normalize to 0-1
                    
                    elevation += sample * amplitude
                    max_value += amplitude
                    
                    amplitude *= self.terrain_params["persistence"]
                    frequency *= self.terrain_params["lacunarity"]
                
                # Normalize elevation
                elevation /= max_value
                elevation *= self.terrain_params["height_multiplier"]
                
                # Determine terrain type based on elevation
                terrain_type = self._determine_terrain_type(elevation)
                
                # Generate moisture with a different hash
                moisture = rng.uniform(0, 1, hash=f"moisture_{x}_{y}")
                
                # Generate temperature with a different hash
                # Temperature tends to decrease with elevation
                base_temp = rng.uniform(0, 1, hash=f"temp_{x}_{y}")
                temperature = base_temp * (1.0 - elevation * 0.5)
                
                # Determine biome based on elevation, moisture, and temperature
                biome = self._determine_biome(elevation, moisture, temperature)
                
                # Create the cell
                cell = Cell(
                    x=x, 
                    y=y, 
                    terrain_type=terrain_type,
                    elevation=elevation,
                    moisture=moisture,
                    temperature=temperature,
                    biome=biome
                )
                
                cells.append(cell)
        
        return cells
    
    def _determine_terrain_type(self, elevation: float) -> str:
        """
        Determine the terrain type based on elevation.
        
        Args:
            elevation (float): The elevation value (0.0-1.0)
            
        Returns:
            str: The terrain type
        """
        water_level = self.terrain_params["water_level"]
        
        if elevation < water_level - 0.05:
            return "deep_water"
        elif elevation < water_level:
            return "shallow_water"
        elif elevation < water_level + 0.05:
            return "beach"
        elif elevation < 0.5:
            return "plains"
        elif elevation < 0.7:
            return "hills"
        elif elevation < 0.85:
            return "mountains"
        else:
            return "peaks"
    
    def _determine_biome(self, elevation: float, moisture: float, temperature: float) -> str:
        """
        Determine the biome based on elevation, moisture, and temperature.
        
        Args:
            elevation (float): The elevation value (0.0-1.0)
            moisture (float): The moisture value (0.0-1.0)
            temperature (float): The temperature value (0.0-1.0)
            
        Returns:
            str: The biome type
        """
        water_level = self.terrain_params["water_level"]
        
        # Underwater biomes
        if elevation < water_level:
            if temperature < 0.3:
                return "cold_ocean"
            elif temperature > 0.7:
                return "warm_ocean"
            else:
                return "ocean"
        
        # Land biomes
        if elevation < 0.5:  # Lowlands
            if moisture < 0.2:
                if temperature > 0.7:
                    return "desert"
                else:
                    return "barren"
            elif moisture < 0.5:
                if temperature < 0.3:
                    return "tundra"
                elif temperature < 0.7:
                    return "grassland"
                else:
                    return "savanna"
            else:
                if temperature < 0.3:
                    return "taiga"
                elif temperature < 0.7:
                    return "forest"
                else:
                    return "rainforest"
        elif elevation < 0.7:  # Hills
            if moisture < 0.3:
                return "rocky_hills"
            elif temperature < 0.4:
                return "coniferous_hills"
            else:
                return "forested_hills"
        else:  # Mountains
            if temperature < 0.2:
                return "snow_peaks"
            elif moisture < 0.3:
                return "dry_mountains"
            else:
                return "alpine"
    
    def _generate_resources(self, region: Region, abundance: float, 
                           rng: DeterministicRNG) -> List[Resource]:
        """
        Generate resources for the region.
        
        Args:
            region (Region): The region to generate resources for
            abundance (float): The resource abundance factor (0.0-1.0)
            rng (DeterministicRNG): The random number generator
            
        Returns:
            List[Resource]: The list of resources
        """
        resources = []
        
        # Define possible resource types by biome
        resource_types_by_biome = {
            "desert": ["gold", "silica", "salt"],
            "barren": ["stone", "iron", "copper"],
            "tundra": ["ice", "crystal", "silver"],
            "grassland": ["herbs", "cattle", "clay"],
            "savanna": ["exotic_herbs", "wildlife", "wood"],
            "taiga": ["fur", "wood", "crystal"],
            "forest": ["wood", "herbs", "game"],
            "rainforest": ["exotic_wood", "exotic_herbs", "wildlife"],
            "rocky_hills": ["stone", "coal", "iron"],
            "coniferous_hills": ["wood", "fur", "copper"],
            "forested_hills": ["wood", "herbs", "iron"],
            "snow_peaks": ["crystal", "silver", "precious_gems"],
            "dry_mountains": ["gold", "iron", "coal"],
            "alpine": ["herbs", "crystal", "precious_gems"],
            "ocean": ["fish", "pearls", "coral"],
            "warm_ocean": ["exotic_fish", "coral", "pearls"],
            "cold_ocean": ["fish", "ice"]
        }
        
        # Calculate number of resources based on abundance and region size
        base_count = int(region.width * region.height * self.resource_params["density"])
        resource_count = max(1, int(base_count * abundance))
        
        # Resource generation
        for _ in range(resource_count):
            # Try to find a valid location
            for attempt in range(10):  # Limit attempts to avoid infinite loops
                # Pick a random cell
                cell_index = rng.randint(0, len(region.cells) - 1)
                cell = region.cells[cell_index]
                
                # Skip water cells
                if "water" in cell.terrain_type or "ocean" in cell.biome:
                    continue
                
                # Get applicable resource types for this biome
                applicable_types = resource_types_by_biome.get(cell.biome, ["generic"])
                
                # Pick a resource type
                resource_type = rng.choice(applicable_types)
                
                # Determine quantity based on abundance and some randomness
                quantity = rng.uniform(10, 100) * abundance
                
                # Determine quality (1-5 stars)
                quality = rng.randint(1, 5)
                
                # Create and add the resource
                resource = Resource(
                    resource_type=resource_type,
                    x=cell.x,
                    y=cell.y,
                    quantity=quantity,
                    quality=quality
                )
                
                resources.append(resource)
                break
        
        return resources
    
    def _generate_points_of_interest(self, region: Region, density: float, 
                                    rng: DeterministicRNG) -> List[PointOfInterest]:
        """
        Generate points of interest for the region.
        
        Args:
            region (Region): The region to generate POIs for
            density (float): The POI density factor (0.0-1.0)
            rng (DeterministicRNG): The random number generator
            
        Returns:
            List[PointOfInterest]: The list of points of interest
        """
        pois = []
        
        # Define possible POI types by biome
        poi_types_by_biome = {
            "desert": ["oasis", "ancient_ruins", "tomb"],
            "barren": ["outpost", "cave", "abandoned_mine"],
            "tundra": ["igloo", "frozen_cave", "research_station"],
            "grassland": ["village", "farm", "shrine"],
            "savanna": ["tribal_village", "hunting_grounds", "monument"],
            "taiga": ["cabin", "hunter_camp", "sacred_grove"],
            "forest": ["woodcutter_camp", "elven_outpost", "ancient_tree"],
            "rainforest": ["temple", "tribal_village", "waterfall"],
            "rocky_hills": ["outpost", "mine", "hermit_cave"],
            "forested_hills": ["watchtower", "druid_circle", "ranger_outpost"],
            "snow_peaks": ["mountaintop_shrine", "dragon_lair", "frozen_castle"],
            "dry_mountains": ["fortress", "mine", "monastery"],
            "alpine": ["chapel", "hot_springs", "wizard_tower"],
            "ocean": ["shipwreck", "coral_formation", "mysterious_island"],
            "warm_ocean": ["pirate_cove", "tropical_island", "trading_post"],
            "cold_ocean": ["ice_floe", "research_vessel", "kraken_lair"]
        }
        
        # Calculate number of POIs based on density and region size
        base_count = int(region.width * region.height * self.poi_params["density"])
        poi_count = max(1, int(base_count * density))
        
        # POI name generators (simplified for example)
        name_prefixes = [
            "Ancient", "Forgotten", "Sacred", "Hidden", "Mysterious", 
            "Abandoned", "Enchanted", "Cursed", "Blessed", "Ruined",
            "Sunken", "Frozen", "Burning", "Whispering", "Towering"
        ]
        
        name_suffixes = {
            "ruins": ["Ruins", "Remnants", "Remains", "Rubble", "Wreckage"],
            "village": ["Village", "Settlement", "Hamlet", "Enclave", "Community"],
            "cave": ["Cave", "Cavern", "Grotto", "Hollow", "Den"],
            "tower": ["Tower", "Spire", "Belfry", "Watchtower", "Minaret"],
            "temple": ["Temple", "Shrine", "Sanctuary", "Chapel", "Cathedral"],
            "forest": ["Forest", "Woods", "Grove", "Thicket", "Woodland"],
            "mountain": ["Mountain", "Peak", "Summit", "Crag", "Bluff"],
            "default": ["Place", "Location", "Site", "Spot", "Area"]
        }
        
        # Track occupied positions to maintain minimum separation
        occupied_positions = set()
        
        # POI generation
        for _ in range(poi_count):
            # Try to find a valid location with minimum separation
            for attempt in range(20):  # Limit attempts to avoid infinite loops
                # Pick a random cell
                cell_index = rng.randint(0, len(region.cells) - 1)
                cell = region.cells[cell_index]
                
                # Skip water cells (unless the POI is water-specific)
                if ("water" in cell.terrain_type or "ocean" in cell.biome) and \
                   cell.biome not in ["ocean", "warm_ocean", "cold_ocean"]:
                    continue
                
                # Check minimum separation
                min_separation = self.poi_params["min_separation"]
                too_close = False
                
                for pos in occupied_positions:
                    dx = pos[0] - cell.x
                    dy = pos[1] - cell.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < min_separation:
                        too_close = True
                        break
                
                if too_close:
                    continue
                
                # Get applicable POI types for this biome
                applicable_types = poi_types_by_biome.get(cell.biome, ["landmark"])
                
                # Pick a POI type
                poi_type = rng.choice(applicable_types)
                
                # Generate a name
                prefix = rng.choice(name_prefixes)
                
                # Choose appropriate suffix category
                suffix_category = "default"
                for key in name_suffixes:
                    if key in poi_type:
                        suffix_category = key
                        break
                
                suffix = rng.choice(name_suffixes[suffix_category])
                name = f"{prefix} {suffix}"
                
                # Create a description
                descriptions = [
                    f"A {poi_type} of unknown origin.",
                    f"A {poi_type} shrouded in mystery.",
                    f"An ancient {poi_type} from a forgotten era.",
                    f"A recently discovered {poi_type}.",
                    f"A notorious {poi_type} known in local legends."
                ]
                description = rng.choice(descriptions)
                
                # Create and add the POI
                poi = PointOfInterest(
                    x=cell.x,
                    y=cell.y,
                    poi_type=poi_type,
                    name=name,
                    description=description
                )
                
                # Add some custom attributes
                poi.attributes = {
                    "discovery_status": rng.choice(["unexplored", "partially_explored", "well_known"]),
                    "danger_level": rng.randint(1, 5),
                    "treasure_value": rng.randint(1, 5)
                }
                
                pois.append(poi)
                
                # Mark position as occupied
                occupied_positions.add((cell.x, cell.y))
                break
        
        return pois 