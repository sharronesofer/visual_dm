import os
import ast
from collections import defaultdict, Counter

def analyze_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except Exception:
        return []

    function_flags = []
    global_vars = []
    dict_keys = Counter()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            arg_count = len(node.args.args)
            if arg_count >= 4:
                function_flags.append((node.name, arg_count))

        if isinstance(node, ast.Global):
            global_vars.extend(node.names)

        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Subscript):  # e.g., char["stats"]["STR"]
                if isinstance(node.value.slice, ast.Constant) and isinstance(node.slice, ast.Constant):
                    key_chain = f'{node.value.slice.value}.{node.slice.value}'
                    dict_keys[key_chain] += 1

    return function_flags, global_vars, dict_keys


def scan_folder(path):
    print("🔍 Class Candidate Analysis\n")
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                functions, globals_used, nested_keys = analyze_file(full_path)

                if functions or globals_used or nested_keys:
                    print(f"📁 {file}")
                for name, count in functions:
                    print(f"  ⚠️  Function '{name}' has {count} arguments — maybe bundle into a class?")
                if globals_used:
                    print(f"  🧨 Uses global variables: {globals_used}")
                for key, freq in nested_keys.items():
                    if freq > 3:
                        print(f"  📦 Accesses nested dict '{key}' {freq} times — consider a class")
                print()


if __name__ == "__main__":
    scan_folder("/Users/Sharrone/Visual_DM/app")  # <- Change if needed
