#!/usr/bin/env python3
"""
Analyze what is actually being tested according to coverage data
"""

import json
import os

def analyze_actual_coverage():
    """Analyze what files/systems actually have coverage"""
    
    if not os.path.exists('coverage.json'):
        print("❌ No coverage.json file found.")
        return
    
    with open('coverage.json', 'r') as f:
        data = json.load(f)
    
    print("=== COVERAGE OVERVIEW ===")
    totals = data.get('totals', {})
    print(f"Total lines: {totals.get('num_statements', 0)}")
    print(f"Covered lines: {totals.get('covered_lines', 0)}")
    print(f"Overall coverage: {totals.get('percent_covered', 0):.1f}%")
    
    print("\n=== SYSTEMS WITH COVERAGE ===")
    system_coverage = {}
    files = data.get('files', {})
    
    for file_path, file_data in files.items():
        if file_path.startswith('backend/systems/'):
            parts = file_path.split('/')
            if len(parts) > 2:
                system = parts[2]
                if system not in system_coverage:
                    system_coverage[system] = {'files': 0, 'total_lines': 0, 'covered_lines': 0}
                
                summary = file_data.get('summary', {})
                system_coverage[system]['files'] += 1
                system_coverage[system]['total_lines'] += summary.get('num_statements', 0)
                system_coverage[system]['covered_lines'] += summary.get('covered_lines', 0)
    
    # Sort by coverage percentage
    sorted_systems = []
    for system, stats in system_coverage.items():
        if stats['total_lines'] > 0:
            pct = (stats['covered_lines'] / stats['total_lines']) * 100
            sorted_systems.append((system, pct, stats))
    
    sorted_systems.sort(key=lambda x: x[1], reverse=True)
    
    for system, pct, stats in sorted_systems:
        status = "✅" if pct > 70 else "⚠️" if pct > 30 else "❌"
        print(f"{status} {pct:5.1f}% - {system:20s} - {stats['files']:3d} files, {stats['covered_lines']:5d}/{stats['total_lines']:5d} lines")
    
    print(f"\n=== DETAILED BREAKDOWN ===")
    
    # Group by coverage level
    high_coverage = [s for s, p, _ in sorted_systems if p > 70]
    medium_coverage = [s for s, p, _ in sorted_systems if 30 <= p <= 70]
    low_coverage = [s for s, p, _ in sorted_systems if p < 30]
    
    print(f"🟢 HIGH COVERAGE (>70%): {len(high_coverage)} systems")
    for system in high_coverage[:10]:  # Show top 10
        print(f"   - {system}")
    if len(high_coverage) > 10:
        print(f"   ... and {len(high_coverage) - 10} more")
    
    print(f"\n🟡 MEDIUM COVERAGE (30-70%): {len(medium_coverage)} systems")
    for system in medium_coverage:
        print(f"   - {system}")
    
    print(f"\n🔴 LOW COVERAGE (<30%): {len(low_coverage)} systems")
    for system in low_coverage:
        print(f"   - {system}")
    
    # Show some specific files with high coverage
    print(f"\n=== TOP COVERED FILES (by coverage %) ===")
    file_coverage = []
    for file_path, file_data in files.items():
        if file_path.startswith('backend/systems/'):
            summary = file_data.get('summary', {})
            if summary.get('num_statements', 0) > 0:
                pct = (summary.get('covered_lines', 0) / summary.get('num_statements', 0)) * 100
                file_coverage.append((file_path, pct, summary.get('num_statements', 0)))
    
    # Sort by coverage percentage and show top 20
    file_coverage.sort(key=lambda x: x[1], reverse=True)
    for file_path, pct, statements in file_coverage[:20]:
        system = file_path.split('/')[2] if len(file_path.split('/')) > 2 else 'unknown'
        filename = file_path.split('/')[-1]
        print(f"{pct:5.1f}% - {system:15s} - {filename}")
    
    print(f"\n=== DIRECTORY LEVEL ANALYSIS ===")
    # Analyze at directory level within each system
    directory_coverage = {}
    
    for file_path, file_data in files.items():
        if file_path.startswith('backend/systems/'):
            parts = file_path.split('/')
            if len(parts) > 3:
                # backend/systems/SYSTEM/DIRECTORY/...
                system = parts[2]
                directory = parts[3]
                key = f"{system}/{directory}"
                
                if key not in directory_coverage:
                    directory_coverage[key] = {'files': 0, 'total_lines': 0, 'covered_lines': 0}
                
                summary = file_data.get('summary', {})
                directory_coverage[key]['files'] += 1
                directory_coverage[key]['total_lines'] += summary.get('num_statements', 0)
                directory_coverage[key]['covered_lines'] += summary.get('covered_lines', 0)
    
    # Show directories with highest coverage
    sorted_dirs = []
    for dir_path, stats in directory_coverage.items():
        if stats['total_lines'] > 0:
            pct = (stats['covered_lines'] / stats['total_lines']) * 100
            sorted_dirs.append((dir_path, pct, stats))
    
    sorted_dirs.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Top 30 directories by coverage:")
    for dir_path, pct, stats in sorted_dirs[:30]:
        status = "✅" if pct > 70 else "⚠️" if pct > 30 else "❌"
        print(f"{status} {pct:5.1f}% - {dir_path:35s} - {stats['files']:2d} files")

if __name__ == "__main__":
    analyze_actual_coverage() 