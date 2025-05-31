#!/usr/bin/env python3
"""
Unity Safe Mode Fix Script
Addresses the critical errors causing Unity to open in safe mode.
"""

import os
import shutil
import json
import glob
import sys
from pathlib import Path
import argparse

def create_backup(project_path, backup_suffix="_backup_unity_fix"):
    """Create a backup of the Unity project before making changes."""
    project_name = os.path.basename(project_path)
    backup_path = f"{project_path}{backup_suffix}"
    
    if os.path.exists(backup_path):
        print(f"⚠️  Backup already exists at {backup_path}")
        response = input("Overwrite existing backup? (y/N): ")
        if response.lower() != 'y':
            print("❌ Backup cancelled. Exiting.")
            return None
        shutil.rmtree(backup_path)
    
    print(f"📦 Creating backup at {backup_path}...")
    shutil.copytree(project_path, backup_path, 
                   ignore=shutil.ignore_patterns('Library', 'Temp', 'Logs', 'obj'))
    print(f"✅ Backup created successfully!")
    return backup_path

def fix_package_dependencies(project_path):
    """Fix package dependency issues."""
    print("\n🔧 Fixing package dependencies...")
    
    # Remove lock file to force re-resolution
    lock_file = os.path.join(project_path, "Packages", "packages-lock.json")
    if os.path.exists(lock_file):
        os.remove(lock_file)
        print("✅ Removed packages-lock.json")
    
    # Update manifest.json
    manifest_path = os.path.join(project_path, "Packages", "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Update Mirror to latest stable version
        if "com.mirror-networking.mirror" in manifest["dependencies"]:
            manifest["dependencies"]["com.mirror-networking.mirror"] = "96.6.4"
            print("✅ Updated Mirror Networking to version 96.6.4")
        
        # Ensure proper scoped registries
        if "scopedRegistries" not in manifest:
            manifest["scopedRegistries"] = []
        
        # Update or add OpenUPM registry
        openupm_registry = {
            "name": "package.openupm.com",
            "url": "https://package.openupm.com",
            "scopes": ["com.endel", "com.mirror-networking"]
        }
        
        # Remove existing OpenUPM registry and add updated one
        manifest["scopedRegistries"] = [reg for reg in manifest["scopedRegistries"] 
                                      if reg.get("name") != "package.openupm.com"]
        manifest["scopedRegistries"].append(openupm_registry)
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print("✅ Updated package manifest")

def fix_dto_files(project_path):
    """Fix DTO files that are missing DataAnnotations namespace."""
    print("\n🔧 Fixing DTO files...")
    
    dto_files = glob.glob(os.path.join(project_path, "Assets", "Scripts", "DTOs", "**", "*.cs"), recursive=True)
    
    for dto_file in dto_files:
        try:
            with open(dto_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file uses DataAnnotations
            if "using System.ComponentModel.DataAnnotations;" in content:
                # Replace with conditional compilation
                new_content = content.replace(
                    "using System.ComponentModel.DataAnnotations;",
                    "#if UNITY_EDITOR || UNITY_STANDALONE\nusing System.ComponentModel.DataAnnotations;\n#endif"
                )
                
                # Also wrap attribute usage
                attributes_to_wrap = [
                    "Required", "StringLength", "Range", "EmailAddress", 
                    "Url", "MinimumLength", "MaximumLength"
                ]
                
                for attr in attributes_to_wrap:
                    # Wrap attribute declarations
                    new_content = new_content.replace(
                        f"[{attr}",
                        f"#if UNITY_EDITOR || UNITY_STANDALONE\n    [{attr}"
                    )
                    new_content = new_content.replace(
                        f"    [{attr}Attribute",
                        f"#if UNITY_EDITOR || UNITY_STANDALONE\n    [{attr}Attribute"
                    )
                
                with open(dto_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Fixed {os.path.relpath(dto_file, project_path)}")
        except Exception as e:
            print(f"⚠️  Error fixing {dto_file}: {e}")

def fix_json_attributes(project_path):
    """Fix JsonPropertyName attribute accessibility issues."""
    print("\n🔧 Fixing JSON attribute issues...")
    
    cs_files = glob.glob(os.path.join(project_path, "Assets", "Scripts", "**", "*.cs"), recursive=True)
    
    for cs_file in cs_files:
        try:
            with open(cs_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "JsonPropertyName" in content:
                # Add proper using directive if missing
                if "using System.Text.Json.Serialization;" not in content:
                    content = "using System.Text.Json.Serialization;\n" + content
                
                # Ensure JsonPropertyNameAttribute is correctly referenced
                content = content.replace(
                    "[JsonPropertyName(",
                    "[JsonPropertyNameAttribute("
                )
                
                with open(cs_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed JSON attributes in {os.path.relpath(cs_file, project_path)}")
        except Exception as e:
            print(f"⚠️  Error fixing {cs_file}: {e}")

def fix_namespace_references(project_path):
    """Fix missing namespace references."""
    print("\n🔧 Fixing namespace references...")
    
    cs_files = glob.glob(os.path.join(project_path, "Assets", "Scripts", "**", "*.cs"), recursive=True)
    
    namespace_fixes = {
        "using VisualDM.Core;": "using VisualDM.Systems;",
        "using NativeWebSocket;": "using NativeWebSocket;",  # Ensure proper case
    }
    
    for cs_file in cs_files:
        try:
            with open(cs_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            for old_ns, new_ns in namespace_fixes.items():
                if old_ns in content and new_ns not in content:
                    content = content.replace(old_ns, new_ns)
                    modified = True
            
            if modified:
                with open(cs_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed namespaces in {os.path.relpath(cs_file, project_path)}")
        except Exception as e:
            print(f"⚠️  Error fixing {cs_file}: {e}")

def fix_duplicate_definitions(project_path):
    """Fix duplicate class definitions."""
    print("\n🔧 Fixing duplicate definitions...")
    
    # Look for ValidationResult duplicates
    validation_files = []
    for cs_file in glob.glob(os.path.join(project_path, "Assets", "Scripts", "**", "*.cs"), recursive=True):
        try:
            with open(cs_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if "class ValidationResult" in content:
                validation_files.append(cs_file)
        except:
            continue
    
    if len(validation_files) > 1:
        print(f"Found {len(validation_files)} ValidationResult definitions:")
        for i, file_path in enumerate(validation_files):
            print(f"  {i+1}. {os.path.relpath(file_path, project_path)}")
        
        # Keep the first one, rename others
        for i, file_path in enumerate(validation_files[1:], 2):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Rename the class
                content = content.replace(
                    "class ValidationResult",
                    f"class ValidationResult{i}"
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Renamed ValidationResult to ValidationResult{i} in {os.path.relpath(file_path, project_path)}")
            except Exception as e:
                print(f"⚠️  Error fixing {file_path}: {e}")

def clear_unity_cache(project_path):
    """Clear Unity cache directories."""
    print("\n🔧 Clearing Unity cache...")
    
    cache_dirs = ["Library", "Temp", "Logs", "obj"]
    
    for cache_dir in cache_dirs:
        cache_path = os.path.join(project_path, cache_dir)
        if os.path.exists(cache_path):
            try:
                shutil.rmtree(cache_path)
                print(f"✅ Cleared {cache_dir}/")
            except Exception as e:
                print(f"⚠️  Could not clear {cache_dir}/: {e}")

def create_missing_directories(project_path):
    """Create missing package directories."""
    print("\n🔧 Creating missing directories...")
    
    missing_dirs = [
        "Packages/com.endel.nativewebsocket/WebSocketExample",
        "Packages/com.unity.multiplayer.tools/MetricTestData/Runtime/TestData/Definitions"
    ]
    
    for missing_dir in missing_dirs:
        dir_path = os.path.join(project_path, missing_dir)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                # Create .gitkeep file
                gitkeep_path = os.path.join(dir_path, ".gitkeep")
                with open(gitkeep_path, 'w') as f:
                    f.write("")
                print(f"✅ Created {missing_dir}")
            except Exception as e:
                print(f"⚠️  Could not create {missing_dir}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fix Unity Safe Mode Issues")
    parser.add_argument("project_path", help="Path to Unity project directory")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--skip-cache-clear", action="store_true", help="Skip clearing Unity cache")
    
    args = parser.parse_args()
    
    project_path = os.path.abspath(args.project_path)
    
    if not os.path.exists(project_path):
        print(f"❌ Project path does not exist: {project_path}")
        sys.exit(1)
    
    if not os.path.exists(os.path.join(project_path, "Assets")):
        print(f"❌ Not a valid Unity project (Assets folder not found): {project_path}")
        sys.exit(1)
    
    print(f"🚀 Starting Unity Safe Mode Fix for: {project_path}")
    
    # Create backup
    if not args.no_backup:
        backup_path = create_backup(project_path)
        if backup_path is None:
            sys.exit(1)
    
    try:
        # Run all fixes
        fix_package_dependencies(project_path)
        fix_dto_files(project_path)
        fix_json_attributes(project_path)
        fix_namespace_references(project_path)
        fix_duplicate_definitions(project_path)
        create_missing_directories(project_path)
        
        if not args.skip_cache_clear:
            clear_unity_cache(project_path)
        
        print("\n🎉 All fixes completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Open Unity (should no longer be in safe mode)")
        print("2. Let Unity reimport all assets (may take several minutes)")
        print("3. Check Package Manager for any remaining issues")
        print("4. Verify all scripts compile successfully")
        print("5. Test your project functionality")
        
    except Exception as e:
        print(f"\n❌ Error during fix process: {e}")
        if not args.no_backup:
            print(f"💡 You can restore from backup at: {backup_path}")
        sys.exit(1)

if __name__ == "__main__":
    main() 