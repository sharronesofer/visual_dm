"""
Integration example for the deterministic random number generation system.

This module demonstrates how the SeedManager and DeterministicRNG classes
work together to provide deterministic random number generation for world generation.
"""
import sys
import os
import logging
from typing import Dict, List, Any, Tuple

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from python_converted.src.worldgen.core.seed_manager import SeedManager
from python_converted.src.worldgen.core.simple_test import DeterministicRNG, ISeedConfig

# Configure logging
logging.basicConfig(level=logging.INFO, 
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("worldgen.random_integration")

class WorldGenerator:
    """
    Sample world generator to demonstrate deterministic RNG integration.
    
    This class shows how to organize random number generation in a hierarchical manner
    to ensure deterministic results across different runs with the same seed.
    """
    
    def __init__(self, master_seed: int = None):
        """
        Initialize the world generator with a master seed.
        
        Args:
            master_seed (int, optional): The master seed for world generation.
                If None, a random seed will be used.
        """
        self.seed_manager = SeedManager(master_seed=master_seed)
        logger.info(f"WorldGenerator initialized with master seed: {self.seed_manager.get_master_seed().value}")
    
    def generate_world(self, width: int = 100, height: int = 100) -> Dict[str, Any]:
        """
        Generate a sample world with deterministic features.
        
        Args:
            width (int, optional): The width of the world. Defaults to 100.
            height (int, optional): The height of the world. Defaults to 100.
            
        Returns:
            Dict[str, Any]: A dictionary representing the generated world.
        """
        # Derive world seed from master seed
        world_seed = self.seed_manager.derive_seed("world", 
                                                context={"width": width, "height": height})
        world_rng = DeterministicRNG(ISeedConfig(seed=world_seed, name="world"))
        
        logger.info(f"Generating world with seed: {world_seed}")
        
        # Generate various world components using derived seeds
        terrain = self._generate_terrain(width, height)
        biomes = self._generate_biomes(width, height, terrain)
        features = self._generate_features(width, height, terrain, biomes)
        resources = self._generate_resources(width, height, terrain, biomes)
        
        # Construct the world data
        world = {
            "seed": world_seed,
            "width": width,
            "height": height,
            "terrain": terrain,
            "biomes": biomes,
            "features": features,
            "resources": resources,
            "metadata": {
                "seed_history": self.seed_manager.export_seed_history()
            }
        }
        
        logger.info(f"World generation complete. Total features: {len(features)}, Total resources: {len(resources)}")
        
        return world
    
    def _generate_terrain(self, width: int, height: int) -> List[List[float]]:
        """
        Generate terrain height map using deterministic RNG.
        
        Args:
            width (int): The width of the terrain.
            height (int): The height of the terrain.
            
        Returns:
            List[List[float]]: A 2D grid of terrain height values.
        """
        # Derive terrain seed from master seed
        terrain_seed = self.seed_manager.derive_seed("terrain", 
                                                  context={"width": width, "height": height})
        terrain_rng = DeterministicRNG(ISeedConfig(seed=terrain_seed, name="terrain"))
        
        logger.info(f"Generating terrain with seed: {terrain_seed}")
        
        # Create sub-generators for different terrain aspects
        elevation_seed = self.seed_manager.derive_seed("elevation", parent_name="terrain")
        elevation_rng = DeterministicRNG(ISeedConfig(seed=elevation_seed, name="elevation"))
        
        roughness_seed = self.seed_manager.derive_seed("roughness", parent_name="terrain")
        roughness_rng = DeterministicRNG(ISeedConfig(seed=roughness_seed, name="roughness"))
        
        # Generate a heightmap using the elevation RNG
        terrain = []
        for y in range(height):
            row = []
            for x in range(width):
                # Use the RNG to generate a height value
                # In a real implementation, this would use noise functions or other algorithms
                # but we're using simple random values for this example
                base_height = elevation_rng.uniform(0.2, 0.8)
                
                # Add some roughness
                roughness = roughness_rng.uniform(0.0, 0.1)
                
                # Combine base height and roughness
                height_value = base_height + roughness
                row.append(height_value)
            terrain.append(row)
        
        return terrain
    
    def _generate_biomes(self, width: int, height: int, terrain: List[List[float]]) -> List[List[str]]:
        """
        Generate biome map using deterministic RNG and terrain data.
        
        Args:
            width (int): The width of the biome map.
            height (int): The height of the biome map.
            terrain (List[List[float]]): The terrain height map.
            
        Returns:
            List[List[str]]: A 2D grid of biome types.
        """
        # Derive biome seed from master seed
        biome_seed = self.seed_manager.derive_seed("biomes", 
                                                context={"width": width, "height": height})
        biome_rng = DeterministicRNG(ISeedConfig(seed=biome_seed, name="biomes"))
        
        logger.info(f"Generating biomes with seed: {biome_seed}")
        
        # Create sub-generators for different biome aspects
        moisture_seed = self.seed_manager.derive_seed("moisture", parent_name="biomes")
        moisture_rng = DeterministicRNG(ISeedConfig(seed=moisture_seed, name="moisture"))
        
        # Define biome types based on elevation and moisture
        biome_types = ["desert", "plains", "forest", "mountains", "snow"]
        
        # Generate biome map
        biomes = []
        for y in range(height):
            row = []
            for x in range(width):
                # Get terrain height
                elevation = terrain[y][x]
                
                # Generate moisture value for this cell
                moisture = moisture_rng.uniform(0.0, 1.0)
                
                # Determine biome type based on elevation and moisture
                if elevation < 0.3:
                    if moisture < 0.3:
                        biome = "desert"
                    else:
                        biome = "plains"
                elif elevation < 0.6:
                    if moisture < 0.4:
                        biome = "plains"
                    else:
                        biome = "forest"
                else:
                    if moisture < 0.3:
                        biome = "mountains"
                    else:
                        biome = "snow"
                        
                # Add some randomness to biome selection
                if biome_rng.boolean(0.05):  # 5% chance to pick a random biome
                    biome = biome_rng.choice(biome_types)
                    
                row.append(biome)
            biomes.append(row)
            
        return biomes
    
    def _generate_features(self, width: int, height: int, 
                          terrain: List[List[float]], biomes: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Generate world features (e.g., structures, landmarks) using deterministic RNG.
        
        Args:
            width (int): The width of the world.
            height (int): The height of the world.
            terrain (List[List[float]]): The terrain height map.
            biomes (List[List[str]]): The biome map.
            
        Returns:
            List[Dict[str, Any]]: A list of feature objects.
        """
        # Derive feature seed from master seed
        feature_seed = self.seed_manager.derive_seed("features", 
                                                  context={"width": width, "height": height})
        feature_rng = DeterministicRNG(ISeedConfig(seed=feature_seed, name="features"))
        
        logger.info(f"Generating features with seed: {feature_seed}")
        
        # Define feature types and their corresponding biomes
        feature_types = {
            "desert": ["oasis", "pyramid", "ruins"],
            "plains": ["village", "farm", "outpost"],
            "forest": ["cabin", "grove", "ancient_tree"],
            "mountains": ["cave", "mine", "fortress"],
            "snow": ["igloo", "frozen_lake", "ice_castle"]
        }
        
        # Generate features
        features = []
        
        # For each biome type, add a specific number of features
        for biome_type in set([item for sublist in biomes for item in sublist]):
            # Derive a specific seed for each biome's features
            biome_feature_seed = self.seed_manager.derive_seed(
                f"features_{biome_type}", parent_name="features")
            biome_feature_rng = DeterministicRNG(
                ISeedConfig(seed=biome_feature_seed, name=f"features_{biome_type}"))
            
            # Determine how many features to generate for this biome
            count = biome_feature_rng.randint(3, 7)
            
            for _ in range(count):
                # Find a valid location for the feature
                attempts = 0
                while attempts < 20:  # Limit attempts to prevent infinite loops
                    x = biome_feature_rng.randint(0, width - 1)
                    y = biome_feature_rng.randint(0, height - 1)
                    
                    # Check if the location has the correct biome
                    if biomes[y][x] == biome_type:
                        # Choose a feature type appropriate for this biome
                        feature_type = biome_feature_rng.choice(feature_types[biome_type])
                        
                        # Create the feature
                        feature = {
                            "type": feature_type,
                            "x": x,
                            "y": y,
                            "biome": biome_type,
                            "elevation": terrain[y][x],
                            # Generate random properties for the feature
                            "size": biome_feature_rng.uniform(0.5, 2.0),
                            "quality": biome_feature_rng.randint(1, 5)
                        }
                        
                        features.append(feature)
                        break
                    
                    attempts += 1
        
        logger.info(f"Generated {len(features)} features")
        return features
    
    def _generate_resources(self, width: int, height: int, 
                           terrain: List[List[float]], biomes: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Generate world resources using deterministic RNG.
        
        Args:
            width (int): The width of the world.
            height (int): The height of the world.
            terrain (List[List[float]]): The terrain height map.
            biomes (List[List[str]]): The biome map.
            
        Returns:
            List[Dict[str, Any]]: A list of resource objects.
        """
        # Derive resource seed from master seed
        resource_seed = self.seed_manager.derive_seed("resources", 
                                                   context={"width": width, "height": height})
        resource_rng = DeterministicRNG(ISeedConfig(seed=resource_seed, name="resources"))
        
        logger.info(f"Generating resources with seed: {resource_seed}")
        
        # Define resource types and their corresponding biomes
        resource_types = {
            "desert": ["gold", "oil", "silica"],
            "plains": ["wheat", "cattle", "clay"],
            "forest": ["wood", "herbs", "game"],
            "mountains": ["iron", "coal", "stone"],
            "snow": ["crystal", "fur", "ice"]
        }
        
        # Generate resources
        resources = []
        
        # For each biome type, add resources
        for biome_type in set([item for sublist in biomes for item in sublist]):
            # Derive a specific seed for each biome's resources
            biome_resource_seed = self.seed_manager.derive_seed(
                f"resources_{biome_type}", parent_name="resources")
            biome_resource_rng = DeterministicRNG(
                ISeedConfig(seed=biome_resource_seed, name=f"resources_{biome_type}"))
            
            # Determine how many resource nodes to generate for this biome
            count = biome_resource_rng.randint(5, 15)
            
            for _ in range(count):
                # Find a valid location for the resource
                attempts = 0
                while attempts < 20:  # Limit attempts to prevent infinite loops
                    x = biome_resource_rng.randint(0, width - 1)
                    y = biome_resource_rng.randint(0, height - 1)
                    
                    # Check if the location has the correct biome
                    if biomes[y][x] == biome_type:
                        # Choose a resource type appropriate for this biome
                        resource_type = biome_resource_rng.choice(resource_types[biome_type])
                        
                        # Create the resource
                        resource = {
                            "type": resource_type,
                            "x": x,
                            "y": y,
                            "biome": biome_type,
                            "elevation": terrain[y][x],
                            # Generate random properties for the resource
                            "quantity": biome_resource_rng.randint(10, 100),
                            "quality": biome_resource_rng.randint(1, 5)
                        }
                        
                        resources.append(resource)
                        break
                    
                    attempts += 1
        
        logger.info(f"Generated {len(resources)} resources")
        return resources
    
    def load_world(self, world_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load a previously generated world using its seed information.
        
        This demonstrates how to recreate the exact same world using the seed history.
        
        Args:
            world_data (Dict[str, Any]): The world data, including seed history.
            
        Returns:
            Dict[str, Any]: The regenerated world (should be identical).
        """
        if "metadata" not in world_data or "seed_history" not in world_data["metadata"]:
            raise ValueError("World data does not contain seed history")
        
        # Load the seed history
        seed_history = world_data["metadata"]["seed_history"]
        
        # Create a new seed manager with the imported history
        new_seed_manager = SeedManager()
        new_seed_manager.import_seed_history(seed_history)
        
        # Replace our seed manager with the imported one
        original_seed_manager = self.seed_manager
        self.seed_manager = new_seed_manager
        
        # Generate the world with the same dimensions
        width = world_data["width"]
        height = world_data["height"]
        regenerated_world = self.generate_world(width, height)
        
        # Restore the original seed manager
        self.seed_manager = original_seed_manager
        
        return regenerated_world

# Example usage of the integration
def verify_deterministic_generation():
    """
    Verify that the world generation is deterministic by comparing
    two worlds generated with the same seed.
    """
    logger.info("Testing deterministic world generation...")
    
    # Create a world generator with a fixed seed
    seed = 12345
    generator = WorldGenerator(master_seed=seed)
    
    # Generate a world
    logger.info("Generating first world...")
    world1 = generator.generate_world(50, 50)
    
    # Create a new world generator with the same seed
    logger.info("Creating new generator with same seed...")
    generator2 = WorldGenerator(master_seed=seed)
    
    # Generate another world
    logger.info("Generating second world...")
    world2 = generator2.generate_world(50, 50)
    
    # Compare the worlds
    logger.info("Comparing worlds...")
    
    # Check basic properties
    assert world1["seed"] == world2["seed"], "World seeds don't match"
    assert len(world1["features"]) == len(world2["features"]), "Feature counts don't match"
    assert len(world1["resources"]) == len(world2["resources"]), "Resource counts don't match"
    
    # Check that features match
    for f1, f2 in zip(world1["features"], world2["features"]):
        assert f1["type"] == f2["type"], "Feature types don't match"
        assert f1["x"] == f2["x"], "Feature X positions don't match"
        assert f1["y"] == f2["y"], "Feature Y positions don't match"
    
    # Check that resources match
    for r1, r2 in zip(world1["resources"], world2["resources"]):
        assert r1["type"] == r2["type"], "Resource types don't match"
        assert r1["x"] == r2["x"], "Resource X positions don't match"
        assert r1["y"] == r2["y"], "Resource Y positions don't match"
    
    logger.info("Worlds match! Generation is deterministic.")
    
    # Now test loading a world from seed history
    logger.info("Testing world loading from seed history...")
    
    # Load the world using its seed history
    loaded_world = generator.load_world(world1)
    
    # Compare the original and loaded worlds
    logger.info("Comparing original and loaded worlds...")
    
    # Check basic properties
    assert world1["seed"] == loaded_world["seed"], "Loaded world seed doesn't match"
    assert len(world1["features"]) == len(loaded_world["features"]), "Loaded feature counts don't match"
    assert len(world1["resources"]) == len(loaded_world["resources"]), "Loaded resource counts don't match"
    
    # Check that features match
    for f1, f2 in zip(world1["features"], loaded_world["features"]):
        assert f1["type"] == f2["type"], "Loaded feature types don't match"
        assert f1["x"] == f2["x"], "Loaded feature X positions don't match"
        assert f1["y"] == f2["y"], "Loaded feature Y positions don't match"
    
    # Check that resources match
    for r1, r2 in zip(world1["resources"], loaded_world["resources"]):
        assert r1["type"] == r2["type"], "Loaded resource types don't match"
        assert r1["x"] == r2["x"], "Loaded resource X positions don't match"
        assert r1["y"] == r2["y"], "Loaded resource Y positions don't match"
    
    logger.info("Loaded world matches original! Seed history works correctly.")
    
    return True

if __name__ == "__main__":
    # Run the verification
    try:
        verify_deterministic_generation()
        print("All tests passed! The deterministic RNG system is working correctly.")
    except AssertionError as e:
        print(f"Test failed: {e}")
        raise 