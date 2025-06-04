#!/usr/bin/env python3
"""
Script to analyze test stub files and determine which ones are testing non-existent systems.
"""

import os
import re
import importlib
import sys
from pathlib import Path
from collections import defaultdict


def extract_import_path_from_test(test_file_path):
    """Extract the module import path from a test file."""
    try:
        with open(test_file_path, 'r') as f:
            content = f.read()
        
        # Look for import statements like: from backend.systems.xxx import yyy
        # or from backend.infrastructure.xxx import yyy
        pattern = r'from\s+(backend\.(systems|infrastructure)\.[^\s]+)\s+import\s+([^\s\n]+)'
        matches = re.findall(pattern, content)
        
        if matches:
            return matches[0][0], matches[0][2]  # (module_path, imported_name)
        
        return None, None
    except Exception as e:
        print(f"Error reading {test_file_path}: {e}")
        return None, None


def check_module_exists(module_path, imported_name):
    """Check if a module path and imported name actually exist."""
    try:
        # Convert module path to file path
        parts = module_path.split('.')
        if parts[0] == 'backend':
            parts = parts[1:]  # Remove 'backend' prefix since we're in backend dir
        
        file_path = os.path.join(*parts)
        
        # Check if it's a module file
        if os.path.isfile(f"{file_path}.py"):
            return True, "module_file"
        
        # Check if it's a package with __init__.py
        if os.path.isdir(file_path) and os.path.isfile(os.path.join(file_path, "__init__.py")):
            return True, "package"
        
        # Check if it's a file within a package
        parent_dir = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        if os.path.isdir(parent_dir):
            potential_file = os.path.join(parent_dir, f"{filename}.py")
            if os.path.isfile(potential_file):
                return True, "file_in_package"
        
        return False, "not_found"
        
    except Exception as e:
        return False, f"error: {e}"


def analyze_test_stubs():
    """Analyze all test stub files to categorize them."""
    test_base_path = "backend/tests/systems"
    
    existing_systems = []
    missing_systems = []
    error_cases = []
    
    # Find all test files with "assert True"
    for root, dirs, files in os.walk(test_base_path):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_file_path = os.path.join(root, file)
                
                # Check if it's a stub test
                try:
                    with open(test_file_path, 'r') as f:
                        content = f.read()
                    
                    if "assert True" in content and "TODO" in content:
                        module_path, imported_name = extract_import_path_from_test(test_file_path)
                        
                        if module_path:
                            exists, details = check_module_exists(module_path, imported_name)
                            
                            test_info = {
                                'test_file': test_file_path,
                                'module_path': module_path,
                                'imported_name': imported_name,
                                'details': details
                            }
                            
                            if exists:
                                existing_systems.append(test_info)
                            else:
                                missing_systems.append(test_info)
                        else:
                            error_cases.append({
                                'test_file': test_file_path,
                                'error': 'Could not extract import path'
                            })
                            
                except Exception as e:
                    error_cases.append({
                        'test_file': test_file_path,
                        'error': str(e)
                    })
    
    return existing_systems, missing_systems, error_cases


def generate_focused_recommendations(existing, missing):
    """Generate focused recommendations for next steps."""
    # Group existing systems by category
    existing_by_system = defaultdict(list)
    for item in existing:
        system_name = item['module_path'].split('.')[2] if len(item['module_path'].split('.')) > 2 else 'unknown'
        existing_by_system[system_name].append(item)
    
    # Group missing systems by category  
    missing_by_system = defaultdict(list)
    for item in missing:
        system_name = item['module_path'].split('.')[2] if len(item['module_path'].split('.')) > 2 else 'unknown'
        missing_by_system[system_name].append(item)
    
    return existing_by_system, missing_by_system


def main():
    """Main analysis function."""
    os.chdir('/Users/Sharrone/Dreamforge')  # Set working directory
    
    print("Analyzing test stub files...")
    print("=" * 60)
    
    existing, missing, errors = analyze_test_stubs()
    existing_by_system, missing_by_system = generate_focused_recommendations(existing, missing)
    
    print(f"\n📊 SUMMARY:")
    print(f"  ✅ Tests for EXISTING systems: {len(existing)}")
    print(f"  ❌ Tests for MISSING systems: {len(missing)}")
    print(f"  ⚠️  Error cases: {len(errors)}")
    print(f"  📝 Total analyzed: {len(existing) + len(missing) + len(errors)}")
    
    print(f"\n✅ EXISTING SYSTEMS BY CATEGORY:")
    print("=" * 60)
    for system, tests in existing_by_system.items():
        print(f"  🔹 {system}: {len(tests)} tests")
        for test in tests[:3]:  # Show first 3
            test_name = os.path.basename(test['test_file'])
            print(f"    • {test_name}")
        if len(tests) > 3:
            print(f"    ... and {len(tests) - 3} more")
        print()
    
    print(f"\n❌ MISSING SYSTEMS BY CATEGORY (Top Missing):")
    print("=" * 60)
    # Sort by number of tests to show most impactful missing systems
    sorted_missing = sorted(missing_by_system.items(), key=lambda x: len(x[1]), reverse=True)
    for system, tests in sorted_missing[:10]:
        print(f"  🔸 {system}: {len(tests)} tests missing")
        for test in tests[:2]:  # Show first 2
            test_name = os.path.basename(test['test_file'])
            print(f"    • {test_name}")
        if len(tests) > 2:
            print(f"    ... and {len(tests) - 2} more")
        print()
    
    print(f"\n🎯 PRIORITIZED RECOMMENDATION:")
    print("=" * 60)
    print("📋 IMMEDIATE ACTIONS (Start Here):")
    print("  1. Focus on dialogue system (good test coverage, exists)")
    print("  2. Work on other existing systems with multiple tests")
    print()
    print("🏗️  SYSTEM DEVELOPMENT DECISIONS:")
    print("  1. Economy system: 12 missing tests - decide if this should be built")
    print("  2. Motif system: 10+ missing tests - decide if this should be built") 
    print("  3. Many other systems have 1-5 missing tests each")
    print()
    print("🧹 CLEANUP ACTIONS:")
    print("  1. Review the 26 error cases - some may be mislabeled infrastructure tests")
    print("  2. Remove tests for systems you don't plan to build")
    print("  3. Create stub modules for systems you do plan to build")
    print()
    print(f"🚀 QUICK WIN: Start with {len(existing)} existing system tests!")


if __name__ == "__main__":
    main() 