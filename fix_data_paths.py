#!/usr/bin/env python3
"""
Fix data paths in the game data registry to point to the correct data directory.
"""

import os
import shutil

def fix_data_paths():
    """Fix data path references and ensure proper data structure."""
    
    # Check if the biomes directory exists in the correct location
    data_dir = "data"
    biomes_dir = os.path.join(data_dir, "biomes")
    
    if not os.path.exists(biomes_dir):
        print(f"❌ Biomes directory not found at {biomes_dir}")
        return False
    
    # Check for required files
    land_types_file = os.path.join(biomes_dir, "land_types.json")
    adjacency_file = os.path.join(biomes_dir, "adjacency.json")
    
    print(f"✅ Checking data files:")
    print(f"  - {land_types_file}: {'EXISTS' if os.path.exists(land_types_file) else 'MISSING'}")
    print(f"  - {adjacency_file}: {'EXISTS' if os.path.exists(adjacency_file) else 'MISSING'}")
    
    # Check data directory structure relative to backend/systems/data/loaders/
    expected_path = os.path.join("backend", "systems", "data", "loaders", "..", "..", "..", "data")
    resolved_path = os.path.abspath(expected_path)
    
    print(f"✅ Data directory paths:")
    print(f"  - Expected: {expected_path}")
    print(f"  - Resolved: {resolved_path}")
    print(f"  - Exists: {os.path.exists(resolved_path)}")
    
    # Check if the races.json file has proper structure for the failing test
    races_file = os.path.join(data_dir, "races.json")
    if os.path.exists(races_file):
        import json
        try:
            with open(races_file, 'r') as f:
                races_data = json.load(f)
            
            print(f"✅ Races file structure:")
            print(f"  - Keys: {list(races_data.keys())}")
            
            # Check if it needs a 'data' wrapper
            if 'data' not in races_data and 'human' in races_data:
                print("  - Needs 'data' wrapper")
                # Create backup
                backup_file = races_file + ".backup"
                shutil.copy2(races_file, backup_file)
                print(f"  - Created backup: {backup_file}")
                
                # Wrap in data structure
                wrapped_data = {
                    "metadata": {
                        "version": "1.0",
                        "last_modified": "2025-01-29"
                    },
                    "data": races_data
                }
                
                with open(races_file, 'w') as f:
                    json.dump(wrapped_data, f, indent=2)
                
                print("  - Fixed races.json structure")
            else:
                print("  - Structure OK")
        except Exception as e:
            print(f"  - Error reading races.json: {e}")
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing data paths...")
    success = fix_data_paths()
    if success:
        print("✅ Data paths check complete")
    else:
        print("❌ Data paths check failed") 