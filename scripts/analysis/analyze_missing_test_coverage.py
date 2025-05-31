#!/usr/bin/env python3
"""
Script to analyze test coverage for systems that don't have matching test directory structure
"""

import os
import subprocess
import json
from pathlib import Path

# List of systems missing test structure from previous analysis
MISSING_TEST_STRUCTURE = [
    'analytics/examples',
    'analytics/models', 
    'analytics/schemas',
    'analytics/services',
    'analytics/services/services',
    'analytics/services/services/collection',
    'analytics/services/services/core',
    'analytics/services/services/processing',
    'analytics/services/services/storage',
    'analytics/utils',
    'arc/events',
    'arc/models',
    'arc/repositories', 
    'arc/routers',
    'arc/schemas',
    'arc/services',
    'arc/utils',
    'character/data/rules',
    'character/handlers',
    'character/inventory',
    'character/inventory/data',
    'character/managers',
    'character/processors',
    'character/services/services',
    'character/services/services/core',
    'character/services/services/core/core',
    'character/services/services/goals',
    'character/services/services/mechanics',
    'character/services/services/mood',
    'character/services/services/progression',
    'character/services/services/social',
    'combat/calculators',
    'combat/coordinators',
    'combat/data',
    'combat/data/quests',
    'combat/effects',
    'combat/effects/core',
    'combat/events',
    'combat/handlers',
    'combat/managers',
    'combat/processors',
    'combat/routers/core',
    'combat/serializers',
    'combat/utils',
    'combat/utils/core',
    'combat/utils/processors',
    'combat/validators',
    'dialogue/routers',
    'diplomacy/calculators',
    'diplomacy/core',
    'diplomacy/events',
    'diplomacy/handlers',
    'diplomacy/managers',
    'diplomacy/models',
    'diplomacy/processors',
    'diplomacy/service_modules',
    'diplomacy/utils',
    'equipment/services',
    'equipment/services/core',
    'faction/models/faction_relationship',
    'integration/event_bus',
    'inventory/calculators',
    'inventory/managers',
    'inventory/models',
    'inventory/utils',
    'inventory/validators',
    'llm/core/core',
    'llm/core/core/core',
    'llm/core/faction',
    'llm/core/integrations',
    'motif/generators',
    'motif/integrations',
    'motif/managers',
    'motif/managers/core',
    'motif/utils',
    'motif/utils/compatibility',
    'motif/utils/context',
    'motif/utils/generation',
    'motif/utils/narrative',
    'motif/utils/pattern',
    'npc/repositories',
    'npc/schemas',
    'npc/services/services',
    'npc/services/services/core',
    'npc/services/services/core/core',
    'population/services',
    'population/services/core',
    'population/services/core/core',
    'quest/core',
    'quest/integrations',
    'quest/managers',
    'religion/services',
    'religion/services/core',
    'shared/core',
    'shared/data',
    'shared/data/rules_json',
    'shared/utils/compatibility',
    'shared/utils/database',
    'shared/utils/formatting',
    'shared/utils/game_mechanics',
    'shared/utils/mathematical',
    'shared/utils/validation',
    'tension_war/utils/alliances',
    'world_generation/biomes',
    'world_generation/generators',
    'world_state/mods/synchronizers'
]

def check_path_exists(path):
    """Check if a system path exists"""
    full_path = Path(f"backend/systems/{path}")
    return full_path.exists() and any(full_path.iterdir())

def run_coverage_for_system(system_path):
    """Run coverage for a specific system path"""
    full_system_path = f"backend/systems/{system_path}"
    
    if not check_path_exists(system_path):
        return None, f"Path does not exist: {full_system_path}"
    
    try:
        # Run pytest with coverage for this specific path
        cmd = [
            'python', '-m', 'pytest', 
            '--cov=' + full_system_path,
            '--cov-report=json',
            '--cov-report=term-missing',
            '-v',
            'backend/tests/',
            '--tb=short'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Try to parse coverage.json if it exists
        coverage_data = None
        if os.path.exists('coverage.json'):
            try:
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
            except:
                pass
                
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'coverage_data': coverage_data
        }, None
        
    except subprocess.TimeoutExpired:
        return None, f"Timeout running coverage for {system_path}"
    except Exception as e:
        return None, f"Error running coverage for {system_path}: {str(e)}"

def analyze_coverage_output(output, system_path):
    """Extract coverage percentage from pytest output"""
    if not output:
        return None
        
    lines = output.get('stdout', '').split('\n')
    
    # Look for coverage percentage in output
    for line in lines:
        if 'TOTAL' in line and '%' in line:
            parts = line.split()
            for part in parts:
                if '%' in part:
                    try:
                        return float(part.replace('%', ''))
                    except:
                        continue
                        
    # Try to get from coverage.json
    coverage_data = output.get('coverage_data')
    if coverage_data and 'totals' in coverage_data:
        total = coverage_data['totals']
        if total.get('num_statements', 0) > 0:
            covered = total.get('covered_lines', 0)
            total_lines = total.get('num_statements', 0)
            return (covered / total_lines) * 100
            
    return None

def main():
    """Main analysis function"""
    print("=== ANALYZING COVERAGE FOR SYSTEMS MISSING TEST STRUCTURE ===\n")
    
    results = {}
    errors = []
    
    # Group by top-level system for better organization
    by_system = {}
    for path in MISSING_TEST_STRUCTURE:
        top_level = path.split('/')[0]
        if top_level not in by_system:
            by_system[top_level] = []
        by_system[top_level].append(path)
    
    print(f"Analyzing {len(MISSING_TEST_STRUCTURE)} directories across {len(by_system)} systems...\n")
    
    for system, paths in sorted(by_system.items()):
        print(f"🔍 ANALYZING SYSTEM: {system}")
        print(f"   Paths to check: {len(paths)}")
        
        system_results = {}
        
        # Run coverage for each path in this system
        for path in paths[:3]:  # Limit to first 3 paths per system to avoid overwhelming output
            print(f"   Checking: {path}")
            
            output, error = run_coverage_for_system(path)
            
            if error:
                errors.append(f"{path}: {error}")
                continue
                
            coverage_pct = analyze_coverage_output(output, path)
            
            if coverage_pct is not None:
                system_results[path] = {
                    'coverage': coverage_pct,
                    'status': 'COVERED' if coverage_pct > 0 else 'NO_COVERAGE'
                }
                status = "✅ COVERED" if coverage_pct > 0 else "❌ NO COVERAGE"
                print(f"      → {status} ({coverage_pct:.1f}%)")
            else:
                system_results[path] = {
                    'coverage': 0,
                    'status': 'UNKNOWN'
                }
                print(f"      → ❓ UNKNOWN (could not determine coverage)")
        
        results[system] = system_results
        print()
    
    # Summary
    print("=== SUMMARY ===")
    
    total_checked = sum(len(paths) for paths in results.values())
    covered_count = 0
    total_coverage = 0
    
    for system, paths in results.items():
        covered_in_system = sum(1 for p in paths.values() if p['coverage'] > 0)
        avg_coverage = sum(p['coverage'] for p in paths.values()) / len(paths) if paths else 0
        
        print(f"{system}: {covered_in_system}/{len(paths)} paths covered (avg: {avg_coverage:.1f}%)")
        
        covered_count += covered_in_system
        total_coverage += avg_coverage
    
    overall_coverage = total_coverage / len(results) if results else 0
    
    print(f"\nOVERALL: {covered_count}/{total_checked} paths have some coverage")
    print(f"AVERAGE COVERAGE: {overall_coverage:.1f}%")
    
    if errors:
        print(f"\nERRORS ENCOUNTERED: {len(errors)}")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    return results

if __name__ == "__main__":
    main() 