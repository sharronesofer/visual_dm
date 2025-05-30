import os
import re
from pathlib import Path

def extract_fastapi_routes(file_path):
    """Extract FastAPI routes from a Python file."""
    routes = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find route definitions (GET, POST, PUT, DELETE, etc.)
        route_patterns = [
            r'@router\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']',
            r'@app\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in route_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for method, path in matches:
                routes.append({
                    'method': method.upper(),
                    'path': path,
                    'file': str(file_path)
                })
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return routes

# Find all router files
router_files = []
for root, dirs, files in os.walk('./backend/systems'):
    for file in files:
        if 'router' in file and file.endswith('.py') and '__pycache__' not in root:
            router_files.append(os.path.join(root, file))

print(f"Found {len(router_files)} router files")

# Extract routes from all files
all_routes = []
for router_file in router_files:
    routes = extract_fastapi_routes(router_file)
    all_routes.extend(routes)

# Group by system
systems = {}
for route in all_routes:
    # Extract system name from file path
    path_parts = route['file'].split('/')
    if 'systems' in path_parts:
        system_idx = path_parts.index('systems')
        if system_idx + 1 < len(path_parts):
            system_name = path_parts[system_idx + 1]
            if system_name not in systems:
                systems[system_name] = []
            systems[system_name].append(route)

print("API Endpoints by System:")
print("=" * 50)
for system, routes in sorted(systems.items()):
    print(f"\n{system.upper()} System ({len(routes)} endpoints):")
    for route in sorted(routes, key=lambda x: (x['method'], x['path'])):
        print(f"  {route['method']:6} {route['path']}")

print(f"\nTotal endpoints found: {len(all_routes)}")
print(f"Total systems: {len(systems)}")

# Create API contract YAML content
yaml_content = """# Visual DM API Contracts
# Generated automatically from FastAPI router files

openapi: 3.0.3
info:
  title: Visual DM API
  description: API contracts for Visual DM backend systems
  version: 1.0.0

paths:
"""

for system, routes in sorted(systems.items()):
    yaml_content += f"\n  # {system.upper()} System\n"
    for route in sorted(routes, key=lambda x: (x['method'], x['path'])):
        yaml_content += f"  {route['path']}:\n"
        yaml_content += f"    {route['method'].lower()}:\n"
        yaml_content += f"      tags: [{system}]\n"
        yaml_content += f"      summary: {system.title()} {route['method']} endpoint\n"
        yaml_content += f"      responses:\n"
        yaml_content += f"        '200':\n"
        yaml_content += f"          description: Successful response\n\n"

# Write to file
with open('api_contracts.yaml', 'w') as f:
    f.write(yaml_content)

print("\nAPI contract written to api_contracts.yaml") 