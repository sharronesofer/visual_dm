#!/usr/bin/env python3

import os
import re
import sys
import glob
import argparse
from typing import Dict, List, Optional, Tuple, Set
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ts2py')

# TypeScript to Python type mapping
TYPE_MAPPING = {
    'string': 'str',
    'number': 'float',
    'boolean': 'bool',
    'any': 'Any',
    'void': 'None',
    'Array<': 'List[',
    'Record<': 'Dict[',
    'Map<': 'Dict[',
    'Set<': 'Set[',
    'Promise<': 'Awaitable[',
    'null': 'None',
    'undefined': 'None',
    'never': 'NoReturn',
}

# Classes to import from typing
TYPING_IMPORTS = {
    'List', 'Dict', 'Tuple', 'Set', 'Optional', 'Union', 'Any', 
    'Callable', 'TypeVar', 'Generic', 'NoReturn', 'Awaitable', 'Protocol'
}

IMPORT_MAPPING = {
    'React': 'None  # React import removed',
    'useState': 'None  # React hooks removed',
    'useEffect': 'None  # React hooks removed',
    'useCallback': 'None  # React hooks removed',
    'useMemo': 'None  # React hooks removed',
    'useRef': 'None  # React hooks removed',
}

def camel_to_snake_case(name: str) -> str:
    """Convert camelCase to snake_case."""
    # Handle special cases where acronyms should remain uppercase
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', name).lower()

def process_imports(content: str) -> Tuple[str, Set[str]]:
    """Process imports and return modified content and required typing imports."""
    typing_imports = set()
    
    # Replace import statements
    def process_import_match(match):
        import_statement = match.group(0)
        if 'from' in import_statement:
            # Handle named imports: import { X, Y } from 'module';
            items_match = re.search(r'{(.*?)}', import_statement)
            if items_match:
                items = [item.strip() for item in items_match.group(1).split(',')]
                module_match = re.search(r'from\s+[\'"](.+?)[\'"]', import_statement)
                if not module_match:
                    return f"# {import_statement} # Could not parse module"
                
                module = module_match.group(1)
                
                # Create Python import
                if module.startswith('./') or module.startswith('../'):
                    # Local import
                    module = module.replace('.ts', '').replace('./', '')
                    return f"from {module} import {', '.join(items)}"
                else:
                    # External module import
                    return f"# from {module} import {', '.join(items)}"
            
            # Default import: import X from 'module';
            default_match = re.search(r'import\s+(\w+)\s+from', import_statement)
            if default_match:
                item = default_match.group(1)
                module_match = re.search(r'from\s+[\'"](.+?)[\'"]', import_statement)
                if not module_match:
                    return f"# {import_statement} # Could not parse module"
                
                module = module_match.group(1)
                
                if module.startswith('./') or module.startswith('../'):
                    # Local import
                    module = module.replace('.ts', '').replace('./', '')
                    return f"from {module} import {item}"
                else:
                    # External module import
                    return f"# import {item} # from {module}"
        
        # Handle direct imports: import * as X from 'module';
        star_match = re.search(r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"](.+?)[\'"]', import_statement)
        if star_match:
            item = star_match.group(1)
            module = star_match.group(2)
            if module.startswith('./') or module.startswith('../'):
                module = module.replace('.ts', '').replace('./', '')
                return f"import {module} as {item}"
            else:
                return f"# import {module} as {item}"
        
        # Basic import: import 'module';
        return f"# {import_statement} # Removed import"
    
    # Process imports
    content = re.sub(r'import .*?;', process_import_match, content)
    
    # Check for typing needs
    for typing_import in TYPING_IMPORTS:
        if f"{typing_import}[" in content:
            typing_imports.add(typing_import)
    
    return content, typing_imports

def process_interfaces(content: str) -> str:
    """Convert TypeScript interfaces to Python classes."""
    def interface_replacer(match):
        interface_name = match.group(1)
        interface_body = match.group(2)
        
        # Convert to Python class
        class_lines = [f"class {interface_name}:"]
        
        # Extract properties
        properties = re.findall(r'(\w+)(\??):\s*([^;]*);', interface_body)
        
        # Add constructor
        if properties:
            init_params = []
            init_body = []
            
            for prop_name, optional, prop_type in properties:
                # Convert type
                for ts_type, py_type in TYPE_MAPPING.items():
                    if ts_type in prop_type:
                        prop_type = prop_type.replace(ts_type, py_type)
                
                # Handle optional parameters
                if optional:
                    init_params.append(f"{camel_to_snake_case(prop_name)}: Optional[{prop_type}] = None")
                else:
                    init_params.append(f"{camel_to_snake_case(prop_name)}: {prop_type}")
                
                # Add assignment
                init_body.append(f"        self.{camel_to_snake_case(prop_name)} = {camel_to_snake_case(prop_name)}")
            
            class_lines.append(f"    def __init__(self, {', '.join(init_params)}):")
            class_lines.extend(init_body)
        else:
            class_lines.append("    pass")
        
        return "\n".join(class_lines)
    
    # Find interfaces and replace them
    interface_pattern = r'export\s+interface\s+(\w+)\s*{([^}]*)}'
    content = re.sub(interface_pattern, interface_replacer, content)
    
    return content

def process_types(content: str) -> str:
    """Convert TypeScript types to Python type aliases."""
    def type_replacer(match):
        type_name = match.group(1)
        type_def = match.group(2)
        
        # Convert union types (| operator)
        if '|' in type_def:
            union_types = [t.strip() for t in type_def.split('|')]
            for i, t in enumerate(union_types):
                for ts_type, py_type in TYPE_MAPPING.items():
                    if ts_type in t:
                        union_types[i] = t.replace(ts_type, py_type)
            
            # Create Union type
            return f"{type_name} = Union[{', '.join(union_types)}]"
        
        # Handle other type definitions
        for ts_type, py_type in TYPE_MAPPING.items():
            if ts_type in type_def:
                type_def = type_def.replace(ts_type, py_type)
        
        return f"{type_name} = {type_def}"
    
    # Find type declarations and replace them
    type_pattern = r'export\s+type\s+(\w+)\s*=\s*([^;]*);'
    content = re.sub(type_pattern, type_replacer, content)
    
    return content

def process_enums(content: str) -> str:
    """Convert TypeScript enums to Python Enums."""
    def enum_replacer(match):
        enum_name = match.group(1)
        enum_body = match.group(2)
        
        # Extract enum values
        enum_values = re.findall(r'(\w+)(?:\s*=\s*([^,]*))?', enum_body)
        
        # Create Python Enum
        enum_lines = [f"class {enum_name}(Enum):"]
        
        for name, value in enum_values:
            if value:
                # Has explicit value
                enum_lines.append(f"    {name} = {value}")
            else:
                # Auto-value, using the name as string
                enum_lines.append(f"    {name} = '{name}'")
        
        return "\n".join(enum_lines)
    
    # Find enums and replace them
    enum_pattern = r'export\s+enum\s+(\w+)\s*{([^}]*)}'
    content = re.sub(enum_pattern, enum_replacer, content)
    
    return content

def process_classes(content: str) -> str:
    """Convert TypeScript classes to Python classes."""
    def class_replacer(match):
        class_def = match.group(0)
        class_name = match.group(1)
        inheritance = match.group(2) if match.group(2) else ""
        class_body = match.group(3) if match.group(3) else ""
        
        # Handle inheritance
        if inheritance:
            inheritance = inheritance.replace('extends', '').replace('implements', '').strip()
            class_def = f"class {class_name}({inheritance}):"
        else:
            class_def = f"class {class_name}:"
        
        # Process class body
        # This is complex and might need special handling for various TS class features
        class_lines = [class_def]
        
        # Extract properties, methods, etc.
        # This is simplified and would need to be expanded for real usage
        
        # Replace 'this.' with 'self.'
        class_body = class_body.replace('this.', 'self.')
        
        # Handle constructor
        constructor_match = re.search(r'constructor\((.*?)\)\s*{([^}]*)}', class_body)
        if constructor_match:
            params = constructor_match.group(1)
            constructor_body = constructor_match.group(2)
            
            # Process params
            params = params.replace('private ', '').replace('public ', '').replace('readonly ', '')
            params = params.replace(': string', ': str').replace(': number', ': float').replace(': boolean', ': bool')
            
            # Create __init__ method
            init_method = f"    def __init__(self, {params}):\n"
            
            # Process constructor body
            constructor_body = constructor_body.replace('this.', 'self.')
            for line in constructor_body.split('\n'):
                if line.strip():
                    init_method += f"        {line.strip()}\n"
            
            class_lines.append(init_method)
        
        # Handle methods
        method_pattern = r'(private|public|protected)?\s*(\w+)\((.*?)\)(?:\s*:\s*([^{]*))?{([^}]*)}'
        for method_match in re.finditer(method_pattern, class_body):
            modifier = method_match.group(1) or ""
            method_name = method_match.group(2)
            params = method_match.group(3)
            return_type = method_match.group(4) or ""
            method_body = method_match.group(5)
            
            # Skip constructor as it's already handled
            if method_name == 'constructor':
                continue
            
            # Process params
            params = params.replace(': string', ': str').replace(': number', ': float').replace(': boolean', ': bool')
            params = "self" + (", " + params if params else "")
            
            # Process return type
            if return_type:
                for ts_type, py_type in TYPE_MAPPING.items():
                    if ts_type in return_type:
                        return_type = return_type.replace(ts_type, py_type)
                return_annotation = f" -> {return_type.strip()}"
            else:
                return_annotation = ""
            
            # Create method
            method_def = f"    def {camel_to_snake_case(method_name)}({params}){return_annotation}:"
            
            # Handle empty methods
            if not method_body.strip():
                method_def += "\n        pass"
                class_lines.append(method_def)
                continue
            
            # Process method body
            method_body = method_body.replace('this.', 'self.')
            method_body_lines = []
            
            for line in method_body.split('\n'):
                if line.strip():
                    # Simple indentation, might need more sophisticated handling
                    method_body_lines.append(f"        {line.strip()}")
            
            class_lines.append(method_def)
            class_lines.extend(method_body_lines)
        
        return "\n".join(class_lines)
    
    # Find classes and replace them
    class_pattern = r'export\s+class\s+(\w+)(?:\s+(extends|implements)\s+([^{]+))?\s*{([^}]*)}'
    # First check if pattern exists
    if re.search(class_pattern, content):
        content = re.sub(class_pattern, class_replacer, content)
    
    return content

def process_functions(content: str) -> str:
    """Convert TypeScript functions to Python functions."""
    def function_replacer(match):
        async_keyword = match.group(1) or ""
        func_name = match.group(2)
        params = match.group(3)
        return_type = match.group(4) or ""
        func_body = match.group(5)
        
        # Process parameters
        params = params.replace(': string', ': str').replace(': number', ': float').replace(': boolean', ': bool')
        
        # Process return type
        if return_type:
            for ts_type, py_type in TYPE_MAPPING.items():
                if ts_type in return_type:
                    return_type = return_type.replace(ts_type, py_type)
            return_annotation = f" -> {return_type.strip()}"
        else:
            return_annotation = ""
        
        # Create function definition
        if async_keyword:
            func_def = f"async def {camel_to_snake_case(func_name)}({params}){return_annotation}:"
        else:
            func_def = f"def {camel_to_snake_case(func_name)}({params}){return_annotation}:"
        
        # Process function body
        func_body_lines = []
        for line in func_body.split('\n'):
            if line.strip():
                func_body_lines.append(f"    {line.strip()}")
        
        # Handle empty functions
        if not func_body_lines:
            func_body_lines = ["    pass"]
        
        return func_def + "\n" + "\n".join(func_body_lines)
    
    # Find functions and replace them
    function_pattern = r'export\s+(async\s+)?function\s+(\w+)\((.*?)\)(?:\s*:\s*([^{]*))?{([^}]*)}'
    if re.search(function_pattern, content):
        content = re.sub(function_pattern, function_replacer, content)
    
    return content

def convert_typescript_to_python(ts_content: str) -> str:
    """Convert TypeScript code to Python."""
    # Process imports and get required typing imports
    content, typing_imports = process_imports(ts_content)
    
    # Add Python imports based on content
    python_imports = []
    
    # Add typing imports if needed
    if typing_imports:
        typing_import_str = ", ".join(sorted(typing_imports))
        python_imports.append(f"from typing import {typing_import_str}")
    
    # Check for Union in type definitions
    if "export type" in content and "|" in content:
        if "Union" not in typing_imports:
            if typing_imports:
                python_imports[-1] = python_imports[-1] + ", Union"
            else:
                python_imports.append("from typing import Union")
    
    # Check for enums
    if "enum" in content.lower():
        python_imports.append("from enum import Enum")
    
    # Process the content
    content = process_interfaces(content)
    content = process_types(content)
    content = process_enums(content)
    content = process_classes(content)
    content = process_functions(content)
    
    # Common replacements
    replacements = [
        # Logical operators
        ('&&', 'and'),
        ('||', 'or'),
        ('!', 'not '),
        
        # Null checks
        ('=== null', 'is None'),
        ('!== null', 'is not None'),
        ('== null', 'is None'),
        ('!= null', 'is not None'),
        
        # Undefined checks
        ('=== undefined', 'is None'),
        ('!== undefined', 'is not None'),
        ('== undefined', 'is None'),
        ('!= undefined', 'is not None'),
        
        # String concatenation
        (' + ', ' + '),  # This one stays as-is
        
        # Array methods
        ('.push(', '.append('),
        ('.pop()', '.pop()'),
        ('.shift()', '.pop(0)'),
        ('.unshift(', '.insert(0, '),
        ('.join(', '.join('),
        ('.map(', 'map(lambda item: '),
        ('.filter(', 'filter(lambda item: '),
        ('.reduce(', 'reduce(lambda acc, item: '),
        ('.forEach(', 'for item in '),
        ('.includes(', '__contains__('),
        
        # Object handling
        ('Object.keys(', 'list('),
        ('Object.values(', 'list('),
        ('Object.entries(', 'list('),
        
        # Console statements
        ('console.log(', 'print('),
        ('console.error(', 'print("ERROR:", '),
        ('console.warn(', 'print("WARNING:", '),
        ('console.info(', 'print("INFO:", '),
        
        # Export statements
        ('export default', '# export default'),
        ('export ', ''),
        
        # Arrow functions (simplified)
        (' => {', 'lambda: '),
        (' => (', 'lambda: ('),
        
        # Template literals (simplified)
        ('`', '"'),
        ('${', '{'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Add imports at the top
    if python_imports:
        return "\n".join(python_imports) + "\n\n" + content
    else:
        return content

def convert_file(input_file: str, output_file: str) -> None:
    """Convert a TypeScript file to Python."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            ts_content = f.read()
        
        # Skip empty files
        if not ts_content.strip():
            logger.warning(f"Skipping empty file: {input_file}")
            return
        
        python_content = convert_typescript_to_python(ts_content)
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_content)
        
        logger.info(f"Converted: {input_file} -> {output_file}")
    except Exception as e:
        logger.error(f"Error converting {input_file}: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())

def main():
    parser = argparse.ArgumentParser(description='Convert TypeScript files to Python')
    parser.add_argument('input', help='Input TypeScript file or directory')
    parser.add_argument('--output', '-o', help='Output Python file or directory')
    parser.add_argument('--recursive', '-r', action='store_true', help='Process directories recursively')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    if os.path.isfile(args.input):
        # Convert a single file
        input_file = args.input
        if args.output:
            output_file = args.output
        else:
            output_file = os.path.splitext(input_file)[0] + '.py'
        
        convert_file(input_file, output_file)
    
    elif os.path.isdir(args.input):
        # Convert all TypeScript files in the directory
        input_dir = args.input
        output_dir = args.output or input_dir.replace('src', 'python_converted')
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        if args.recursive:
            pattern = os.path.join(input_dir, '**', '*.ts')
            files = glob.glob(pattern, recursive=True)
        else:
            pattern = os.path.join(input_dir, '*.ts')
            files = glob.glob(pattern)
        
        for input_file in files:
            # Skip node_modules and test files if present
            if 'node_modules' in input_file or '__tests__' in input_file:
                continue
            
            rel_path = os.path.relpath(input_file, input_dir)
            output_file = os.path.join(output_dir, rel_path.replace('.ts', '.py'))
            
            convert_file(input_file, output_file)
    
    else:
        logger.error(f"Input path does not exist: {args.input}")
        sys.exit(1)

if __name__ == '__main__':
    main() 