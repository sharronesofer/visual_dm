#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(cmd):
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def check_folder_usage(folder):
    """Check if a folder is being imported anywhere in the codebase."""
    cmd = f"find backend -name '*.py' -type f -exec grep -l 'from {folder} import\\|import {folder}\\.' {{}} \\; | head -5"
    result = run_command(cmd)
    
    if result:
        print(f"✅ '{folder}' is used in at least these files:")
        for line in result.splitlines():
            print(f"   - {line}")
        return True
    else:
        print(f"❌ '{folder}' does not appear to be imported anywhere")
        return False

# Folders we suspect might be unused
SUSPECT_FOLDERS = [
    "AIBackend", "arc", "asset_generation", "code_quality", "component-audit", 
    "combat", "factions", "game", "hexmap", "item", "load-tests", "loot", 
    "main", "models", "motifs", "npcs", "pois", "python_converted", "python_demo", 
    "regions", "screens", "search", "social", "ts_analysis", "ts_conversion", 
    "visuals", "websocket", "world"
]

unused_folders = []

for folder in sorted(SUSPECT_FOLDERS):
    print(f"\nChecking: {folder}")
    if not check_folder_usage(folder):
        unused_folders.append(folder)

print("\n---------------------------")
print(f"Found {len(unused_folders)} unused folders out of {len(SUSPECT_FOLDERS)} checked:")
for folder in unused_folders:
    print(f"- backend/{folder}")
    
# Save to file
with open("unused_folders.txt", "w") as f:
    for folder in unused_folders:
        f.write(f"{folder}\n")

print("\nList of unused folders saved to unused_folders.txt") 