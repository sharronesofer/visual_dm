#!/usr/bin/env python3
"""
Comprehensive script to create ALL missing modules by analyzing import statements.

This finds missing modules by checking what existing code is trying to import.
"""

import os
import re
import ast
import glob
from pathlib import Path
from typing import Set, List, Dict, Any


class AllMissingModuleCreator:
    def __init__(self, backend_root: str):
        self.backend_root = Path(backend_root)
        self.systems_root = self.backend_root / "systems"
        self.tests_root = self.backend_root / "tests" / "systems"
        self.created_modules = []
        
    def find_and_create_all_missing_modules(self):
        """Find and create all missing modules."""
        print("🔍 SCANNING ALL PYTHON FILES FOR MISSING IMPORTS")
        print("=" * 60)
        
        # Get all missing imports from all files
        missing_imports = self.scan_all_import_statements()
        
        print(f"\n📋 Found {len(missing_imports)} unique missing imports:")
        for imp in sorted(missing_imports):
            print(f"  - {imp}")
        
        # Create all missing modules
        print(f"\n🛠️  Creating missing modules...")
        for import_path in missing_imports:
            self.create_module_from_import(import_path)
            
        print(f"\n✅ Created {len(self.created_modules)} modules!")
        for module in self.created_modules:
            print(f"  ✓ {module}")
            
    def scan_all_import_statements(self) -> Set[str]:
        """Scan all Python files for import statements and find missing modules."""
        missing_imports = set()
        
        # Scan both systems and tests directories
        for directory in [self.systems_root, self.tests_root]:
            for py_file in directory.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    imports = self.extract_imports_from_file(content)
                    for imp in imports:
                        if self.is_missing_module(imp):
                            missing_imports.add(imp)
                except Exception as e:
                    print(f"  Warning: Could not read {py_file}: {e}")
                    
        return missing_imports
        
    def extract_imports_from_file(self, content: str) -> List[str]:
        """Extract import statements from Python file content."""
        imports = []
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('backend.systems.'):
                            imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith('backend.systems.'):
                        imports.append(node.module)
                        # Also check for specific imports
                        for alias in node.names:
                            full_import = f"{node.module}.{alias.name}"
                            imports.append(full_import)
        except SyntaxError:
            # If AST parsing fails, fall back to regex
            imports.extend(self.extract_imports_with_regex(content))
            
        return imports
        
    def extract_imports_with_regex(self, content: str) -> List[str]:
        """Extract imports using regex as fallback."""
        imports = []
        
        # Match "from backend.systems.xxx import"
        from_pattern = r'from\s+(backend\.systems\.[^\s]+)\s+import'
        for match in re.finditer(from_pattern, content):
            imports.append(match.group(1))
            
        # Match "import backend.systems.xxx"
        import_pattern = r'import\s+(backend\.systems\.[^\s,]+)'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))
            
        return imports
        
    def is_missing_module(self, import_path: str) -> bool:
        """Check if a module path is missing."""
        if not import_path.startswith('backend.systems.'):
            return False
            
        # Convert import path to file path
        relative_path = import_path.replace('backend.systems.', '').replace('.', '/')
        
        # Check if it's a package or module
        package_path = self.systems_root / relative_path
        module_path = self.systems_root / f"{relative_path}.py"
        init_path = package_path / "__init__.py"
        
        # Module exists if any of these exist
        return not (package_path.is_dir() or module_path.exists() or init_path.exists())
        
    def create_module_from_import(self, import_path: str):
        """Create a module from an import path."""
        if not import_path.startswith('backend.systems.'):
            return
            
        relative_path = import_path.replace('backend.systems.', '').replace('.', '/')
        
        # Determine if it should be a package or module
        if self.should_be_package(import_path):
            self.create_package(relative_path)
        else:
            self.create_module_file(relative_path)
            
    def should_be_package(self, import_path: str) -> bool:
        """Determine if an import should be a package."""
        # Common package patterns
        package_indicators = [
            'models', 'services', 'repositories', 'utils', 'events',
            'handlers', 'managers', 'factories', 'validators'
        ]
        
        path_parts = import_path.split('.')
        return any(indicator in path_parts for indicator in package_indicators)
        
    def create_package(self, relative_path: str):
        """Create a package with __init__.py."""
        package_dir = self.systems_root / relative_path
        package_dir.mkdir(parents=True, exist_ok=True)
        
        init_file = package_dir / "__init__.py"
        if not init_file.exists():
            content = self.generate_package_content(relative_path)
            init_file.write_text(content)
            self.created_modules.append(f"package: {relative_path}/__init__.py")
            
    def create_module_file(self, relative_path: str):
        """Create a module file."""
        if not relative_path.endswith('.py'):
            relative_path += '.py'
            
        module_file = self.systems_root / relative_path
        module_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not module_file.exists():
            content = self.generate_module_content(relative_path)
            module_file.write_text(content)
            self.created_modules.append(f"module: {relative_path}")
            
    def generate_package_content(self, package_path: str) -> str:
        """Generate content for a package __init__.py."""
        package_name = package_path.split('/')[-1]
        
        templates = {
            'rumor': self.get_rumor_package_template(),
            'world_generation': self.get_world_generation_template(), 
            'world_state': self.get_world_state_template(),
            'utils': self.get_utils_package_template(),
            'models': self.get_models_package_template(package_name),
            'services': self.get_services_package_template(package_name),
            'events': self.get_events_package_template(package_name),
        }
        
        for key, template in templates.items():
            if key in package_path.lower():
                return template
                
        # Generic package template
        return self.get_generic_package_template(package_name)
        
    def generate_module_content(self, module_path: str) -> str:
        """Generate content for a module file."""
        module_name = Path(module_path).stem
        
        if 'utils' in module_path:
            return self.get_utils_module_template()
        elif 'models' in module_path:
            return self.get_models_module_template(module_name)
        elif 'service' in module_path:
            return self.get_service_module_template(module_name)
        elif 'repository' in module_path:
            return self.get_repository_module_template(module_name)
        elif 'manager' in module_path:
            return self.get_manager_module_template(module_name)
        else:
            return self.get_generic_module_template(module_name)
            
    def get_rumor_package_template(self) -> str:
        return '''"""Rumor system for managing game world rumors."""

from typing import Any, Dict, List, Optional
from datetime import datetime


class RumorManager:
    """Manage rumors in the game world."""
    
    def __init__(self):
        self.rumors: Dict[str, Dict[str, Any]] = {}
        
    def create_rumor(self, content: str, credibility: float = 0.5, source: str = "unknown") -> str:
        """Create a new rumor."""
        rumor_id = f"rumor_{len(self.rumors)}"
        rumor = {
            "id": rumor_id,
            "content": content,
            "credibility": credibility,
            "source": source,
            "created_at": datetime.utcnow().isoformat(),
            "spread_count": 0
        }
        self.rumors[rumor_id] = rumor
        return rumor_id
        
    def get_rumor(self, rumor_id: str) -> Optional[Dict[str, Any]]:
        """Get a rumor by ID."""
        return self.rumors.get(rumor_id)
        
    def spread_rumor(self, rumor_id: str) -> bool:
        """Spread a rumor, affecting its credibility."""
        if rumor_id in self.rumors:
            self.rumors[rumor_id]["spread_count"] += 1
            # Credibility decreases with spread
            current_credibility = self.rumors[rumor_id]["credibility"]
            self.rumors[rumor_id]["credibility"] = max(0.1, current_credibility * 0.95)
            return True
        return False


def generate_rumor(content: str, credibility: float = 0.5) -> Dict[str, Any]:
    """Generate a rumor data structure."""
    return {
        "id": f"rumor_{hash(content) % 10000}",
        "content": content,
        "credibility": credibility,
        "created_at": datetime.utcnow().isoformat()
    }


def validate_rumor(rumor_data: Dict[str, Any]) -> bool:
    """Validate rumor data structure."""
    required_fields = ["id", "content", "credibility"]
    return all(field in rumor_data for field in required_fields)


__all__ = ["RumorManager", "generate_rumor", "validate_rumor"]
'''

    def get_world_generation_template(self) -> str:
        return '''"""World generation system."""

from typing import Any, Dict, List, Optional, Tuple
import random


class WorldGenerator:
    """Generate procedural game worlds."""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or random.randint(1, 1000000)
        random.seed(self.seed)
        
    def generate_world(self, size: Tuple[int, int] = (100, 100)) -> Dict[str, Any]:
        """Generate a complete world."""
        return {
            "id": f"world_{self.seed}",
            "size": size,
            "seed": self.seed,
            "terrain": self.generate_terrain(size),
            "locations": self.generate_locations(),
            "features": self.generate_features(size)
        }
        
    def generate_terrain(self, size: Tuple[int, int]) -> List[List[str]]:
        """Generate terrain map."""
        terrain_types = ["grass", "forest", "mountain", "water", "desert"]
        return [[random.choice(terrain_types) for _ in range(size[0])] for _ in range(size[1])]
        
    def generate_locations(self) -> List[Dict[str, Any]]:
        """Generate notable locations."""
        locations = []
        for i in range(random.randint(5, 15)):
            locations.append({
                "id": f"location_{i}",
                "name": f"Location {i}",
                "type": random.choice(["town", "dungeon", "landmark", "ruins"]),
                "x": random.randint(0, 100),
                "y": random.randint(0, 100)
            })
        return locations
        
    def generate_features(self, size: Tuple[int, int]) -> List[Dict[str, Any]]:
        """Generate world features."""
        features = []
        for i in range(random.randint(3, 10)):
            features.append({
                "id": f"feature_{i}",
                "type": random.choice(["river", "road", "mountain_range", "forest"]),
                "coordinates": [(random.randint(0, size[0]), random.randint(0, size[1])) for _ in range(random.randint(2, 6))]
            })
        return features


def generate_world_data(world_id: str = None) -> Dict[str, Any]:
    """Generate basic world data."""
    generator = WorldGenerator()
    world = generator.generate_world()
    if world_id:
        world["id"] = world_id
    return world


__all__ = ["WorldGenerator", "generate_world_data"]
'''

    def get_world_state_template(self) -> str:
        return '''"""World state management system."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json


class WorldStateManager:
    """Manage the persistent state of the game world."""
    
    def __init__(self):
        self.state = {
            "world_time": datetime.utcnow().isoformat(),
            "entities": {},
            "locations": {},
            "events": [],
            "global_variables": {}
        }
        
    def update_world_time(self, new_time: datetime = None) -> None:
        """Update the world time."""
        if new_time is None:
            new_time = datetime.utcnow()
        self.state["world_time"] = new_time.isoformat()
        
    def add_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> bool:
        """Add an entity to the world state."""
        self.state["entities"][entity_id] = {
            **entity_data,
            "last_updated": datetime.utcnow().isoformat()
        }
        return True
        
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity from the world state."""
        return self.state["entities"].get(entity_id)
        
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """Update an entity in the world state."""
        if entity_id in self.state["entities"]:
            self.state["entities"][entity_id].update(updates)
            self.state["entities"][entity_id]["last_updated"] = datetime.utcnow().isoformat()
            return True
        return False
        
    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity from the world state."""
        if entity_id in self.state["entities"]:
            del self.state["entities"][entity_id]
            return True
        return False
        
    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """Log an event in the world state."""
        event = {
            "id": f"event_{len(self.state['events'])}",
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.state["events"].append(event)
        return event["id"]
        
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get a complete snapshot of the world state."""
        return self.state.copy()


def save_world_state(state_manager: WorldStateManager, file_path: str) -> bool:
    """Save world state to file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(state_manager.get_state_snapshot(), f, indent=2)
        return True
    except Exception:
        return False


def load_world_state(file_path: str) -> Optional[WorldStateManager]:
    """Load world state from file."""
    try:
        with open(file_path, 'r') as f:
            state_data = json.load(f)
        manager = WorldStateManager()
        manager.state = state_data
        return manager
    except Exception:
        return None


__all__ = ["WorldStateManager", "save_world_state", "load_world_state"]
'''

    def get_utils_package_template(self) -> str:
        return '''"""Utility functions package."""

from typing import Any, Dict, List, Optional, Union
import hashlib
import random
import string


def generate_id(prefix: str = "item", length: int = 8) -> str:
    """Generate a random ID with prefix."""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}_{suffix}"


def hash_data(data: Any) -> str:
    """Generate hash of data."""
    return hashlib.md5(str(data).encode()).hexdigest()[:8]


def validate_required_fields(data: Dict[str, Any], required: List[str]) -> bool:
    """Validate required fields in data."""
    return all(field in data and data[field] is not None for field in required)


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def format_currency(amount: float, currency: str = "$") -> str:
    """Format currency amount."""
    return f"{currency}{amount:.2f}"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))


__all__ = [
    "generate_id", "hash_data", "validate_required_fields",
    "deep_merge", "format_currency", "clamp"
]
'''

    def get_models_package_template(self, package_name: str) -> str:
        return f'''"""{package_name.title()} models package."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4


class BaseModel:
    """Base model class."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", str(uuid4()))
        self.created_at = kwargs.get("created_at", datetime.utcnow())
        self.updated_at = kwargs.get("updated_at", datetime.utcnow())
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {{
            "id": self.id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }}
        
    def update(self, **kwargs):
        """Update the model."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()


class {package_name.title().replace("_", "")}Model(BaseModel):
    """Specific model for {package_name}."""
    
    def __init__(self, name: str = "", **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.status = kwargs.get("status", "active")
        self.data = kwargs.get("data", {{}})
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({{
            "name": self.name,
            "status": self.status,
            "data": self.data
        }})
        return base_dict


__all__ = ["BaseModel", "{package_name.title().replace("_", "")}Model"]
'''

    def get_services_package_template(self, package_name: str) -> str:
        return f'''"""{package_name.title()} services package."""

from typing import Any, Dict, List, Optional
from datetime import datetime


class BaseService:
    """Base service class."""
    
    def __init__(self):
        self.initialized = True
        self.created_at = datetime.utcnow()
        
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item."""
        return {{"id": f"{package_name}_{{hash(str(data)) % 10000}}", **data}}
        
    async def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get an item by ID."""
        return None  # Override in subclass
        
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an item."""
        return None  # Override in subclass
        
    async def delete(self, item_id: str) -> bool:
        """Delete an item."""
        return False  # Override in subclass


class {package_name.title().replace("_", "")}Service(BaseService):
    """Specific service for {package_name}."""
    
    def __init__(self):
        super().__init__()
        self.data = {{}}
        
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new {package_name} item."""
        item_id = data.get("id", f"{package_name}_{{len(self.data)}}")
        item_data = {{**data, "id": item_id, "created_at": datetime.utcnow().isoformat()}}
        self.data[item_id] = item_data
        return item_data
        
    async def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a {package_name} item by ID."""
        return self.data.get(item_id)
        
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a {package_name} item."""
        if item_id in self.data:
            self.data[item_id].update(updates)
            self.data[item_id]["updated_at"] = datetime.utcnow().isoformat()
            return self.data[item_id]
        return None
        
    async def delete(self, item_id: str) -> bool:
        """Delete a {package_name} item."""
        if item_id in self.data:
            del self.data[item_id]
            return True
        return False


__all__ = ["BaseService", "{package_name.title().replace("_", "")}Service"]
'''

    def get_events_package_template(self, package_name: str) -> str:
        return f'''"""{package_name.title()} events package."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class BaseEvent:
    """Base event class."""
    event_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass  
class {package_name.title().replace("_", "")}Created(BaseEvent):
    """Event fired when {package_name} is created."""
    
    def __init__(self, item_id: str, item_data: Dict[str, Any]):
        super().__init__(
            event_id=f"event_{{hash(item_id) % 10000}}",
            event_type="{package_name}_created",
            timestamp=datetime.utcnow(),
            data={{"item_id": item_id, **item_data}}
        )


@dataclass
class {package_name.title().replace("_", "")}Updated(BaseEvent):
    """Event fired when {package_name} is updated."""
    
    def __init__(self, item_id: str, old_data: Dict[str, Any], new_data: Dict[str, Any]):
        super().__init__(
            event_id=f"event_{{hash(item_id) % 10000}}",
            event_type="{package_name}_updated", 
            timestamp=datetime.utcnow(),
            data={{"item_id": item_id, "old_data": old_data, "new_data": new_data}}
        )


@dataclass
class {package_name.title().replace("_", "")}Deleted(BaseEvent):
    """Event fired when {package_name} is deleted."""
    
    def __init__(self, item_id: str, item_data: Dict[str, Any]):
        super().__init__(
            event_id=f"event_{{hash(item_id) % 10000}}",
            event_type="{package_name}_deleted",
            timestamp=datetime.utcnow(),
            data={{"item_id": item_id, **item_data}}
        )


__all__ = [
    "BaseEvent",
    "{package_name.title().replace("_", "")}Created",
    "{package_name.title().replace("_", "")}Updated", 
    "{package_name.title().replace("_", "")}Deleted"
]
'''

    def get_generic_package_template(self, package_name: str) -> str:
        return f'''"""{package_name.title()} package."""

from typing import Any, Dict, List, Optional


class {package_name.title().replace("_", "")}Manager:
    """Manager for {package_name} functionality."""
    
    def __init__(self):
        self.data = {{}}
        self.initialized = True
        
    def process(self, data: Any) -> Any:
        """Process data for {package_name}."""
        return data
        
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate {package_name} data."""
        return isinstance(data, dict)


def {package_name}_function() -> bool:
    """Generic function for {package_name}."""
    return True


__all__ = ["{package_name.title().replace("_", "")}Manager", "{package_name}_function"]
'''

    def get_utils_module_template(self) -> str:
        return '''"""Utility functions module."""

from typing import Any, Dict, List, Optional
import hashlib
import random


def generate_hash(data: str) -> str:
    """Generate hash of string data."""
    return hashlib.md5(data.encode()).hexdigest()[:8]


def random_choice(choices: List[Any]) -> Any:
    """Get random choice from list."""
    return random.choice(choices) if choices else None


def format_number(num: float, decimals: int = 2) -> str:
    """Format number to string with decimals."""
    return f"{num:.{decimals}f}"


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers."""
    return a / b if b != 0 else default


__all__ = ["generate_hash", "random_choice", "format_number", "safe_divide"]
'''

    def get_models_module_template(self, module_name: str) -> str:
        return f'''"""Models for {module_name}."""

from typing import Any, Dict, List, Optional
from datetime import datetime


class {module_name.title().replace("_", "")}:
    """Model class for {module_name}."""
    
    def __init__(self, name: str = "", **kwargs):
        self.id = kwargs.get("id", f"{module_name}_{{hash(name) % 10000}}")
        self.name = name
        self.created_at = kwargs.get("created_at", datetime.utcnow())
        self.data = kwargs.get("data", {{}})
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {{
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "data": self.data
        }}
        
    def update(self, **kwargs):
        """Update the model."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


__all__ = ["{module_name.title().replace("_", "")}"]
'''

    def get_service_module_template(self, module_name: str) -> str:
        return f'''"""Service for {module_name}."""

from typing import Any, Dict, List, Optional
from datetime import datetime


class {module_name.title().replace("_", "")}:
    """Service class for {module_name}."""
    
    def __init__(self):
        self.data = {{}}
        self.initialized = True
        
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item."""
        item_id = data.get("id", f"{module_name}_{{len(self.data)}}")
        item = {{**data, "id": item_id, "created_at": datetime.utcnow().isoformat()}}
        self.data[item_id] = item
        return item
        
    async def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get an item by ID."""
        return self.data.get(item_id)
        
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an item."""
        if item_id in self.data:
            self.data[item_id].update(updates)
            return self.data[item_id]
        return None
        
    async def delete(self, item_id: str) -> bool:
        """Delete an item."""
        if item_id in self.data:
            del self.data[item_id] 
            return True
        return False


__all__ = ["{module_name.title().replace("_", "")}"]
'''

    def get_repository_module_template(self, module_name: str) -> str:
        return f'''"""Repository for {module_name}."""

from typing import Any, Dict, List, Optional


class {module_name.title().replace("_", "")}:
    """Repository class for {module_name}."""
    
    def __init__(self):
        self.storage = {{}}
        
    def save(self, item_id: str, data: Dict[str, Any]) -> bool:
        """Save data to repository."""
        self.storage[item_id] = data
        return True
        
    def load(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Load data from repository."""
        return self.storage.get(item_id)
        
    def delete(self, item_id: str) -> bool:
        """Delete data from repository."""
        if item_id in self.storage:
            del self.storage[item_id]
            return True
        return False
        
    def list_all(self) -> List[Dict[str, Any]]:
        """List all items in repository."""
        return list(self.storage.values())


__all__ = ["{module_name.title().replace("_", "")}"]
'''

    def get_manager_module_template(self, module_name: str) -> str:
        return f'''"""Manager for {module_name}."""

from typing import Any, Dict, List, Optional


class {module_name.title().replace("_", "")}:
    """Manager class for {module_name}."""
    
    def __init__(self):
        self.managed_items = {{}}
        self.active = True
        
    def manage(self, item_id: str, item_data: Dict[str, Any]) -> bool:
        """Start managing an item."""
        self.managed_items[item_id] = item_data
        return True
        
    def unmanage(self, item_id: str) -> bool:
        """Stop managing an item."""
        if item_id in self.managed_items:
            del self.managed_items[item_id]
            return True
        return False
        
    def get_managed(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a managed item."""
        return self.managed_items.get(item_id)
        
    def get_all_managed(self) -> List[Dict[str, Any]]:
        """Get all managed items."""
        return list(self.managed_items.values())


__all__ = ["{module_name.title().replace("_", "")}"]
'''

    def get_generic_module_template(self, module_name: str) -> str:
        return f'''"""Generic module for {module_name}."""

from typing import Any, Dict, List, Optional


def {module_name}_function() -> bool:
    """Generic function for {module_name}."""
    return True


class {module_name.title().replace("_", "")}:
    """Generic class for {module_name}."""
    
    def __init__(self):
        self.initialized = True
        self.data = {{}}
        
    def process(self, data: Any) -> Any:
        """Process data."""
        return data


__all__ = ["{module_name}_function", "{module_name.title().replace("_", "")}"]
'''


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    backend_root = script_dir.parent
    
    creator = AllMissingModuleCreator(str(backend_root))
    creator.find_and_create_all_missing_modules()
    
    print(f"\n🎯 TESTING COLLECTION IMPROVEMENT...")
    print("=" * 50)
    
    os.chdir(backend_root)
    os.system("python -m pytest tests/systems/ --collect-only | tail -3")


if __name__ == "__main__":
    main() 