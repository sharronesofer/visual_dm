#!/usr/bin/env python3
"""
Task 36: JavaScript/TypeScript to Python Converter
Handles conversion of JavaScript/TypeScript syntax found in .py files to valid Python syntax.
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Set
import json

class JSPythonConverter:
    """Converts JavaScript/TypeScript syntax to Python syntax in .py files."""
    
    def __init__(self, backend_path: str = "backend"):
        self.backend_path = Path(backend_path)
        self.converted_files: List[Path] = []
        self.failed_files: List[Tuple[Path, str]] = []
        self.changes_made = 0
        
    def run_conversion(self):
        """Main method to run the JavaScript to Python conversion."""
        print("🔄 Starting JavaScript/TypeScript to Python conversion...")
        
        files_to_convert = self._get_js_python_files()
        print(f"📁 Found {len(files_to_convert)} files with JavaScript/TypeScript syntax")
        
        for file_path in files_to_convert:
            try:
                self._convert_file(file_path)
                self.converted_files.append(file_path)
            except Exception as e:
                self.failed_files.append((file_path, str(e)))
                print(f"   ⚠️ Failed to convert {file_path}: {e}")
        
        self._generate_report()
        print(f"✅ Conversion complete! {len(self.converted_files)} files converted.")
        
    def _get_js_python_files(self) -> List[Path]:
        """Get all .py files that contain JavaScript/TypeScript syntax."""
        files = []
        for file_path in self.backend_path.rglob("*.py"):
            if self._has_js_syntax(file_path):
                files.append(file_path)
        return files
    
    def _has_js_syntax(self, file_path: Path) -> bool:
        """Check if a Python file contains JavaScript/TypeScript syntax."""
        try:
            content = file_path.read_text(encoding='utf-8')
            js_patterns = [
                r'class\s+\w+\s*\{',  # class ClassName {
                r'function\s+\w+\s*\(',  # function functionName(
                r'async\s+function',  # async function
                r'constructor\s*\(',  # constructor(
                r'this\.',  # this.property
                r'private\s+\w+:',  # private property: type
                r'public\s+\w+:',  # public property: type
                r'Promise<',  # Promise<Type>
                r'}\s*from\s+[\'"]',  # } from "module"
                r'import\s*\{.*\}\s*from',  # import { ... } from
                r'const\s+\w+\s*[:=]',  # const variable = or const variable:
                r'let\s+\w+\s*[:=]',  # let variable = or let variable:
                r'interface\s+\w+',  # interface InterfaceName
                r'enum\s+\w+',  # enum EnumName
                r'type\s+\w+\s*=',  # type TypeName =
                r'export\s+(class|function|const|let|interface|enum)',  # export declarations
            ]
            
            for pattern in js_patterns:
                if re.search(pattern, content):
                    return True
            return False
        except Exception:
            return False
    
    def _convert_file(self, file_path: Path):
        """Convert a single file from JavaScript/TypeScript to Python syntax."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Convert the content
            content = self._convert_content(content)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                self.changes_made += 1
                print(f"   ✅ Converted {file_path}")
            
        except Exception as e:
            raise Exception(f"Error converting {file_path}: {e}")
    
    def _convert_content(self, content: str) -> str:
        """Convert JavaScript/TypeScript content to Python syntax."""
        lines = content.split('\n')
        converted_lines = []
        
        for line in lines:
            converted_line = self._convert_line(line)
            converted_lines.append(converted_line)
        
        return '\n'.join(converted_lines)
    
    def _convert_line(self, line: str) -> str:
        """Convert a single line from JavaScript/TypeScript to Python."""
        original_line = line
        
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('//'):
            return line
        
        # Convert import statements
        line = self._convert_imports(line)
        
        # Convert class definitions
        line = self._convert_class_definitions(line)
        
        # Convert function definitions
        line = self._convert_function_definitions(line)
        
        # Convert variable declarations
        line = self._convert_variable_declarations(line)
        
        # Convert object/array syntax
        line = self._convert_object_syntax(line)
        
        # Convert method calls and properties
        line = self._convert_method_calls(line)
        
        # Convert control structures
        line = self._convert_control_structures(line)
        
        # Convert type annotations
        line = self._convert_type_annotations(line)
        
        # Remove JavaScript-specific keywords
        line = self._remove_js_keywords(line)
        
        # Convert braces to Python indentation (simple cases)
        line = self._convert_braces(line)
        
        return line
    
    def _convert_imports(self, line: str) -> str:
        """Convert JavaScript/TypeScript import statements to Python."""
        # Convert: import { ... } from "module" to: from module import ...
        import_pattern = r'import\s*\{([^}]+)\}\s*from\s*[\'"]([^\'"]+)[\'"]'
        match = re.search(import_pattern, line)
        if match:
            items = match.group(1).strip()
            module = match.group(2)
            return f"from {module} import {items}"
        
        # Convert: import module from "path" to: import module
        import_pattern2 = r'import\s+(\w+)\s+from\s*[\'"]([^\'"]+)[\'"]'
        match2 = re.search(import_pattern2, line)
        if match2:
            module_name = match2.group(1)
            return f"import {module_name}"
        
        # Convert basic import with path
        if re.search(r'import.*from.*[\'"]', line):
            return "# " + line + " # TODO: Convert import"
        
        return line
    
    def _convert_class_definitions(self, line: str) -> str:
        """Convert JavaScript/TypeScript class definitions to Python."""
        # Convert: class ClassName { to: class ClassName:
        class_pattern = r'class\s+(\w+)\s*\{'
        match = re.search(class_pattern, line)
        if match:
            class_name = match.group(1)
            indent = len(line) - len(line.lstrip())
            return ' ' * indent + f"class {class_name}:"
        
        # Convert: interface ClassName to: class ClassName:
        interface_pattern = r'interface\s+(\w+)'
        match = re.search(interface_pattern, line)
        if match:
            interface_name = match.group(1)
            indent = len(line) - len(line.lstrip())
            return ' ' * indent + f"class {interface_name}:"
        
        return line
    
    def _convert_function_definitions(self, line: str) -> str:
        """Convert JavaScript/TypeScript function definitions to Python."""
        # Convert: function functionName(params) { to: def function_name(params):
        func_pattern = r'(async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*[:{]'
        match = re.search(func_pattern, line)
        if match:
            is_async = match.group(1) is not None
            func_name = self._to_snake_case(match.group(2))
            params = match.group(3)
            indent = len(line) - len(line.lstrip())
            async_prefix = "async " if is_async else ""
            return ' ' * indent + f"{async_prefix}def {func_name}({params}):"
        
        # Convert: constructor(params) { to: def __init__(self, params):
        constructor_pattern = r'constructor\s*\(([^)]*)\)\s*\{'
        match = re.search(constructor_pattern, line)
        if match:
            params = match.group(1)
            if params:
                params = f"self, {params}"
            else:
                params = "self"
            indent = len(line) - len(line.lstrip())
            return ' ' * indent + f"def __init__({params}):"
        
        # Convert: methodName(params): Type { to: def method_name(self, params):
        method_pattern = r'(\w+)\s*\(([^)]*)\)\s*:\s*\w+\s*\{'
        match = re.search(method_pattern, line)
        if match:
            method_name = self._to_snake_case(match.group(1))
            params = match.group(2)
            if params:
                params = f"self, {params}"
            else:
                params = "self"
            indent = len(line) - len(line.lstrip())
            return ' ' * indent + f"def {method_name}({params}):"
        
        return line
    
    def _convert_variable_declarations(self, line: str) -> str:
        """Convert JavaScript/TypeScript variable declarations to Python."""
        # Convert: const variableName = value to: variable_name = value
        const_pattern = r'const\s+(\w+)\s*[:=]\s*(.+)'
        match = re.search(const_pattern, line)
        if match:
            var_name = self._to_snake_case(match.group(1))
            value = match.group(2)
            indent = len(line) - len(line.lstrip())
            return ' ' * indent + f"{var_name} = {value}"
        
        # Convert: let variableName = value to: variable_name = value
        let_pattern = r'let\s+(\w+)\s*[:=]\s*(.+)'
        match = re.search(let_pattern, line)
        if match:
            var_name = self._to_snake_case(match.group(1))
            value = match.group(2)
            indent = len(line) - len(line.lstrip())
            return ' ' * indent + f"{var_name} = {value}"
        
        return line
    
    def _convert_object_syntax(self, line: str) -> str:
        """Convert JavaScript object/array syntax to Python."""
        # Convert object property syntax
        line = re.sub(r'(\w+):\s*([^,}]+)', r'"\1": \2', line)
        
        # Convert array syntax (basic cases)
        line = re.sub(r'Array\((\d+)\)\.fill\(([^)]+)\)', r'[\2] * \1', line)
        
        return line
    
    def _convert_method_calls(self, line: str) -> str:
        """Convert JavaScript method calls and property access to Python."""
        # Convert: this.property to: self.property
        line = re.sub(r'\bthis\.', 'self.', line)
        
        # Convert: promise.then() to: await promise
        line = re.sub(r'\.then\s*\(', '.then(', line)  # Keep for now, complex conversion
        
        return line
    
    def _convert_control_structures(self, line: str) -> str:
        """Convert JavaScript control structures to Python."""
        # Convert: for (const item of items) { to: for item in items:
        for_of_pattern = r'for\s*\(\s*(?:const|let)\s+(\w+)\s+of\s+([^)]+)\)\s*\{'
        match = re.search(for_of_pattern, line)
        if match:
            var_name = match.group(1)
            iterable = match.group(2)
            indent = len(line) - len(line.lstrip())
            return ' ' * indent + f"for {var_name} in {iterable}:"
        
        # Convert: if (condition) { to: if condition:
        if_pattern = r'if\s*\(([^)]+)\)\s*\{'
        match = re.search(if_pattern, line)
        if match:
            condition = match.group(1)
            indent = len(line) - len(line.lstrip())
            return ' ' * indent + f"if {condition}:"
        
        return line
    
    def _convert_type_annotations(self, line: str) -> str:
        """Convert TypeScript type annotations to Python type hints."""
        # Convert: variableName: Type = to: variable_name: Type =
        type_pattern = r'(\w+):\s*([A-Z]\w*)\s*='
        match = re.search(type_pattern, line)
        if match:
            var_name = self._to_snake_case(match.group(1))
            type_name = match.group(2)
            # Map common TypeScript types to Python types
            type_mapping = {
                'string': 'str',
                'number': 'float',
                'boolean': 'bool',
                'Array': 'List',
                'Object': 'Dict',
                'Promise': 'Any',  # Will need more complex handling
            }
            python_type = type_mapping.get(type_name, type_name)
            line = re.sub(r'\w+:\s*[A-Z]\w*\s*=', f'{var_name}: {python_type} =', line)
        
        return line
    
    def _remove_js_keywords(self, line: str) -> str:
        """Remove JavaScript-specific keywords."""
        # Remove visibility modifiers
        line = re.sub(r'\b(private|public|protected)\s+', '', line)
        
        # Remove export keyword
        line = re.sub(r'\bexport\s+', '', line)
        
        # Remove type annotations after colons (simple cases)
        line = re.sub(r':\s*\w+\s*(?=[,;)}])', '', line)
        
        return line
    
    def _convert_braces(self, line: str) -> str:
        """Convert JavaScript braces to Python indentation markers."""
        # Replace closing braces with pass (when they're alone on a line)
        if re.match(r'^\s*}\s*$', line):
            indent = len(line) - len(line.lstrip())
            return ' ' * indent + "pass"
        
        # Remove opening braces at end of lines
        line = re.sub(r'\s*\{\s*$', ':', line)
        
        return line
    
    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase to snake_case."""
        # Insert underscore before uppercase letters (except first)
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', name)
        return name.lower()
    
    def _generate_report(self):
        """Generate a comprehensive report of the conversion process."""
        report = {
            "summary": {
                "total_files_processed": len(self.converted_files) + len(self.failed_files),
                "successfully_converted": len(self.converted_files),
                "failed_conversions": len(self.failed_files),
                "changes_made": self.changes_made
            },
            "converted_files": [str(f) for f in self.converted_files],
            "failed_files": [{"file": str(f), "error": error} for f, error in self.failed_files]
        }
        
        # Save detailed report
        report_path = Path("task_36_js_python_conversion_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("📋 JAVASCRIPT TO PYTHON CONVERSION REPORT")
        print("="*60)
        print(f"✅ Files Successfully Converted: {len(self.converted_files)}")
        print(f"❌ Files Failed to Convert: {len(self.failed_files)}")
        print(f"🔧 Total Changes Made: {self.changes_made}")
        
        if self.failed_files:
            print("\n⚠️ FAILED CONVERSIONS:")
            for file_path, error in self.failed_files[:10]:  # Show first 10
                print(f"   • {file_path}: {error}")
            if len(self.failed_files) > 10:
                print(f"   ... and {len(self.failed_files) - 10} more")
        
        print(f"\n📄 Detailed report saved to: {report_path}")

if __name__ == "__main__":
    converter = JSPythonConverter()
    converter.run_conversion() 