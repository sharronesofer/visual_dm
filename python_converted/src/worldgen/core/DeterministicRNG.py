#!/usr/bin/env python3
"""
DeterministicRNG.py - Deterministic random number generator implementation

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, TypeVar, Callable
import math
import sys
import math
import random
from abc import ABC, abstractmethod
import math
from .IWorldGenerator import IRandomGenerator

T = TypeVar('T')

class ISeedConfig:
    """Interface for seed configuration"""
    def __init__(self, seed: int, name: str = None, parent: 'ISeedConfig' = None):
        self.seed = seed
        self.name = name
        self.parent = parent

class IRandomGenerator:
    """Interface for random number generators"""
    def random(self) -> float:
        """Get a random number between 0 and 1"""
        pass
        
    def random_int(self, min_val: int, max_val: int) -> int:
        """Get a random integer between min (inclusive) and max (inclusive)"""
        pass
        
    def random_element(self, array: List[T]) -> T:
        """Get a random element from an array"""
        pass
        
    def random_weighted_element(self, elements: List[T], weights: List[float]) -> T:
        """Get a random weighted element from an array with weights"""
        pass
        
    def create_child(self, name: str) -> 'IRandomGenerator':
        """Create a child random generator with a derived seed"""
        pass
        
    def get_state(self) -> Dict:
        """Get the current state of the RNG (for debugging/logging)"""
        pass
        
    def reset(self) -> None:
        """Reset the RNG to its initial state"""
        pass

class DeterministicRNG(IRandomGenerator):
    """
    Implementation of a deterministic random number generator
    This uses a xorshift algorithm to ensure consistent results across platforms
    """
    
    def __init__(self, seed_config: ISeedConfig):
        """
        Create a new deterministic random number generator
        
        Args:
            seed_config: The seed configuration
        """
        self.seed_config = seed_config
        self.state = self.init_state(seed_config.seed)
        self.initial_state = self.state
    
    def init_state(self, seed: int) -> int:
        """
        Initialize the state from a seed value
        
        Args:
            seed: The seed value
            
        Returns:
            The initial state
        """
        return abs(seed) if seed != 0 else 1
    
    def next(self) -> int:
        """
        Implements the xorshift algorithm for random number generation
        This provides better statistical properties than naive PRNGs
        
        Returns:
            A random integer
        """
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x
        return x
    
    def get_seed_config(self) -> ISeedConfig:
        """
        Get the seed configuration
        
        Returns:
            The seed configuration
        """
        return self.seed_config
    
    def random(self) -> float:
        """
        Get a random number between 0 and 1
        
        Returns:
            A random number in [0, 1)
        """
        return abs(self.next()) / 0x7FFFFFFF
    
    def random_int(self, min_val: int, max_val: int) -> int:
        """
        Get a random integer between min (inclusive) and max (inclusive)
        
        Args:
            min_val: The minimum value (inclusive)
            max_val: The maximum value (inclusive)
            
        Returns:
            A random integer in [min, max]
        """
        return math.floor(self.random() * (max_val - min_val + 1)) + min_val
    
    def random_element(self, array: List[T]) -> T:
        """
        Get a random element from an array
        
        Args:
            array: The array to select from
            
        Returns:
            A random element
            
        Raises:
            ValueError: If the array is empty
        """
        if len(array) == 0:
            raise ValueError('Cannot select from an empty array')
        return array[self.randomInt(0, len(array) - 1)]
    
    def random_weighted_element(self, elements: List[T], weights: List[float]) -> T:
        """
        Get a random weighted element from an array with weights
        
        Args:
            elements: The elements array
            weights: The corresponding weights
            
        Returns:
            A randomly selected element based on weights
            
        Raises:
            ValueError: If the arrays are empty or have different lengths
        """
        if len(elements) == 0:
            raise ValueError('Cannot select from an empty array')
        if len(elements) != len(weights):
            raise ValueError('Elements and weights arrays must have the same length')
        
        total_weight = sum(weights)
        random_value = self.random() * total_weight
        
        for i in range(len(elements)):
            random_value -= weights[i]
            if random_value <= 0:
                return elements[i]
        
        return elements[-1]
    
    def create_child(self, name: str) -> 'DeterministicRNG':
        """
        Create a child random generator with a derived seed
        
        Args:
            name: The name for the child generator
            
        Returns:
            A new random generator with a derived seed
        """
        child_seed = self.seed_config.seed
        
        for char in name:
            child_seed = (child_seed * 31 + ord(char)) & 0xFFFFFFFF
        
        child_seed_config = ISeedConfig(
            seed=child_seed,
            name=name,
            parent=self.seed_config
        )
        
        return DeterministicRNG(child_seed_config)
    
    def get_state(self) -> Dict:
        """
        Get the current state of the RNG (for debugging/logging)
        
        Returns:
            The current state
        """
        return {
            'state': self.state,
            'initial_state': self.initial_state,
            'seed_config': {
                'seed': self.seed_config.seed,
                'name': self.seed_config.name
            }
        }
    
    def reset(self) -> None:
        """
        Reset the RNG to its initial state
        """
        self.state = self.initial_state 