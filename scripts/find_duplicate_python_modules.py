#!/usr/bin/env python3

"""
Find duplicate Python modules in the Visual DM project.
This script analyzes Python files to find duplicates based on:
- Exact file matches
- Module name duplicates
- Similar content (fuzzy matching)

Usage: python find_duplicate_python_modules.py [project_root] [output_file]
"""

import os
import sys
import hashlib
import json
import re
from collections import defaultdict
import difflib

class DuplicateAnalyzer:
    def __init__(self, root_dir):
        """Initialize the analyzer with the project root directory."""
        self.root_dir = os.path.abspath(root_dir)
        self.py_files = []
        self.file_hashes = {}
        self.module_names = defaultdict(list)
        self.exact_duplicates = {}
        self.name_duplicates = {}
        self.module_duplicates = {}
        self.fuzzy_duplicates = {}
        
    def scan_files(self):
        """Scan the project directory for Python files and analyze them."""
        print(f"Scanning Python files in {self.root_dir}...")
        for root, _, files in os.walk(self.root_dir):
            # Skip .git, __pycache__, venv, etc.
            if any(skip in root for skip in ['.git', '__pycache__', 'venv', 'env', 'node_modules']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.root_dir)
                    
                    try:
                        # Get file hash for exact duplicate detection
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                            file_hash = hashlib.md5(file_content).hexdigest()
                            
                        # Process module name
                        module_name = os.path.splitext(file)[0]
                        
                        # Check if the file contains class definitions
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Extract module imports
                            module_imports = re.findall(r'(?:from|import)\s+([a-zA-Z0-9_.]+)', content)
                            
                        # Store file info
                        file_info = {
                            'path': file_path,
                            'relative_path': relative_path,
                            'hash': file_hash,
                            'module_name': module_name,
                            'imports': module_imports
                        }
                        
                        self.py_files.append(file_info)
                        
                        # Track by hash for exact duplicates
                        if file_hash not in self.file_hashes:
                            self.file_hashes[file_hash] = []
                        self.file_hashes[file_hash].append(file_info)
                        
                        # Track by module name
                        self.module_names[module_name].append(file_info)
                        
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
        
        print(f"Found {len(self.py_files)} Python files.")
        return self.py_files
        
    def find_exact_duplicates(self):
        """Find files with identical content based on hash."""
        self.exact_duplicates = {hash: files for hash, files in self.file_hashes.items() if len(files) > 1}
        print(f"Found {len(self.exact_duplicates)} exact duplicate groups.")
        return self.exact_duplicates
        
    def find_name_duplicates(self):
        """Find files with the same module name."""
        self.name_duplicates = {name: files for name, files in self.module_names.items() if len(files) > 1}
        print(f"Found {len(self.name_duplicates)} module name duplicate groups.")
        return self.name_duplicates
        
    def find_module_duplicates(self):
        """Find modules with similar import patterns, suggesting related functionality."""
        # Group modules by their import patterns
        import_groups = defaultdict(list)
        for file_info in self.py_files:
            imports_key = ','.join(sorted(file_info['imports']))
            if imports_key and len(file_info['imports']) > 3:  # Only consider files with significant imports
                import_groups[imports_key].append(file_info)
        
        self.module_duplicates = {imports: files for imports, files in import_groups.items() if len(files) > 1}
        print(f"Found {len(self.module_duplicates)} module duplicate groups.")
        return self.module_duplicates
        
    def find_fuzzy_duplicates(self):
        """Find files with similar content (fuzzy matching)."""
        # Compare files with similar module names
        for module_name, files in self.name_duplicates.items():
            if len(files) > 1:
                similar_files = self.analyze_similarity(files)
                if similar_files:
                    self.fuzzy_duplicates[module_name] = similar_files
        
        print(f"Found {len(self.fuzzy_duplicates)} fuzzy duplicate groups.")
        return self.fuzzy_duplicates
        
    def compare_file_content(self, file1, file2):
        """Compare the content similarity between two files."""
        try:
            with open(file1, 'r', encoding='utf-8', errors='ignore') as f1:
                content1 = f1.readlines()
            with open(file2, 'r', encoding='utf-8', errors='ignore') as f2:
                content2 = f2.readlines()
            
            # Use difflib to compute similarity ratio
            similarity = difflib.SequenceMatcher(None, ''.join(content1), ''.join(content2)).ratio()
            
            return similarity
        except Exception as e:
            print(f"Error comparing {file1} and {file2}: {e}")
            return 0.0
            
    def analyze_similarity(self, file_list, threshold=0.7):
        """Analyze the similarity between multiple files."""
        result = []
        file_paths = [file_info['path'] for file_info in file_list]
        
        for i in range(len(file_paths)):
            similar_files = []
            for j in range(len(file_paths)):
                if i != j:
                    similarity = self.compare_file_content(file_paths[i], file_paths[j])
                    if similarity >= threshold:
                        similar_files.append({
                            'path': file_list[j]['relative_path'],
                            'similarity': similarity
                        })
            
            if similar_files:
                result.append({
                    'path': file_list[i]['relative_path'],
                    'similar_files': similar_files
                })
                
        return result
        
    def generate_report(self, output_file=None):
        """Generate a comprehensive report of duplicate findings."""
        # Make sure we've done all analysis
        self.find_exact_duplicates()
        self.find_name_duplicates()
        self.find_module_duplicates()
        self.find_fuzzy_duplicates()
        
        report = {
            'summary': {
                'total_python_files': len(self.py_files),
                'exact_duplicate_groups': len(self.exact_duplicates),
                'name_duplicate_groups': len(self.name_duplicates),
                'module_duplicate_groups': len(self.module_duplicates),
                'fuzzy_duplicate_groups': len(self.fuzzy_duplicates)
            },
            'exact_duplicates': {},
            'name_duplicates': {},
            'module_duplicates': {},
            'fuzzy_duplicates': {}
        }
        
        # Format exact duplicates
        for hash_value, files in self.exact_duplicates.items():
            paths = [f['relative_path'] for f in files]
            report['exact_duplicates'][hash_value] = paths
        
        # Format name duplicates
        for module_name, files in self.name_duplicates.items():
            paths = [f['relative_path'] for f in files]
            report['name_duplicates'][module_name] = paths
            
        # Format module duplicates
        for imports, files in self.module_duplicates.items():
            module_key = f"shared_imports_{len(files)}"
            paths = [f['relative_path'] for f in files]
            report['module_duplicates'][module_key] = {
                'imports': imports.split(','),
                'files': paths
            }
            
        # Format fuzzy duplicates
        for module_name, similar_groups in self.fuzzy_duplicates.items():
            report['fuzzy_duplicates'][module_name] = similar_groups
            
        # Print summary to console
        print("\nDuplicate Analysis Summary:")
        print(f"Total Python files: {report['summary']['total_python_files']}")
        print(f"Exact duplicate groups: {report['summary']['exact_duplicate_groups']}")
        print(f"Module name duplicate groups: {report['summary']['name_duplicate_groups']}")
        print(f"Module duplicate groups: {report['summary']['module_duplicate_groups']}")
        print(f"Fuzzy duplicate groups: {report['summary']['fuzzy_duplicate_groups']}")
        
        # Write report to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nDetailed report written to {output_file}")
            
        return report

def main():
    """Main function to run the duplicate analyzer."""
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python find_duplicate_python_modules.py [project_root] [output_file]")
        sys.exit(1)
        
    project_root = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "python_duplicates_report.json"
    
    # Run analyzer
    analyzer = DuplicateAnalyzer(project_root)
    analyzer.scan_files()
    analyzer.generate_report(output_file)

if __name__ == "__main__":
    main() 