#!/usr/bin/env python3
"""
Testing Protocol for Task 41 - Strategic Implementation
Handles the three-phase testing protocol without overwhelming the system
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class TestingProtocol:
    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.test_results = {}
        
    def run_command_with_timeout(self, cmd, timeout=30):
        """Run command with timeout to prevent hanging"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, 
                timeout=timeout, cwd=self.backend_path
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s"
    
    def get_all_systems(self):
        """Get all systems organized by priority tiers"""
        return {
            # Foundation Layer - Core dependencies
            "foundation": [
                "shared", "events", "data", "storage", "analytics", "auth_user", "llm"
            ],
            
            # Core Game Layer - Character and world mechanics
            "core_game": [
                "character", "time", "world_generation", "region"
            ],
            
            # Gameplay Layer - Combat and interaction systems
            "gameplay": [
                "combat", "magic", "equipment", "inventory"
            ],
            
            # World Simulation Layer - Dynamic world systems  
            "world_sim": [
                "poi", "world_state", "population"
            ],
            
            # Social Layer - NPCs and factions
            "social": [
                "npc", "faction", "diplomacy", "memory"
            ],
            
            # Interaction Layer - Player communication
            "interaction": [
                "dialogue", "tension_war"
            ],
            
            # Economic Layer - Trade and resources
            "economic": [
                "economy", "crafting", "loot"
            ],
            
            # Content Layer - Dynamic content generation
            "content": [
                "quest", "rumor", "religion"
            ],
            
            # Advanced Layer - Meta-narrative systems
            "advanced": [
                "motif", "arc"
            ],
            
            # Integration Layer - Cross-system coordination
            "integration": [
                "integration"
            ]
        }
    
    def phase1_test_execution(self, tier_filter=None):
        """Phase 1: Test Execution and Error Resolution"""
        print("=== PHASE 1: TEST EXECUTION AND ERROR RESOLUTION ===")
        
        all_systems = self.get_all_systems()
        results = {}
        
        # Filter systems by tier if specified
        if tier_filter:
            if tier_filter in all_systems:
                systems_to_test = {tier_filter: all_systems[tier_filter]}
            else:
                print(f"❌ Unknown tier: {tier_filter}")
                return {}
        else:
            systems_to_test = all_systems
        
        for tier_name, systems in systems_to_test.items():
            print(f"\n🏗️ Testing {tier_name.upper()} LAYER:")
            
            for system in systems:
                print(f"\n🔍 Testing {system} system...")
                cmd = f"python -m pytest tests/systems/{system}/ --tb=short --maxfail=3 -q"
                returncode, stdout, stderr = self.run_command_with_timeout(cmd, timeout=30)
                
                if returncode == 0:
                    print(f"✅ {system}: All tests passed")
                    results[system] = "PASSED"
                elif returncode == -1:
                    print(f"⏱️ {system}: Tests timed out")
                    results[system] = "TIMEOUT"
                elif returncode == 4:  # No tests found
                    print(f"⚠️ {system}: No tests found")
                    results[system] = "NO_TESTS"
                else:
                    print(f"❌ {system}: Some tests failed")
                    results[system] = "FAILED"
                    
        return results
    
    def phase2_structure_enforcement(self):
        """Phase 2: Test Location and Structure Enforcement"""
        print("\n=== PHASE 2: TEST LOCATION AND STRUCTURE ENFORCEMENT ===")
        
        # Check for test files in wrong locations
        print("🔍 Scanning for misplaced test files...")
        cmd = "find ./systems -name 'test*.py' -type f"
        returncode, stdout, stderr = self.run_command_with_timeout(cmd, timeout=10)
        
        if stdout.strip():
            print(f"❌ Found test files in systems directory:")
            for line in stdout.strip().split('\n'):
                print(f"   {line}")
            return False
        else:
            print("✅ No test files found in systems directory - structure is canonical")
            return True
    
    def phase3_canonical_imports(self):
        """Phase 3: Canonical Imports Enforcement"""
        print("\n=== PHASE 3: CANONICAL IMPORTS ENFORCEMENT ===")
        
        # Check for non-canonical imports
        print("🔍 Checking for non-canonical imports...")
        cmd = "grep -r 'from systems\\.' tests/systems/ | head -10"
        returncode, stdout, stderr = self.run_command_with_timeout(cmd, timeout=10)
        
        if stdout.strip():
            print(f"❌ Found non-canonical imports:")
            for line in stdout.strip().split('\n'):
                print(f"   {line}")
            return False
        else:
            print("✅ All imports appear to use canonical backend.systems structure")
            return True
    
    def get_quick_coverage_sample(self, systems=None):
        """Get coverage for a sample to assess overall health"""
        print("\n=== QUICK COVERAGE SAMPLE ===")
        
        # Default to foundation systems for quick health check
        if systems is None:
            systems = ["shared", "events", "data"]
            
        for system in systems:
            print(f"📊 Coverage sample for {system}...")
            cmd = f"python -m pytest tests/systems/{system}/ --cov=backend.systems.{system} --cov-report=term-missing -q"
            returncode, stdout, stderr = self.run_command_with_timeout(cmd, timeout=20)
            
            if returncode == 0:
                # Extract coverage percentage
                for line in stdout.split('\n'):
                    if 'TOTAL' in line and '%' in line:
                        print(f"✅ {system}: {line}")
                        break
            else:
                print(f"❌ {system}: Coverage check failed")
    
    def print_system_summary(self):
        """Print summary of all systems to be tested"""
        print("\n📋 COMPLETE SYSTEM INVENTORY (27 Systems):")
        print("=" * 60)
        
        all_systems = self.get_all_systems()
        total_systems = 0
        
        for tier_name, systems in all_systems.items():
            print(f"\n🏗️ {tier_name.upper()} LAYER ({len(systems)} systems):")
            for system in systems:
                print(f"   • {system}")
            total_systems += len(systems)
        
        print(f"\n📊 TOTAL: {total_systems} systems to test")
        print("=" * 60)
    
    def run_protocol(self, tier_filter=None, coverage_systems=None):
        """Execute the complete testing protocol"""
        print("🚀 TASK 41 TESTING PROTOCOL - COMPREHENSIVE IMPLEMENTATION")
        print("🎯 All 27 Backend Systems")
        print("=" * 60)
        
        # Show system inventory
        self.print_system_summary()
        
        # Phase 1: Test Execution
        phase1_results = self.phase1_test_execution(tier_filter)
        
        # Phase 2: Structure Enforcement
        phase2_success = self.phase2_structure_enforcement()
        
        # Phase 3: Canonical Imports
        phase3_success = self.phase3_canonical_imports()
        
        # Quick Coverage Assessment
        self.get_quick_coverage_sample(coverage_systems)
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TESTING PROTOCOL SUMMARY")
        print("=" * 60)
        
        if phase1_results:
            # Organize results by status
            passed = [k for k, v in phase1_results.items() if v == "PASSED"]
            failed = [k for k, v in phase1_results.items() if v == "FAILED"]
            no_tests = [k for k, v in phase1_results.items() if v == "NO_TESTS"]
            timeout = [k for k, v in phase1_results.items() if v == "TIMEOUT"]
            
            print(f"Phase 1 - Test Execution ({len(phase1_results)} systems tested):")
            if passed:
                print(f"   ✅ PASSED ({len(passed)}): {', '.join(passed)}")
            if failed:
                print(f"   ❌ FAILED ({len(failed)}): {', '.join(failed)}")
            if no_tests:
                print(f"   ⚠️ NO_TESTS ({len(no_tests)}): {', '.join(no_tests)}")
            if timeout:
                print(f"   ⏱️ TIMEOUT ({len(timeout)}): {', '.join(timeout)}")
        
        print(f"\nPhase 2 - Structure Enforcement: {'✅ PASSED' if phase2_success else '❌ FAILED'}")
        print(f"Phase 3 - Canonical Imports: {'✅ PASSED' if phase3_success else '❌ FAILED'}")
        
        return {
            'phase1': phase1_results,
            'phase2': phase2_success,
            'phase3': phase3_success
        }

if __name__ == "__main__":
    import sys
    
    protocol = TestingProtocol()
    
    # Allow tier filtering from command line
    tier_filter = sys.argv[1] if len(sys.argv) > 1 else None
    
    if tier_filter == "list":
        protocol.print_system_summary()
    else:
        results = protocol.run_protocol(tier_filter) 