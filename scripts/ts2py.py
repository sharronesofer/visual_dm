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
import ast
import logging
import json
from type_converter import TypeConverter

class TypeScriptToPythonConverter:
    """
    TypeScript to Python converter using advanced TypeConverter for type annotations.

    Features:
    - Converts TypeScript files to Python code with type annotations
    - Integrates with TypeConverter for advanced type support
    - Handles interfaces, enums, type aliases, and JSX/React components
    - Supports configuration options for type conversion behavior
    - Provides logging for type conversion operations
    """
    def __init__(self, config=None):
        """
        Initialize the converter.
        Args:
            config (dict, optional): Configuration options for type conversion and logging.
        """
        self.config = config or {}
        self.type_converter = TypeConverter(self.config.get('type_conversion_options', {}))
        self.imports = set()
        self.logger = logging.getLogger("ts2py.typeconv")
    
    def convert_file(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Convert a TypeScript file to Python.
        Args:
            input_file (str): Path to the TypeScript file.
            output_file (str, optional): Path to the output Python file. If None, auto-generates.
        Returns:
            str: Path to the generated Python file.
        """
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
        """
        Convert TypeScript content to Python code.
        Args:
            ts_content (str): The TypeScript source code as a string.
        Returns:
            str: The converted Python code as a string.
        """
        # Reset imports and type converter for each conversion
        self.type_converter = TypeConverter(self.config.get('type_conversion_options', {}))
        self.imports = set()
        
        # --- React/JSX Detection and Conversion ---
        if self.contains_jsx(ts_content):
            return self.convert_react_component(ts_content)
        # --- End React/JSX ---
        
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
        imports_text = '\n'.join(self.type_converter.get_imports()) + '\n\n'
        
        return imports_text + py_code
    
    def convert_interfaces(self, ts_code: str) -> str:
        """
        Convert TypeScript interfaces to Python classes.
        Args:
            ts_code (str): TypeScript code string.
        Returns:
            str: Python code with class definitions.
        """
        def interface_replacement(match):
            interface_name = match.group(1)
            interface_body = match.group(2)
            properties = []
            for line in interface_body.split(';'):
                line = line.strip()
                if not line:
                    continue
                if '{' in line and '}' in line:
                    line = line.replace('{', 'Dict[str, Any]')
                    line = line.replace('}', '')
                if ':' in line:
                    prop_parts = line.split(':', 1)
                    prop_name = prop_parts[0].strip()
                    prop_type = prop_parts[1].strip()
                    try:
                        py_type = self.type_converter.convert(prop_type)
                        self.logger.info(f"Converted {prop_type} -> {py_type}")
                    except Exception as e:
                        self.logger.warning(f"Failed to convert type '{prop_type}': {e}")
                        py_type = 'Any'
                    properties.append(f"    {prop_name}: {py_type}")
            if properties:
                class_def = f"class {interface_name}:\n"
                return class_def + '\n'.join(properties)
            else:
                return f"class {interface_name}:\n    pass"
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
        """
        Convert TypeScript type definitions to Python type aliases.
        Args:
            ts_code (str): TypeScript code string.
        Returns:
            str: Python code with type alias definitions.
        """
        def type_replacement(match):
            type_name = match.group(1)
            type_def = match.group(2)
            try:
                py_type = self.type_converter.convert(type_def)
                self.logger.info(f"Converted type alias {type_name}: {type_def} -> {py_type}")
            except Exception as e:
                self.logger.warning(f"Failed to convert type alias '{type_name}': {e}")
                py_type = 'Any'
            return f"{type_name} = {py_type}"
            
        # Match type patterns
        pattern = r'type\s+(\w+)\s*=\s*([^;]+);?'
        return re.sub(pattern, type_replacement, ts_code)
    
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

    def contains_jsx(self, ts_content: str) -> bool:
        """Detect if the TypeScript content contains JSX/React code."""
        # Simple heuristic: look for angle brackets not part of generics, or React import
        if re.search(r'<[A-Za-z][^>]*>', ts_content) and 'function' in ts_content:
            return True
        if 'import React' in ts_content or 'from "react"' in ts_content:
            return True
        return False

    def write_jinja2_template(self, component_name: str, template_str: str) -> str:
        """Write the Jinja2 template to disk in scripts/templates/generated/ as kebab-case."""
        import os
        import re
        # Convert CamelCase or PascalCase to kebab-case
        kebab = re.sub(r'(?<!^)(?=[A-Z])', '-', component_name).lower()
        filename = f"{kebab}.jinja2"
        out_dir = os.path.join(os.path.dirname(__file__), "templates", "generated")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(template_str)
        return out_path

    def _extract_brace_block(self, text, start_index):
        """Extract a block of text enclosed in braces starting from start_index."""
        depth = 0
        block = []
        in_block = False
        for i, c in enumerate(text[start_index:], start=start_index):
            if c == '{':
                depth += 1
                in_block = True
            elif c == '}':
                depth -= 1
            if in_block:
                block.append(c)
            if in_block and depth == 0:
                break
        return ''.join(block)

    def convert_react_component(self, ts_content: str) -> str:
        """Parse React/JSX components and output a Jinja2 template for each detected component, writing to disk."""
        logger = logging.getLogger("ts2py.react")

        # Find all functional components (function declarations returning JSX)
        func_components = []
        for m in re.finditer(r'function\s+(\w+)\s*\(([^)]*)\)\s*{', ts_content):
            name, args = m.group(1), m.group(2)
            body_start = m.end() - 1
            body = self._extract_brace_block(ts_content, body_start)
            func_components.append((name, args, body))
        # Find all class components (class extends React.Component)
        class_components = []
        for m in re.finditer(r'class\s+(\w+)\s+extends\s+React\.Component\s*{', ts_content):
            name = m.group(1)
            body_start = m.end() - 1
            body = self._extract_brace_block(ts_content, body_start)
            class_components.append((name, body))

        output_paths = []
        # Process functional components
        for name, args, body in func_components:
            # Robustly extract the return JSX (handles multi-line and nested parens)
            jsx_code = None
            return_match = re.search(r'return\s*\((.*)\);', body, re.DOTALL)
            if return_match:
                jsx_code = return_match.group(1).strip()
            else:
                # Try to find return <JSX> on a single line
                return_match = re.search(r'return\s+(<.*>);', body, re.DOTALL)
                if return_match:
                    jsx_code = return_match.group(1).strip()
            if jsx_code:
                ast = self.parse_jsx_to_ast(jsx_code)
                jinja_template = self.jsx_ast_to_jinja2(ast)
                out_path = self.write_jinja2_template(name, jinja_template)
                output_paths.append(out_path)
        # Process class components similarly (look for render method)
        for name, body in class_components:
            render_match = re.search(r'render\s*\([^)]*\)\s*{', body)
            if render_match:
                render_body_start = render_match.end() - 1
                render_body = self._extract_brace_block(body, render_body_start)
                jsx_code = None
                return_match = re.search(r'return\s*\((.*)\);', render_body, re.DOTALL)
                if return_match:
                    jsx_code = return_match.group(1).strip()
                else:
                    return_match = re.search(r'return\s+(<.*>);', render_body, re.DOTALL)
                    if return_match:
                        jsx_code = return_match.group(1).strip()
                if jsx_code:
                    ast = self.parse_jsx_to_ast(jsx_code)
                    jinja_template = self.jsx_ast_to_jinja2(ast)
                    out_path = self.write_jinja2_template(name, jinja_template)
                    output_paths.append(out_path)
        if output_paths:
            return ("# React/JSX components detected.\n"
                    "# Jinja2 templates generated and written to:\n" +
                    '\n'.join(f"#   {p}" for p in output_paths) + '\n')
        # Fallback: log AST structure
        ast_nodes = []
        for name, args, body in func_components:
            ast_nodes.append({
                'type': 'FunctionalComponent',
                'name': name,
                'args': args,
                'body': body.strip()
            })
        for name, body in class_components:
            ast_nodes.append({
                'type': 'ClassComponent',
                'name': name,
                'body': body.strip()
            })
        ast_dump = json.dumps(ast_nodes, indent=2)
        return (
            '# React/JSX component detected.\n'
            '# Parsed AST structure:\n'
            f'# {ast_dump}\n'
            'pass\n'
        )

    def parse_jsx_to_ast(self, jsx_code: str):
        """Very basic recursive descent parser for JSX to AST. Handles nested elements, fragments, children, props, and expressions."""
        import xml.etree.ElementTree as ET
        import html
        # Preprocess: replace React.Fragment with fragment, self-closing tags, etc.
        jsx_code = jsx_code.replace('<React.Fragment>', '<fragment>').replace('</React.Fragment>', '</fragment>')
        jsx_code = re.sub(r'<([A-Za-z0-9_]+)([^>]*)/>', r'<\1\2></\1>', jsx_code)  # expand self-closing
        # Replace JS expressions with placeholders
        exprs = {}
        def expr_repl(match):
            key = f'__EXPR_{len(exprs)}__'
            exprs[key] = match.group(1)
            return key
        jsx_code = re.sub(r'\{([^}]+)\}', expr_repl, jsx_code)
        # Parse as XML
        try:
            root = ET.fromstring(jsx_code)
        except Exception as e:
            return {'type': 'Raw', 'code': jsx_code, 'error': str(e)}
        def node_to_ast(node):
            children = [node_to_ast(child) for child in node]
            text = (node.text or '').strip()
            tail = (node.tail or '').strip()
            props = dict(re.findall(r'(\w+)="([^"]*)"', ET.tostring(node, encoding='unicode')))
            # Restore expressions in text
            for k, v in exprs.items():
                text = text.replace(k, '{' + v + '}')
                tail = tail.replace(k, '{' + v + '}')
            return {
                'type': 'JSXElement',
                'tag': node.tag,
                'props': props,
                'text': text,
                'tail': tail,
                'children': children
            }
        return node_to_ast(root)

    def jsx_ast_to_jinja2(self, ast):
        """Recursively convert JSX AST to Jinja2 template syntax, handling fragments, children, expressions, conditionals, and lists."""
        if ast['type'] == 'Raw':
            return ast['code']
        tag = ast['tag']
        props = ast['props']
        text = ast['text']
        tail = ast['tail']
        children = ast['children']
        # Handle fragment
        if tag == 'fragment':
            return ''.join(self.jsx_ast_to_jinja2(child) for child in children)
        # Handle conditional rendering (simple ternary)
        if text and '?' in text and ':' in text:
            # {condition ? a : b}
            m = re.match(r'\{(.+?)\?(.+?):(.+)\}', text)
            if m:
                cond, a, b = m.groups()
                return f'{{% if {cond.strip()} %}}{a.strip()}{{% else %}}{b.strip()}{{% endif %}}'
        # Handle list rendering (map)
        if text and '.map(' in text:
            # {items.map(item => <div>{item}</div>)}
            m = re.match(r'\{([\w\.]+)\.map\((\w+)\s*=>\s*(<.+>)\)\}', text)
            if m:
                arr, var, inner = m.groups()
                inner_ast = self.parse_jsx_to_ast(inner)
                return f'{{% for {var} in {arr} %}}{self.jsx_ast_to_jinja2(inner_ast)}{{% endfor %}}'
        # Build props string
        props_str = ' '.join(f'{k}="{v}"' for k, v in props.items())
        # Replace {var} with {{ var }}
        def jinja_expr(s):
            return re.sub(r'\{([^}]+)\}', r'{{ \1 }}', s)
        content = jinja_expr(text) + ''.join(self.jsx_ast_to_jinja2(child) for child in children) + jinja_expr(tail)
        return f'<{tag} {props_str}>{content}</{tag}>' if props_str else f'<{tag}>{content}</{tag}>'

def main():
    """
    Command-line entry point for the TypeScript to Python converter.
    Parses arguments, sets up logging and config, and runs the conversion.
    """
    parser = argparse.ArgumentParser(description='Convert TypeScript to Python')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--input', help='TypeScript file to convert')
    group.add_argument('--batch', help='Path to file containing list of TypeScript files to convert')
    parser.add_argument('--output', help='Output Python file path')
    parser.add_argument('--output-dir', default='python_converted', help='Output directory for batch conversion')
    parser.add_argument('--strict', action='store_true', help='Enable strict type conversion mode')
    parser.add_argument('--fallback-to-any', action='store_true', help='Fallback to Any for unsupported types')
    parser.add_argument('--log-level', default='WARNING', help='Logging level (DEBUG, INFO, WARNING, ERROR)')
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.WARNING))
    config = {
        'type_conversion_options': {
            'strict_mode': args.strict,
            'fallback_to_any': args.fallback_to_any,
            'log_level': args.log_level.upper(),
        }
    }
    converter = TypeScriptToPythonConverter(config)
    
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