#!/usr/bin/env python3

import os
import re
import hashlib
import shutil
from collections import defaultdict, Counter
from pathlib import Path
import ast
import textwrap

class Phase3FunctionalDeduplicator:
    def __init__(self, backend_dir, dry_run=True):
        self.backend_dir = Path(backend_dir)
        self.dry_run = dry_run
        self.backup_dir = self.backend_dir.parent / "systems_phase3_backup"
        
        # Tracking
        self.actions_taken = []
        self.files_removed = []
        self.files_updated = []
        self.shared_modules_created = []
        
        # Deduplication data
        self.duplicate_functions = defaultdict(list)
        self.duplicate_classes = defaultdict(list)
        self.constructor_patterns = defaultdict(list)
        
    def create_backup(self):
        """Create backup before Phase 3 deduplication"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print(f"🔄 Creating Phase 3 backup at {self.backup_dir}")
        shutil.copytree(self.backend_dir, self.backup_dir)
        print(f"✅ Backup completed")
    
    def extract_function_details(self, content, file_path):
        """Extract detailed function information"""
        functions = []
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get function source
                    func_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                    func_source = '\n'.join(func_lines)
                    
                    # Normalize function body for comparison
                    normalized_body = self.normalize_function_body(func_source)
                    
                    # Extract parameters
                    params = [arg.arg for arg in node.args.args]
                    
                    # Check if it's a constructor
                    is_constructor = node.name == '__init__'
                    
                    # Check if it's infrastructure (common patterns)
                    is_infrastructure = any(pattern in node.name.lower() for pattern in [
                        'create_database', 'setup', 'init_db', 'migrate', 'table', 'schema'
                    ])
                    
                    functions.append({
                        'name': node.name,
                        'source': func_source,
                        'normalized': normalized_body,
                        'hash': hashlib.md5(normalized_body.encode()).hexdigest(),
                        'params': params,
                        'param_count': len(params),
                        'file': file_path,
                        'line_start': node.lineno,
                        'line_end': node.end_lineno,
                        'is_constructor': is_constructor,
                        'is_infrastructure': is_infrastructure,
                        'docstring': ast.get_docstring(node) or ""
                    })
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return functions
    
    def normalize_function_body(self, func_source):
        """Normalize function body for comparison"""
        # Remove function signature line
        lines = func_source.split('\n')[1:]  # Skip def line
        
        # Remove leading whitespace consistently
        normalized_lines = []
        for line in lines:
            # Remove comments
            line = re.sub(r'#.*$', '', line)
            # Normalize whitespace
            line = re.sub(r'\s+', ' ', line.strip())
            if line:  # Skip empty lines
                normalized_lines.append(line)
        
        # Join and normalize further
        normalized = '\n'.join(normalized_lines)
        
        # Normalize string literals
        normalized = re.sub(r'"[^"]*"', '"STR"', normalized)
        normalized = re.sub(r"'[^']*'", "'STR'", normalized)
        
        # Normalize variable names in simple assignments
        normalized = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*=', 'VAR =', normalized)
        
        return normalized.strip()
    
    def find_duplicate_functions(self):
        """Find all duplicate functions across the codebase"""
        print("🔍 Finding duplicate functions...")
        
        all_functions = []
        python_files = list(self.backend_dir.rglob("*.py"))
        
        # Extract all functions
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                functions = self.extract_function_details(content, file_path)
                all_functions.extend(functions)
                
            except Exception as e:
                continue
        
        print(f"   📊 Extracted {len(all_functions)} functions")
        
        # Group by hash for exact duplicates
        function_hashes = defaultdict(list)
        for func in all_functions:
            function_hashes[func['hash']].append(func)
        
        # Find duplicates
        duplicate_count = 0
        constructor_count = 0
        infrastructure_count = 0
        
        for hash_val, funcs in function_hashes.items():
            if len(funcs) > 1:
                # Group by function name for better organization
                by_name = defaultdict(list)
                for func in funcs:
                    by_name[func['name']].append(func)
                
                for name, name_funcs in by_name.items():
                    if len(name_funcs) > 1:
                        self.duplicate_functions[name].extend(name_funcs)
                        duplicate_count += len(name_funcs) - 1
                        
                        if name_funcs[0]['is_constructor']:
                            constructor_count += len(name_funcs) - 1
                        elif name_funcs[0]['is_infrastructure']:
                            infrastructure_count += len(name_funcs) - 1
        
        print(f"   🔴 Found {duplicate_count} duplicate functions")
        print(f"   🏗️  Constructor duplicates: {constructor_count}")
        print(f"   🔧 Infrastructure duplicates: {infrastructure_count}")
        
        return duplicate_count
    
    def create_shared_database_module(self):
        """Create shared database infrastructure module"""
        db_dir = self.backend_dir / "infrastructure" / "database"
        
        if not self.dry_run:
            db_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all database-related functions
        db_functions = []
        for name, funcs in self.duplicate_functions.items():
            if any(pattern in name.lower() for pattern in [
                'create_database', 'create_table', 'setup', 'migrate', 'init_db'
            ]):
                # Take the best implementation (longest, most complete)
                best_func = max(funcs, key=lambda f: len(f['source']) + len(f['docstring']))
                db_functions.append(best_func)
        
        if not db_functions:
            return None
        
        # Create shared database module
        db_module_content = '''"""
Shared database infrastructure functions.
Consolidates duplicate database setup and table creation functions.
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
import logging


class DatabaseManager:
    """Centralized database management for all systems"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(os.getcwd(), "systems.db")
        self.connection = None
    
    def connect(self) -> sqlite3.Connection:
        """Establish database connection"""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


def create_database_tables(tables_config: List[Dict[str, Any]], db_path: str = None) -> bool:
    """
    Universal table creation function.
    Replaces all duplicate create_database_tables functions.
    
    Args:
        tables_config: List of table configurations
        db_path: Optional database path
    
    Returns:
        bool: Success status
    """
    try:
        db_manager = DatabaseManager(db_path)
        conn = db_manager.connect()
        cursor = conn.cursor()
        
        for table_config in tables_config:
            table_name = table_config.get('name')
            columns = table_config.get('columns', [])
            
            # Build CREATE TABLE statement
            column_defs = []
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if col.get('primary_key'):
                    col_def += " PRIMARY KEY"
                if col.get('not_null'):
                    col_def += " NOT NULL"
                if col.get('unique'):
                    col_def += " UNIQUE"
                column_defs.append(col_def)
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
            cursor.execute(create_sql)
        
        conn.commit()
        db_manager.close()
        
        logging.info(f"Successfully created {len(tables_config)} tables")
        return True
        
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        return False


def setup_database_schema(system_name: str, schema_config: Dict[str, Any]) -> bool:
    """
    Universal database schema setup.
    Replaces system-specific setup functions.
    """
    try:
        tables = schema_config.get('tables', [])
        indexes = schema_config.get('indexes', [])
        
        # Create tables
        if not create_database_tables(tables):
            return False
        
        # Create indexes
        if indexes:
            db_manager = DatabaseManager()
            conn = db_manager.connect()
            cursor = conn.cursor()
            
            for index in indexes:
                index_sql = f"CREATE INDEX IF NOT EXISTS {index['name']} ON {index['table']} ({', '.join(index['columns'])})"
                cursor.execute(index_sql)
            
            conn.commit()
            db_manager.close()
        
        logging.info(f"Database schema setup complete for {system_name}")
        return True
        
    except Exception as e:
        logging.error(f"Error setting up database schema for {system_name}: {e}")
        return False


# Global database manager instance
global_db = DatabaseManager()
'''
        
        db_file = db_dir / "shared_database.py"
        
        if not self.dry_run:
            with open(db_file, 'w') as f:
                f.write(db_module_content)
            
            # Create __init__.py
            init_file = db_dir / "__init__.py"
            with open(init_file, 'w') as f:
                f.write('from .shared_database import *\n')
        
        self.shared_modules_created.append(str(db_file))
        self.actions_taken.append(f"Created shared database module: {db_file}")
        
        return db_file
    
    def create_shared_base_classes(self):
        """Create shared base classes for common constructors"""
        base_dir = self.backend_dir / "infrastructure" / "base_classes"
        
        if not self.dry_run:
            base_dir.mkdir(parents=True, exist_ok=True)
        
        # Analyze constructor patterns
        constructor_funcs = self.duplicate_functions.get('__init__', [])
        
        if len(constructor_funcs) < 10:  # Not worth consolidating
            return None
        
        # Create base classes for common patterns
        base_classes_content = '''"""
Shared base classes to reduce constructor duplication.
Common patterns extracted from duplicate __init__ methods.
"""

from abc import ABC
from typing import Any, Dict, Optional, List
import logging


class BaseEntity(ABC):
    """Base class for all entity objects"""
    
    def __init__(self, id: Optional[str] = None, name: str = "", data: Dict[str, Any] = None):
        self.id = id
        self.name = name
        self.data = data or {}
        self.created_at = None
        self.updated_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'data': self.data,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load entity from dictionary"""
        self.id = data.get('id')
        self.name = data.get('name', "")
        self.data = data.get('data', {})
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')


class BaseManager(ABC):
    """Base class for all manager objects"""
    
    def __init__(self, config: Dict[str, Any] = None, logger: logging.Logger = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize the manager"""
        try:
            self._setup()
            self.initialized = True
            self.logger.info(f"{self.__class__.__name__} initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.__class__.__name__}: {e}")
            return False
    
    def _setup(self):
        """Override in subclasses for specific setup"""
        pass


class BaseRepository(ABC):
    """Base class for all repository objects"""
    
    def __init__(self, db_connection=None, table_name: str = ""):
        self.db_connection = db_connection
        self.table_name = table_name
    
    def create(self, data: Dict[str, Any]) -> bool:
        """Create new record"""
        raise NotImplementedError
    
    def read(self, id: Any) -> Optional[Dict[str, Any]]:
        """Read record by ID"""
        raise NotImplementedError
    
    def update(self, id: Any, data: Dict[str, Any]) -> bool:
        """Update record"""
        raise NotImplementedError
    
    def delete(self, id: Any) -> bool:
        """Delete record"""
        raise NotImplementedError


class BaseService(ABC):
    """Base class for all service objects"""
    
    def __init__(self, repository=None, config: Dict[str, Any] = None):
        self.repository = repository
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        return True  # Override in subclasses
    
    def process_error(self, error: Exception) -> Dict[str, Any]:
        """Standard error processing"""
        self.logger.error(f"Error in {self.__class__.__name__}: {error}")
        return {
            'success': False,
            'error': str(error),
            'service': self.__class__.__name__
        }
'''
        
        base_file = base_dir / "base_classes.py"
        
        if not self.dry_run:
            with open(base_file, 'w') as f:
                f.write(base_classes_content)
            
            # Create __init__.py
            init_file = base_dir / "__init__.py"
            with open(init_file, 'w') as f:
                f.write('from .base_classes import *\n')
        
        self.shared_modules_created.append(str(base_file))
        self.actions_taken.append(f"Created shared base classes: {base_file}")
        
        return base_file
    
    def replace_duplicate_functions(self):
        """Replace duplicate functions with imports from shared modules"""
        print("🔄 Replacing duplicate functions...")
        
        files_updated = 0
        functions_removed = 0
        
        # Database functions replacement
        db_import = "from backend.infrastructure.database import create_database_tables, setup_database_schema"
        
        # Common base class imports
        base_imports = {
            'BaseEntity': 'from backend.infrastructure.base_classes import BaseEntity',
            'BaseManager': 'from backend.infrastructure.base_classes import BaseManager',
            'BaseRepository': 'from backend.infrastructure.base_classes import BaseRepository',
            'BaseService': 'from backend.infrastructure.base_classes import BaseService'
        }
        
        python_files = list(self.backend_dir.rglob("*.py"))
        
        for file_path in python_files:
            if str(file_path) in self.files_removed:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                modified = False
                
                # Replace database functions
                for name, funcs in self.duplicate_functions.items():
                    if any(pattern in name.lower() for pattern in [
                        'create_database', 'create_table', 'setup_database'
                    ]):
                        # Check if this file has the function
                        for func in funcs:
                            if func['file'] == file_path:
                                # Remove the function definition
                                func_pattern = re.escape(func['source'])
                                content = re.sub(func_pattern, '', content, flags=re.DOTALL)
                                
                                # Add import if not present
                                if db_import not in content:
                                    content = self._add_import_to_file(content, db_import)
                                
                                modified = True
                                functions_removed += 1
                                break
                
                # Replace duplicate constructors with base class inheritance
                # (This would require more sophisticated AST manipulation)
                # For now, we'll focus on removing exact duplicates
                
                if modified and not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    files_updated += 1
                    self.files_updated.append(str(file_path))
                
            except Exception as e:
                print(f"Error updating {file_path}: {e}")
                continue
        
        print(f"✅ Updated {files_updated} files")
        print(f"✅ Removed {functions_removed} duplicate functions")
        
        return files_updated, functions_removed
    
    def _add_import_to_file(self, content, import_statement):
        """Add import statement to file in appropriate location"""
        lines = content.split('\n')
        
        # Find last import line
        import_line_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                import_line_idx = i + 1
        
        # Insert new import
        lines.insert(import_line_idx, import_statement)
        return '\n'.join(lines)
    
    def remove_empty_files(self):
        """Remove files that became empty or nearly empty after deduplication"""
        print("🗑️  Removing empty files...")
        
        removed_count = 0
        python_files = list(self.backend_dir.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                
                # Count non-empty, non-comment lines
                lines = [line.strip() for line in content.split('\n')]
                meaningful_lines = [
                    line for line in lines 
                    if line and not line.startswith('#') and not line.startswith(('import ', 'from '))
                ]
                
                # If file has very few meaningful lines, remove it
                if len(meaningful_lines) <= 2:
                    self.actions_taken.append(f"Removing empty file: {file_path}")
                    self.files_removed.append(str(file_path))
                    
                    if not self.dry_run:
                        file_path.unlink()
                        removed_count += 1
                    
            except Exception as e:
                continue
        
        print(f"✅ Removed {removed_count} empty files")
        return removed_count
    
    def run_phase3_deduplication(self):
        """Run complete Phase 3 functional deduplication"""
        print("🚀 STARTING PHASE 3 FUNCTIONAL DEDUPLICATION")
        print("=" * 70)
        
        # Create backup
        if not self.dry_run:
            self.create_backup()
        
        # Find duplicates
        duplicate_count = self.find_duplicate_functions()
        
        if duplicate_count == 0:
            print("✅ No functional duplicates found!")
            return {'functions_removed': 0, 'files_updated': 0}
        
        # Create shared modules
        self.create_shared_database_module()
        self.create_shared_base_classes()
        
        # Replace duplicates
        files_updated, functions_removed = self.replace_duplicate_functions()
        
        # Clean up empty files
        empty_files_removed = self.remove_empty_files()
        
        # Final statistics
        print("\n" + "=" * 70)
        print("🎉 PHASE 3 DEDUPLICATION COMPLETE!")
        print("=" * 70)
        print(f"📈 RESULTS:")
        print(f"   Functions removed: {functions_removed}")
        print(f"   Files updated: {files_updated}")
        print(f"   Empty files removed: {empty_files_removed}")
        print(f"   Shared modules created: {len(self.shared_modules_created)}")
        
        if self.dry_run:
            print(f"\n⚠️  DRY RUN MODE - No changes were actually made")
            print(f"   Run with dry_run=False to apply changes")
        else:
            print(f"\n✅ CHANGES APPLIED")
            print(f"   Backup created at: {self.backup_dir}")
        
        return {
            'functions_removed': functions_removed,
            'files_updated': files_updated,
            'empty_files_removed': empty_files_removed,
            'shared_modules': len(self.shared_modules_created)
        }


def main():
    backend_dir = "backend/systems"
    
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found: {backend_dir}")
        return
    
    # Run dry-run first
    print("🧪 RUNNING DRY RUN FIRST...")
    deduplicator = Phase3FunctionalDeduplicator(backend_dir, dry_run=True)
    results = deduplicator.run_phase3_deduplication()
    
    print(f"\n🤔 DRY RUN RESULTS:")
    print(f"Would remove {results['functions_removed']} duplicate functions")
    print(f"Would update {results['files_updated']} files")
    print(f"Would remove {results['empty_files_removed']} empty files")
    print(f"Would create {results['shared_modules']} shared modules")
    
    # Ask for confirmation
    response = input(f"\n❓ Proceed with Phase 3 deduplication? (y/N): ").strip().lower()
    
    if response == 'y':
        print(f"\n🎯 RUNNING PHASE 3 DEDUPLICATION...")
        actual_deduplicator = Phase3FunctionalDeduplicator(backend_dir, dry_run=False)
        actual_results = actual_deduplicator.run_phase3_deduplication()
        
        # Final file count
        remaining_files = len(list(Path(backend_dir).rglob("*.py")))
        print(f"\n📊 FINAL STATS:")
        print(f"   Remaining Python files: {remaining_files}")
        
        # Count lines
        total_lines = 0
        for py_file in Path(backend_dir).rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    total_lines += len(f.readlines())
            except Exception:
                pass
        
        print(f"   Remaining lines of code: {total_lines:,}")
        
    else:
        print("🚫 Phase 3 deduplication cancelled")


if __name__ == "__main__":
    main() 