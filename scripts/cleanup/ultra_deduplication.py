#!/usr/bin/env python3

import os
import re
import hashlib
import shutil
from collections import defaultdict
from pathlib import Path
import ast
import textwrap

class UltraDeduplicator:
    def __init__(self, backend_dir, dry_run=True):
        self.backend_dir = Path(backend_dir)
        self.dry_run = dry_run
        self.backup_dir = self.backend_dir.parent / "systems_ultra_dedup_backup"
        
        # Tracking
        self.actions_taken = []
        self.files_removed = []
        self.utility_modules_created = []
        self.imports_updated = []
        
    def create_backup(self):
        """Create full backup before deduplication"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print(f"🔄 Creating backup at {self.backup_dir}")
        shutil.copytree(self.backend_dir, self.backup_dir)
        print(f"✅ Backup completed")
    
    def normalize_code(self, code):
        """Normalize code for comparison"""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # Remove excessive whitespace
        code = re.sub(r'\s+', ' ', code)
        code = re.sub(r'\s*([{}()[\],;:])\s*', r'\1', code)
        
        # Normalize string literals and numbers
        code = re.sub(r'"[^"]*"', '"STRING"', code)
        code = re.sub(r"'[^']*'", "'STRING'", code)
        code = re.sub(r'\b\d+\b', 'NUMBER', code)
        
        return code.strip()
    
    def extract_utility_functions(self, file_content):
        """Extract utility functions that appear to be duplicated"""
        utility_functions = []
        
        # Look for common utility function patterns
        utility_patterns = [
            r'def generate_hash\(.*?\):.*?(?=def|\n\n|$)',
            r'def random_choice\(.*?\):.*?(?=def|\n\n|$)',
            r'def format_number\(.*?\):.*?(?=def|\n\n|$)',
            r'def safe_divide\(.*?\):.*?(?=def|\n\n|$)',
            r'def validate_data\(.*?\):.*?(?=def|\n\n|$)',
            r'def serialize_data\(.*?\):.*?(?=def|\n\n|$)',
            r'def deserialize_data\(.*?\):.*?(?=def|\n\n|$)',
        ]
        
        for pattern in utility_patterns:
            matches = re.findall(pattern, file_content, re.DOTALL)
            for match in matches:
                utility_functions.append(match.strip())
        
        return utility_functions
    
    def extract_classes(self, file_content):
        """Extract class definitions"""
        classes = []
        lines = file_content.split('\n')
        current_class = []
        in_class = False
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('class '):
                if current_class:
                    classes.append('\n'.join(current_class))
                current_class = [line]
                in_class = True
                indent_level = len(line) - len(line.lstrip())
            elif in_class:
                if line.strip() == '':
                    current_class.append(line)
                elif len(line) - len(line.lstrip()) > indent_level or line.strip().startswith('#'):
                    current_class.append(line)
                else:
                    # End of class
                    classes.append('\n'.join(current_class))
                    current_class = []
                    in_class = False
                    if stripped.startswith('class '):
                        current_class = [line]
                        in_class = True
                        indent_level = len(line) - len(line.lstrip())
        
        if current_class:
            classes.append('\n'.join(current_class))
        
        return classes
    
    def find_duplicate_files(self):
        """Find all duplicate files using multiple techniques"""
        print("🔍 Finding duplicate files...")
        
        exact_duplicates = defaultdict(list)
        structural_duplicates = defaultdict(list)
        
        python_files = list(self.backend_dir.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Exact duplicates
                content_hash = hashlib.md5(content.encode()).hexdigest()
                exact_duplicates[content_hash].append(file_path)
                
                # Structural duplicates (normalized content)
                if len(content.strip()) > 50:  # Skip very small files
                    normalized = self.normalize_code(content)
                    struct_hash = hashlib.md5(normalized.encode()).hexdigest()
                    structural_duplicates[struct_hash].append(file_path)
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        # Filter to only groups with duplicates
        exact_dupes = [files for files in exact_duplicates.values() if len(files) > 1]
        struct_dupes = [files for files in structural_duplicates.values() if len(files) > 1]
        
        return exact_dupes, struct_dupes
    
    def create_shared_utilities_module(self):
        """Create shared utilities module for common functions"""
        utils_dir = self.backend_dir / "infrastructure" / "shared_utils"
        
        if not self.dry_run:
            utils_dir.mkdir(parents=True, exist_ok=True)
        
        # Common utility functions that appear everywhere
        common_utils_content = '''"""
Shared utility functions used across multiple systems.
This module consolidates commonly duplicated utility functions.
"""

import hashlib
import random
from typing import Any, List, Union


def generate_hash(data: str) -> str:
    """Generate MD5 hash of string data"""
    return hashlib.md5(data.encode()).hexdigest()


def random_choice(choices: List[Any]) -> Any:
    """Safely choose random item from list"""
    if not choices:
        return None
    return random.choice(choices)


def format_number(num: float, decimals: int = 2) -> str:
    """Format number with specified decimal places"""
    return f"{num:.{decimals}f}"


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers with default for division by zero"""
    if b == 0:
        return default
    return a / b


def validate_data(data: Any, required_fields: List[str] = None) -> bool:
    """Validate data has required fields"""
    if required_fields is None:
        return data is not None
    
    if not isinstance(data, dict):
        return False
    
    return all(field in data for field in required_fields)


def serialize_data(data: Any) -> str:
    """Serialize data to JSON string"""
    import json
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return ""


def deserialize_data(data_str: str) -> Any:
    """Deserialize JSON string to data"""
    import json
    try:
        return json.loads(data_str)
    except (json.JSONDecodeError, TypeError):
        return None
'''
        
        utils_file = utils_dir / "common_utils.py"
        
        if not self.dry_run:
            with open(utils_file, 'w') as f:
                f.write(common_utils_content)
            
            # Create __init__.py
            init_file = utils_dir / "__init__.py"
            with open(init_file, 'w') as f:
                f.write('from .common_utils import *\n')
        
        self.utility_modules_created.append(str(utils_file))
        self.actions_taken.append(f"Created shared utilities module: {utils_file}")
        
        return utils_file
    
    def create_shared_event_system(self):
        """Create shared event system module"""
        event_dir = self.backend_dir / "infrastructure" / "event_system"
        
        if not self.dry_run:
            event_dir.mkdir(parents=True, exist_ok=True)
        
        # EventBase and EventDispatcher that's duplicated everywhere
        event_base_content = '''"""
Shared event system classes used across multiple systems.
This module consolidates the EventBase and EventDispatcher that were duplicated.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable
import asyncio
from datetime import datetime
import uuid


class EventBase(ABC):
    """Base class for all events in the system"""
    
    def __init__(self, event_type: str = None, data: Dict[str, Any] = None):
        self.event_id = str(uuid.uuid4())
        self.event_type = event_type or self.__class__.__name__
        self.timestamp = datetime.now()
        self.data = data or {}
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process the event data"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }


class EventDispatcher:
    """Event dispatcher for managing event subscriptions and dispatch"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._middleware: List[Callable] = []
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe a handler to an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe a handler from an event type"""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def dispatch(self, event: EventBase) -> None:
        """Dispatch an event to all subscribed handlers"""
        handlers = self._handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    async def dispatch_async(self, event: EventBase) -> None:
        """Asynchronously dispatch an event"""
        handlers = self._handlers.get(event.event_type, [])
        
        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    handler(event)
            except Exception as e:
                print(f"Error in async event handler: {e}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to process events"""
        self._middleware.append(middleware)


# Global event dispatcher instance
global_dispatcher = EventDispatcher()
'''
        
        event_file = event_dir / "event_base.py"
        
        if not self.dry_run:
            with open(event_file, 'w') as f:
                f.write(event_base_content)
            
            # Create __init__.py
            init_file = event_dir / "__init__.py"
            with open(init_file, 'w') as f:
                f.write('from .event_base import *\n')
        
        self.utility_modules_created.append(str(event_file))
        self.actions_taken.append(f"Created shared event system: {event_file}")
        
        return event_file
    
    def remove_exact_duplicates(self, exact_dupes):
        """Remove exact duplicate files, keeping the best one"""
        print(f"🗑️  Removing {len(exact_dupes)} groups of exact duplicates...")
        
        removed_count = 0
        
        for group in exact_dupes:
            if len(group) <= 1:
                continue
            
            # Sort by path length and prefer files in main directories
            group_sorted = sorted(group, key=lambda x: (
                len(str(x)),  # Prefer shorter paths
                'utils' not in str(x).lower(),  # Prefer non-utils
                'test' not in str(x).lower(),   # Prefer non-test files
                str(x)  # Alphabetical as tiebreaker
            ))
            
            # Keep the first (best) file, remove others
            keep_file = group_sorted[0]
            remove_files = group_sorted[1:]
            
            self.actions_taken.append(f"Keeping: {keep_file}")
            
            for remove_file in remove_files:
                self.actions_taken.append(f"Removing duplicate: {remove_file}")
                self.files_removed.append(str(remove_file))
                
                if not self.dry_run:
                    try:
                        remove_file.unlink()
                        removed_count += 1
                    except Exception as e:
                        print(f"Error removing {remove_file}: {e}")
        
        print(f"✅ Removed {removed_count} exact duplicate files")
        return removed_count
    
    def consolidate_stub_files(self, struct_dupes):
        """Remove structural duplicates that are likely stub files"""
        print(f"🧹 Consolidating {len(struct_dupes)} groups of structural duplicates...")
        
        removed_count = 0
        
        for group in struct_dupes:
            if len(group) <= 1:
                continue
            
            # Check if these are likely stub files (very small, similar structure)
            stub_candidates = []
            for file_path in group:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().strip()
                    
                    # Identify stub files: very small, mostly imports/constants
                    if (len(content) < 200 or  # Very small files
                        content.count('\n') < 10 or  # Few lines
                        len([l for l in content.split('\n') if l.strip() and not l.strip().startswith(('#', 'import', 'from'))]) < 3):
                        stub_candidates.append(file_path)
                        
                except Exception:
                    continue
            
            # If most files in group are stubs, remove duplicates
            if len(stub_candidates) > len(group) * 0.7:  # 70% are stubs
                # Keep one, remove others
                keep_file = stub_candidates[0]
                remove_files = stub_candidates[1:]
                
                self.actions_taken.append(f"Keeping stub: {keep_file}")
                
                for remove_file in remove_files:
                    self.actions_taken.append(f"Removing stub duplicate: {remove_file}")
                    self.files_removed.append(str(remove_file))
                    
                    if not self.dry_run:
                        try:
                            remove_file.unlink()
                            removed_count += 1
                        except Exception as e:
                            print(f"Error removing {remove_file}: {e}")
        
        print(f"✅ Removed {removed_count} structural duplicate files")
        return removed_count
    
    def replace_utility_imports(self):
        """Replace utility function usage with imports from shared module"""
        print("🔗 Updating imports to use shared utilities...")
        
        python_files = list(self.backend_dir.rglob("*.py"))
        updated_count = 0
        
        # Utility function patterns to replace
        utility_patterns = {
            'generate_hash': 'from infrastructure.shared_utils import generate_hash',
            'random_choice': 'from infrastructure.shared_utils import random_choice', 
            'format_number': 'from infrastructure.shared_utils import format_number',
            'safe_divide': 'from infrastructure.shared_utils import safe_divide',
            'validate_data': 'from infrastructure.shared_utils import validate_data',
            'serialize_data': 'from infrastructure.shared_utils import serialize_data',
            'deserialize_data': 'from infrastructure.shared_utils import deserialize_data',
        }
        
        for file_path in python_files:
            if str(file_path) in self.files_removed:
                continue  # Skip files we're removing
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                modified = False
                
                # Check if file contains duplicate utility functions
                for func_name, import_statement in utility_patterns.items():
                    func_pattern = fr'def {func_name}\([^)]*\):.*?(?=def|\nclass|\n\n|\Z)'
                    
                    if re.search(func_pattern, content, re.DOTALL):
                        # Remove the function definition
                        content = re.sub(func_pattern, '', content, flags=re.DOTALL)
                        
                        # Add import if not already present
                        if import_statement not in content:
                            # Find good place to add import
                            lines = content.split('\n')
                            import_line_idx = 0
                            
                            # Find last import line
                            for i, line in enumerate(lines):
                                if line.strip().startswith(('import ', 'from ')):
                                    import_line_idx = i + 1
                            
                            lines.insert(import_line_idx, import_statement)
                            content = '\n'.join(lines)
                        
                        modified = True
                
                if modified and not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_count += 1
                    self.imports_updated.append(str(file_path))
                    
            except Exception as e:
                print(f"Error updating {file_path}: {e}")
                continue
        
        print(f"✅ Updated imports in {updated_count} files")
        return updated_count
    
    def replace_event_class_usage(self):
        """Replace EventBase and EventDispatcher usage with shared classes"""
        print("🎭 Updating event class usage...")
        
        python_files = list(self.backend_dir.rglob("*.py"))
        updated_count = 0
        
        event_import = "from infrastructure.event_system import EventBase, EventDispatcher"
        
        for file_path in python_files:
            if str(file_path) in self.files_removed:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                modified = False
                
                # Check if file defines EventBase or EventDispatcher
                if re.search(r'class EventBase[:\(]', content) or re.search(r'class EventDispatcher[:\(]', content):
                    # Remove class definitions
                    content = re.sub(r'class EventBase.*?(?=\nclass|\ndef|\n\n|\Z)', '', content, flags=re.DOTALL)
                    content = re.sub(r'class EventDispatcher.*?(?=\nclass|\ndef|\n\n|\Z)', '', content, flags=re.DOTALL)
                    
                    # Add import if not present
                    if event_import not in content and ('EventBase' in content or 'EventDispatcher' in content):
                        lines = content.split('\n')
                        import_line_idx = 0
                        
                        for i, line in enumerate(lines):
                            if line.strip().startswith(('import ', 'from ')):
                                import_line_idx = i + 1
                        
                        lines.insert(import_line_idx, event_import)
                        content = '\n'.join(lines)
                    
                    modified = True
                
                if modified and not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_count += 1
                    
            except Exception as e:
                print(f"Error updating event classes in {file_path}: {e}")
                continue
        
        print(f"✅ Updated event class usage in {updated_count} files")
        return updated_count
    
    def run_ultra_deduplication(self):
        """Run the complete ultra deduplication process"""
        print("🚀 STARTING ULTRA DEDUPLICATION")
        print("=" * 60)
        
        # Create backup
        if not self.dry_run:
            self.create_backup()
        
        # Find duplicates
        exact_dupes, struct_dupes = self.find_duplicate_files()
        
        print(f"\n📊 DUPLICATION ANALYSIS:")
        print(f"   Exact duplicates: {sum(len(group) - 1 for group in exact_dupes)} files")
        print(f"   Structural duplicates: {sum(len(group) - 1 for group in struct_dupes)} files")
        
        # Create shared modules
        self.create_shared_utilities_module()
        self.create_shared_event_system()
        
        # Remove duplicates
        exact_removed = self.remove_exact_duplicates(exact_dupes)
        struct_removed = self.consolidate_stub_files(struct_dupes)
        
        # Update imports
        utils_updated = self.replace_utility_imports()
        events_updated = self.replace_event_class_usage()
        
        # Final statistics
        total_removed = exact_removed + struct_removed
        
        print("\n" + "=" * 60)
        print("🎉 ULTRA DEDUPLICATION COMPLETE!")
        print("=" * 60)
        print(f"📈 RESULTS:")
        print(f"   Files removed: {total_removed}")
        print(f"   Utility modules created: {len(self.utility_modules_created)}")
        print(f"   Files updated for utilities: {utils_updated}")
        print(f"   Files updated for events: {events_updated}")
        
        if self.dry_run:
            print(f"\n⚠️  DRY RUN MODE - No changes were actually made")
            print(f"   Run with dry_run=False to apply changes")
        else:
            print(f"\n✅ CHANGES APPLIED")
            print(f"   Backup created at: {self.backup_dir}")
        
        return {
            'files_removed': total_removed,
            'modules_created': len(self.utility_modules_created),
            'files_updated': utils_updated + events_updated,
            'actions': self.actions_taken
        }


def main():
    backend_dir = "backend/systems"
    
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found: {backend_dir}")
        return
    
    # Run in dry-run mode first
    print("🧪 RUNNING DRY RUN FIRST...")
    deduplicator = UltraDeduplicator(backend_dir, dry_run=True)
    results = deduplicator.run_ultra_deduplication()
    
    print(f"\n🤔 DRY RUN RESULTS:")
    print(f"Would remove {results['files_removed']} files")
    print(f"Would create {results['modules_created']} shared modules")
    print(f"Would update {results['files_updated']} files")
    
    # Ask for confirmation
    response = input(f"\n❓ Proceed with actual deduplication? (y/N): ").strip().lower()
    
    if response == 'y':
        print(f"\n🎯 RUNNING ACTUAL DEDUPLICATION...")
        actual_deduplicator = UltraDeduplicator(backend_dir, dry_run=False)
        actual_results = actual_deduplicator.run_ultra_deduplication()
        
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
        print("🚫 Deduplication cancelled")


if __name__ == "__main__":
    main() 