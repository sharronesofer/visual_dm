#!/usr/bin/env python3
"""
Analyze coverage gap for systems missing test structure by examining existing coverage data
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def analyze_coverage_from_json():
    """Analyze coverage from existing coverage.json file"""
    
    if not os.path.exists('coverage.json'):
        print("❌ No coverage.json file found. Run pytest with coverage first.")
        return
    
    with open('coverage.json', 'r') as f:
        coverage_data = json.load(f)
    
    print("=== COVERAGE GAP ANALYSIS FOR MISSING TEST DIRECTORIES ===\n")
    
    # Systems missing test structure (from previous analysis)
    missing_test_structure = {
        'analytics': ['examples', 'models', 'schemas', 'services', 'utils'],
        'arc': ['events', 'models', 'repositories', 'routers', 'schemas', 'services', 'utils'],
        'character': ['data/rules', 'handlers', 'inventory', 'managers', 'processors', 'services/services'],
        'combat': ['calculators', 'coordinators', 'data', 'effects', 'events', 'handlers', 'managers', 'processors', 'routers/core', 'serializers', 'utils', 'validators'],
        'dialogue': ['routers'],
        'diplomacy': ['calculators', 'core', 'events', 'handlers', 'managers', 'models', 'processors', 'service_modules', 'utils'],
        'equipment': ['services'],
        'faction': ['models/faction_relationship'],
        'integration': ['event_bus'],
        'inventory': ['calculators', 'managers', 'models', 'utils', 'validators'],
        'llm': ['core/core', 'core/faction', 'core/integrations'],
        'motif': ['generators', 'integrations', 'managers', 'utils'],
        'npc': ['repositories', 'schemas', 'services/services'],
        'population': ['services'],
        'quest': ['core', 'integrations', 'managers'],
        'religion': ['services'],
        'shared': ['core', 'data', 'utils'],
        'tension_war': ['utils/alliances'],
        'world_generation': ['biomes', 'generators'],
        'world_state': ['mods/synchronizers']
    }
    
    # Analyze coverage by system
    results = {}
    total_coverage_found = 0
    total_files_checked = 0
    
    for system, missing_dirs in missing_test_structure.items():
        print(f"🔍 Analyzing {system} system...")
        
        system_results = {}
        system_covered_files = 0
        system_total_files = 0
        
        for missing_dir in missing_dirs:
            full_path = f"backend/systems/{system}/{missing_dir}"
            
            # Find files in coverage data that match this path
            covered_files = []
            for file_path in coverage_data.get('files', {}):
                if file_path.startswith(full_path):
                    file_info = coverage_data['files'][file_path]
                    coverage_pct = 0
                    if file_info.get('summary', {}).get('num_statements', 0) > 0:
                        covered = file_info['summary'].get('covered_lines', 0)
                        total = file_info['summary'].get('num_statements', 0)
                        coverage_pct = (covered / total) * 100
                    
                    covered_files.append({
                        'file': file_path,
                        'coverage': coverage_pct,
                        'statements': file_info['summary'].get('num_statements', 0),
                        'covered': file_info['summary'].get('covered_lines', 0)
                    })
            
            if covered_files:
                avg_coverage = sum(f['coverage'] for f in covered_files) / len(covered_files)
                total_statements = sum(f['statements'] for f in covered_files)
                total_covered = sum(f['covered'] for f in covered_files)
                
                system_results[missing_dir] = {
                    'files': len(covered_files),
                    'avg_coverage': avg_coverage,
                    'total_statements': total_statements,
                    'total_covered': total_covered,
                    'status': 'COVERED' if avg_coverage > 0 else 'NO_COVERAGE'
                }
                
                status = "✅ COVERED" if avg_coverage > 50 else "⚠️  LOW" if avg_coverage > 0 else "❌ NONE"
                print(f"   {missing_dir}: {status} ({avg_coverage:.1f}%, {len(covered_files)} files)")
                
                if avg_coverage > 0:
                    system_covered_files += len(covered_files)
                system_total_files += len(covered_files)
            else:
                system_results[missing_dir] = {
                    'files': 0,
                    'avg_coverage': 0,
                    'status': 'NOT_FOUND'
                }
                print(f"   {missing_dir}: ❓ NOT FOUND (no files in coverage data)")
        
        results[system] = system_results
        total_coverage_found += system_covered_files
        total_files_checked += system_total_files
        print()
    
    # Summary
    print("=== SUMMARY ANALYSIS ===")
    
    systems_with_coverage = 0
    total_dirs_checked = 0
    dirs_with_coverage = 0
    
    for system, dirs in results.items():
        has_coverage = any(d['avg_coverage'] > 0 for d in dirs.values())
        if has_coverage:
            systems_with_coverage += 1
            
        system_dirs_covered = sum(1 for d in dirs.values() if d['avg_coverage'] > 0)
        total_dirs_checked += len(dirs)
        dirs_with_coverage += system_dirs_covered
        
        coverage_summary = f"{system_dirs_covered}/{len(dirs)} directories"
        avg_system_coverage = sum(d['avg_coverage'] for d in dirs.values()) / len(dirs) if dirs else 0
        
        status = "✅" if avg_system_coverage > 50 else "⚠️" if avg_system_coverage > 10 else "❌"
        print(f"{status} {system}: {coverage_summary} covered (avg: {avg_system_coverage:.1f}%)")
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Systems analyzed: {len(results)}")
    print(f"   Systems with some coverage: {systems_with_coverage}")
    print(f"   Directories checked: {total_dirs_checked}")
    print(f"   Directories with coverage: {dirs_with_coverage}")
    print(f"   Coverage rate: {(dirs_with_coverage/total_dirs_checked)*100:.1f}%")
    
    # Gap Analysis
    print(f"\n🎯 COVERAGE GAP ANALYSIS:")
    no_coverage_systems = []
    low_coverage_systems = []
    
    for system, dirs in results.items():
        avg_coverage = sum(d['avg_coverage'] for d in dirs.values()) / len(dirs) if dirs else 0
        if avg_coverage == 0:
            no_coverage_systems.append(system)
        elif avg_coverage < 50:
            low_coverage_systems.append(system)
    
    if no_coverage_systems:
        print(f"   ❌ NO COVERAGE: {', '.join(no_coverage_systems)}")
    
    if low_coverage_systems:
        print(f"   ⚠️  LOW COVERAGE: {', '.join(low_coverage_systems)}")
    
    good_coverage = len(results) - len(no_coverage_systems) - len(low_coverage_systems)
    if good_coverage > 0:
        print(f"   ✅ GOOD COVERAGE: {good_coverage} systems")
    
    print(f"\n💡 CONCLUSION:")
    if dirs_with_coverage / total_dirs_checked > 0.5:
        print("   Most missing test directories are actually covered by integration tests")
        print("   This suggests good test coverage despite missing dedicated unit test directories")
    else:
        print("   Significant coverage gaps exist - missing test directories represent real gaps")
        print("   Consider adding dedicated unit tests for uncovered directories")

if __name__ == "__main__":
    analyze_coverage_from_json() 