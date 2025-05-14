"""
Seed Management Module for WorldGen

This module provides a SeedManager class for managing random number seeds
in a hierarchical deterministic manner, ensuring reproducible results
across different world generation runs.
"""
import hashlib
from typing import Dict, List, Optional, Union, Any
import logging
from dataclasses import dataclass
import json
import time

# Setup logger
logger = logging.getLogger("worldgen.seed_manager")

@dataclass
class SeedInfo:
    """
    Information about a seed and its usage context.
    
    Attributes:
        value (int): The actual seed value
        name (str): A descriptive name for the seed
        parent_name (Optional[str]): Name of the parent seed (if derived)
        timestamp (float): When the seed was created/used
        context (Dict[str, Any]): Additional context information
    """
    value: int
    name: str
    parent_name: Optional[str] = None
    timestamp: float = 0.0
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values after initialization"""
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if self.context is None:
            self.context = {}

class SeedManager:
    """
    Manages seeds for deterministic random number generation.
    
    The SeedManager provides a central service for creating, tracking, and deriving
    seeds in a hierarchical manner. This ensures consistent, reproducible random
    number generation throughout the world generation pipeline.
    
    Key features:
    - Master seed management for entire world generation
    - Hierarchical seed derivation with consistent algorithms
    - Seed history tracking for debugging and reproducibility
    - Named seeds for better organization and traceability
    - Logging of seed usage and relationships
    
    Usage example:
        # Initialize with a master seed
        seed_manager = SeedManager(master_seed=12345)
        
        # Get the master seed (returns a SeedInfo object)
        master_info = seed_manager.get_master_seed()
        
        # Create a derived seed for terrain generation
        terrain_seed = seed_manager.derive_seed("terrain_generation")
        
        # Create a further derived seed for mountain generation
        mountain_seed = seed_manager.derive_seed("mountain_generation", parent_name="terrain_generation")
        
        # Explicitly register an external seed
        seed_manager.register_seed(54321, "custom_feature", parent_name="terrain_generation")
        
        # Export seed history for reproducibility
        history = seed_manager.export_seed_history()
    """
    
    def __init__(self, master_seed: Optional[int] = None):
        """
        Initialize a new SeedManager.
        
        Args:
            master_seed (Optional[int]): The master seed value to use.
                If None, a random seed will be generated.
        """
        self._seeds: Dict[str, SeedInfo] = {}
        self._seed_heritage: Dict[str, List[str]] = {}  # Maps parent names to child names
        
        # If no master seed is provided, generate one
        if master_seed is None:
            import random
            master_seed = random.randint(1, 2**31 - 1)
        
        # Register the master seed
        self._master_seed_name = "master"
        self.register_seed(master_seed, self._master_seed_name)
        
        logger.info(f"SeedManager initialized with master seed: {master_seed}")
    
    def get_master_seed(self) -> SeedInfo:
        """
        Get information about the master seed.
        
        Returns:
            SeedInfo: Information about the master seed.
        """
        return self._seeds[self._master_seed_name]
    
    def register_seed(self, seed_value: int, name: str, parent_name: Optional[str] = None, 
                      context: Optional[Dict[str, Any]] = None) -> SeedInfo:
        """
        Register a new seed with the manager.
        
        This method allows explicitly registering a known seed value, which is useful
        for integrating external seeds or pre-defined seeds into the tracking system.
        
        Args:
            seed_value (int): The seed value to register.
            name (str): A unique name for this seed.
            parent_name (Optional[str]): The name of the parent seed, if any.
            context (Optional[Dict[str, Any]]): Additional context information.
                
        Returns:
            SeedInfo: Information about the registered seed.
                
        Raises:
            ValueError: If a seed with the given name already exists.
        """
        if name in self._seeds:
            raise ValueError(f"Seed with name '{name}' already exists.")
        
        # Create the seed info
        seed_info = SeedInfo(
            value=seed_value,
            name=name,
            parent_name=parent_name,
            context=context or {}
        )
        
        # Register the seed
        self._seeds[name] = seed_info
        
        # Update heritage tracking
        if parent_name:
            if parent_name not in self._seed_heritage:
                self._seed_heritage[parent_name] = []
            self._seed_heritage[parent_name].append(name)
        
        logger.debug(f"Registered seed: {name} = {seed_value}" + 
                    (f" (derived from {parent_name})" if parent_name else ""))
        
        return seed_info
    
    def derive_seed(self, name: str, parent_name: Optional[str] = None,
                   context: Optional[Dict[str, Any]] = None) -> int:
        """
        Derive a new seed from a parent seed.
        
        This method creates a new deterministic seed derived from a parent seed,
        ensuring the same relationship between parent and child seeds across
        different runs.
        
        Args:
            name (str): Name for the derived seed.
            parent_name (Optional[str]): Name of the parent seed to derive from.
                If None, derives from the master seed.
            context (Optional[Dict[str, Any]]): Additional context information.
                
        Returns:
            int: The derived seed value.
                
        Raises:
            ValueError: If the parent seed doesn't exist.
            ValueError: If a seed with the given name already exists.
        """
        if name in self._seeds:
            raise ValueError(f"Seed with name '{name}' already exists.")
        
        # Default to master seed if no parent specified
        if parent_name is None:
            parent_name = self._master_seed_name
        
        # Verify parent exists
        if parent_name not in self._seeds:
            raise ValueError(f"Parent seed '{parent_name}' does not exist.")
        
        parent_info = self._seeds[parent_name]
        parent_seed = parent_info.value
        
        # Derive the new seed using a deterministic algorithm
        # We use a hash-based approach for good distribution and minimal collisions
        derived_seed = self._derive_seed_value(parent_seed, name)
        
        # Register the derived seed
        seed_info = self.register_seed(
            derived_seed,
            name,
            parent_name=parent_name,
            context=context
        )
        
        return derived_seed
    
    def _derive_seed_value(self, parent_seed: int, name: str) -> int:
        """
        Internal method to derive a seed value from a parent seed.
        
        Uses a hash-based approach to ensure good distribution and minimal collisions.
        
        Args:
            parent_seed (int): The parent seed value.
            name (str): The name for the new seed.
            
        Returns:
            int: The derived seed value.
        """
        # Create a string combining the parent seed and name
        combined = f"{parent_seed}:{name}"
        
        # Use SHA-256 to hash the combined string
        hash_obj = hashlib.sha256(combined.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert the first 8 bytes of the hash to an integer
        # We use only positive values to ensure compatibility
        derived_value = int(hash_hex[:16], 16) % (2**31 - 1)
        
        return derived_value
    
    def get_seed(self, name: str) -> int:
        """
        Get a seed value by name.
        
        Args:
            name (str): The name of the seed to retrieve.
            
        Returns:
            int: The seed value.
            
        Raises:
            KeyError: If no seed with the given name exists.
        """
        if name not in self._seeds:
            raise KeyError(f"No seed with name '{name}' exists.")
        
        return self._seeds[name].value
    
    def get_seed_info(self, name: str) -> SeedInfo:
        """
        Get detailed information about a seed.
        
        Args:
            name (str): The name of the seed to retrieve.
            
        Returns:
            SeedInfo: Information about the seed.
            
        Raises:
            KeyError: If no seed with the given name exists.
        """
        if name not in self._seeds:
            raise KeyError(f"No seed with name '{name}' exists.")
        
        return self._seeds[name]
    
    def get_child_seeds(self, parent_name: str) -> List[str]:
        """
        Get the names of all seeds derived from a given parent.
        
        Args:
            parent_name (str): The name of the parent seed.
            
        Returns:
            List[str]: List of child seed names.
        """
        return self._seed_heritage.get(parent_name, [])
    
    def export_seed_history(self) -> Dict[str, Any]:
        """
        Export the complete seed history for reproducibility.
        
        This method exports all seed information in a format suitable for
        saving and later reproduction of the exact same world generation.
        
        Returns:
            Dict[str, Any]: A serializable dictionary of seed history.
        """
        result = {
            "master_seed": self.get_master_seed().value,
            "seeds": {}
        }
        
        # Convert seed info objects to serializable dictionaries
        for name, info in self._seeds.items():
            result["seeds"][name] = {
                "value": info.value,
                "parent": info.parent_name,
                "timestamp": info.timestamp,
                "context": info.context
            }
        
        return result
    
    def import_seed_history(self, history: Dict[str, Any]) -> None:
        """
        Import a previously exported seed history.
        
        This allows recreating the exact same sequence of seeds used in
        a previous world generation run.
        
        Args:
            history (Dict[str, Any]): The seed history to import.
            
        Raises:
            ValueError: If the seed history format is invalid.
        """
        if "master_seed" not in history or "seeds" not in history:
            raise ValueError("Invalid seed history format")
        
        # Clear existing seeds and heritage
        self._seeds = {}
        self._seed_heritage = {}
        
        # Register the master seed first
        master_seed = history["master_seed"]
        self.register_seed(master_seed, self._master_seed_name)
        
        # Register all other seeds
        seeds = history["seeds"]
        
        # First pass: register seeds without parents (except master which is already registered)
        for name, info in seeds.items():
            if name != self._master_seed_name and info["parent"] is None:
                self.register_seed(
                    info["value"],
                    name,
                    context=info.get("context", {})
                )
        
        # Second pass: register seeds with parents
        # We may need multiple passes if seeds have ancestors other than the master seed
        remaining = {name: info for name, info in seeds.items() 
                    if name != self._master_seed_name and info["parent"] is not None}
        
        while remaining:
            registered_count = 0
            
            for name, info in list(remaining.items()):
                parent = info["parent"]
                if parent in self._seeds:
                    # Parent exists, so we can register this seed
                    self.register_seed(
                        info["value"],
                        name,
                        parent_name=parent,
                        context=info.get("context", {})
                    )
                    del remaining[name]
                    registered_count += 1
            
            # If we didn't register any seeds in this pass, we have a circular dependency
            if registered_count == 0 and remaining:
                raise ValueError("Circular dependency detected in seed history")
        
        logger.info(f"Imported seed history with {len(self._seeds)} seeds")
    
    def log_all_seeds(self, level: int = logging.INFO) -> None:
        """
        Log all registered seeds for debugging purposes.
        
        Args:
            level (int): The logging level to use.
        """
        logger.log(level, f"---- Seed Manager: {len(self._seeds)} seeds ----")
        logger.log(level, f"Master seed: {self.get_master_seed().value} ({self._master_seed_name})")
        
        # Log all seeds, organized by parentage
        # Start with seeds that have no parent (except master)
        orphans = [name for name, info in self._seeds.items() 
                  if name != self._master_seed_name and info.parent_name is None]
        
        for name in orphans:
            self._log_seed_and_children(name, "", level)
        
        # Log children of master seed
        for name in self.get_child_seeds(self._master_seed_name):
            self._log_seed_and_children(name, "", level)
    
    def _log_seed_and_children(self, name: str, prefix: str, level: int) -> None:
        """
        Recursively log a seed and its children.
        
        Args:
            name (str): The seed name to log.
            prefix (str): Prefix for hierarchical display.
            level (int): The logging level to use.
        """
        info = self._seeds[name]
        parent = f" (from {info.parent_name})" if info.parent_name else ""
        
        logger.log(level, f"{prefix}├── {name}: {info.value}{parent}")
        
        # Log children with increased indentation
        children = self.get_child_seeds(name)
        for child in children:
            self._log_seed_and_children(child, prefix + "│   ", level) 