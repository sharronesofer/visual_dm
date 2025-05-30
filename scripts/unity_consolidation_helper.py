#!/usr/bin/env python3
"""
Unity Consolidation Helper Script

This script helps identify potential duplicates in the Unity codebase and generates
reports to assist with the consolidation process.
"""

import os
import re
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Optional
import glob
import fnmatch

# Configuration
UNITY_PROJECT_PATH = "../VDM"
DEFAULT_OUTPUT_DIR = "consolidation_reports"


@dataclass
class CodeFile:
    """Represents a code file in the Unity project."""
    path: str
    namespace: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    referenced_namespaces: List[str] = field(default_factory=list)
    referenced_classes: List[str] = field(default_factory=list)
    script_size: int = 0
    last_modified: str = ""


@dataclass
class DuplicateClassReport:
    """Report for duplicate class implementations."""
    class_name: str
    implementations: List[CodeFile] = field(default_factory=list)
    reference_count: Dict[str, int] = field(default_factory=dict)
    recommendation: str = ""


@dataclass
class ConsolidationReport:
    """Overall consolidation report."""
    duplicate_classes: List[DuplicateClassReport] = field(default_factory=list)
    circular_dependencies: List[str] = field(default_factory=list)
    static_reference_patterns: List[str] = field(default_factory=list)
    asset_stats: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


def find_csharp_files(root_dir: str) -> List[str]:
    """Find all C# files in the Unity project."""
    return [
        os.path.normpath(path)
        for path in glob.glob(f"{root_dir}/**/*.cs", recursive=True)
    ]


def extract_namespace(content: str) -> Optional[str]:
    """Extract namespace from C# file content."""
    namespace_match = re.search(r'namespace\s+([^\s{]+)', content)
    if namespace_match:
        return namespace_match.group(1)
    return None


def extract_classes(content: str) -> List[str]:
    """Extract class names from C# file content."""
    class_matches = re.finditer(
        r'(public|private|protected|internal)?\s*class\s+(\w+)', content)
    return [match.group(2) for match in class_matches]


def extract_references(content: str) -> (List[str], List[str]):
    """Extract namespace and class references from file content."""
    using_matches = re.finditer(r'using\s+([^;]+);', content)
    referenced_namespaces = [match.group(1) for match in using_matches]
    
    # Extract direct class references (simple approach, may miss some)
    words = re.findall(r'\b[A-Z][a-zA-Z0-9]*\b', content)
    potential_classes = set([w for w in words if w[0].isupper() and w != 'I'])
    
    return referenced_namespaces, list(potential_classes)


def analyze_file(file_path: str) -> CodeFile:
    """Analyze a C# file and extract key information."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        namespace = extract_namespace(content)
        classes = extract_classes(content)
        ref_namespaces, ref_classes = extract_references(content)
        
        stats = os.stat(file_path)
        
        return CodeFile(
            path=file_path,
            namespace=namespace,
            classes=classes,
            referenced_namespaces=ref_namespaces,
            referenced_classes=ref_classes,
            script_size=len(content),
            last_modified=stats.st_mtime
        )
    except Exception as e:
        print(f"Error analyzing file {file_path}: {e}")
        return CodeFile(path=file_path)


def find_duplicate_classes(files: List[CodeFile]) -> List[DuplicateClassReport]:
    """Find classes that have multiple implementations."""
    class_to_files: Dict[str, List[CodeFile]] = {}
    
    # Group files by class names
    for file in files:
        for class_name in file.classes:
            if class_name not in class_to_files:
                class_to_files[class_name] = []
            class_to_files[class_name].append(file)
    
    # Create reports for duplicate classes
    duplicate_reports = []
    for class_name, implementations in class_to_files.items():
        if len(implementations) > 1:
            report = DuplicateClassReport(
                class_name=class_name,
                implementations=implementations
            )
            
            # Count references to each implementation
            for impl in implementations:
                rel_path = os.path.relpath(impl.path, UNITY_PROJECT_PATH)
                report.reference_count[rel_path] = 0
            
            # Generate recommendation based on implementation details
            if "Manager" in class_name:
                report.recommendation = f"Consolidate {class_name} implementations, retaining the most comprehensive version with all required functionality."
            else:
                report.recommendation = f"Review {class_name} implementations for possible consolidation."
                
            duplicate_reports.append(report)
    
    return duplicate_reports


def find_circular_dependencies(files: List[CodeFile]) -> List[str]:
    """Identify potential circular dependencies in the codebase."""
    namespace_to_refs: Dict[str, Set[str]] = {}
    
    # Build dependency graph
    for file in files:
        if file.namespace:
            if file.namespace not in namespace_to_refs:
                namespace_to_refs[file.namespace] = set()
                
            for ref_ns in file.referenced_namespaces:
                if ref_ns != file.namespace:  # Skip self-references
                    namespace_to_refs[file.namespace].add(ref_ns)
    
    # Simple cycle detection (this is a basic approach and may miss some cycles)
    circular_deps = []
    for ns, refs in namespace_to_refs.items():
        for ref in refs:
            if ref in namespace_to_refs and ns in namespace_to_refs[ref]:
                circular_deps.append(f"Circular dependency: {ns} <-> {ref}")
    
    return circular_deps


def find_static_references(files: List[CodeFile]) -> List[str]:
    """Find patterns of static references that might indicate tight coupling."""
    static_patterns = []
    
    static_instance_pattern = re.compile(r'(\w+)\.Instance')
    
    for file in files:
        try:
            with open(file.path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            matches = static_instance_pattern.findall(content)
            if matches:
                unique_instances = set(matches)
                for instance in unique_instances:
                    if instance not in ['this', 'base', 'null', 'true', 'false']:
                        rel_path = os.path.relpath(file.path, UNITY_PROJECT_PATH)
                        static_patterns.append(f"{rel_path}: Uses {instance}.Instance")
        except Exception as e:
            print(f"Error searching for static references in {file.path}: {e}")
    
    return static_patterns


def analyze_asset_directories() -> Dict[str, int]:
    """Analyze asset directories for statistics."""
    asset_stats = {}
    
    # Count files in key directories
    for dir_name in ['Scripts', 'VisualDM', 'Resources', 'Prefabs']:
        dir_path = os.path.join(UNITY_PROJECT_PATH, 'Assets', dir_name)
        if os.path.exists(dir_path):
            file_count = sum(len(files) for _, _, files in os.walk(dir_path))
            asset_stats[dir_name] = file_count
    
    return asset_stats


def generate_consolidation_report(files: List[CodeFile]) -> ConsolidationReport:
    """Generate a complete consolidation report."""
    report = ConsolidationReport()
    
    print("Finding duplicate classes...")
    report.duplicate_classes = find_duplicate_classes(files)
    
    print("Analyzing for circular dependencies...")
    report.circular_dependencies = find_circular_dependencies(files)
    
    print("Finding static reference patterns...")
    report.static_reference_patterns = find_static_references(files)
    
    print("Analyzing asset directory statistics...")
    report.asset_stats = analyze_asset_directories()
    
    # Generate general recommendations
    report.recommendations = [
        "Consolidate duplicate managers into single implementations",
        "Replace static Instance references with dependency injection where possible",
        "Break circular dependencies by introducing interfaces",
        "Move assets from the nested VisualDM directory to the appropriate locations",
        "Update the Bootstrap scene to reference the consolidated scripts"
    ]
    
    return report


def analyze_project(output_dir: str):
    """Analyze the Unity project and generate consolidation reports."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Analyzing Unity project at: {UNITY_PROJECT_PATH}")
    
    # Find all C# files
    print("Finding C# files...")
    csharp_files = find_csharp_files(UNITY_PROJECT_PATH)
    print(f"Found {len(csharp_files)} C# files")
    
    # Analyze each file
    print("Analyzing files...")
    analyzed_files = []
    for file_path in csharp_files:
        analyzed_files.append(analyze_file(file_path))
    
    # Generate comprehensive report
    print("Generating consolidation report...")
    report = generate_consolidation_report(analyzed_files)
    
    # Save report as JSON
    report_path = os.path.join(output_dir, "consolidation_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(report), f, indent=2)
    
    # Generate a more readable text summary
    summary_path = os.path.join(output_dir, "consolidation_summary.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Unity Project Consolidation Summary\n\n")
        
        f.write("## Duplicate Classes\n")
        for i, dup in enumerate(report.duplicate_classes, 1):
            f.write(f"{i}. **{dup.class_name}**\n")
            f.write(f"   - Implementations: {len(dup.implementations)}\n")
            for impl in dup.implementations:
                rel_path = os.path.relpath(impl.path, UNITY_PROJECT_PATH)
                f.write(f"     - {rel_path} (Namespace: {impl.namespace})\n")
            f.write(f"   - Recommendation: {dup.recommendation}\n\n")
        
        f.write("## Circular Dependencies\n")
        for dep in report.circular_dependencies:
            f.write(f"- {dep}\n")
        f.write("\n")
        
        f.write("## Static Reference Patterns\n")
        static_refs_count = len(report.static_reference_patterns)
        f.write(f"Found {static_refs_count} static reference patterns.\n")
        if static_refs_count > 0:
            f.write("Top 20 examples:\n")
            for pattern in report.static_reference_patterns[:20]:
                f.write(f"- {pattern}\n")
        f.write("\n")
        
        f.write("## Asset Statistics\n")
        for dir_name, count in report.asset_stats.items():
            f.write(f"- {dir_name}: {count} files\n")
        f.write("\n")
        
        f.write("## Recommendations\n")
        for i, rec in enumerate(report.recommendations, 1):
            f.write(f"{i}. {rec}\n")
    
    print(f"Report saved to {report_path}")
    print(f"Summary saved to {summary_path}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Analyze Unity project for consolidation')
    parser.add_argument('--project', default=UNITY_PROJECT_PATH,
                        help='Path to Unity project')
    parser.add_argument('--output', default=DEFAULT_OUTPUT_DIR,
                        help='Output directory for reports')
    
    args = parser.parse_args()
    
    global UNITY_PROJECT_PATH
    UNITY_PROJECT_PATH = args.project
    
    analyze_project(args.output)


if __name__ == "__main__":
    main() 