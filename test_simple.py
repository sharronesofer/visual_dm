#!/usr/bin/env python3
"""
Simple test script to test diplomacy models directly
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Try to import the models directly
try:
    # Import directly from the file without going through package __init__.py
    import importlib.util
    
    # Load the core_models module directly
    spec = importlib.util.spec_from_file_location(
        "core_models", 
        "backend/systems/diplomacy/models/core_models.py"
    )
    core_models = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core_models)
    
    # Test the enum
    print("DiplomaticStatus values:")
    for status in core_models.DiplomaticStatus:
        print(f"  {status.name} = {status.value}")
    
    print("\nTest passed: Models can be imported directly")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 