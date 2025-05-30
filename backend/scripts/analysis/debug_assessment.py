#!/usr/bin/env python3
"""Debug script to check path detection"""

from pathlib import Path

def debug_paths():
    print(f"Current working directory: {Path.cwd()}")
    
    backend_path = Path(".")
    systems_path = backend_path / "systems"
    
    print(f"Backend path: {backend_path.absolute()}")
    print(f"Systems path: {systems_path.absolute()}")
    print(f"Systems path exists: {systems_path.exists()}")
    
    if systems_path.exists():
        system_dirs = [d for d in systems_path.iterdir() 
                      if d.is_dir() and not d.name.startswith('__')]
        print(f"Found {len(system_dirs)} system directories:")
        for d in sorted(system_dirs):
            print(f"  - {d.name}")
    else:
        print("Systems path does not exist!")

if __name__ == "__main__":
    debug_paths() 