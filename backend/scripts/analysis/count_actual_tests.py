#!/usr/bin/env python3
"""
Count all actual test functions in the backend
"""

import ast
import os
from pathlib import Path

def count_tests_in_file(filepath):
    """Count test functions in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
            
        test_count = 0
        class_test_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_count += 1
            elif isinstance(node, ast.AsyncFunctionDef) and node.name.startswith('test_'):
                test_count += 1
            elif isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                # Count methods in test classes
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'):
                        class_test_count += 1
                        
        return test_count + class_test_count
        
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return 0

def main():
    backend_root = Path('.')
    total_tests = 0
    test_files = 0
    file_details = []
    
    # Walk through all Python files
    for root, dirs, files in os.walk(backend_root):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', '.pytest_cache', 'venv', '.env']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                
                # Check if it's likely a test file
                is_test_file = (
                    'test' in file.lower() or 
                    file.startswith('test_') or
                    'test' in str(filepath).lower()
                )
                
                if is_test_file:
                    test_count = count_tests_in_file(filepath)
                    if test_count > 0:
                        total_tests += test_count
                        test_files += 1
                        file_details.append((str(filepath), test_count))
    
    print(f"🔍 COMPREHENSIVE TEST COUNT ANALYSIS")
    print("=" * 50)
    print(f"Total test functions found: {total_tests:,}")
    print(f"Test files with actual tests: {test_files}")
    print(f"Average tests per file: {total_tests/max(test_files,1):.1f}")
    print()
    
    # Show top test files by count
    print("📊 TOP TEST FILES BY COUNT:")
    file_details.sort(key=lambda x: x[1], reverse=True)
    for filepath, count in file_details[:20]:
        print(f"{count:4d} tests - {filepath}")
    
    print("\n" + "=" * 50)
    print(f"If pytest is only finding ~3k tests but we have {total_tests:,} test functions,")
    print("there are likely collection issues preventing discovery of all tests.")

if __name__ == "__main__":
    main() 