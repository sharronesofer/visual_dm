#!/usr/bin/env python3
"""
TypeScript File Analyzer

This script analyzes TypeScript files to identify:
1. Import dependencies (both internal and external)
2. Export structures
3. TypeScript-specific features used
4. Estimated complexity

Output: CSV and JSON reports of the TypeScript file inventory with analysis.
"""

import os
import re
import csv
import json
import glob
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any, Optional

# Patterns for TypeScript analysis
TS_IMPORT_PATTERN = re.compile(r'import\s+(?:{([^}]*)}\s+from\s+)?[\'\"]([^\'\"]+)[\'\"](;?)')
TS_EXPORT_PATTERN = re.compile(r'export\s+(?:default\s+)?(?:(class|interface|enum|const|type|function)\s+)?(\w+)')
TS_INTERFACE_PATTERN = re.compile(r'interface\s+(\w+)(?:\s+extends\s+(\w+))?')
TS_TYPE_PATTERN = re.compile(r'type\s+(\w+)\s*=')
TS_GENERIC_PATTERN = re.compile(r'<(\w+(?:,\s*\w+)*)>')
TS_ENUM_PATTERN = re.compile(r'enum\s+(\w+)')
TS_DECORATOR_PATTERN = re.compile(r'@(\w+)(?:\(.*\))?')

# Complexity factors
COMPLEXITY_FACTORS = {
    'imports': 0.1,       # Each import adds 0.1
    'exports': 0.2,       # Each export adds 0.2
    'interfaces': 0.5,    # Each interface adds 0.5
    'types': 0.3,         # Each type alias adds 0.3
    'generics': 0.4,      # Each generic adds 0.4
    'enums': 0.2,         # Each enum adds 0.2
    'decorators': 0.3,    # Each decorator adds 0.3
    'lines': 0.01,        # Each line adds 0.01
    'advanced_types': 0.5 # Each advanced type (union, intersection) adds 0.5
}

class TypeScriptFile:
    """Represents a TypeScript file with analysis information."""
    
    def __init__(self, path: str):
        self.path = path
        self.content = ""
        self.imports: List[Tuple[str, List[str]]] = []  # (module_path, [imported_items])
        self.exports: List[Tuple[str, str]] = []  # (export_type, name)
        self.interfaces: List[str] = []
        self.types: List[str] = []
        self.generics: List[str] = []
        self.enums: List[str] = []
        self.decorators: List[str] = []
        self.has_advanced_types = False
        self.line_count = 0
        self.complexity = 0.0
        
    def load_content(self) -> None:
        """Load file content."""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.line_count = len(self.content.splitlines())
        except Exception as e:
            print(f"Error loading file {self.path}: {e}")
            self.content = ""
            
    def analyze(self) -> None:
        """Analyze the TypeScript file content."""
        if not self.content:
            self.load_content()
        
        # Analyze imports
        for match in TS_IMPORT_PATTERN.finditer(self.content):
            imported_items = []
            if match.group(1):
                imported_items = [item.strip() for item in match.group(1).split(',')]
            module_path = match.group(2)
            self.imports.append((module_path, imported_items))
        
        # Analyze exports
        for match in TS_EXPORT_PATTERN.finditer(self.content):
            export_type = match.group(1) if match.group(1) else "variable"
            export_name = match.group(2)
            self.exports.append((export_type, export_name))
        
        # Analyze interfaces
        for match in TS_INTERFACE_PATTERN.finditer(self.content):
            self.interfaces.append(match.group(1))
        
        # Analyze type aliases
        for match in TS_TYPE_PATTERN.finditer(self.content):
            self.types.append(match.group(1))
        
        # Analyze generics
        for match in TS_GENERIC_PATTERN.finditer(self.content):
            for generic in match.group(1).split(','):
                self.generics.append(generic.strip())
        
        # Analyze enums
        for match in TS_ENUM_PATTERN.finditer(self.content):
            self.enums.append(match.group(1))
        
        # Analyze decorators
        for match in TS_DECORATOR_PATTERN.finditer(self.content):
            self.decorators.append(match.group(1))
        
        # Check for advanced types
        self.has_advanced_types = '|' in self.content or '&' in self.content
        
        # Calculate complexity
        self.calculate_complexity()
    
    def calculate_complexity(self) -> None:
        """Calculate estimated complexity score."""
        self.complexity = (
            len(self.imports) * COMPLEXITY_FACTORS['imports'] +
            len(self.exports) * COMPLEXITY_FACTORS['exports'] +
            len(self.interfaces) * COMPLEXITY_FACTORS['interfaces'] +
            len(self.types) * COMPLEXITY_FACTORS['types'] +
            len(self.generics) * COMPLEXITY_FACTORS['generics'] +
            len(self.enums) * COMPLEXITY_FACTORS['enums'] +
            len(self.decorators) * COMPLEXITY_FACTORS['decorators'] +
            self.line_count * COMPLEXITY_FACTORS['lines'] +
            (1 if self.has_advanced_types else 0) * COMPLEXITY_FACTORS['advanced_types']
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'path': self.path,
            'line_count': self.line_count,
            'imports': [{
                'module': module,
                'items': items
            } for module, items in self.imports],
            'exports': [{
                'type': export_type,
                'name': name
            } for export_type, name in self.exports],
            'interfaces': self.interfaces,
            'types': self.types,
            'generics': self.generics,
            'enums': self.enums,
            'decorators': self.decorators,
            'has_advanced_types': self.has_advanced_types,
            'complexity': round(self.complexity, 2)
        }
        
    def to_csv_row(self) -> Dict[str, Any]:
        """Convert to CSV row format."""
        # Count external vs internal imports
        external_imports = sum(1 for module, _ in self.imports 
                              if not module.startswith('.') and not module.startswith('/'))
        internal_imports = len(self.imports) - external_imports
        
        # Convert lists to comma-separated strings
        return {
            'path': self.path,
            'line_count': self.line_count,
            'complexity': round(self.complexity, 2),
            'exports_count': len(self.exports),
            'total_imports': len(self.imports),
            'external_imports': external_imports,
            'internal_imports': internal_imports,
            'interfaces_count': len(self.interfaces),
            'types_count': len(self.types),
            'enums_count': len(self.enums),
            'generics_count': len(self.generics),
            'decorators_count': len(self.decorators),
            'has_advanced_types': 'Yes' if self.has_advanced_types else 'No',
            'exports': ';'.join(f"{t}:{n}" for t, n in self.exports),
            'imported_modules': ';'.join(module for module, _ in self.imports)
        }


def find_ts_files(root_dir: str, exclude_patterns: List[str] = None) -> List[str]:
    """Find all TypeScript files in the directory."""
    if exclude_patterns is None:
        exclude_patterns = ['node_modules', 'dist', 'build', '.git']
    
    exclude_patterns = [os.path.join(root_dir, pattern) for pattern in exclude_patterns]
    
    ts_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        if any(dirpath.startswith(pattern) for pattern in exclude_patterns):
            continue
        
        for filename in filenames:
            if filename.endswith('.ts') and not filename.endswith('.d.ts'):
                ts_files.append(os.path.join(dirpath, filename))
    
    return ts_files


def analyze_ts_files(file_paths: List[str]) -> List[TypeScriptFile]:
    """Analyze a list of TypeScript files."""
    ts_files = []
    for i, path in enumerate(file_paths):
        if i % 100 == 0:
            print(f"Analyzing file {i+1}/{len(file_paths)}: {path}")
        
        ts_file = TypeScriptFile(path)
        try:
            ts_file.analyze()
            ts_files.append(ts_file)
        except Exception as e:
            print(f"Error analyzing {path}: {e}")
    
    return ts_files


def generate_dependency_graph(ts_files: List[TypeScriptFile]) -> Dict[str, List[str]]:
    """Generate a dependency graph of TypeScript files."""
    # Map file paths to their exports
    exports_by_path = {}
    relative_paths = {}
    
    for ts_file in ts_files:
        # Create a simplified relative path for comparison with imports
        rel_path = ts_file.path.replace('\\', '/')
        if rel_path.startswith('./'):
            rel_path = rel_path[2:]
        
        # Strip .ts extension for comparison
        if rel_path.endswith('.ts'):
            rel_path = rel_path[:-3]
        
        exports_by_path[rel_path] = [name for _, name in ts_file.exports]
        relative_paths[ts_file.path] = rel_path
    
    # Build dependency graph
    graph = defaultdict(list)
    
    for ts_file in ts_files:
        for module, _ in ts_file.imports:
            # Handle relative imports
            if module.startswith('.'):
                # Convert relative path to absolute path
                base_dir = os.path.dirname(ts_file.path)
                module_path = os.path.normpath(os.path.join(base_dir, module))
                
                # Find matching file
                for path, rel_path in relative_paths.items():
                    if module_path in path or module in rel_path:
                        graph[ts_file.path].append(path)
                        break
            else:
                # For external modules, just note the dependency
                graph[ts_file.path].append(f"external:{module}")
    
    return dict(graph)


def export_to_json(ts_files: List[TypeScriptFile], output_path: str) -> None:
    """Export analysis results to JSON file."""
    data = {
        'file_count': len(ts_files),
        'files': [ts_file.to_dict() for ts_file in ts_files]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"JSON report exported to {output_path}")


def export_to_csv(ts_files: List[TypeScriptFile], output_path: str) -> None:
    """Export analysis results to CSV file."""
    if not ts_files:
        print("No files to export")
        return
    
    fieldnames = list(ts_files[0].to_csv_row().keys())
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ts_file in ts_files:
            writer.writerow(ts_file.to_csv_row())
    
    print(f"CSV report exported to {output_path}")


def export_dependency_graph(dependency_graph: Dict[str, List[str]], output_path: str) -> None:
    """Export dependency graph to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dependency_graph, f, indent=2)
    
    print(f"Dependency graph exported to {output_path}")


def generate_summary(ts_files: List[TypeScriptFile]) -> Dict[str, Any]:
    """Generate summary statistics of the analysis."""
    if not ts_files:
        return {}
    
    total_lines = sum(ts_file.line_count for ts_file in ts_files)
    avg_complexity = sum(ts_file.complexity for ts_file in ts_files) / len(ts_files)
    
    # Count various features
    interface_count = sum(len(ts_file.interfaces) for ts_file in ts_files)
    type_count = sum(len(ts_file.types) for ts_file in ts_files)
    enum_count = sum(len(ts_file.enums) for ts_file in ts_files)
    decorator_count = sum(len(ts_file.decorators) for ts_file in ts_files)
    
    # Count files with advanced types
    advanced_types_count = sum(1 for ts_file in ts_files if ts_file.has_advanced_types)
    
    # Collect all external dependencies
    external_deps = set()
    for ts_file in ts_files:
        for module, _ in ts_file.imports:
            if not module.startswith('.') and not module.startswith('/'):
                external_deps.add(module)
    
    # Group files by complexity range
    complexity_ranges = {
        'Low (0-2)': 0,
        'Medium (2-5)': 0,
        'High (5-10)': 0,
        'Very High (10+)': 0
    }
    
    for ts_file in ts_files:
        if ts_file.complexity < 2:
            complexity_ranges['Low (0-2)'] += 1
        elif ts_file.complexity < 5:
            complexity_ranges['Medium (2-5)'] += 1
        elif ts_file.complexity < 10:
            complexity_ranges['High (5-10)'] += 1
        else:
            complexity_ranges['Very High (10+)'] += 1
    
    return {
        'file_count': len(ts_files),
        'total_lines': total_lines,
        'avg_lines_per_file': total_lines / len(ts_files),
        'avg_complexity': avg_complexity,
        'interface_count': interface_count,
        'type_count': type_count,
        'enum_count': enum_count,
        'decorator_count': decorator_count,
        'advanced_types_count': advanced_types_count,
        'external_dependencies': sorted(list(external_deps)),
        'external_dependencies_count': len(external_deps),
        'complexity_distribution': complexity_ranges
    }


def export_summary(summary: Dict[str, Any], output_path: str) -> None:
    """Export summary statistics to a text file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# TypeScript Files Analysis Summary\n\n")
        
        f.write(f"Total Files: {summary['file_count']}\n")
        f.write(f"Total Lines: {summary['total_lines']}\n")
        f.write(f"Average Lines per File: {summary['avg_lines_per_file']:.2f}\n")
        f.write(f"Average Complexity: {summary['avg_complexity']:.2f}\n\n")
        
        f.write("## TypeScript Feature Usage\n\n")
        f.write(f"Interfaces: {summary['interface_count']}\n")
        f.write(f"Type Aliases: {summary['type_count']}\n")
        f.write(f"Enums: {summary['enum_count']}\n")
        f.write(f"Decorators: {summary['decorator_count']}\n")
        f.write(f"Files with Advanced Types: {summary['advanced_types_count']}\n\n")
        
        f.write("## Complexity Distribution\n\n")
        for range_name, count in summary['complexity_distribution'].items():
            percentage = (count / summary['file_count']) * 100
            f.write(f"{range_name}: {count} files ({percentage:.1f}%)\n")
        f.write("\n")
        
        f.write("## External Dependencies\n\n")
        f.write(f"Total External Dependencies: {summary['external_dependencies_count']}\n\n")
        for dep in summary['external_dependencies']:
            f.write(f"- {dep}\n")
    
    print(f"Summary exported to {output_path}")


def main():
    """Main function."""
    print("TypeScript File Analyzer")
    print("=======================")
    
    # Create output directory if it doesn't exist
    output_dir = 'scripts/ts_analysis'
    os.makedirs(output_dir, exist_ok=True)
    
    # Load files from inventory or find them
    inventory_file = 'ts_files_inventory.txt'
    if os.path.exists(inventory_file):
        print(f"Loading files from inventory: {inventory_file}")
        with open(inventory_file, 'r', encoding='utf-8') as f:
            file_paths = [line.strip() for line in f if line.strip()]
    else:
        print("Finding TypeScript files...")
        file_paths = find_ts_files('.')
        
        # Save inventory for future use
        with open(inventory_file, 'w', encoding='utf-8') as f:
            for path in file_paths:
                f.write(f"{path}\n")
    
    print(f"Found {len(file_paths)} TypeScript files.")
    
    # Analyze files
    print("Analyzing TypeScript files...")
    ts_files = analyze_ts_files(file_paths)
    
    # Generate dependency graph
    print("Generating dependency graph...")
    dependency_graph = generate_dependency_graph(ts_files)
    
    # Generate summary
    print("Generating summary...")
    summary = generate_summary(ts_files)
    
    # Export results
    print("Exporting results...")
    export_to_json(ts_files, f"{output_dir}/ts_analysis.json")
    export_to_csv(ts_files, f"{output_dir}/ts_analysis.csv")
    export_dependency_graph(dependency_graph, f"{output_dir}/ts_dependency_graph.json")
    export_summary(summary, f"{output_dir}/ts_analysis_summary.txt")
    
    print("\nAnalysis complete!")
    print(f"Results exported to directory: {output_dir}")


if __name__ == "__main__":
    main() 