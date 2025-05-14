import os
import ast
from collections import defaultdict
from typing import List, Tuple, Dict, Set, Optional, Any

EXCLUDED_DIRS: Set[str] = {
    "venv", "__pycache__", ".git", ".mypy_cache", 
    ".pytest_cache", "site-packages", "build", "dist"
}

def extract_routes(filepath: str) -> List[Tuple[str, Tuple[str, ...], str, int]]:
    """Extract route information from a Python file.
    
    Args:
        filepath: Path to the Python file to analyze
        
    Returns:
        List of tuples containing (route_path, methods, filepath, line_number)
    """
    routes: List[Tuple[str, Tuple[str, ...], str, int]] = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filepath)
    except (SyntaxError, IOError) as e:
        print(f"❌ Error parsing {filepath}: {e}")
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for deco in node.decorator_list:
                if (
                    isinstance(deco, ast.Call) 
                    and hasattr(deco.func, 'attr') 
                    and deco.func.attr == 'route'
                ):
                    route_path: Optional[str] = deco.args[0].s if deco.args else None
                    methods: List[str] = ['GET']
                    for kw in deco.keywords:
                        if kw.arg == 'methods' and isinstance(kw.value, ast.List):
                            methods = [m.s for m in kw.value.elts if isinstance(m, ast.Str)]
                    if route_path:
                        routes.append((route_path, tuple(sorted(methods)), filepath, node.lineno))
    return routes

def analyze_routes_for_duplicates(directory: str) -> None:
    """Analyze Flask routes in a directory for duplicates.
    
    Args:
        directory: Path to the directory to analyze
    """
    print("🔍 Precise Flask Route Duplication Check:\n")
    occurrences: Dict[Tuple[str, Tuple[str, ...]], List[Tuple[str, int]]] = defaultdict(list)

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                routes = extract_routes(path)
                for route, methods, filepath, line in routes:
                    occurrences[(route, methods)].append((filepath, line))

    duplicates = {k: v for k, v in occurrences.items() if len(v) > 1}

    if duplicates:
        for (route, methods), instances in duplicates.items():
            methods_display = ','.join(methods)
            print(f"⚠️ Route '{route}' [{methods_display}] duplicated in:")
            for filepath, line in instances:
                print(f"  - {filepath} (line {line})")
            print()
    else:
        print("✅ No duplicate routes found!")

if __name__ == "__main__":
    project_path = "/Users/Sharrone/Visual_DM"
    analyze_routes_for_duplicates(project_path)
