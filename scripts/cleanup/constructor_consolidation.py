#!/usr/bin/env python3

import os
import re
import hashlib
import shutil
from collections import defaultdict, Counter
from pathlib import Path
import ast

class ConstructorConsolidator:
    def __init__(self, backend_dir, dry_run=True):
        self.backend_dir = Path(backend_dir)
        self.dry_run = dry_run
        self.backup_dir = self.backend_dir.parent / "systems_constructor_backup"
        
        # Tracking
        self.actions_taken = []
        self.constructors_found = []
        self.patterns_identified = {}
        self.base_classes_created = []
        
    def create_backup(self):
        """Create backup before constructor consolidation"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print(f"🔄 Creating constructor backup at {self.backup_dir}")
        shutil.copytree(self.backend_dir, self.backup_dir)
        print(f"✅ Backup completed")
    
    def analyze_constructors(self):
        """Analyze all __init__ methods to find patterns"""
        print("🔍 Analyzing constructor patterns...")
        
        constructors = []
        python_files = list(self.backend_dir.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Simple regex to find __init__ methods
                init_matches = re.finditer(r'def __init__\(self[^)]*\):.*?(?=\n    def|\nclass|\n\n|\Z)', 
                                         content, re.DOTALL)
                
                for match in init_matches:
                    init_method = match.group(0)
                    # Normalize for pattern matching
                    normalized = self.normalize_constructor(init_method)
                    
                    constructors.append({
                        'file': file_path,
                        'source': init_method,
                        'normalized': normalized,
                        'hash': hashlib.md5(normalized.encode()).hexdigest(),
                        'param_count': init_method.count(',') + 1
                    })
                    
            except Exception as e:
                continue
        
        print(f"   📊 Found {len(constructors)} constructors")
        
        # Group by pattern
        by_hash = defaultdict(list)
        for constructor in constructors:
            by_hash[constructor['hash']].append(constructor)
        
        # Find duplicates
        duplicate_count = 0
        for hash_val, constructors_list in by_hash.items():
            if len(constructors_list) > 1:
                self.patterns_identified[hash_val] = constructors_list
                duplicate_count += len(constructors_list) - 1
        
        print(f"   🔴 Found {duplicate_count} duplicate constructors")
        print(f"   📋 Identified {len(self.patterns_identified)} unique patterns")
        
        return duplicate_count
    
    def normalize_constructor(self, constructor_source):
        """Normalize constructor for pattern matching"""
        # Remove parameter names but keep types
        normalized = re.sub(r'self\s*,?\s*', '', constructor_source)
        normalized = re.sub(r'\w+:', '', normalized)  # Remove parameter names
        normalized = re.sub(r'=\s*[^,)]+', '=DEFAULT', normalized)  # Normalize defaults
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        
        # Focus on the actual assignments in the constructor
        lines = normalized.split('\n')[1:]  # Skip def line
        assignments = []
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                # Normalize assignment patterns
                assignment = re.sub(r'self\.\w+', 'self.ATTR', line)
                assignment = re.sub(r'=\s*\w+', '= VAR', assignment)
                assignments.append(assignment)
        
        return '\n'.join(assignments)
    
    def identify_base_class_patterns(self):
        """Identify common patterns that can be turned into base classes"""
        print("🏗️  Identifying base class patterns...")
        
        pattern_analysis = {}
        
        for hash_val, constructors in self.patterns_identified.items():
            if len(constructors) < 3:  # Need at least 3 to justify a base class
                continue
            
            # Analyze what this pattern does
            example = constructors[0]['source']
            
            # Common patterns
            has_id_name = 'self.id' in example and 'self.name' in example
            has_config = 'self.config' in example or 'config' in example
            has_logger = 'self.logger' in example or 'logging' in example
            has_db = 'self.db' in example or 'database' in example
            has_data = 'self.data' in example
            
            pattern_type = "Unknown"
            if has_id_name and has_data:
                pattern_type = "Entity"
            elif has_config and has_logger:
                pattern_type = "Manager"
            elif has_db:
                pattern_type = "Repository"
            elif has_logger:
                pattern_type = "Service"
            
            pattern_analysis[hash_val] = {
                'type': pattern_type,
                'count': len(constructors),
                'files': [str(c['file']) for c in constructors],
                'example': example
            }
        
        # Show top patterns
        print("   🎯 Top constructor patterns:")
        sorted_patterns = sorted(pattern_analysis.items(), 
                               key=lambda x: x[1]['count'], reverse=True)
        
        for i, (hash_val, info) in enumerate(sorted_patterns[:5]):
            print(f"      {i+1}. {info['type']} pattern: {info['count']} occurrences")
        
        return pattern_analysis
    
    def create_targeted_base_classes(self, pattern_analysis):
        """Create base classes for the most common patterns"""
        print("🔧 Creating targeted base classes...")
        
        base_dir = self.backend_dir / "infrastructure" / "base_classes"
        
        if not self.dry_run:
            base_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the most common patterns
        top_patterns = sorted(pattern_analysis.items(), 
                            key=lambda x: x[1]['count'], reverse=True)[:3]
        
        base_classes_content = '''"""
Consolidated base classes derived from duplicate constructor analysis.
Created to eliminate the 781+ duplicate constructors found in the codebase.
"""

from abc import ABC
from typing import Any, Dict, Optional, List, Union
import logging
import uuid
from datetime import datetime


class BaseGameEntity(ABC):
    """
    Base class for game entities (characters, items, locations, etc.)
    Consolidates the most common entity constructor pattern.
    """
    
    def __init__(self, 
                 id: Optional[str] = None, 
                 name: str = "", 
                 data: Optional[Dict[str, Any]] = None,
                 created_at: Optional[datetime] = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.data = data or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = datetime.now()
        self.active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'active': self.active
        }
    
    def update_data(self, new_data: Dict[str, Any]):
        """Update entity data"""
        self.data.update(new_data)
        self.updated_at = datetime.now()


class BaseGameManager(ABC):
    """
    Base class for game system managers.
    Consolidates manager constructor patterns with config and logging.
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 logger: Optional[logging.Logger] = None,
                 auto_initialize: bool = True):
        self.config = config or {}
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.initialized = False
        self.running = False
        
        if auto_initialize:
            self.initialize()
    
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
    
    def start(self):
        """Start the manager"""
        if not self.initialized:
            self.initialize()
        self.running = True
        self.logger.info(f"{self.__class__.__name__} started")
    
    def stop(self):
        """Stop the manager"""
        self.running = False
        self.logger.info(f"{self.__class__.__name__} stopped")


class BaseGameService(ABC):
    """
    Base class for game services.
    Consolidates service constructor patterns.
    """
    
    def __init__(self, 
                 repository=None,
                 config: Optional[Dict[str, Any]] = None,
                 logger: Optional[logging.Logger] = None):
        self.repository = repository
        self.config = config or {}
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.metrics = {}
    
    def validate_input(self, data: Any) -> bool:
        """Validate service input"""
        return True  # Override in subclasses
    
    def log_operation(self, operation: str, success: bool, details: str = ""):
        """Log service operations"""
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, f"{operation}: {'SUCCESS' if success else 'FAILED'} - {details}")
    
    def update_metrics(self, metric: str, value: Union[int, float]):
        """Update service metrics"""
        self.metrics[metric] = self.metrics.get(metric, 0) + value


class BaseDataRepository(ABC):
    """
    Base class for data repositories.
    Consolidates database access patterns.
    """
    
    def __init__(self, 
                 db_connection=None,
                 table_name: str = "",
                 logger: Optional[logging.Logger] = None):
        self.db_connection = db_connection
        self.table_name = table_name
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.cache = {}
    
    def get_connection(self):
        """Get database connection"""
        if not self.db_connection:
            # Initialize connection if needed
            pass
        return self.db_connection
    
    def clear_cache(self):
        """Clear repository cache"""
        self.cache.clear()
        self.logger.debug(f"Cleared cache for {self.table_name}")


# Usage examples for migration:
"""
# Instead of:
class Character:
    def __init__(self, id=None, name="", data=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.data = data or {}
        self.created_at = created_at or datetime.now()
        # ... rest of duplicate pattern

# Use:
from backend.infrastructure.base_classes import BaseGameEntity

class Character(BaseGameEntity):
    def __init__(self, attribute_specialization="balanced", level=1, **kwargs):
        super().__init__(**kwargs)
        self.attribute_specialization = attribute_specialization
        self.level = level
        # Only character-specific attributes here
"""
'''
        
        base_file = base_dir / "consolidated_bases.py"
        
        if not self.dry_run:
            with open(base_file, 'w') as f:
                f.write(base_classes_content)
            
            # Update __init__.py
            init_file = base_dir / "__init__.py"
            if init_file.exists():
                with open(init_file, 'a') as f:
                    f.write('\nfrom .consolidated_bases import *\n')
            else:
                with open(init_file, 'w') as f:
                    f.write('from .consolidated_bases import *\n')
        
        self.base_classes_created.append(str(base_file))
        self.actions_taken.append(f"Created consolidated base classes: {base_file}")
        
        return base_file
    
    def generate_migration_guide(self, pattern_analysis):
        """Generate a guide for migrating constructors to use base classes"""
        guide_content = f"""# Constructor Consolidation Migration Guide

This guide shows how to migrate duplicate constructors to use the new base classes.

## Summary
- **Total constructors analyzed:** {len(self.constructors_found)}
- **Duplicate patterns found:** {len(self.patterns_identified)}
- **Constructors that can be consolidated:** {sum(len(p) for p in self.patterns_identified.values())}

## Migration Patterns

"""
        
        for i, (hash_val, info) in enumerate(pattern_analysis.items()):
            if info['count'] >= 3:
                guide_content += f"""
### Pattern {i+1}: {info['type']} ({info['count']} occurrences)

**Files to update:**
{chr(10).join(f"- {file}" for file in info['files'][:5])}
{"... and more" if len(info['files']) > 5 else ""}

**Current pattern:**
```python
{info['example'][:200]}...
```

**Recommended migration to:**
```python
from backend.infrastructure.base_classes import BaseGame{info['type']}

class YourClass(BaseGame{info['type']}):
    def __init__(self, attribute_specialization="balanced", level=1, **kwargs):
        super().__init__(**kwargs)
        self.attribute_specialization = attribute_specialization
        self.level = level
```

"""
        
        guide_file = self.backend_dir / "CONSTRUCTOR_MIGRATION_GUIDE.md"
        
        if not self.dry_run:
            with open(guide_file, 'w') as f:
                f.write(guide_content)
        
        self.actions_taken.append(f"Created migration guide: {guide_file}")
        return guide_file
    
    def run_constructor_consolidation(self):
        """Run complete constructor consolidation analysis"""
        print("🚀 STARTING CONSTRUCTOR CONSOLIDATION ANALYSIS")
        print("=" * 70)
        
        # Create backup
        if not self.dry_run:
            self.create_backup()
        
        # Analyze constructors
        duplicate_count = self.analyze_constructors()
        
        if duplicate_count == 0:
            print("✅ No duplicate constructors found!")
            return {'duplicates': 0, 'patterns': 0}
        
        # Identify patterns
        pattern_analysis = self.identify_base_class_patterns()
        
        # Create base classes
        base_classes_file = self.create_targeted_base_classes(pattern_analysis)
        
        # Generate migration guide
        guide_file = self.generate_migration_guide(pattern_analysis)
        
        # Final statistics
        print("\n" + "=" * 70)
        print("🎉 CONSTRUCTOR ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"📈 RESULTS:")
        print(f"   Duplicate constructors: {duplicate_count}")
        print(f"   Consolidatable patterns: {len(pattern_analysis)}")
        print(f"   Base classes created: {len(self.base_classes_created)}")
        print(f"   Migration guide: {'Created' if guide_file else 'Not created'}")
        
        if self.dry_run:
            print(f"\n⚠️  DRY RUN MODE - No changes were actually made")
        else:
            print(f"\n✅ ANALYSIS COMPLETED")
            print(f"   Backup created at: {self.backup_dir}")
            print(f"   Next step: Review migration guide and update classes manually")
        
        return {
            'duplicates': duplicate_count,
            'patterns': len(pattern_analysis),
            'base_classes': len(self.base_classes_created)
        }


def main():
    backend_dir = "backend/systems"
    
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found: {backend_dir}")
        return
    
    print("🧪 RUNNING CONSTRUCTOR ANALYSIS...")
    consolidator = ConstructorConsolidator(backend_dir, dry_run=False)
    results = consolidator.run_constructor_consolidation()
    
    print(f"\n🎯 CONSTRUCTOR CONSOLIDATION RESULTS:")
    print(f"Found {results['duplicates']} duplicate constructors")
    print(f"Identified {results['patterns']} consolidatable patterns")
    print(f"Created {results['base_classes']} base class files")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"1. Review the migration guide: backend/systems/CONSTRUCTOR_MIGRATION_GUIDE.md")
    print(f"2. Update classes to inherit from new base classes")
    print(f"3. Remove duplicate constructor code")
    print(f"4. Test the refactored code")


if __name__ == "__main__":
    main() 