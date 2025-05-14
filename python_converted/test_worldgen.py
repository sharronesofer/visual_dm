#!/usr/bin/env python3
"""
Test script for the World Generation System Python implementation.
This script verifies that the basic functionality of the converted code works.
"""

import sys
import time
import os
from typing import Dict, Any

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Test core components directly
    from src.worldgen.core.DeterministicRNG import DeterministicRNG, ISeedConfig
    
    # Test a basic RNG generation
    seed_config = ISeedConfig(seed=12345, name="test_seed")
    rng = DeterministicRNG(seed_config)
    
    print("=== World Generation System Python Tests ===")
    print("Testing DeterministicRNG...")
    
    # Generate some random numbers
    numbers = [rng.random() for _ in range(5)]
    print(f"- Generated random numbers: {numbers}")
    
    # Reset and verify determinism
    rng.reset()
    numbers2 = [rng.random() for _ in range(5)]
    print(f"- After reset: {numbers2}")
    
    if numbers == numbers2:
        print("✓ RNG is deterministic")
    else:
        print("✗ RNG is NOT deterministic")
    
    print("\nTests completed successfully")
    
except ImportError as e:
    print(f"Error importing worldgen module: {e}")
    print("Make sure the conversion was successful and the module structure is correct.")
    sys.exit(1)
except Exception as e:
    print(f"Test failed: {e}")
    sys.exit(1) 