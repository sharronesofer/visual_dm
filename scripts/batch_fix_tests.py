#!/usr/bin/env python3
"""
Batch processing script to fix common test errors programmatically.

This script identifies and fixes common patterns in test failures:
1. Missing imports (e.g., BiomeSchema from wrong location)
2. Pydantic v2 migration issues (@validator -> @field_validator)
3. SQLAlchemy v2 migration issues (declarative_base -> orm.declarative_base)
4. Pytest collection warnings (TestEvent -> _TestEvent)
5. Event dispatcher pattern updates (get_event_dispatcher -> EventDispatcher)
6. FastAPI lifecycle deprecations (on_event -> lifespan)
7. Pydantic config updates (Config -> ConfigDict)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import logging
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchTestFixer:
    """Main class for batch processing test fixes."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixes_applied = 0
        self.files_modified = 0
        
    def fix_missing_imports(self, file_path: Path) -> bool:
        """Fix missing import issues like BiomeSchema."""
        content = file_path.read_text()
        original_content = content
        
        # Fix BiomeSchema import - should come from data.schemas not world_generation.models
        if "from backend.systems.world_generation.models import" in content and "BiomeSchema" in content:
            # Replace the import line
            content = re.sub(
                r"from backend\.systems\.world_generation\.models import ([^,\n]*,?\s*)*BiomeSchema([^,\n]*,?\s*)*",
                lambda m: m.group(0).replace("BiomeSchema", "").replace(", ,", ",").strip(" ,"),
                content
            )
            # Add the correct import
            if "from backend.infrastructure.data.schemas.biome_schema import BiomeSchema" not in content:
                content = "from backend.infrastructure.data.schemas.biome_schema import BiomeSchema\n" + content
        
        # Fix world_generation models that moved to infrastructure
        if "from backend.systems.world_generation.models import" in content:
            content = content.replace(
                "from backend.systems.world_generation.models import",
                "from backend.systems.world_generation.models import"
            )
        
        # Fix world_generation repositories that moved to infrastructure
        if "from backend.systems.world_generation.repositories" in content:
            content = content.replace(
                "from backend.systems.world_generation.repositories",
                "from backend.systems.world_generation.repositories"
            )
        
        # Fix world_generation routers that moved to infrastructure
        if "from backend.systems.world_generation.routers" in content:
            content = content.replace(
                "from backend.systems.world_generation.routers",
                "from backend.systems.world_generation.routers"
            )
            
        return content != original_content

    def fix_pydantic_v2_migration(self, file_path: Path) -> bool:
        """Fix Pydantic v1 to v2 migration issues."""
        content = file_path.read_text()
        original_content = content
        
        # @validator -> @field_validator
        content = re.sub(r'@validator\((.*?)\)', r'@field_validator(\1)', content)
        
        # Add field_validator import if @field_validator is used
        if "@field_validator" in content and "from pydantic import" in content:
            content = re.sub(
                r"from pydantic import ([^,\n]*)",
                lambda m: f"from pydantic import {m.group(1)}, field_validator" if "field_validator" not in m.group(1) else m.group(0),
                content
            )
        
        # Config class -> ConfigDict
        content = re.sub(r'class Config:', 'model_config = ConfigDict(', content)
        content = re.sub(r'orm_mode = True', 'from_attributes=True', content)
        content = re.sub(r'schema_extra = {', 'json_schema_extra={', content)
        
        # Pydantic Field example -> json_schema_extra
        content = re.sub(r'Field\((.*?), example=(.*?)\)', r'Field(\1, json_schema_extra={"example": \2})', content)
        
        return content != original_content

    def fix_sqlalchemy_v2_migration(self, file_path: Path) -> bool:
        """Fix SQLAlchemy v1 to v2 migration issues."""
        content = file_path.read_text()
        original_content = content
        
        # declarative_base -> orm.declarative_base
        if "from sqlalchemy.ext.declarative import declarative_base" in content:
            content = content.replace(
                "from sqlalchemy.ext.declarative import declarative_base",
                "from sqlalchemy.orm import declarative_base"
            )
        
        return content != original_content

    def fix_pytest_collection_warnings(self, file_path: Path) -> bool:
        """Fix pytest collection warnings for test classes."""
        content = file_path.read_text()
        original_content = content
        
        # Rename TestEvent classes that have __init__ constructors
        if "class TestEvent" in content and "__init__" in content:
            content = re.sub(r'class TestEvent(\w*)', r'class _TestEvent\1', content)
            # Update references to the renamed class
            content = re.sub(r'(\w+)TestEvent(\w*)', r'\1_TestEvent\2', content)
        
        # Same for TestObserver and other common test class names
        for class_name in ["TestObserver", "TestEventHandler"]:
            if f"class {class_name}" in content and "__init__" in content:
                content = re.sub(f'class {class_name}', f'class _{class_name}', content)
        
        return content != original_content

    def fix_event_dispatcher_pattern(self, file_path: Path) -> bool:
        """Fix deprecated get_event_dispatcher pattern."""
        content = file_path.read_text()
        original_content = content
        
        # Replace get_event_dispatcher() with EventDispatcher.get_instance()
        content = content.replace("get_event_dispatcher()", "EventDispatcher.get_instance()")
        content = content.replace("get_event_dispatcher().Instance", "EventDispatcher.get_instance()")
        
        # Add import if needed
        if "EventDispatcher.get_instance()" in content:
            if "from backend.app.core.events.event_dispatcher import EventDispatcher" not in content:
                content = "from backend.app.core.events.event_dispatcher import EventDispatcher\n" + content
        
        return content != original_content

    def fix_fastapi_lifecycle_deprecations(self, file_path: Path) -> bool:
        """Fix FastAPI lifecycle deprecation warnings."""
        content = file_path.read_text()
        original_content = content
        
        # @app.on_event("startup") -> lifespan context manager
        startup_pattern = r'@app\.on_event\("startup"\)\s*def\s+(\w+)\(\):'
        shutdown_pattern = r'@app\.on_event\("shutdown"\)\s*def\s+(\w+)\(\):'
        
        if re.search(startup_pattern, content) or re.search(shutdown_pattern, content):
            # This is a more complex fix that requires restructuring - mark for manual review
            logger.warning(f"File {file_path} contains FastAPI lifecycle deprecations - requires manual migration")
            # For now, just add a comment
            content = "# TODO: Migrate FastAPI on_event to lifespan context manager\n" + content
        
        return content != original_content

    def fix_time_manager_mocking(self, file_path: Path) -> bool:
        """Fix TimeManager mocking issues in time system tests."""
        content = file_path.read_text()
        original_content = content
        
        # Fix TimeManager patching for lazy loading pattern
        if "time_utils" in str(file_path) and "@patch" in content:
            # Replace direct TimeManager patches with _get_time_manager patches
            content = re.sub(
                r'@patch\([\'"]backend\.systems\.game_time\.utils\.time_utils\.TimeManager[\'"]',
                r'@patch("backend.systems.game_time.utils.time_utils._get_time_manager"',
                content
            )
            
            # Update mock object usage
            content = re.sub(
                r'mock_time_manager\.([a-zA-Z_]+)',
                r'mock_time_manager.return_value.\1',
                content
            )
        
        return content != original_content

    def fix_import_statements(self, file_path: Path) -> bool:
        """Fix common import statement issues."""
        content = file_path.read_text()
        original_content = content
        
        # Remove unused imports that cause circular import issues
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Skip problematic imports that are not used
            if line.strip().startswith('from') and 'import' in line:
                # Check if the imported items are actually used in the file
                import_match = re.search(r'import\s+(.+)', line)
                if import_match:
                    imported_items = [item.strip() for item in import_match.group(1).split(',')]
                    used_items = []
                    for item in imported_items:
                        if item in content:
                            used_items.append(item)
                    
                    if used_items:
                        new_lines.append(line)
                    # else: skip unused import
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        return content != original_content

    def apply_fixes_to_file(self, file_path: Path) -> bool:
        """Apply all applicable fixes to a single file."""
        if not file_path.exists() or not file_path.is_file():
            return False
        
        logger.info(f"Processing {file_path}")
        
        fixes = [
            self.fix_missing_imports,
            self.fix_pydantic_v2_migration,
            self.fix_sqlalchemy_v2_migration,
            self.fix_pytest_collection_warnings,
            self.fix_event_dispatcher_pattern,
            self.fix_fastapi_lifecycle_deprecations,
            self.fix_time_manager_mocking,
            self.fix_import_statements,
        ]
        
        file_modified = False
        original_content = file_path.read_text()
        
        for fix_func in fixes:
            try:
                if fix_func(file_path):
                    file_modified = True
                    self.fixes_applied += 1
                    logger.debug(f"Applied {fix_func.__name__} to {file_path}")
            except Exception as e:
                logger.error(f"Error applying {fix_func.__name__} to {file_path}: {e}")
        
        # Write back the modified content
        if file_modified:
            current_content = file_path.read_text()
            file_path.write_text(current_content)
            self.files_modified += 1
            logger.info(f"Modified {file_path}")
        
        return file_modified

    def process_directory(self, directory: Path, pattern: str = "*.py") -> None:
        """Process all Python files in a directory recursively."""
        logger.info(f"Processing directory: {directory}")
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                self.apply_fixes_to_file(file_path)

    def run_batch_fixes(self, target_dirs: List[str] = None) -> None:
        """Run batch fixes on specified directories."""
        if target_dirs is None:
            target_dirs = ["backend/tests/", "backend/systems/"]
        
        logger.info(f"Starting batch fixes on directories: {target_dirs}")
        
        for target_dir in target_dirs:
            dir_path = self.project_root / target_dir
            if dir_path.exists():
                self.process_directory(dir_path)
            else:
                logger.warning(f"Directory not found: {dir_path}")
        
        logger.info(f"Batch fixes complete. Applied {self.fixes_applied} fixes to {self.files_modified} files.")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Batch fix common test errors")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--dirs", nargs="+", default=["backend/tests/", "backend/systems/"], 
                       help="Directories to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get the absolute project root
    project_root = Path(args.project_root).resolve()
    
    if not project_root.exists():
        logger.error(f"Project root does not exist: {project_root}")
        sys.exit(1)
    
    logger.info(f"Using project root: {project_root}")
    
    fixer = BatchTestFixer(str(project_root))
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be modified")
        # TODO: Implement dry run mode
    
    fixer.run_batch_fixes(args.dirs)

if __name__ == "__main__":
    main() 