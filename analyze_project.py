import os
import ast

EXCLUDED_DIRS = {"venv", "__pycache__", ".git", ".mypy_cache", ".pytest_cache", "site-packages", "build", "dist"}

def analyze_python_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return (0, 0, 0, 0)

    code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
    total_lines = len(code_lines)

    try:
        tree = ast.parse("".join(lines))
    except Exception:
        return (total_lines, 0, 0, 0)

    function_count = sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
    class_count = sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    import_count = sum(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree))

    return (total_lines, function_count, class_count, import_count)


def analyze_directory(directory):
    print("📊 Project Complexity Summary\n")
    for root, dirs, files in os.walk(directory):
        # Exclude garbage folders
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                lines, funcs, classes, imports = analyze_python_file(path)
                flag = "🚨" if lines > 500 or funcs > 15 else ""
                print(f"{path:<50} — {lines:>4} lines, {funcs:>2} functions, {classes:>2} classes, {imports:>2} imports {flag}")


if __name__ == "__main__":
    project_path = "/Users/Sharrone/Visual_DM"  # 👈 Use absolute path to your game folder
    analyze_directory(project_path)
