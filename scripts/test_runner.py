#!/usr/bin/env python3
"""
Test Runner Script for Visual DM Backend

Provides different testing strategies to handle the 7859 test suite efficiently.
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse
import time

# Test systems in order of dependencies
FOUNDATION_SYSTEMS = ["shared", "events", "data", "storage"]
CORE_SYSTEMS = ["character", "time", "world_generation"] 
GAMEPLAY_SYSTEMS = ["combat", "magic", "equipment", "inventory"]
WORLD_SYSTEMS = ["region", "poi", "world_state"]
SOCIAL_SYSTEMS = ["npc", "faction", "population"]
INTERACTION_SYSTEMS = ["dialogue", "diplomacy", "memory"]
ECONOMIC_SYSTEMS = ["economy", "crafting", "loot"]
CONTENT_SYSTEMS = ["quest", "rumor", "religion"]
ADVANCED_SYSTEMS = ["motif", "arc", "tension_war"]
SUPPORT_SYSTEMS = ["analytics", "auth_user", "llm"]

ALL_SYSTEM_GROUPS = {
    "foundation": FOUNDATION_SYSTEMS,
    "core": CORE_SYSTEMS, 
    "gameplay": GAMEPLAY_SYSTEMS,
    "world": WORLD_SYSTEMS,
    "social": SOCIAL_SYSTEMS,
    "interaction": INTERACTION_SYSTEMS,
    "economic": ECONOMIC_SYSTEMS,
    "content": CONTENT_SYSTEMS,
    "advanced": ADVANCED_SYSTEMS,
    "support": SUPPORT_SYSTEMS
}

def run_command(cmd, background=False):
    """Run a command and handle output"""
    print(f"🔄 Running: {cmd}")
    start_time = time.time()
    
    if background:
        # Run in background
        process = subprocess.Popen(
            cmd, shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True
        )
        return process
    else:
        # Run with real-time output
        result = subprocess.run(cmd, shell=True, capture_output=False)
        elapsed = time.time() - start_time
        print(f"⏱️  Completed in {elapsed:.2f}s")
        return result

def test_system(system_name, coverage=False, verbose=False):
    """Test a single system"""
    test_path = f"backend/tests/systems/{system_name}/"
    
    if not os.path.exists(test_path):
        print(f"❌ System tests not found: {test_path}")
        return False
        
    cmd_parts = ["python", "-m", "pytest", test_path]
    
    if coverage:
        cmd_parts.extend([f"--cov=backend.systems.{system_name}", "--cov-report=term-missing"])
    
    if verbose:
        cmd_parts.append("-v")
    else:
        cmd_parts.append("-q")
        
    cmd_parts.append("--tb=short")
    
    cmd = " ".join(cmd_parts)
    result = run_command(cmd)
    
    if result.returncode == 0:
        print(f"✅ {system_name} tests passed")
        return True
    else:
        print(f"❌ {system_name} tests failed")
        return False

def test_system_group(group_name, coverage=False, verbose=False):
    """Test a group of related systems"""
    if group_name not in ALL_SYSTEM_GROUPS:
        print(f"❌ Unknown system group: {group_name}")
        print(f"Available groups: {', '.join(ALL_SYSTEM_GROUPS.keys())}")
        return False
        
    systems = ALL_SYSTEM_GROUPS[group_name]
    print(f"🏗️  Testing {group_name} systems: {', '.join(systems)}")
    
    passed = 0
    total = len(systems)
    
    for system in systems:
        if test_system(system, coverage, verbose):
            passed += 1
            
    print(f"📊 {group_name} Results: {passed}/{total} systems passed")
    return passed == total

def run_all_tests_background():
    """Run all tests in background"""
    cmd = "python -m pytest backend/tests/ --tb=short -q"
    print("🚀 Running ALL tests in background...")
    print("⚠️  This will take several minutes...")
    process = run_command(cmd, background=True)
    return process

def run_coverage_report():
    """Generate comprehensive coverage report"""
    cmd = "python -m pytest backend/tests/ --cov=backend.systems --cov-report=html --cov-report=term --tb=no -q"
    print("📈 Generating coverage report...")
    print("⚠️  This will take several minutes...")
    result = run_command(cmd)
    
    if result.returncode == 0:
        print("✅ Coverage report generated in htmlcov/")
    return result

def run_fast_smoke_test():
    """Run a quick smoke test on key systems"""
    key_systems = ["analytics", "character", "combat", "quest", "arc"]
    print("🔥 Running fast smoke test on key systems...")
    print("   (Running 1-2 tests per system for speed)")
    
    passed = 0
    for system in key_systems:
        # Run just the first test file from each system for speed
        cmd = f"python -m pytest backend/tests/systems/{system}/ -k 'test_simple or test_basic or test_core' --maxfail=1 -q --tb=short"
        print(f"🔍 Testing {system}...")
        result = run_command(cmd)
        if result.returncode == 0:
            passed += 1
            print(f"✅ {system}")
        else:
            print(f"❌ {system}")
            
    print(f"📊 Smoke Test Results: {passed}/{len(key_systems)} systems passed")
    return passed == len(key_systems)

def run_single_test_file(filepath):
    """Run a single test file"""
    if not os.path.exists(filepath):
        print(f"❌ Test file not found: {filepath}")
        return False
        
    cmd = f"python -m pytest {filepath} -v --tb=short"
    print(f"🔍 Running single test file: {filepath}")
    result = run_command(cmd)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Visual DM Test Runner")
    parser.add_argument("--system", help="Test a specific system")
    parser.add_argument("--group", help="Test a system group", choices=ALL_SYSTEM_GROUPS.keys())
    parser.add_argument("--file", help="Test a single file")
    parser.add_argument("--all", action="store_true", help="Run all tests (background)")
    parser.add_argument("--coverage", action="store_true", help="Include coverage report")
    parser.add_argument("--smoke", action="store_true", help="Run fast smoke test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.smoke:
        return run_fast_smoke_test()
    elif args.file:
        return run_single_test_file(args.file)
    elif args.system:
        return test_system(args.system, args.coverage, args.verbose)
    elif args.group:
        return test_system_group(args.group, args.coverage, args.verbose)
    elif args.all:
        if args.coverage:
            return run_coverage_report()
        else:
            process = run_all_tests_background()
            print("🔄 Tests running in background. Check terminal for progress.")
            return True
    else:
        print("🚀 Visual DM Test Runner")
        print("\nQuick options:")
        print("  python scripts/test_runner.py --smoke                    # Fast smoke test")
        print("  python scripts/test_runner.py --file backend/tests/...   # Single test file")
        print("  python scripts/test_runner.py --group foundation         # Test foundation systems")
        print("  python scripts/test_runner.py --system analytics         # Test single system")
        print("  python scripts/test_runner.py --all --coverage           # Full coverage report")
        print("\nSystem groups:", ", ".join(ALL_SYSTEM_GROUPS.keys()))
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 