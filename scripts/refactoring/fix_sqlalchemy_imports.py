#!/usr/bin/env python3

import os
import re
from pathlib import Path

# Base directories
BACKEND_SYSTEMS_DIR = Path("backend/systems")

def find_model_dirs():
    """Find all directories that likely contain SQLAlchemy models."""
    model_dirs = []
    
    # Look for directories named "models"
    for root, dirs, _ in os.walk(BACKEND_SYSTEMS_DIR):
        if "models" in dirs:
            model_dir = Path(root) / "models"
            model_dirs.append(model_dir)
    
    return model_dirs

def analyze_model_file(file_path):
    """Analyze a model file for SQLAlchemy model definitions and relationships."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Look for class definitions that might be SQLAlchemy models
    class_defs = re.findall(r'class\s+(\w+)[\(:]', content)
    
    # Look for relationship definitions
    relationships = re.findall(r'relationship\s*\(\s*([^",\s][^",)]*)', content)
    string_relationships = re.findall(r'relationship\s*\(\s*"([^"]*)"', content)
    
    return {
        'file': file_path,
        'classes': class_defs,
        'relationships': relationships,
        'string_relationships': string_relationships
    }

def create_init_file(model_dir, model_files):
    """Create or update an __init__.py file in the model directory."""
    init_file = model_dir / "__init__.py"
    
    # Collect all model classes and their dependencies
    models = []
    for model_file in model_files:
        analysis = analyze_model_file(model_file)
        models.append(analysis)
    
    # Create content for __init__.py
    content = '"""SQLAlchemy models for this module.\n\nThis file imports all models in the correct order to avoid circular dependencies.\n"""\n\n'
    
    # Add imports for all model files
    for model_file in model_files:
        rel_path = model_file.relative_to(model_dir)
        module_name = str(rel_path.with_suffix(''))
        if '/' in module_name:
            continue  # Skip files in subdirectories for now
        
        content += f"from . import {module_name}\n"
    
    content += "\n# Import all models to ensure they're registered with SQLAlchemy\n"
    
    # Add explicit imports for all model classes
    for model in models:
        if not model['classes']:
            continue
            
        module_name = str(model['file'].relative_to(model_dir).with_suffix(''))
        if '/' in module_name:
            continue  # Skip files in subdirectories for now
            
        for class_name in model['classes']:
            content += f"from .{module_name} import {class_name}\n"
    
    content += "\n# Explicitly configure all mappers to resolve any remaining issues\n"
    content += "from sqlalchemy.orm import configure_mappers\nconfigure_mappers()\n"
    
    # Write the content to the file
    with open(init_file, 'w') as f:
        f.write(content)
    
    print(f"Created/updated {init_file}")

def main():
    """Main function to fix SQLAlchemy model imports."""
    print("Finding model directories...")
    model_dirs = find_model_dirs()
    print(f"Found {len(model_dirs)} model directories.")
    
    # Process each model directory
    for model_dir in model_dirs:
        print(f"\nProcessing {model_dir}...")
        
        # Find all Python files in the model directory
        model_files = []
        for root, _, files in os.walk(model_dir):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    file_path = Path(root) / file
                    model_files.append(file_path)
        
        if not model_files:
            print(f"No model files found in {model_dir}")
            continue
        
        print(f"Found {len(model_files)} model files.")
        create_init_file(model_dir, model_files)
    
    print("\nModel import fix completed!")
    print("Please check the generated __init__.py files and adjust them as needed.")

if __name__ == "__main__":
    main() 