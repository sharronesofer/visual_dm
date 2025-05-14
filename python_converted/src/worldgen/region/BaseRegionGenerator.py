"""
BaseRegionGenerator - Abstract base class for region generators

This module provides the BaseRegionGenerator abstract class that serves as
a foundation for both procedural and hand-crafted region generators in the
WorldGen system.
"""
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from python_converted.src.worldgen.core.IWorldGenerator import (
    IRegionGenerator, GeneratorType, Region,
    RegionGeneratorOptions, GenerationResult
)
from python_converted.src.worldgen.core.simple_test import DeterministicRNG, ISeedConfig
from python_converted.src.worldgen.core.seed_manager import SeedManager

class BaseRegionGenerator(ABC, IRegionGenerator):
    """
    Abstract base class for region generators in the WorldGen system.
    
    This class provides common functionality for all region generators, including
    deterministic random number generation, debug information generation,
    and basic region structure setup. Both procedural and hand-crafted generators
    should inherit from this class.
    
    Attributes:
        seed_manager (SeedManager): The seed manager for deterministic RNG
    """
    
    def __init__(self):
        """Initialize the base region generator"""
        self.seed_manager = SeedManager()
        
    def generate(self, options: RegionGeneratorOptions) -> GenerationResult:
        """
        Generate a region based on the provided options.
        
        This method handles the common generation flow for all region types,
        including timing, RNG setup, and error handling. Specific generation
        logic is delegated to the abstract generateRegion method.
        
        Args:
            options (RegionGeneratorOptions): Options for region generation
            
        Returns:
            GenerationResult: The generated region or error information
        """
        start_time = time.time()
        
        try:
            # Ensure we have a valid seed
            seed_config = self._ensure_seed_config(options)
            
            # Create a deterministic RNG for this region
            rng = DeterministicRNG(seed_config)
            
            # Generate the region using the implementation-specific method
            region = self._generate_region(options, rng)
            
            # Add debug information if needed
            debug_info = self._generate_debug_info(options, rng)
            if debug_info:
                region.metadata["debug"] = debug_info
                
            # Calculate generation time
            generation_time = time.time() - start_time
            
            # Create the result object
            result = GenerationResult(
                region=region,
                success=True,
                generation_time=generation_time
            )
            
            # Add seed information to the metadata
            result.metadata["seed"] = options.seed
            result.metadata["generation_type"] = self.get_type().value
            
            return result
            
        except Exception as e:
            # Handle any errors during generation
            generation_time = time.time() - start_time
            
            # Create an error result
            result = GenerationResult(
                region=self._create_empty_region(options),
                success=False,
                error=str(e),
                generation_time=generation_time
            )
            
            return result
    
    def _ensure_seed_config(self, options: RegionGeneratorOptions) -> ISeedConfig:
        """
        Ensure we have a valid seed configuration for deterministic generation.
        
        Args:
            options (RegionGeneratorOptions): The generation options
            
        Returns:
            ISeedConfig: A valid seed configuration
        """
        # Use the provided seed or generate a new one
        seed_value = options.seed if options.seed != 0 else int(time.time() * 1000)
        
        # Register the seed with the manager
        region_seed_name = f"region_{options.region_type or 'generic'}"
        
        # If the master seed isn't set, use this seed as the master
        if not hasattr(self.seed_manager, '_master_seed_name'):
            self.seed_manager = SeedManager(master_seed=seed_value)
            seed_value = self.seed_manager.derive_seed(region_seed_name, context={
                "width": options.width,
                "height": options.height,
                "region_type": options.region_type
            })
        else:
            # Derive a new seed for this specific region
            seed_value = self.seed_manager.derive_seed(region_seed_name, context={
                "width": options.width,
                "height": options.height,
                "region_type": options.region_type
            })
        
        return ISeedConfig(seed=seed_value, name=region_seed_name)
    
    def _generate_debug_info(self, options: RegionGeneratorOptions, 
                            rng: DeterministicRNG) -> Dict[str, Any]:
        """
        Generate debug information for the region.
        
        Args:
            options (RegionGeneratorOptions): The generation options
            rng (DeterministicRNG): The random number generator
            
        Returns:
            Dict[str, Any]: Debug information
        """
        # By default, just include basic information
        debug_info = {
            "generator_type": self.get_type().value,
            "width": options.width,
            "height": options.height,
            "seed": options.seed,
            "region_type": options.region_type or "generic"
        }
        
        # Add any additional parameters
        for key, value in options.additional_params.items():
            debug_info[key] = value
        
        return debug_info
    
    def _create_empty_region(self, options: RegionGeneratorOptions) -> Region:
        """
        Create an empty region structure, used when generation fails.
        
        Args:
            options (RegionGeneratorOptions): The generation options
            
        Returns:
            Region: An empty region structure
        """
        region_id = f"error_{int(time.time())}"
        return Region(
            id=region_id,
            name=f"Error Region {region_id}",
            width=options.width,
            height=options.height
        )
    
    def _generate_region_id(self, options: RegionGeneratorOptions, 
                           rng: DeterministicRNG) -> str:
        """
        Generate a unique ID for the region.
        
        Args:
            options (RegionGeneratorOptions): The generation options
            rng (DeterministicRNG): The random number generator
            
        Returns:
            str: A unique region ID
        """
        # Generate a deterministic ID based on the seed and options
        prefix = options.region_type or "region"
        random_part = str(abs(hash(str(options.seed))))[-6:]
        return f"{prefix}_{random_part}"
    
    def _generate_region_name(self, options: RegionGeneratorOptions, 
                             rng: DeterministicRNG) -> str:
        """
        Generate a name for the region.
        
        Args:
            options (RegionGeneratorOptions): The generation options
            rng (DeterministicRNG): The random number generator
            
        Returns:
            str: A region name
        """
        # By default, use a simple naming scheme
        # Subclasses can override for more sophisticated naming
        prefix = options.region_type.capitalize() if options.region_type else "Region"
        random_part = str(abs(hash(str(options.seed))))[-4:]
        
        return f"{prefix} {random_part}"
    
    @abstractmethod
    def _generate_region(self, options: RegionGeneratorOptions, 
                        rng: DeterministicRNG) -> Region:
        """
        Generate the region content.
        
        This abstract method must be implemented by all subclasses to provide
        specific region generation logic.
        
        Args:
            options (RegionGeneratorOptions): The generation options
            rng (DeterministicRNG): The random number generator
            
        Returns:
            Region: The generated region
        """
        pass
    
    @abstractmethod
    def get_type(self) -> GeneratorType:
        """
        Get the type of this generator.
        
        Returns:
            GeneratorType: The generator type (PROCEDURAL, HANDCRAFTED)
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this generator.
        
        Returns:
            Dict[str, Any]: A dictionary of capabilities
        """
        pass 