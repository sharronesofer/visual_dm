#!/usr/bin/env python3

import os
import re
import hashlib
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import ast
import sys

def normalize_code(code):
    """Normalize code by removing whitespace, comments, and standardizing variable names"""
    # Remove comments
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
    code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
    
    # Remove excessive whitespace
    code = re.sub(r'\s+', ' ', code)
    code = re.sub(r'\s*([{}()[\],;:])\s*', r'\1', code)
    
    # Normalize string literals
    code = re.sub(r'"[^"]*"', '"STRING"', code)
    code = re.sub(r"'[^']*'", "'STRING'", code)
    
    # Normalize numbers
    code = re.sub(r'\b\d+\b', 'NUMBER', code)
    
    return code.strip()

def extract_variable_names(code):
    """Extract variable names from code"""
    # Simple regex-based extraction
    variables = set()
    # Function parameters and local variables
    vars_match = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', code)
    variables.update(vars_match)
    
    # Function names
    func_match = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
    variables.update(func_match)
    
    # Class names
    class_match = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
    variables.update(class_match)
    
    return variables

def create_variable_normalized_code(code):
    """Create version of code with variables normalized to VAR1, VAR2, etc."""
    variables = extract_variable_names(code)
    var_map = {}
    normalized = code
    
    for i, var in enumerate(sorted(variables)):
        if len(var) > 2:  # Skip very short variable names
            var_map[var] = f'VAR{i}'
            normalized = re.sub(r'\b' + re.escape(var) + r'\b', f'VAR{i}', normalized)
    
    return normalized, var_map

def get_structural_hash(code):
    """Get hash of code structure (ignoring variable names and literals)"""
    try:
        # Parse AST and get structure
        tree = ast.parse(code)
        # Convert AST to string representation focusing on structure
        structure = ast.dump(tree, annotate_fields=False, include_attributes=False)
        return hashlib.md5(structure.encode()).hexdigest()
    except:
        # Fallback to normalized code hash
        normalized = normalize_code(code)
        return hashlib.md5(normalized.encode()).hexdigest()

def similarity_ratio(code1, code2):
    """Calculate similarity ratio between two code snippets"""
    normalized1 = normalize_code(code1)
    normalized2 = normalize_code(code2)
    return SequenceMatcher(None, normalized1, normalized2).ratio()

def extract_functions(file_content):
    """Extract function definitions from file content"""
    functions = []
    lines = file_content.split('\n')
    current_function = []
    in_function = False
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('def ') or stripped.startswith('async def '):
            if current_function:
                functions.append('\n'.join(current_function))
            current_function = [line]
            in_function = True
            indent_level = len(line) - len(line.lstrip())
        elif in_function:
            if line.strip() == '':
                current_function.append(line)
            elif len(line) - len(line.lstrip()) > indent_level or line.strip().startswith('#'):
                current_function.append(line)
            else:
                # End of function
                functions.append('\n'.join(current_function))
                current_function = []
                in_function = False
                if stripped.startswith('def ') or stripped.startswith('async def '):
                    current_function = [line]
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
    
    if current_function:
        functions.append('\n'.join(current_function))
    
    return functions

def extract_classes(file_content):
    """Extract class definitions from file content"""
    classes = []
    lines = file_content.split('\n')
    current_class = []
    in_class = False
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('class '):
            if current_class:
                classes.append('\n'.join(current_class))
            current_class = [line]
            in_class = True
            indent_level = len(line) - len(line.lstrip())
        elif in_class:
            if line.strip() == '':
                current_class.append(line)
            elif len(line) - len(line.lstrip()) > indent_level or line.strip().startswith('#'):
                current_class.append(line)
            else:
                # End of class
                classes.append('\n'.join(current_class))
                current_class = []
                in_class = False
                if stripped.startswith('class '):
                    current_class = [line]
                    in_class = True
                    indent_level = len(line) - len(line.lstrip())
    
    if current_class:
        classes.append('\n'.join(current_class))
    
    return classes

def analyze_advanced_duplicates(backend_dir):
    """Perform advanced duplicate analysis"""
    print("🔍 Advanced Duplicate Code Analysis")
    print("=" * 50)
    
    # Collect all Python files
    python_files = []
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Analyzing {len(python_files)} Python files...")
    
    # Analysis data structures
    exact_duplicates = defaultdict(list)
    structural_duplicates = defaultdict(list)
    similar_functions = defaultdict(list)
    similar_classes = defaultdict(list)
    variable_normalized_duplicates = defaultdict(list)
    
    all_functions = []
    all_classes = []
    file_contents = {}
    
    # Read all files and extract content
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                file_contents[file_path] = content
                
                # Extract functions and classes
                functions = extract_functions(content)
                classes = extract_classes(content)
                
                for func in functions:
                    if len(func.strip()) > 50:  # Skip very small functions
                        all_functions.append((file_path, func))
                
                for cls in classes:
                    if len(cls.strip()) > 50:  # Skip very small classes
                        all_classes.append((file_path, cls))
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    print(f"Extracted {len(all_functions)} functions and {len(all_classes)} classes")
    
    # 1. Exact duplicate detection (whole files)
    print("\n1. Finding exact file duplicates...")
    for file_path, content in file_contents.items():
        content_hash = hashlib.md5(content.encode()).hexdigest()
        exact_duplicates[content_hash].append(file_path)
    
    # 2. Structural duplicate detection
    print("2. Finding structural duplicates...")
    for file_path, content in file_contents.items():
        if len(content.strip()) > 100:  # Skip very small files
            struct_hash = get_structural_hash(content)
            structural_duplicates[struct_hash].append(file_path)
    
    # 3. Variable-normalized duplicates
    print("3. Finding variable-normalized duplicates...")
    for file_path, content in file_contents.items():
        if len(content.strip()) > 100:
            normalized, var_map = create_variable_normalized_code(content)
            norm_hash = hashlib.md5(normalized.encode()).hexdigest()
            variable_normalized_duplicates[norm_hash].append((file_path, var_map))
    
    # 4. Similar function detection
    print("4. Finding similar functions...")
    function_signatures = {}
    for i, (file_path1, func1) in enumerate(all_functions):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(all_functions)} functions")
        
        func_normalized = normalize_code(func1)
        func_hash = hashlib.md5(func_normalized.encode()).hexdigest()
        
        if func_hash not in function_signatures:
            function_signatures[func_hash] = []
        function_signatures[func_hash].append((file_path1, func1))
    
    # 5. Similar class detection
    print("5. Finding similar classes...")
    class_signatures = {}
    for file_path, cls in all_classes:
        cls_normalized = normalize_code(cls)
        cls_hash = hashlib.md5(cls_normalized.encode()).hexdigest()
        
        if cls_hash not in class_signatures:
            class_signatures[cls_hash] = []
        class_signatures[cls_hash].append((file_path, cls))
    
    # Generate report
    print("\n" + "="*70)
    print("📊 ADVANCED DUPLICATE ANALYSIS RESULTS")
    print("="*70)
    
    # Exact file duplicates
    exact_dupe_files = [files for files in exact_duplicates.values() if len(files) > 1]
    if exact_dupe_files:
        print(f"\n🔴 EXACT FILE DUPLICATES: {len(exact_dupe_files)} groups")
        total_exact_dupes = sum(len(group) - 1 for group in exact_dupe_files)
        print(f"   → {total_exact_dupes} files are exact duplicates")
        
        for i, group in enumerate(exact_dupe_files[:10]):  # Show top 10
            print(f"\n   Group {i+1} ({len(group)} files):")
            for file_path in group:
                rel_path = os.path.relpath(file_path, backend_dir)
                print(f"     • {rel_path}")
    
    # Structural duplicates
    struct_dupe_files = [files for files in structural_duplicates.values() if len(files) > 1]
    if struct_dupe_files:
        print(f"\n🟡 STRUCTURAL DUPLICATES: {len(struct_dupe_files)} groups")
        total_struct_dupes = sum(len(group) - 1 for group in struct_dupe_files)
        print(f"   → {total_struct_dupes} files have identical structure")
        
        for i, group in enumerate(struct_dupe_files[:5]):  # Show top 5
            print(f"\n   Group {i+1} ({len(group)} files):")
            for file_path in group:
                rel_path = os.path.relpath(file_path, backend_dir)
                print(f"     • {rel_path}")
    
    # Variable-normalized duplicates
    var_norm_dupes = [files for files in variable_normalized_duplicates.values() if len(files) > 1]
    if var_norm_dupes:
        print(f"\n🟠 VARIABLE-NORMALIZED DUPLICATES: {len(var_norm_dupes)} groups")
        total_var_norm = sum(len(group) - 1 for group in var_norm_dupes)
        print(f"   → {total_var_norm} files are identical except for variable names")
        
        for i, group in enumerate(var_norm_dupes[:5]):  # Show top 5
            print(f"\n   Group {i+1} ({len(group)} files):")
            for file_path, var_map in group:
                rel_path = os.path.relpath(file_path, backend_dir)
                print(f"     • {rel_path}")
    
    # Function duplicates
    func_dupe_groups = [funcs for funcs in function_signatures.values() if len(funcs) > 1]
    if func_dupe_groups:
        print(f"\n🔵 DUPLICATE FUNCTIONS: {len(func_dupe_groups)} groups")
        total_func_dupes = sum(len(group) - 1 for group in func_dupe_groups)
        print(f"   → {total_func_dupes} functions are duplicates")
        
        # Show most duplicated functions
        func_dupe_groups.sort(key=len, reverse=True)
        for i, group in enumerate(func_dupe_groups[:10]):
            print(f"\n   Group {i+1} ({len(group)} instances):")
            func_name = group[0][1].split('\n')[0].strip()
            print(f"     Function: {func_name}")
            for file_path, func in group[:5]:  # Show first 5 instances
                rel_path = os.path.relpath(file_path, backend_dir)
                print(f"       • {rel_path}")
            if len(group) > 5:
                print(f"       ... and {len(group) - 5} more")
    
    # Class duplicates
    class_dupe_groups = [classes for classes in class_signatures.values() if len(classes) > 1]
    if class_dupe_groups:
        print(f"\n🟣 DUPLICATE CLASSES: {len(class_dupe_groups)} groups")
        total_class_dupes = sum(len(group) - 1 for group in class_dupe_groups)
        print(f"   → {total_class_dupes} classes are duplicates")
        
        class_dupe_groups.sort(key=len, reverse=True)
        for i, group in enumerate(class_dupe_groups[:5]):
            print(f"\n   Group {i+1} ({len(group)} instances):")
            class_name = group[0][1].split('\n')[0].strip()
            print(f"     Class: {class_name}")
            for file_path, cls in group:
                rel_path = os.path.relpath(file_path, backend_dir)
                print(f"       • {rel_path}")
    
    # Summary and potential savings
    print("\n" + "="*70)
    print("💾 POTENTIAL CLEANUP SAVINGS")
    print("="*70)
    
    total_files = len(python_files)
    total_removable = (total_exact_dupes + total_struct_dupes + total_var_norm + 
                      total_func_dupes + total_class_dupes)
    
    print(f"Total Python files analyzed: {total_files}")
    print(f"Exact file duplicates: {total_exact_dupes}")
    print(f"Structural duplicates: {total_struct_dupes}")
    print(f"Variable-normalized duplicates: {total_var_norm}")
    print(f"Duplicate functions: {total_func_dupes}")
    print(f"Duplicate classes: {total_class_dupes}")
    print(f"\nTotal potentially removable items: {total_removable}")
    
    # Calculate lines of code in duplicates
    total_duplicate_lines = 0
    for group in exact_dupe_files:
        if group:
            try:
                with open(group[0], 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                total_duplicate_lines += lines * (len(group) - 1)
            except:
                pass
    
    print(f"Estimated duplicate lines of code: {total_duplicate_lines:,}")
    
    return {
        'exact_duplicates': exact_dupe_files,
        'structural_duplicates': struct_dupe_files,
        'variable_normalized': var_norm_dupes,
        'function_duplicates': func_dupe_groups,
        'class_duplicates': class_dupe_groups,
        'total_removable': total_removable,
        'duplicate_lines': total_duplicate_lines
    }

if __name__ == "__main__":
    backend_dir = "backend/systems"
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found: {backend_dir}")
        sys.exit(1)
    
    results = analyze_advanced_duplicates(backend_dir)
    
    print(f"\n🎯 RECOMMENDATION:")
    if results['total_removable'] > 100:
        print(f"With {results['total_removable']} removable duplicates and {results['duplicate_lines']:,} duplicate lines,")
        print(f"there's significant opportunity for further code reduction!")
        print(f"\nNext steps:")
        print(f"1. Create automated deduplication script")
        print(f"2. Focus on exact and structural duplicates first")
        print(f"3. Consolidate duplicate functions into shared utilities")
        print(f"4. Could potentially reduce codebase by another 30-50%")
    else:
        print(f"Codebase appears to be reasonably deduplicated.") 