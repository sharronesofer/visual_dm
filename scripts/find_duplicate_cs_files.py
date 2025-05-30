#!/usr/bin/env python3

"""
Find duplicate C# files in the Visual DM project.
This script analyzes C# files to find duplicates based on:
- Exact file matches
- Class name duplicates
- Singleton pattern implementations
- Manager classes with similar functionality
- Similar content based on fuzzy matching

Usage: python find_duplicate_cs_files.py [project_root] [output_file]
"""

import os
import sys
import hashlib
import json
import re
from collections import defaultdict
import difflib

class CSharpDuplicateAnalyzer:
    def __init__(self, root_dir):
        """Initialize the analyzer with the project root directory."""
        self.root_dir = os.path.abspath(root_dir)
        self.cs_files = []
        self.file_hashes = {}
        self.namespaces = defaultdict(list)
        self.classes = defaultdict(list)
        self.singletons = defaultdict(list)
        self.managers = defaultdict(list)
        
    def scan_files(self):
        """Scan the project directory for C# files and analyze them."""
        print(f"Scanning C# files in {self.root_dir}...")
        for root, _, files in os.walk(self.root_dir):
            # Skip certain directories
            if any(skip in root for skip in ['.git', 'obj', 'bin', 'Library', 'Temp', 'Logs']):
                continue
                
            for file in files:
                if file.endswith('.cs'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.root_dir)
                    
                    try:
                        # Get file hash for exact duplicate detection
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                            file_hash = hashlib.md5(file_content).hexdigest()
                            
                        # Analyze C# file contents
                        file_info = self._analyze_csharp_file(file_path, relative_path)
                        file_info['hash'] = file_hash
                        
                        self.cs_files.append(file_info)
                        
                        # Track by hash for exact duplicates
                        if file_hash not in self.file_hashes:
                            self.file_hashes[file_hash] = []
                        self.file_hashes[file_hash].append(file_info)
                        
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
        
        print(f"Found {len(self.cs_files)} C# files.")
        return self.cs_files
        
    def _analyze_csharp_file(self, file_path, relative_path):
        """Analyze a C# file to extract namespace, classes, and pattern information."""
        file_info = {
            'path': file_path,
            'relative_path': relative_path,
            'namespace': '',
            'classes': [],
            'is_singleton': False,
            'is_manager': False,
            'manager_type': ''
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Extract namespace
                namespace_match = re.search(r'namespace\s+([a-zA-Z0-9_.]+)', content)
                if namespace_match:
                    namespace = namespace_match.group(1)
                    file_info['namespace'] = namespace
                    self.namespaces[namespace].append(file_info)
                
                # Extract class definitions
                class_matches = re.finditer(r'(?:public|private|internal|protected)\s+(?:static\s+)?class\s+([a-zA-Z0-9_]+)', content)
                for match in class_matches:
                    class_name = match.group(1)
                    file_info['classes'].append(class_name)
                    self.classes[class_name].append(file_info)
                    
                    # Check for singleton pattern
                    if re.search(r'private\s+static\s+\w+\s+_instance', content) and \
                       re.search(r'(?:public|internal)\s+static\s+\w+\s+Instance', content):
                        file_info['is_singleton'] = True
                        self.singletons[class_name].append(file_info)
                    
                    # Check for manager classes
                    if class_name.endswith('Manager') or 'Manager' in class_name:
                        file_info['is_manager'] = True
                        # Extract prefix (e.g., GameManager -> Game)
                        prefix = class_name.replace('Manager', '')
                        file_info['manager_type'] = prefix
                        self.managers[prefix].append(file_info)
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return file_info
    
    def find_exact_duplicates(self):
        """Find files with identical content based on hash."""
        exact_duplicates = {hash: files for hash, files in self.file_hashes.items() if len(files) > 1}
        print(f"Found {len(exact_duplicates)} exact duplicate groups.")
        return exact_duplicates
        
    def find_namespace_duplicates(self):
        """Find namespaces that appear in multiple locations with different implementations."""
        namespace_duplicates = {}
        
        for namespace, files in self.namespaces.items():
            if len(files) > 1:
                # Check if files have different hashes
                hashes = {f['hash'] for f in files}
                if len(hashes) > 1:
                    namespace_duplicates[namespace] = files
        
        print(f"Found {len(namespace_duplicates)} namespace duplicate groups.")
        return namespace_duplicates
        
    def find_class_duplicates(self):
        """Find classes that appear in multiple locations with different implementations."""
        class_duplicates = {}
        
        for class_name, files in self.classes.items():
            if len(files) > 1:
                # Check if files have different hashes
                hashes = {f['hash'] for f in files}
                if len(hashes) > 1:
                    class_duplicates[class_name] = files
        
        print(f"Found {len(class_duplicates)} class duplicate groups.")
        return class_duplicates
        
    def find_singleton_duplicates(self):
        """Find singleton pattern implementations that appear in multiple locations."""
        singleton_duplicates = {name: files for name, files in self.singletons.items() if len(files) > 1}
        print(f"Found {len(singleton_duplicates)} singleton duplicate groups.")
        return singleton_duplicates
        
    def find_manager_duplicates(self):
        """Find manager classes with the same responsibility area."""
        manager_duplicates = {prefix: files for prefix, files in self.managers.items() 
                             if len(files) > 1 and len(prefix) > 0}
        print(f"Found {len(manager_duplicates)} manager duplicate groups.")
        return manager_duplicates
        
    def compare_file_content(self, file1, file2, threshold=0.7):
        """Compare the content similarity between two files."""
        try:
            with open(file1, 'r', encoding='utf-8', errors='ignore') as f1:
                content1 = f1.readlines()
            with open(file2, 'r', encoding='utf-8', errors='ignore') as f2:
                content2 = f2.readlines()
            
            # Use difflib to compute similarity ratio
            similarity = difflib.SequenceMatcher(None, ''.join(content1), ''.join(content2)).ratio()
            
            return {
                'file1': os.path.relpath(file1, self.root_dir),
                'file2': os.path.relpath(file2, self.root_dir),
                'similarity': similarity,
                'is_similar': similarity >= threshold
            }
        except Exception as e:
            print(f"Error comparing {file1} and {file2}: {e}")
            return {
                'file1': os.path.relpath(file1, self.root_dir),
                'file2': os.path.relpath(file2, self.root_dir),
                'similarity': 0.0,
                'is_similar': False,
                'error': str(e)
            }
            
    def find_similar_files(self, threshold=0.7):
        """Find files with similar content based on fuzzy matching."""
        similar_files = []
        
        # Compare class duplicates for similarity
        class_duplicates = self.find_class_duplicates()
        for class_name, files in class_duplicates.items():
            file_paths = [f['path'] for f in files]
            
            for i in range(len(file_paths)):
                for j in range(i+1, len(file_paths)):
                    similarity_info = self.compare_file_content(file_paths[i], file_paths[j], threshold)
                    if similarity_info['is_similar']:
                        similar_files.append({
                            'type': 'class_duplicate',
                            'class_name': class_name,
                            'similarity_info': similarity_info
                        })
        
        # Compare manager duplicates for similarity
        manager_duplicates = self.find_manager_duplicates()
        for prefix, files in manager_duplicates.items():
            file_paths = [f['path'] for f in files]
            
            for i in range(len(file_paths)):
                for j in range(i+1, len(file_paths)):
                    similarity_info = self.compare_file_content(file_paths[i], file_paths[j], threshold)
                    if similarity_info['is_similar']:
                        similar_files.append({
                            'type': 'manager_duplicate',
                            'manager_prefix': prefix,
                            'similarity_info': similarity_info
                        })
        
        print(f"Found {len(similar_files)} similar file pairs.")
        return similar_files
        
    def generate_report(self, output_file=None):
        """Generate a comprehensive report of duplicate findings."""
        # Run all analyses
        exact_duplicates = self.find_exact_duplicates()
        namespace_duplicates = self.find_namespace_duplicates()
        class_duplicates = self.find_class_duplicates()
        singleton_duplicates = self.find_singleton_duplicates()
        manager_duplicates = self.find_manager_duplicates()
        similar_files = self.find_similar_files()
        
        report = {
            'summary': {
                'total_cs_files': len(self.cs_files),
                'exact_duplicate_groups': len(exact_duplicates),
                'namespace_duplicate_groups': len(namespace_duplicates),
                'class_duplicate_groups': len(class_duplicates),
                'singleton_duplicate_groups': len(singleton_duplicates),
                'manager_duplicate_groups': len(manager_duplicates),
                'similar_file_pairs': len(similar_files)
            },
            'exact_duplicates': {},
            'namespace_duplicates': {},
            'class_duplicates': {},
            'singleton_duplicates': {},
            'manager_duplicates': {},
            'similar_files': similar_files
        }
        
        # Format exact duplicates
        for hash_value, files in exact_duplicates.items():
            paths = [f['relative_path'] for f in files]
            report['exact_duplicates'][hash_value] = paths
        
        # Format namespace duplicates
        for namespace, files in namespace_duplicates.items():
            paths = [f['relative_path'] for f in files]
            report['namespace_duplicates'][namespace] = paths
            
        # Format class duplicates
        for class_name, files in class_duplicates.items():
            paths = [f['relative_path'] for f in files]
            report['class_duplicates'][class_name] = paths
            
        # Format singleton duplicates
        for class_name, files in singleton_duplicates.items():
            paths = [f['relative_path'] for f in files]
            report['singleton_duplicates'][class_name] = paths
            
        # Format manager duplicates
        for prefix, files in manager_duplicates.items():
            paths = [f['relative_path'] for f in files]
            report['manager_duplicates'][prefix] = paths
            
        # Print summary to console
        print("\nDuplicate Analysis Summary:")
        print(f"Total C# files: {report['summary']['total_cs_files']}")
        print(f"Exact duplicate groups: {report['summary']['exact_duplicate_groups']}")
        print(f"Namespace duplicate groups: {report['summary']['namespace_duplicate_groups']}")
        print(f"Class duplicate groups: {report['summary']['class_duplicate_groups']}")
        print(f"Singleton duplicate groups: {report['summary']['singleton_duplicate_groups']}")
        print(f"Manager duplicate groups: {report['summary']['manager_duplicate_groups']}")
        print(f"Similar file pairs: {report['summary']['similar_file_pairs']}")
        
        # Write report to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nDetailed report written to {output_file}")
            
            # Also create a human-readable version
            txt_output = os.path.splitext(output_file)[0] + '.txt'
            with open(txt_output, 'w') as f:
                f.write("# Duplicate C# Files Report\n\n")
                
                f.write("## Summary\n")
                for key, value in report['summary'].items():
                    f.write(f"- {key}: {value}\n")
                
                f.write("\n## Manager Duplicates (highest priority to fix)\n")
                for prefix, paths in report['manager_duplicates'].items():
                    f.write(f"\n### '{prefix}Manager' appears in multiple locations\n")
                    for path in paths:
                        f.write(f"- {path}\n")
                
                f.write("\n## Singleton Duplicates\n")
                for class_name, paths in report['singleton_duplicates'].items():
                    f.write(f"\n### Singleton '{class_name}' appears in multiple locations\n")
                    for path in paths:
                        f.write(f"- {path}\n")
                
                f.write("\n## Class Duplicates\n")
                for class_name, paths in report['class_duplicates'].items():
                    f.write(f"\n### Class '{class_name}' appears in multiple locations\n")
                    for path in paths:
                        f.write(f"- {path}\n")
                
                f.write("\n## Namespace Duplicates\n")
                for namespace, paths in report['namespace_duplicates'].items():
                    f.write(f"\n### Namespace '{namespace}' appears in multiple locations\n")
                    for path in paths:
                        f.write(f"- {path}\n")
                
                f.write("\n## Exact Duplicates\n")
                for hash_value, paths in report['exact_duplicates'].items():
                    f.write(f"\n### Duplicate Group (hash: {hash_value[:8]})\n")
                    for path in paths:
                        f.write(f"- {path}\n")
                
                f.write("\n## Similar Files\n")
                for item in report['similar_files']:
                    f.write(f"\n### {item['type']}: {item.get('class_name', item.get('manager_prefix', 'Unknown'))}\n")
                    f.write(f"- {item['similarity_info']['file1']} and {item['similarity_info']['file2']}\n")
                    f.write(f"- Similarity: {item['similarity_info']['similarity']:.2%}\n")
            
            print(f"Human-readable report written to {txt_output}")
            
        return report

def main():
    """Main function to run the duplicate analyzer."""
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python find_duplicate_cs_files.py [project_root] [output_file]")
        sys.exit(1)
        
    project_root = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "cs_duplicates_report.json"
    
    # Run analyzer
    analyzer = CSharpDuplicateAnalyzer(project_root)
    analyzer.scan_files()
    analyzer.generate_report(output_file)

if __name__ == "__main__":
    main() 