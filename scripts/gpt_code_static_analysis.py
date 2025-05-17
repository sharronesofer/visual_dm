#!/usr/bin/env python3
"""
Static analysis tool for detecting common GPT-generated code issues in Python code.
"""
import ast
import os
import sys
import re
import shutil
from typing import List, Tuple, Optional

Issue = Tuple[str, int, str, str]  # (filename, lineno, issue_type, suggestion)

# --- Rule Implementations ---
def check_deprecated_api(node: ast.AST, filename: str) -> Optional[Issue]:
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if (
                node.func.attr == 'get_event_loop' and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'asyncio'
            ):
                return (filename, node.lineno, 'Deprecated API',
                        'Use asyncio.new_event_loop() or asyncio.get_running_loop() instead.')
    return None

def check_resource_management(node: ast.AST, filename: str) -> Optional[Issue]:
    # Look for open() not in a with statement
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
        parent = getattr(node, 'parent', None)
        while parent:
            if isinstance(parent, ast.With):
                return None  # Properly managed
            parent = getattr(parent, 'parent', None)
        return (filename, node.lineno, 'Resource Management',
                'Use a with statement to open files to ensure they are closed.')
    return None

def check_error_handling(node: ast.AST, filename: str) -> Optional[Issue]:
    if isinstance(node, ast.ExceptHandler):
        # Bare except
        if node.type is None:
            return (filename, node.lineno, 'Error Handling',
                    'Avoid bare except; catch specific exceptions.')
        # Silent pass
        for n in node.body:
            if isinstance(n, ast.Pass):
                return (filename, node.lineno, 'Error Handling',
                        'Do not silently pass in except blocks; log or handle the error.')
    return None

def check_security_vulnerabilities(node: ast.AST, filename: str) -> Optional[Issue]:
    # Detect eval usage
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'eval':
        return (filename, node.lineno, 'Security',
                'Avoid ast.literal_eval(  # autofix: safer eval); use safe parsing or ast.literal_eval if needed.')
    # Detect hardcoded secrets (simple regex on source)
    return None

def check_performance_antipatterns(node: ast.AST, filename: str) -> Optional[Issue]:
    # Detect inefficient for-loops appending to list (could be a list comp)
    if isinstance(node, ast.For):
        if (
            isinstance(node.body, list) and
            any(isinstance(n, ast.Expr) and isinstance(getattr(n, 'value', None), ast.Call) and
                isinstance(getattr(n.value, 'func', None), ast.Attribute) and
                n.value.func.attr == 'append' for n in node.body)
        ):
            return (filename, node.lineno, 'Performance',
                    'Consider using a list comprehension for better performance.')
    return None

def check_mutable_default_args(node: ast.AST, filename: str) -> Optional[Issue]:
    if isinstance(node, ast.FunctionDef):
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                return (filename, node.lineno, 'Language-Specific',
                        'Do not use mutable default arguments; use None and set in body.')
    return None

# --- AST Parent Linking ---
def add_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

# --- File Analysis ---
def analyze_file(filepath: str) -> List[Issue]:
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
        add_parents(tree)
        for node in ast.walk(tree):
            for check in [
                check_deprecated_api,
                check_resource_management,
                check_error_handling,
                check_security_vulnerabilities,
                check_performance_antipatterns,
                check_mutable_default_args
            ]:
                issue = check(node, filepath)
                if issue:
                    issues.append(issue)
        # Regex for hardcoded secrets (very basic)
        for i, line in enumerate(source.splitlines(), 1):
            if re.search(r'password\s*=\s*["\"][^"\"]+["\"]', line, re.IGNORECASE):
                issues.append((filepath, i, 'Security', 'Possible hardcoded password. Use environment variables or config files.'))
    except Exception as e:
        issues.append((filepath, 0, 'Analysis Error', str(e)))
    return issues

# --- Directory Traversal ---
def analyze_path(path: str) -> List[Issue]:
    issues = []
    if os.path.isfile(path) and path.endswith('.py'):
        issues.extend(analyze_file(path))
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    issues.extend(analyze_file(os.path.join(root, file)))
    return issues

# --- Reporting ---
def print_report(issues: List[Issue]):
    if not issues:
        print('No issues found.')
        return
    print(f'Found {len(issues)} issue(s):')
    for filename, lineno, issue_type, suggestion in issues:
        print(f'{filename}:{lineno}: [{issue_type}] {suggestion}')

# --- Fix Implementations ---
def fix_deprecated_api(source: str) -> Tuple[str, int]:
    # Replace 'asyncio.new_event_loop()' with 'asyncio.new_event_loop()'
    pattern = r'(asyncio)\.get_event_loop\(\)'
    fixed, n = re.subn(pattern, r'\1.new_event_loop()', source)
    return fixed, n

def fix_resource_management(source: str) -> Tuple[str, int]:
    # Only handle simple cases: open() assigned to a variable, not already in a with
    pattern = r'^(\s*)(\w+)\s*=\s*open\(([^\n]+)\)\n((?:\s+[^\n]+\n)+)'  # naive
    def repl(match):
        indent, var, args, body = match.groups()
        # Only fix if var is used in body and not already in a with
        if f'{var}.' in body:
            new_code = f"{indent}with open({args}) as {var}:  # autofix: resource management\n"
            # Remove one indent from body
            body_lines = body.splitlines(True)
            body_fixed = ''.join([l[len(indent)+4:] if l.startswith(indent + '    ') else l for l in body_lines])
            return new_code + body_fixed
        return match.group(0)
    fixed, n = re.subn(pattern, repl, source, flags=re.MULTILINE)
    return fixed, n

def fix_error_handling(source: str) -> Tuple[str, int]:
    # Replace 'except Exception:  # autofix: specify exception' with 'except Exception:'
    fixed, n1 = re.subn(r'except\s*:', 'except Exception:  # autofix: specify exception', source)
    # Replace 'pass' in except blocks with a print statement
    fixed2, n2 = re.subn(r'(?<=except Exception:  # autofix: specify exception\n)(\s*)pass', r'\1print("Exception occurred")  # autofix: handle error', fixed)
    return fixed2, n1 + n2

def fix_security_eval(source: str) -> Tuple[str, int]:
    # Replace 'ast.literal_eval(  # autofix: safer eval' with 'ast.literal_eval(' (add import if needed)
    fixed, n = re.subn(r'(?<![\w\.])eval\(', 'ast.literal_eval(  # autofix: safer eval', source)
    if n > 0 and 'import ast' not in fixed:
        fixed = 'import ast  # autofix: added for safer eval\n' + fixed
    return fixed, n

def fix_mutable_default_args(source: str) -> Tuple[str, int]:
    # Replace mutable default args with None and set in body
    pattern = r'def (\w+)\(([^\)]*\[\]\s*=\s*\[\]|[^\)]*\{\}\s*=\s*\{\}|[^\)]*\{\}\s*=\s*set\(\))[^\)]*\):'
    def repl(match):
        func_name, args = match.groups()
        # Only handle list/dict/set default
        new_args = re.sub(r'(\w+)\s*=\s*(\[\]|\{\}|set\(\))', r'\1=None  # autofix: avoid mutable default', args)
        return f'def {func_name}({new_args}):'
    fixed, n = re.subn(pattern, repl, source)
    # Add body fix: set to []/{} if None
    if n > 0:
        lines = fixed.splitlines(True)
        for i, line in enumerate(lines):
            m = re.match(r'(\s*)def (\w+)\(([^)]*)\):', line)
            if m:
                indent = m.group(1) + '    '
                args = m.group(3)
                for arg in re.findall(r'(\w+)=None', args):
                    # Insert after def line
                    lines.insert(i+1, f'{indent}if {arg} is None: {arg} = []  # autofix: set default\n')
        fixed = ''.join(lines)
    return fixed, n

def apply_fixes(source: str) -> Tuple[str, List[str]]:
    fixes = []
    orig = source
    source, n = fix_deprecated_api(source)
    if n: fixes.append(f"Deprecated API: {n} fix(es)")
    source2, n2 = fix_resource_management(source)
    if n2: fixes.append(f"Resource Management: {n2} fix(es)")
    source = source2
    source2, n3 = fix_error_handling(source)
    if n3: fixes.append(f"Error Handling: {n3} fix(es)")
    source = source2
    source2, n4 = fix_security_eval(source)
    if n4: fixes.append(f"Security (eval): {n4} fix(es)")
    source = source2
    source2, n5 = fix_mutable_default_args(source)
    if n5: fixes.append(f"Mutable Default Args: {n5} fix(es)")
    source = source2
    return source, fixes

def analyze_and_fix_file(filepath: str, autofix: bool) -> List[Issue]:
    issues = analyze_file(filepath)
    fixes_applied = []
    if autofix:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            fixed, fixes = apply_fixes(source)
            if fixes and fixed != source:
                backup_path = filepath + '.bak'
                shutil.copy2(filepath, backup_path)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed)
                fixes_applied = fixes
        except Exception as e:
            issues.append((filepath, 0, 'Autofix Error', str(e)))
    if fixes_applied:
        issues.append((filepath, 0, 'Autofix', f"Applied: {', '.join(fixes_applied)}"))
    return issues

def analyze_and_fix_path(path: str, autofix: bool) -> List[Issue]:
    issues = []
    if os.path.isfile(path) and path.endswith('.py'):
        issues.extend(analyze_and_fix_file(path, autofix))
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    issues.extend(analyze_and_fix_file(os.path.join(root, file), autofix))
    return issues

# --- Main CLI ---
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Static analysis for common GPT-generated code issues (Python)')
    parser.add_argument('target', help='Target Python file or directory')
    parser.add_argument('--autofix', action='store_true', help='Automatically fix detected issues (in-place, makes .bak backups)')
    args = parser.parse_args()
    issues = analyze_and_fix_path(args.target, args.autofix)
    print_report(issues) 