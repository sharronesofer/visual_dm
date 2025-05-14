#!/usr/bin/env python3
"""
TypeScript to Python Converter

This script converts TypeScript files to Python code with proper type annotations.
It handles interfaces, enums, and type aliases commonly found in TypeScript.

Usage:
  python ts2py.py --input <typescript_file> [--output <output_file>]
  python ts2py.py --batch <file_list.txt> [--output-dir <directory>]
"""

import os
import re
import sys
import argparse
from typing import Dict, List, Tuple, Optional, Any, Set, Union, TypeVar

# Type mappings from TypeScript to Python
TYPE_MAPPING = {
    'string': 'str',
    'number': 'float',
    'boolean': 'bool',
    'any': 'Any',
    'void': 'None',
    'null': 'None',
    'undefined': 'None',
    'object': 'dict',
    'Object': 'dict',
    'Array<': 'List[',
    'Record<': 'Dict[',
    'Map<': 'Dict[',
    'Set<': 'Set[',
    'Promise<': 'Awaitable['
}

class TypeScriptToPythonConverter:
    """Simple converter for TypeScript to Python."""
    
    def __init__(self):
        self.imports = set([
            "from typing import Dict, List, Optional, Any, Union"
        ])
    
    def convert_file(self, input_file: str, output_file: Optional[str] = None) -> str:
        """Convert a TypeScript file to Python."""
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + '.py'
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(input_file, 'r', encoding='utf-8') as f:
            ts_content = f.read()
        
        py_content = self.convert_content(ts_content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(py_content)
        
        return output_file
    
    def convert_content(self, ts_content: str) -> str:
        """Convert TypeScript content to Python."""
        # Reset imports for each conversion
        self.imports = set([
            "from typing import Dict, List, Optional, Any, Union"
        ])
        
        # Parse the TypeScript content
        py_lines = []
        
        # Remove comments and blank lines first
        ts_lines = []
        for line in ts_content.splitlines():
            line = re.sub(r'\/\/.*$', '', line)  # Remove single-line comments
            if line.strip():
                ts_lines.append(line)
        
        # Skip import statements for now (we'll add Python-specific imports)
        ts_code = '\n'.join([line for line in ts_lines if not line.strip().startswith('import ')])
        
        # Process enums
        if 'enum' in ts_code:
            self.imports.add("from enum import Enum")
            
        # Convert interfaces to classes
        py_code = self.convert_interfaces(ts_code)
        
        # Convert enums
        py_code = self.convert_enums(py_code)
        
        # Convert exports
        py_code = self.remove_exports(py_code)
        
        # Convert types
        py_code = self.convert_types(py_code)
        
        # Add imports at the top
        imports_text = '\n'.join(sorted(self.imports)) + '\n\n'
        
        return imports_text + py_code
    
    def convert_interfaces(self, ts_code: str) -> str:
        """Convert TypeScript interfaces to Python classes."""
        def interface_replacement(match):
            interface_name = match.group(1)
            interface_body = match.group(2)
            
            # Parse properties from the interface body
            properties = []
            for line in interface_body.split(';'):
                line = line.strip()
                if not line:
                    continue
                
                # Handle special case for nested objects
                if '{' in line and '}' in line:
                    # Simplified handling - in a real converter, this would need more care
                    line = line.replace('{', 'Dict[str, Any]')
                    line = line.replace('}', '')
                
                # Handle property with type annotation
                if ':' in line:
                    prop_parts = line.split(':', 1)
                    prop_name = prop_parts[0].strip()
                    prop_type = prop_parts[1].strip()
                    
                    # Convert types
                    py_type = self.convert_type(prop_type)
                    
                    # Add to properties
                    properties.append(f"    {prop_name}: {py_type}")
            
            # Create the Python class
            if properties:
                class_def = f"class {interface_name}:\n"
                return class_def + '\n'.join(properties)
            else:
                return f"class {interface_name}:\n    pass"
                
        # Match interface patterns with careful handling of nested braces
        pattern = r'interface\s+(\w+)(?:\s+extends\s+\w+)?\s*{([^}]+)}'
        return re.sub(pattern, interface_replacement, ts_code)
    
    def convert_enums(self, ts_code: str) -> str:
        """Convert TypeScript enums to Python enums."""
        def enum_replacement(match):
            enum_name = match.group(1)
            enum_body = match.group(2)
            
            # Parse enum values
            values = []
            for line in enum_body.split(','):
                line = line.strip()
                if not line:
                    continue
                
                # Handle enum value with or without assigned value
                if '=' in line:
                    parts = line.split('=', 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    values.append(f"    {key} = {value}")
                else:
                    values.append(f"    {line} = '{line}'")
            
            # Create the Python enum
            enum_def = f"class {enum_name}(Enum):\n"
            return enum_def + '\n'.join(values)
            
        # Match enum pattern
        pattern = r'enum\s+(\w+)\s*{([^}]+)}'
        return re.sub(pattern, enum_replacement, ts_code)
    
    def remove_exports(self, ts_code: str) -> str:
        """Remove export keywords."""
        ts_code = re.sub(r'export\s+', '', ts_code)
        return re.sub(r'export\s*{[^}]*}', '', ts_code)
    
    def convert_types(self, ts_code: str) -> str:
        """Convert TypeScript type definitions to Python type aliases."""
        def type_replacement(match):
            type_name = match.group(1)
            type_def = match.group(2)
            
            # Convert the type definition
            py_type = self.convert_type(type_def)
            
            return f"{type_name} = {py_type}"
            
        # Match type patterns
        pattern = r'type\s+(\w+)\s*=\s*([^;]+);?'
        return re.sub(pattern, type_replacement, ts_code)
    
    def convert_type(self, ts_type: str) -> str:
        """Convert a TypeScript type to a Python type annotation."""
        # Remove any semicolons or trailing garbage
        ts_type = ts_type.strip().rstrip(';')
        
        # Apply direct type conversions
        py_type = ts_type
        for ts_key, py_key in TYPE_MAPPING.items():
            py_type = py_type.replace(ts_key, py_key)
        
        # Convert array notation
        if py_type.endswith('[]'):
            base_type = py_type[:-2]
            py_type = f"List[{self.convert_type(base_type)}]"
        
        # Convert angle brackets to square brackets (for generics)
        if '<' in py_type and '>' in py_type:
            # Extract the parts
            match = re.match(r'(\w+)<(.+)>', py_type)
            if match:
                container, type_args = match.groups()
                container = TYPE_MAPPING.get(container, container)
                
                # Handle multiple type arguments
                if ',' in type_args:
                    args = [self.convert_type(arg.strip()) for arg in type_args.split(',')]
                    py_type = f"{container}[{', '.join(args)}]"
                else:
                    py_type = f"{container}[{self.convert_type(type_args)}]"
        
        # Handle union types
        if '|' in py_type:
            types = [self.convert_type(t.strip()) for t in py_type.split('|')]
            py_type = f"Union[{', '.join(types)}]"
            self.imports.add("from typing import Union")
        
        return py_type
    
    def batch_convert(self, file_list: str, output_dir: str = "python_converted") -> Tuple[int, int, List[str]]:
        """Convert multiple TypeScript files."""
        success_count = 0
        failure_count = 0
        failed_files = []
        
        # Read the list of files
        with open(file_list, 'r', encoding='utf-8') as f:
            files = [line.strip() for line in f if line.strip()]
        
        # Process each file
        for ts_file in files:
            try:
                # Compute the output path
                rel_path = ts_file
                if ts_file.startswith('./'):
                    rel_path = ts_file[2:]
                    
                output_path = os.path.join(output_dir, rel_path)
                output_path = os.path.splitext(output_path)[0] + '.py'
                
                # Convert the file
                self.convert_file(ts_file, output_path)
                print(f"Converted {ts_file} to {output_path}")
                success_count += 1
            except Exception as e:
                print(f"Failed to convert {ts_file}: {str(e)}")
                failure_count += 1
                failed_files.append(ts_file)
        
        return success_count, failure_count, failed_files

def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description='Convert TypeScript to Python')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--input', help='TypeScript file to convert')
    group.add_argument('--batch', help='Path to file containing list of TypeScript files to convert')
    parser.add_argument('--output', help='Output Python file path')
    parser.add_argument('--output-dir', default='python_converted', help='Output directory for batch conversion')
    
    args = parser.parse_args()
    converter = TypeScriptToPythonConverter()
    
    if args.batch:
        success, failure, failed_files = converter.batch_convert(args.batch, args.output_dir)
        print(f"Batch conversion complete: {success} successes, {failure} failures")
        if failed_files:
            print("Failed files:")
            for f in failed_files:
                print(f"  - {f}")
    else:
        output_file = converter.convert_file(args.input, args.output)
        print(f"Converted {args.input} to {output_file}")

if __name__ == '__main__':
    main() 