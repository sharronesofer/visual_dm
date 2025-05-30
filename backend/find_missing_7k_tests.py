#!/usr/bin/env python3
"""
Find Missing 7K Tests

Identifies the root cause of why 7,229+ tests aren't being discovered.
"""

import os
import sys
import subprocess
from pathlib import Path
import re
import ast

class Missing7kTestFinder:
    def __init__(self, backend_root: str = None):
        self.backend_root = Path(backend_root or os.getcwd())
        print(f"Backend root: {self.backend_root}")
        self.all_test_files = []
        self.discovered_test_files = []
        self.missing_test_files = []
        
    def find_all_test_files(self):
        """Find ALL test files in the backend"""
        print("🔍 Finding ALL test files...")
        
        test_files = []
        for test_file in self.backend_root.glob("tests/**/*.py"):
            if test_file.name.startswith("test_") or test_file.name.endswith("_test.py"):
                test_files.append(test_file)
        
        self.all_test_files = test_files
        print(f"📋 Found {len(test_files)} total test files")
        return test_files
    
    def find_discovered_test_files(self):
        """Find which test files pytest is actually discovering"""
        print("🔍 Finding discovered test files...")
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', '--collect-only', '-q', '--tb=no'
            ], cwd=self.backend_root, capture_output=True, text=True, timeout=120)
            
            output = result.stdout + result.stderr
            lines = output.split('\n')
            
            discovered_files = set()
            for line in lines:
                # Look for file paths in pytest output
                if "tests/" in line and ".py" in line:
                    # Extract file path
                    match = re.search(r'(tests/[^:]+\.py)', line)
                    if match:
                        file_path = match.group(1)
                        discovered_files.add(file_path)
            
            self.discovered_test_files = list(discovered_files)
            print(f"📋 Pytest discovered {len(discovered_files)} test files")
            return list(discovered_files)
            
        except Exception as e:
            print(f"Error finding discovered files: {e}")
            return []
    
    def find_missing_test_files(self):
        """Find test files that aren't being discovered"""
        print("🔍 Finding missing test files...")
        
        all_relative_paths = set()
        for test_file in self.all_test_files:
            relative_path = str(test_file.relative_to(self.backend_root))
            all_relative_paths.add(relative_path)
        
        discovered_relative_paths = set(self.discovered_test_files)
        
        missing_paths = all_relative_paths - discovered_relative_paths
        self.missing_test_files = list(missing_paths)
        
        print(f"📋 Found {len(missing_paths)} missing test files")
        return list(missing_paths)
    
    def analyze_missing_file_patterns(self):
        """Analyze patterns in missing test files"""
        print("🔍 Analyzing missing file patterns...")
        
        # Group by directory
        directory_counts = {}
        for missing_file in self.missing_test_files:
            directory = '/'.join(missing_file.split('/')[:-1])
            directory_counts[directory] = directory_counts.get(directory, 0) + 1
        
        print(f"📊 MISSING FILES BY DIRECTORY:")
        for directory, count in sorted(directory_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {count:3d} files - {directory}")
        
        return directory_counts
    
    def check_import_issues_in_missing_files(self):
        """Check for import issues in missing test files"""
        print("🔍 Checking import issues in missing files...")
        
        import_issues = []
        syntax_issues = []
        
        for missing_file in self.missing_test_files[:50]:  # Check first 50
            file_path = self.backend_root / missing_file
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    
                    # Check for syntax issues
                    try:
                        ast.parse(content)
                    except SyntaxError as e:
                        syntax_issues.append({
                            'file': missing_file,
                            'error': str(e),
                            'line': e.lineno
                        })
                        continue
                    
                    # Check for problematic imports
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('from backend.') and 'import' in line:
                            # Try to simulate the import
                            try:
                                module_part = line.split('from ')[1].split(' import')[0].strip()
                                # Check if this module path exists
                                module_path = self.backend_root / module_part.replace('backend.', '').replace('.', '/')
                                
                                if not (module_path.exists() or (module_path.parent / f"{module_path.name}.py").exists()):
                                    import_issues.append({
                                        'file': missing_file,
                                        'line': i + 1,
                                        'import': line.strip(),
                                        'missing_module': module_part
                                    })
                            except:
                                pass
                
                except Exception as e:
                    syntax_issues.append({
                        'file': missing_file,
                        'error': f"Could not read file: {e}",
                        'line': 0
                    })
        
        print(f"📊 SYNTAX ISSUES: {len(syntax_issues)}")
        for issue in syntax_issues[:10]:
            print(f"  {issue['file']}:{issue['line']} - {issue['error']}")
        
        print(f"📊 IMPORT ISSUES: {len(import_issues)}")
        for issue in import_issues[:10]:
            print(f"  {issue['file']}:{issue['line']} - {issue['import']}")
            print(f"    Missing: {issue['missing_module']}")
        
        return syntax_issues, import_issues
    
    def check_missing_init_files(self):
        """Check for missing __init__.py files that might block discovery"""
        print("🔍 Checking for missing __init__.py files...")
        
        missing_inits = []
        
        # Check all test directories
        test_dirs = set()
        for test_file in self.all_test_files:
            test_dir = test_file.parent
            while test_dir != self.backend_root and test_dir.name != "tests":
                test_dirs.add(test_dir)
                test_dir = test_dir.parent
        
        for test_dir in test_dirs:
            init_file = test_dir / "__init__.py"
            if not init_file.exists():
                missing_inits.append(str(test_dir.relative_to(self.backend_root)))
        
        print(f"📊 MISSING __init__.py FILES: {len(missing_inits)}")
        for missing_init in missing_inits[:20]:
            print(f"  {missing_init}/__init__.py")
        
        return missing_inits
    
    def count_tests_in_missing_files(self):
        """Count how many test functions are in missing files"""
        print("🔍 Counting tests in missing files...")
        
        total_missing_tests = 0
        
        for missing_file in self.missing_test_files:
            file_path = self.backend_root / missing_file
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    test_count = len(re.findall(r'\ndef test_', content))
                    total_missing_tests += test_count
                except:
                    pass
        
        print(f"📊 ESTIMATED MISSING TESTS: {total_missing_tests}")
        return total_missing_tests
    
    def find_root_causes(self):
        """Find the root causes blocking 7k+ tests"""
        print("🔍 FINDING ROOT CAUSES FOR 7K+ MISSING TESTS")
        print("=" * 80)
        
        # Get all data
        self.find_all_test_files()
        self.find_discovered_test_files()
        self.find_missing_test_files()
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total test files: {len(self.all_test_files)}")
        print(f"  Discovered files: {len(self.discovered_test_files)}")
        print(f"  Missing files: {len(self.missing_test_files)}")
        
        # Analyze patterns
        print("\n" + "=" * 80)
        directory_counts = self.analyze_missing_file_patterns()
        
        print("\n" + "=" * 80)
        missing_inits = self.check_missing_init_files()
        
        print("\n" + "=" * 80)
        syntax_issues, import_issues = self.check_import_issues_in_missing_files()
        
        print("\n" + "=" * 80)
        missing_test_count = self.count_tests_in_missing_files()
        
        # Identify root causes
        print("\n🎯 ROOT CAUSE ANALYSIS:")
        print("=" * 80)
        
        if len(missing_inits) > 20:
            print(f"🚨 MAJOR ISSUE: {len(missing_inits)} missing __init__.py files!")
            print("   This could prevent entire directory trees from being discovered")
        
        if len(syntax_issues) > 10:
            print(f"🚨 MAJOR ISSUE: {len(syntax_issues)} files with syntax errors!")
            print("   These files can't be parsed at all")
        
        if len(import_issues) > 20:
            print(f"🚨 MAJOR ISSUE: {len(import_issues)} files with import errors!")
            print("   These files fail during import phase")
        
        # Find the biggest directory with missing files
        if directory_counts:
            biggest_missing_dir = max(directory_counts.items(), key=lambda x: x[1])
            print(f"🚨 BIGGEST MISSING DIRECTORY: {biggest_missing_dir[0]} ({biggest_missing_dir[1]} files)")
        
        print(f"\n📊 ESTIMATED IMPACT:")
        print(f"  Missing test functions: ~{missing_test_count}")
        print(f"  Missing test files: {len(self.missing_test_files)}")
        print(f"  Discovery rate: {len(self.discovered_test_files)/len(self.all_test_files)*100:.1f}%")
        
        return {
            'missing_files': len(self.missing_test_files),
            'missing_inits': len(missing_inits),
            'syntax_issues': len(syntax_issues),
            'import_issues': len(import_issues),
            'missing_tests': missing_test_count,
            'biggest_missing_dir': biggest_missing_dir if directory_counts else None
        }

if __name__ == "__main__":
    finder = Missing7kTestFinder()
    result = finder.find_root_causes()
    
    print("\n🎯 RECOMMENDED ACTIONS:")
    print("=" * 80)
    
    if result['missing_inits'] > 10:
        print("1. CREATE MISSING __init__.py FILES (HIGH PRIORITY)")
        print("   This could unlock hundreds of test files")
    
    if result['syntax_issues'] > 5:
        print("2. FIX SYNTAX ERRORS (HIGH PRIORITY)")
        print("   These files are completely broken")
    
    if result['import_issues'] > 10:
        print("3. FIX IMPORT CHAINS (MEDIUM PRIORITY)")
        print("   These files fail to load")
    
    if result['biggest_missing_dir']:
        print(f"4. FOCUS ON {result['biggest_missing_dir'][0]} DIRECTORY")
        print(f"   {result['biggest_missing_dir'][1]} files missing from this directory") 