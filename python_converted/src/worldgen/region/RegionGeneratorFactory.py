"""
RegionGeneratorFactory - Factory for creating region generators

This module provides the RegionGeneratorFactory class responsible for creating,
registering, and managing different types of region generators.
"""
from typing import Dict, List, Optional, Any
import logging

from python_converted.src.worldgen.core.IWorldGenerator import (
    IRegionGenerator, GeneratorType, RegionGeneratorOptions,
    Region, GenerationResult
)
from python_converted.src.worldgen.region.ProceduralRegionGenerator import ProceduralRegionGenerator
from python_converted.src.worldgen.region.HandcraftedRegionGenerator import (
    HandcraftedRegionGenerator, HandcraftedRegionGeneratorOptions
)

# Create logger
logger = logging.getLogger("worldgen.factory")

class GeneratorRegistry:
    """
    Registry for holding and providing access to generator instances.
    
    This class allows registering generators by name and type, and
    providing controlled access to the registered generators.
    
    Attributes:
        generators (Dict[str, IRegionGenerator]): Dictionary of registered generators
    """
    
    def __init__(self):
        """Initialize the generator registry."""
        self.generators: Dict[str, IRegionGenerator] = {}
    
    def register(self, name: str, generator: IRegionGenerator) -> bool:
        """
        Register a generator with the registry.
        
        Args:
            name (str): The name to register the generator under
            generator (IRegionGenerator): The generator instance
            
        Returns:
            bool: True if successful, False if the name is already in use
        """
        if name in self.generators:
            logger.warning(f"Generator with name '{name}' already exists")
            return False
        
        self.generators[name] = generator
        logger.info(f"Registered generator '{name}' of type {generator.get_type().value}")
        return True
    
    def get(self, name: str) -> Optional[IRegionGenerator]:
        """
        Get a generator by name.
        
        Args:
            name (str): The name of the generator to retrieve
            
        Returns:
            Optional[IRegionGenerator]: The generator instance, or None if not found
        """
        return self.generators.get(name)
    
    def get_all(self) -> Dict[str, IRegionGenerator]:
        """
        Get all registered generators.
        
        Returns:
            Dict[str, IRegionGenerator]: Dictionary of all registered generators
        """
        return self.generators
    
    def get_names(self) -> List[str]:
        """
        Get the names of all registered generators.
        
        Returns:
            List[str]: List of generator names
        """
        return list(self.generators.keys())

class RegionGeneratorFactory:
    """
    Factory for creating and managing region generators.
    
    This class provides facilities for creating, registering, and accessing
    different types of region generators. It manages a registry of generators
    and provides convenience methods for creating regions with different
    generator types.
    
    Attributes:
        registry (GeneratorRegistry): The registry of generators
    """
    
    def __init__(self):
        """Initialize the region generator factory."""
        self.registry = GeneratorRegistry()
        
        # Register the built-in generators
        self._register_built_in_generators()
    
    def _register_built_in_generators(self):
        """Register the built-in generator types."""
        # Register the procedural generator
        self.registry.register('procedural', ProceduralRegionGenerator())
        
        # Register the handcrafted generator
        self.registry.register('handcrafted', HandcraftedRegionGenerator())
    
    def get_generator(self, name: str) -> Optional[IRegionGenerator]:
        """
        Get a generator by name.
        
        Args:
            name (str): The name of the generator to retrieve
            
        Returns:
            Optional[IRegionGenerator]: The generator instance, or None if not found
        """
        return self.registry.get(name)
    
    def get_generator_by_type(self, generator_type: GeneratorType) -> Optional[IRegionGenerator]:
        """
        Get a generator by type.
        
        This method returns the first generator found with the specified type.
        
        Args:
            generator_type (GeneratorType): The type of generator to retrieve
            
        Returns:
            Optional[IRegionGenerator]: The generator instance, or None if not found
        """
        for generator in self.registry.get_all().values():
            if generator.get_type() == generator_type:
                return generator
        
        return None
    
    def register_generator(self, name: str, generator: IRegionGenerator) -> bool:
        """
        Register a generator with the factory.
        
        Args:
            name (str): The name to register the generator under
            generator (IRegionGenerator): The generator instance
            
        Returns:
            bool: True if successful, False if the name is already in use
        """
        return self.registry.register(name, generator)
    
    def get_generators(self) -> Dict[str, IRegionGenerator]:
        """
        Get all registered generators.
        
        Returns:
            Dict[str, IRegionGenerator]: Dictionary of all registered generators
        """
        return self.registry.get_all()
    
    def get_generator_names(self) -> List[str]:
        """
        Get the names of all registered generators.
        
        Returns:
            List[str]: List of generator names
        """
        return self.registry.get_names()
    
    def create_procedural_region(self, options: RegionGeneratorOptions) -> GenerationResult:
        """
        Create a region using the procedural generator.
        
        Args:
            options (RegionGeneratorOptions): The generation options
            
        Returns:
            GenerationResult: The generation result
            
        Raises:
            ValueError: If the procedural generator is not registered
        """
        generator = self.get_generator('procedural')
        if not generator:
            raise ValueError("Procedural generator not registered")
        
        return generator.generate(options)
    
    def create_handcrafted_region(self, options: HandcraftedRegionGeneratorOptions) -> GenerationResult:
        """
        Create a region using the handcrafted generator.
        
        Args:
            options (HandcraftedRegionGeneratorOptions): The generation options
            
        Returns:
            GenerationResult: The generation result
            
        Raises:
            ValueError: If the handcrafted generator is not registered
        """
        generator = self.get_generator('handcrafted')
        if not generator:
            raise ValueError("Handcrafted generator not registered")
        
        return generator.generate(options)
    
    # Singleton pattern for the factory
    _default_instance = None
    
    @staticmethod
    def get_default_instance() -> 'RegionGeneratorFactory':
        """
        Get the default factory instance.
        
        Returns:
            RegionGeneratorFactory: The default factory instance
        """
        if RegionGeneratorFactory._default_instance is None:
            RegionGeneratorFactory._default_instance = RegionGeneratorFactory()
        
        return RegionGeneratorFactory._default_instance 