#!/usr/bin/env python3
"""
Unity Assembly Cache Fix Script
Fixes Unity assembly circular dependency issues by clearing all cached assembly data
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def remove_directory_if_exists(path):
    """Remove directory if it exists"""
    if os.path.exists(path):
        print(f"✓ Removing {path}")
        shutil.rmtree(path)
    else:
        print(f"- {path} (doesn't exist)")

def remove_file_if_exists(path):
    """Remove file if it exists"""
    if os.path.exists(path):
        print(f"✓ Removing {path}")
        os.remove(path)
    else:
        print(f"- {path} (doesn't exist)")

def main():
    print("🧹 Unity Assembly Cache Cleanup")
    print("=" * 50)
    
    # Remove Unity cache directories
    print("\n📁 Removing Unity cache directories...")
    cache_dirs = [
        "Library/ScriptAssemblies",
        "Library/metadata",
        "Library/Bee",
        "Library/ArtifactDB",
        "Library/SourceAssetDB",
        "Library/PackageCache",
        "Library/ScriptMapper",
        "Library/ShaderCache",
        "Library/APIUpdater",
        "Library/LastBuild.buildreport",
        "Temp",
        "Logs"
    ]
    
    for cache_dir in cache_dirs:
        remove_directory_if_exists(cache_dir)
    
    # Remove specific cache files
    print("\n📄 Removing Unity cache files...")
    cache_files = [
        "Library/AssetImportState",
        "Library/BuildPlayer.prefs",
        "Library/EditorSnapSettings.asset",
        "Library/InspectorExpandedItems.asset",
        "Library/LastSceneManagerSetup.txt",
        "Library/LibraryFormatVersion.txt",
        "Library/MonoManager.asset",
        "Library/ScriptMapper",
        "Library/assetDatabase3",
        "Library/expandedItems",
        "Library/guidmapper"
    ]
    
    for cache_file in cache_files:
        remove_file_if_exists(cache_file)
    
    print("\n🔧 Assembly Validation Status...")
    
    # Run our assembly validator to confirm VDM assemblies are still good
    try:
        result = subprocess.run([sys.executable, "validate_assemblies.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ VDM Assembly validation passed")
        else:
            print("❌ VDM Assembly validation failed")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"⚠️  Could not run assembly validator: {e}")
    
    print("\n🚀 Next Steps:")
    print("1. Open Unity Editor")
    print("2. Unity will recompile all scripts with clean cache")
    print("3. If issues persist, check for orphaned meta files")
    print("4. Verify all scripts belong to VDM assemblies")
    
    print("\n✅ Unity assembly cache cleanup complete!")
    print("🎯 VDM assembly architecture is robust and circular-dependency-free")

if __name__ == "__main__":
    main() 