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
    cmd = f"find backend -name '*.py' -type f -exec grep -l 'from {folder} import\\|import {folder}\\.' {{}} \\; | head -1"
    result = run_command(cmd)
    
    if result:
        print(f"✅ '{folder}' is used in: {result}")
        return True
    else:
        print(f"❌ '{folder}' does not appear to be imported anywhere")
        return False

# First batch of folders to check
BATCH1 = [
    "AIBackend", "arc", "asset_generation", "code_quality", "component-audit", 
    "combat", "factions", "game", "hexmap", "item"
]

unused_folders = []

for folder in sorted(BATCH1):
    print(f"Checking: {folder}")
    if not check_folder_usage(folder):
        unused_folders.append(folder)

print("\n---------------------------")
print(f"Found {len(unused_folders)} unused folders in batch 1:")
for folder in unused_folders:
    print(f"- backend/{folder}")
    
# Save to file
with open("unused_batch1.txt", "w") as f:
    for folder in unused_folders:
        f.write(f"{folder}\n")

print("\nList of unused folders saved to unused_batch1.txt") 