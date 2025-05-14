import os
import ast

EXCLUDED_DIRS = {"venv", "__pycache__", ".git", ".mypy_cache", ".pytest_cache", "site-packages", "build", "dist"}


def analyze_stub_functions(filepath, max_stub_length=3):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return []

    try:
        tree = ast.parse(content)
    except Exception:
        return []

    stub_functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_lineno = node.lineno
            end_lineno = getattr(node, 'end_lineno', start_lineno)

            function_length = end_lineno - start_lineno + 1

            if function_length <= max_stub_length:
                stub_functions.append((node.name, function_length, start_lineno))

    return stub_functions


def analyze_directory_for_stubs(directory, max_stub_length=3):
    print("🔍 Stub Function Analysis (short functions ≤ 3 lines):\n")

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                stubs = analyze_stub_functions(path, max_stub_length)

                if stubs:
                    print(f"\n📌 {path}")
                    for name, length, line in stubs:
                        print(f"  • `{name}` (line {line}) — {length} lines")


if __name__ == "__main__":
    project_path = "/Users/Sharrone/Visual_DM"  # 👈 Your project path here
    analyze_directory_for_stubs(project_path, max_stub_length=3)