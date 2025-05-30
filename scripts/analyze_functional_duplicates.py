#!/usr/bin/env python3
"""
Functional Duplication Analysis Script
Finds actual code duplication beyond just organizational issues.
"""

import os
import ast
import hashlib
from pathlib import Path
from collections import defaultdict, Counter

class FunctionalDuplicationAnalyzer:
    def __init__(self, systems_path="backend/systems"):
        self.systems_path = Path(systems_path)
        self.function_signatures = defaultdict(list)
        self.function_bodies = defaultdict(list)
        self.class_signatures = defaultdict(list)
        self.duplicate_files = defaultdict(list)
        
    def analyze_file(self, file_path):
        """Analyze a Python file for functions and classes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Function signature
                    args = [arg.arg for arg in node.args.args]
                    signature = f"{node.name}({', '.join(args)})"
                    self.function_signatures[signature].append(str(file_path))
                    
                    # Function body hash (for exact duplication detection)
                    body_source = ast.get_source_segment(content, node)
                    if body_source:
                        body_hash = hashlib.md5(body_source.encode()).hexdigest()[:8]
                        self.function_bodies[body_hash].append((str(file_path), node.name, signature))
                
                elif isinstance(node, ast.ClassDef):
                    # Class signatures
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    class_sig = f"{node.name}({', '.join(methods)})"
                    self.class_signatures[class_sig].append(str(file_path))
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def find_duplicate_files(self):
        """Find files with identical or very similar names"""
        file_names = defaultdict(list)
        
        for file_path in self.systems_path.rglob("*.py"):
            if '__pycache__' in str(file_path):
                continue
                
            name = file_path.name
            # Group similar names
            base_name = name.replace('.py', '').replace('_', '').lower()
            file_names[base_name].append(str(file_path))
        
        # Find duplicates
        for base_name, files in file_names.items():
            if len(files) > 1:
                self.duplicate_files[base_name] = files
    
    def analyze_all(self):
        """Run complete analysis"""
        print("🔍 ANALYZING FUNCTIONAL DUPLICATION...")
        
        python_files = list(self.systems_path.rglob("*.py"))
        total_files = len([f for f in python_files if '__pycache__' not in str(f)])
        
        print(f"📁 Analyzing {total_files} Python files...")
        
        for file_path in python_files:
            if '__pycache__' in str(file_path):
                continue
            self.analyze_file(file_path)
        
        self.find_duplicate_files()
        self.print_analysis()
    
    def print_analysis(self):
        """Print analysis results"""
        print("\n" + "="*60)
        print("FUNCTIONAL DUPLICATION ANALYSIS RESULTS")
        print("="*60)
        
        # Duplicate function signatures
        duplicate_functions = {sig: files for sig, files in self.function_signatures.items() 
                             if len(files) > 1}
        
        print(f"\n🔥 DUPLICATE FUNCTION SIGNATURES: {len(duplicate_functions)}")
        for signature, files in sorted(duplicate_functions.items()):
            if len(files) > 3:  # Only show significant duplicates
                print(f"• {signature}")
                for file in files[:5]:  # Show first 5
                    system = file.split('/')[2] if '/' in file else 'unknown'
                    print(f"  └─ {system}: {file.split('/')[-1]}")
                if len(files) > 5:
                    print(f"  └─ ... and {len(files) - 5} more")
        
        # Identical function bodies
        identical_bodies = {hash_val: funcs for hash_val, funcs in self.function_bodies.items() 
                           if len(funcs) > 1}
        
        print(f"\n💀 IDENTICAL FUNCTION BODIES: {len(identical_bodies)}")
        for hash_val, funcs in sorted(identical_bodies.items()):
            if len(funcs) > 1:
                print(f"• Hash {hash_val}: {funcs[0][1]}() - {len(funcs)} copies")
                for file, func_name, signature in funcs[:3]:
                    system = file.split('/')[2] if '/' in file else 'unknown'
                    print(f"  └─ {system}: {file.split('/')[-1]}")
        
        # Duplicate file names
        print(f"\n📋 DUPLICATE FILE NAMES: {len(self.duplicate_files)}")
        total_duplicate_files = 0
        for base_name, files in sorted(self.duplicate_files.items()):
            if len(files) > 1:
                print(f"• {base_name}.py - {len(files)} versions:")
                total_duplicate_files += len(files) - 1  # Count extras
                for file in files:
                    system = file.split('/')[2] if '/' in file else 'unknown'
                    size = Path(file).stat().st_size if Path(file).exists() else 0
                    print(f"  └─ {system}: {size:,} bytes")
        
        # Summary statistics
        print(f"\n📊 DUPLICATION SUMMARY:")
        print(f"• Function signature duplicates: {len(duplicate_functions)}")
        print(f"• Identical function bodies: {len(identical_bodies)}")
        print(f"• Duplicate file names: {len(self.duplicate_files)}")
        print(f"• Extra files that could be eliminated: {total_duplicate_files}")
        
        # Estimate code reduction potential
        total_functions = len(self.function_signatures)
        duplicate_function_count = sum(len(files) - 1 for files in duplicate_functions.values())
        
        if total_functions > 0:
            duplicate_percentage = (duplicate_function_count / total_functions) * 100
            print(f"• Potential function reduction: {duplicate_percentage:.1f}%")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if len(duplicate_functions) > 10:
            print("• CRITICAL: High function duplication - immediate refactoring needed")
        if len(identical_bodies) > 5:
            print("• URGENT: Identical code blocks - consolidate immediately")
        if len(self.duplicate_files) > 20:
            print("• HIGH: Many duplicate files - review and merge")
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Review duplicate function signatures for consolidation")
        print("2. Merge identical function bodies")
        print("3. Eliminate redundant files")
        print("4. Create shared utility modules")
        print("5. Update imports after consolidation")

def main():
    analyzer = FunctionalDuplicationAnalyzer()
    analyzer.analyze_all()

if __name__ == "__main__":
    main() 