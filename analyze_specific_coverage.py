#!/usr/bin/env python3
"""
Script to analyze coverage for specific systems that are missing test directory structure
but run without errors
"""

import subprocess
import json
import os
from pathlib import Path

def run_specific_coverage(system_module, test_pattern=None):
    """Run coverage for a specific system module"""
    try:
        # Basic coverage command
        cmd = [
            'python', '-m', 'pytest', 
            '--cov=' + system_module,
            '--cov-report=json',
            '--cov-report=term-missing',
            '-v',
            'backend/tests/',
            '--tb=short',
            '-q'
        ]
        
        if test_pattern:
            cmd.append(f"-k {test_pattern}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Parse coverage data
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
        }
        
    except Exception as e:
        return {'error': str(e)}

def analyze_specific_systems():
    """Analyze specific systems that should have coverage but missing test structure"""
    
    # Focus on systems that showed coverage in our previous analysis
    systems_to_check = [
        # Analytics system components
        'backend.systems.analytics.models',
        'backend.systems.analytics.schemas',
        
        # Arc system components  
        'backend.systems.arc.events',
        'backend.systems.arc.models',
        'backend.systems.arc.repositories',
        'backend.systems.arc.services',
        'backend.systems.arc.utils',
        
        # Diplomacy system components
        'backend.systems.diplomacy.core',
        'backend.systems.diplomacy.events',
        'backend.systems.diplomacy.calculators',
        
        # Equipment system components
        'backend.systems.equipment.services',
        
        # Faction system components
        'backend.systems.faction.models.faction_relationship',
        
        # Inventory system components
        'backend.systems.inventory.managers',
        'backend.systems.inventory.models',
        
        # NPC system components
        'backend.systems.npc.repositories',
        'backend.systems.npc.schemas',
        
        # Quest system components
        'backend.systems.quest.integrations',
        'backend.systems.quest.managers',
        
        # Religion system components
        'backend.systems.religion.services',
        
        # Population system components
        'backend.systems.population.services.core.core'
    ]
    
    print("=== FOCUSED COVERAGE ANALYSIS ===")
    print(f"Analyzing {len(systems_to_check)} specific system modules...\n")
    
    results = {}
    
    for system in systems_to_check:
        print(f"🔍 Analyzing: {system}")
        
        result = run_specific_coverage(system)
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
            continue
            
        if result['returncode'] != 0:
            print(f"   ⚠️  Non-zero exit code: {result['returncode']}")
            if result['stderr']:
                print(f"   Error output: {result['stderr'][:200]}...")
            continue
        
        # Extract coverage percentage
        coverage_pct = None
        if result['coverage_data'] and 'totals' in result['coverage_data']:
            total = result['coverage_data']['totals']
            if total.get('num_statements', 0) > 0:
                covered = total.get('covered_lines', 0)
                total_lines = total.get('num_statements', 0)
                coverage_pct = (covered / total_lines) * 100
        
        if coverage_pct is not None:
            results[system] = {
                'coverage': coverage_pct,
                'statements': total.get('num_statements', 0),
                'covered': total.get('covered_lines', 0),
                'missing': total.get('missing_lines', 0)
            }
            
            status = "✅ GOOD" if coverage_pct >= 80 else "⚠️  MODERATE" if coverage_pct >= 50 else "❌ LOW"
            print(f"   {status} Coverage: {coverage_pct:.1f}% ({total.get('covered_lines', 0)}/{total.get('num_statements', 0)} lines)")
        else:
            print(f"   ❓ Could not determine coverage")
        
        print()
    
    # Summary
    print("=== SUMMARY ===")
    
    if results:
        covered_systems = [s for s, r in results.items() if r['coverage'] > 0]
        high_coverage = [s for s, r in results.items() if r['coverage'] >= 80]
        medium_coverage = [s for s, r in results.items() if 50 <= r['coverage'] < 80]
        low_coverage = [s for s, r in results.items() if 0 < r['coverage'] < 50]
        
        avg_coverage = sum(r['coverage'] for r in results.values()) / len(results)
        total_statements = sum(r['statements'] for r in results.values())
        total_covered = sum(r['covered'] for r in results.values())
        
        print(f"Systems analyzed: {len(results)}")
        print(f"Systems with coverage: {len(covered_systems)}")
        print(f"High coverage (≥80%): {len(high_coverage)}")
        print(f"Medium coverage (50-79%): {len(medium_coverage)}")  
        print(f"Low coverage (<50%): {len(low_coverage)}")
        print(f"Average coverage: {avg_coverage:.1f}%")
        print(f"Total statements: {total_statements}")
        print(f"Total covered: {total_covered}")
        
        if high_coverage:
            print(f"\n✅ HIGH COVERAGE SYSTEMS:")
            for system in high_coverage:
                r = results[system]
                print(f"  - {system}: {r['coverage']:.1f}%")
        
        if low_coverage:
            print(f"\n❌ LOW COVERAGE SYSTEMS:")
            for system in low_coverage:
                r = results[system]
                print(f"  - {system}: {r['coverage']:.1f}%")
    
    return results

if __name__ == "__main__":
    analyze_specific_systems() 