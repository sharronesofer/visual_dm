import warnings
import sys

# Configure warnings to show all details
warnings.filterwarnings('always')

# Capture the warnings
with warnings.catch_warnings(record=True) as caught_warnings:
    # Import the modules that might generate warnings
    from backend.systems.auth_user.services import *
    from backend.systems.auth_user.services.auth_service import *
    from backend.systems.inventory.models import *
    
    # Print the captured warnings
    print(f"Captured {len(caught_warnings)} warnings:")
    for i, warning in enumerate(caught_warnings):
        print(f"\nWarning {i+1}:")
        print(f"  Category: {warning.category.__name__}")
        print(f"  Message: {warning.message}")
        print(f"  File: {warning.filename}")
        print(f"  Line: {warning.lineno}") 