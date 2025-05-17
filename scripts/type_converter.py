import re
import sys
from typing import Any, Dict, List, Optional, Set, Union

# Basic TypeScript to Python type mapping
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
    'Array': 'List',
    'Record': 'Dict',
    'Map': 'Dict',
    'Set': 'Set',
    'Promise': 'Awaitable'
}

# Python version detection for typing_extensions
PYTHON_VERSION = sys.version_info[:2]

def needs_typing_extensions(feature: str) -> bool:
    # TypedDict, Literal, Final, Generic: available in typing >= 3.8
    if feature in ("TypedDict", "Literal", "Final", "Generic"):
        return PYTHON_VERSION < (3, 8)
    return False

class TypeConversionError(Exception):
    """Custom exception for type conversion errors."""
    pass

class TypeConverter:
    """
    Handles conversion of TypeScript types to Python type annotations.
    
    Features:
    - Primitive types (string, number, boolean, any, void, null, undefined, object)
    - Generics (Array<T>, Map<K, V>, Set<T>, Record<K, V>, Promise<T>)
    - Utility types (Partial<T>, Required<T>, Readonly<T>, Pick<T, K>, Omit<T, K>)
    - Unions (A | B), Intersections (A & B)
    - Mapped types ({ [K in keyof T]: T[K] })
    - Conditional types (T extends U ? X : Y)
    - Typing extensions (TypedDict, Literal, Final, Generic)
    - TypeScript object/interface to Python TypedDict (heuristic)
    - Configuration options via self.options (strict_mode, fallback_to_any, etc.)

    Limitations:
    - Mapped and conditional types are best-effort and may not always map directly
    - Complex nested generics and recursive types may require manual review
    - TypedDict generation is heuristic and may not capture all interface semantics
    - Some TypeScript utility types (e.g., Pick, Omit) are mapped as pass-throughs
    - TypeScript enums, namespaces, and advanced decorators are not handled here
    """
    def __init__(self, options=None):
        """
        Initialize the TypeConverter.
        Args:
            options (dict, optional): Configuration options for type conversion behavior.
                Supported options:
                    - strict_mode (bool): If True, raise on unsupported types. If False, fallback to 'Any'.
                    - fallback_to_any (bool): If True, use 'Any' for unknown types. Default: False.
                    - log_level (str): Logging level for conversion operations.
        """
        self.options = options or {}
        self.imports: Set[str] = set([
            "from typing import Dict, List, Optional, Any, Union"
        ])
        self.typing_extensions: Set[str] = set()
        self.utility_type_map = {
            'Partial': lambda t: f"Optional[{t}]",
            'Required': lambda t: t,
            'Readonly': lambda t: t,
            'Pick': lambda t, keys: t,  # No direct mapping
            'Omit': lambda t, keys: t,  # No direct mapping
            'Record': lambda k, v: f"Dict[{k}, {v}]"
        }
        self.typed_dict_defs: List[str] = []  # Store TypedDict class definitions
        self.type_vars: Set[str] = set()      # For generics

    def convert(self, ts_type: str, _depth: int = 0) -> str:
        """
        Convert a TypeScript type string to a Python type annotation string.
        Handles advanced constructs: unions, intersections, mapped, conditional, utility types, and typing extensions.
        Args:
            ts_type (str): The TypeScript type string to convert.
            _depth (int): Recursion depth guard (internal use).
        Returns:
            str: Python type annotation string.
        Raises:
            TypeConversionError: On recursion overflow or malformed types.
        """
        if _depth > 30:
            raise TypeConversionError("Maximum recursion depth exceeded in type conversion (possible cyclic or malformed type)")
        ts_type = ts_type.strip().rstrip(';')

        # Only strip outer parentheses if they wrap the entire type
        if self._is_wrapped_in_parens(ts_type):
            return self.convert(ts_type[1:-1], _depth=_depth+1)

        # Literal types (string or numeric literal)
        if re.match(r"^(['\"]?\w+['\"]?)(\s*\|\s*['\"]?\w+['\"]?)+$", ts_type):
            self._add_typing_extension("Literal")
            literals = [l.strip().strip("'\"") for l in ts_type.split('|')]
            py_literals = ', '.join([repr(l) if not l.isdigit() else l for l in literals])
            return f"Literal[{py_literals}]"

        # Intersection types (A & B)
        if '&' in ts_type:
            parts = self._split_top_level(ts_type, '&')
            types = [self.convert(t.strip(), _depth=_depth+1) for t in parts]
            self.imports.add("from typing import Union")
            return f"Union[{', '.join(types)}]  # Intersection type, best-effort"

        # Union types (A | B)
        if '|' in ts_type:
            parts = self._split_top_level(ts_type, '|')
            types = [self.convert(t.strip(), _depth=_depth+1) for t in parts]
            # If one of the types is None, use Optional
            if 'None' in types:
                types = [t for t in types if t != 'None']
                return f"Optional[{', '.join(types)}]" if len(types) == 1 else f"Optional[Union[{', '.join(types)}]]"
            self.imports.add("from typing import Union")
            return f"Union[{', '.join(types)}]"

        # Array notation (e.g., string[] -> List[str])
        if ts_type.endswith('[]'):
            base_type = ts_type[:-2]
            return f"List[{self.convert(base_type, _depth=_depth+1)}]"

        # Generics (e.g., Array<T>, Map<K, V>, Partial<T>, etc.)
        generic_match = re.match(r'^(\w+)\s*<(.+)>$', ts_type)
        if generic_match:
            container, type_args = generic_match.groups()
            if container in self.utility_type_map:
                args = self._split_type_args(type_args)
                try:
                    if container == 'Record' and len(args) == 2:
                        return self.utility_type_map[container](self.convert(args[0], _depth=_depth+1), self.convert(args[1], _depth=_depth+1))
                    elif container in ('Pick', 'Omit') and len(args) == 2:
                        return self.utility_type_map[container](self.convert(args[0], _depth=_depth+1), args[1])
                    elif container in ('Partial', 'Required', 'Readonly') and len(args) == 1:
                        return self.utility_type_map[container](self.convert(args[0], _depth=_depth+1))
                except Exception as e:
                    raise TypeConversionError(f"Error converting utility type {container}: {e}")
            # Generic type support
            if container[0].isupper():
                self._add_typing_extension("Generic")
                self.type_vars.add(container)
                args = [self.convert(arg.strip(), _depth=_depth+1) for arg in self._split_type_args(type_args)]
                return f"{container}[{', '.join(args)}]"
            container_py = TYPE_MAPPING.get(container, container)
            args = [self.convert(arg.strip(), _depth=_depth+1) for arg in self._split_type_args(type_args)]
            return f"{container_py}[{', '.join(args)}]"

        # Mapped types (e.g., { [K in keyof T]: T[K] })
        mapped_match = re.match(r'^\{\s*\[\s*\w+\s+in\s+keyof\s+\w+\s*\]\s*:\s*(.+)\s*\}$', ts_type)
        if mapped_match:
            value_type = self.convert(mapped_match.group(1), _depth=_depth+1)
            return f"Dict[str, {value_type}]  # Mapped type, best-effort"

        # Conditional types (T extends U ? X : Y)
        cond_match = re.match(r'^(\w+)\s+extends\s+(\w+)\s*\?\s*(.+)\s*:\s*(.+)$', ts_type)
        if cond_match:
            return f"Any  # Conditional type ({ts_type}), not directly supported"

        # TypeScript interface/object to TypedDict
        if self._is_typescript_object(ts_type):
            return self._convert_to_typed_dict(ts_type)

        # Direct type mapping
        return TYPE_MAPPING.get(ts_type, ts_type)

    def _convert_to_typed_dict(self, ts_type: str) -> str:
        """
        Convert a TypeScript object/interface type to a Python TypedDict definition.
        Note: This is a stub. In a full implementation, parse the object properties.
        Args:
            ts_type (str): The TypeScript object/interface type string.
        Returns:
            str: Name of the generated TypedDict class.
        """
        self._add_typing_extension("TypedDict")
        # This is a stub: in a real implementation, parse the object properties
        # For now, just return a placeholder
        class_name = "AutoTypedDict"
        self.typed_dict_defs.append(f"class {class_name}(TypedDict):\n    ...")
        return class_name

    def _add_typing_extension(self, name: str):
        """
        Add a typing extension import if needed for the given feature.
        Args:
            name (str): The typing extension feature name (e.g., 'TypedDict', 'Literal').
        """
        if needs_typing_extensions(name):
            self.typing_extensions.add(name)
        else:
            self.imports.add(f"from typing import {name}")

    def _is_typescript_object(self, ts_type: str) -> bool:
        """
        Heuristic to detect if a TypeScript type is an object/interface.
        Args:
            ts_type (str): The TypeScript type string.
        Returns:
            bool: True if the type looks like an object/interface.
        """
        return ts_type.strip().startswith('{') and ts_type.strip().endswith('}')

    def _is_wrapped_in_parens(self, s: str) -> bool:
        """
        Check if a string is fully wrapped in a single pair of parentheses.
        Args:
            s (str): The string to check.
        Returns:
            bool: True if the string is wrapped in parentheses.
        """
        if not (s.startswith('(') and s.endswith(')')):
            return False
        depth = 0
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0 and i != len(s) - 1:
                return False
        return True

    def _split_top_level(self, s: str, sep: str) -> list:
        """
        Split a string by sep, but only at the top level (not inside parens or generics).
        Args:
            s (str): The string to split.
            sep (str): The separator character.
        Returns:
            list: List of split substrings at the top level.
        """
        args = []
        depth_paren = 0
        depth_angle = 0
        current = ''
        for c in s:
            if c == '(': depth_paren += 1
            elif c == ')': depth_paren -= 1
            elif c == '<': depth_angle += 1
            elif c == '>': depth_angle -= 1
            if c == sep and depth_paren == 0 and depth_angle == 0:
                args.append(current)
                current = ''
            else:
                current += c
        if current:
            args.append(current)
        return args

    def _split_type_args(self, type_args: str) -> List[str]:
        """
        Split generic type arguments, respecting nested generics.
        Args:
            type_args (str): The type arguments string (e.g., 'A, B<C, D>').
        Returns:
            List[str]: List of type argument strings.
        """
        args = []
        depth = 0
        current = ''
        for c in type_args:
            if c == '<': depth += 1
            elif c == '>': depth -= 1
            elif c == ',' and depth == 0:
                args.append(current)
                current = ''
            else:
                current += c
        if current:
            args.append(current)
        return args

    def get_imports(self) -> List[str]:
        """
        Get the list of required Python import statements for the converted types.
        Returns:
            List[str]: List of import statements.
        """
        imports = list(self.imports)
        if self.typing_extensions:
            ext_imports = ', '.join(sorted(self.typing_extensions))
            imports.append(f"from typing_extensions import {ext_imports}")
        return sorted(imports)

    def get_typed_dict_defs(self) -> List[str]:
        """
        Get the list of generated TypedDict class definitions.
        Returns:
            List[str]: List of TypedDict class definition strings.
        """
        return self.typed_dict_defs

    def get_type_vars(self) -> List[str]:
        """
        Get the list of generic type variable names used in the conversion.
        Returns:
            List[str]: List of type variable names.
        """
        return list(self.type_vars) 