from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, List, Optional, Set, Union
import json
import os
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from enum import Enum
import importlib.util
import sys

from backend.systems.world_state.core.types import WorldState, StateCategory, WorldRegion
from backend.systems.world_state.core.loader import WorldStateLoader

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("modsynchronizer")

# Router for mod synchronization endpoints
router = APIRouter(
    prefix="/api/mods",
    tags=["mods"],
    responses={404: {"description": "Not found"}},
)

# Define models for mod synchronization
class ModDependency(BaseModel):
    id: str
    version: Optional[str] = None
    required: bool = True

class ModIncompatibility(BaseModel):
    id: str
    version_range: Optional[str] = None

class ModInfo(BaseModel):
    id: str
    name: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None
    dependencies: List[ModDependency] = []
    incompatibilities: List[ModIncompatibility] = []
    load_priority: int = 100  # Lower numbers load first

class ConflictType(str, Enum):
    ENTITY_OVERRIDE = "entity_override"
    DEPENDENCY_MISSING = "dependency_missing"
    INCOMPATIBLE_MODS = "incompatible_mods"
    CIRCULAR_DEPENDENCY = "circular_dependency"

class ConflictResolutionStrategy(str, Enum):
    USE_HIGHEST_PRIORITY = "use_highest_priority"
    MERGE_DATA = "merge_data"
    IGNORE_CONFLICT = "ignore_conflict"
    DISABLE_MOD = "disable_mod"

class ModConflict(BaseModel):
    entity_id: str
    conflicting_mods: List[str]
    type: ConflictType
    description: str

class ConflictResolutionRequest(BaseModel):
    conflict_id: str
    resolution_strategy: ConflictResolutionStrategy
    mod_to_use: Optional[str] = None  # For USE_HIGHEST_PRIORITY strategy

class SyncStatus(BaseModel):
    in_progress: bool = False
    success: Optional[bool] = None
    last_sync: Optional[datetime] = None
    conflicts: List[ModConflict] = []

# In-memory storage for mod synchronization state
# In a production system, this would be persisted in a database
mod_registry: Dict[str, ModInfo] = {}
active_mods: Set[str] = set()
sync_state = SyncStatus()
sync_connections: List[WebSocket] = []

# Base directory for mod data
MOD_BASE_DIR = Path("backend/data/modding/mods")
MOD_SCHEMA_DIR = Path("backend/data/modding/schemas")

class ModSynchronizer:
    """
    Handles synchronization between game mods and the world state system.
    """
    
    def __init__(self, 
                 mods_directory: str = "data/mods",
                 schemas_directory: str = "data/schemas",
                 state_loader: Optional[WorldStateLoader] = None):
        """
        Initialize the mod synchronizer.
        
        Args:
            mods_directory: Directory containing game mods
            schemas_directory: Directory containing validation schemas
            state_loader: Optional state loader instance (creates one if None)
        """
        self.mods_directory = mods_directory
        self.schemas_directory = schemas_directory
        self.state_loader = state_loader or WorldStateLoader()
        
        # Cache of loaded mods
        self.loaded_mods: Dict[str, Dict[str, Any]] = {}
        
        # Track enabled mods
        self.enabled_mods: Set[str] = set()
        
        # Ensure mod schema directories exist
        os.makedirs(mods_directory, exist_ok=True)
        os.makedirs(schemas_directory, exist_ok=True)
    
    def discover_mods(self) -> List[Dict[str, Any]]:
        """
        Discover all available mods and their metadata.
        
        Returns:
            List of mod metadata dictionaries
        """
        mods = []
        
        try:
            # Get all directories in the mods directory
            mod_dirs = [d for d in os.listdir(self.mods_directory) 
                     if os.path.isdir(os.path.join(self.mods_directory, d))]
            
            for mod_dir in mod_dirs:
                mod_path = os.path.join(self.mods_directory, mod_dir)
                manifest_path = os.path.join(mod_path, "manifest.json")
                
                if not os.path.exists(manifest_path):
                    logger.warning(f"Mod directory '{mod_dir}' has no manifest.json, skipping")
                    continue
                
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                    
                    # Validate manifest has required fields
                    if not self._validate_manifest(manifest):
                        logger.warning(f"Mod '{mod_dir}' has invalid manifest, skipping")
                        continue
                    
                    # Add the mod path to the manifest
                    manifest["path"] = mod_path
                    mods.append(manifest)
                    
                except Exception as e:
                    logger.error(f"Error loading mod manifest for '{mod_dir}': {str(e)}")
            
            # Sort mods by load priority if specified
            mods.sort(key=lambda m: m.get("load_priority", 100))
            return mods
            
        except Exception as e:
            logger.error(f"Error discovering mods: {str(e)}")
            return []
    
    def load_mod(self, mod_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific mod by ID.
        
        Args:
            mod_id: The ID of the mod to load
            
        Returns:
            The loaded mod data or None if not found/invalid
        """
        # Check cache first
        if mod_id in self.loaded_mods:
            return self.loaded_mods[mod_id]
        
        try:
            # Discover all mods
            all_mods = self.discover_mods()
            
            # Find the requested mod
            mod = next((m for m in all_mods if m["id"] == mod_id), None)
            if not mod:
                logger.warning(f"Mod '{mod_id}' not found")
                return None
            
            # Load the mod data
            mod_data = self._load_mod_data(mod)
            if not mod_data:
                logger.warning(f"Failed to load data for mod '{mod_id}'")
                return None
            
            # Validate the mod data
            if not self._validate_mod_data(mod_data, mod):
                logger.warning(f"Mod '{mod_id}' data failed validation")
                return None
            
            # Cache the loaded mod
            self.loaded_mods[mod_id] = mod_data
            return mod_data
            
        except Exception as e:
            logger.error(f"Error loading mod '{mod_id}': {str(e)}")
            return None
    
    def apply_mod(self, mod_id: str, world_state: Dict[str, Any]) -> bool:
        """
        Apply a mod to the world state.
        
        Args:
            mod_id: The ID of the mod to apply
            world_state: The world state to modify
            
        Returns:
            True if applied successfully, False otherwise
        """
        try:
            # Load the mod if not already loaded
            mod_data = self.load_mod(mod_id)
            if not mod_data:
                return False
            
            # Execute the mod's Python code if provided
            if "scripts" in mod_data:
                success = self._execute_mod_scripts(mod_data["scripts"], world_state)
                if not success:
                    return False
            
            # Apply state changes
            if "state_changes" in mod_data:
                self._apply_state_changes(mod_data["state_changes"], world_state)
            
            # Apply regions
            if "regions" in mod_data:
                self._apply_regions(mod_data["regions"], world_state)
            
            # Apply factions
            if "factions" in mod_data:
                self._apply_factions(mod_data["factions"], world_state)
            
            # Apply NPCs
            if "npcs" in mod_data:
                self._apply_npcs(mod_data["npcs"], world_state)
            
            # Mark the mod as enabled
            self.enabled_mods.add(mod_id)
            
            # Update the active mods list in world state
            if "metadata" not in world_state:
                world_state["metadata"] = {}
            
            if "active_mods" not in world_state["metadata"]:
                world_state["metadata"]["active_mods"] = []
                
            # Add mod to active mods if not already there
            if mod_id not in world_state["metadata"]["active_mods"]:
                world_state["metadata"]["active_mods"].append(mod_id)
            
            logger.info(f"Successfully applied mod '{mod_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Error applying mod '{mod_id}': {str(e)}")
            return False
    
    def apply_all_mods(self, world_state: Dict[str, Any]) -> bool:
        """
        Apply all discovered mods to the world state.
        
        Args:
            world_state: The world state to modify
            
        Returns:
            True if all mods applied successfully, False otherwise
        """
        try:
            # Discover all mods
            all_mods = self.discover_mods()
            
            # Track successes
            success_count = 0
            failure_count = 0
            
            # Apply each mod
            for mod in all_mods:
                mod_id = mod["id"]
                
                # Skip disabled mods
                if not mod.get("enabled", True):
                    logger.info(f"Skipping disabled mod '{mod_id}'")
                    continue
                    
                # Apply the mod
                success = self.apply_mod(mod_id, world_state)
                if success:
                    success_count += 1
                else:
                    failure_count += 1
            
            logger.info(f"Applied {success_count} mods successfully, {failure_count} failed")
            return failure_count == 0
            
        except Exception as e:
            logger.error(f"Error applying all mods: {str(e)}")
            return False
    
    def _validate_manifest(self, manifest: Dict[str, Any]) -> bool:
        """
        Validate a mod manifest.
        
        Args:
            manifest: The manifest to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["id", "name", "version", "description"]
        for field in required_fields:
            if field not in manifest:
                logger.warning(f"Manifest missing required field: {field}")
                return False
        
        return True
    
    def _load_mod_data(self, mod: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Load the data for a mod.
        
        Args:
            mod: The mod metadata
            
        Returns:
            The loaded mod data or None if failed
        """
        mod_path = mod["path"]
        
        # Combined mod data
        mod_data = {
            "metadata": mod,
            "state_changes": [],
            "regions": [],
            "factions": [],
            "npcs": [],
            "scripts": []
        }
        
        # Load state changes
        state_changes_path = os.path.join(mod_path, "state_changes.json")
        if os.path.exists(state_changes_path):
            try:
                with open(state_changes_path, 'r') as f:
                    mod_data["state_changes"] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading state changes for mod '{mod['id']}': {str(e)}")
        
        # Load regions
        regions_path = os.path.join(mod_path, "regions.json")
        if os.path.exists(regions_path):
            try:
                with open(regions_path, 'r') as f:
                    mod_data["regions"] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading regions for mod '{mod['id']}': {str(e)}")
        
        # Load factions
        factions_path = os.path.join(mod_path, "factions.json")
        if os.path.exists(factions_path):
            try:
                with open(factions_path, 'r') as f:
                    mod_data["factions"] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading factions for mod '{mod['id']}': {str(e)}")
        
        # Load NPCs
        npcs_path = os.path.join(mod_path, "npcs.json")
        if os.path.exists(npcs_path):
            try:
                with open(npcs_path, 'r') as f:
                    mod_data["npcs"] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading NPCs for mod '{mod['id']}': {str(e)}")
        
        # Load scripts
        scripts_dir = os.path.join(mod_path, "scripts")
        if os.path.exists(scripts_dir) and os.path.isdir(scripts_dir):
            script_files = [f for f in os.listdir(scripts_dir) if f.endswith('.py')]
            for script_file in script_files:
                script_path = os.path.join(scripts_dir, script_file)
                mod_data["scripts"].append(script_path)
        
        return mod_data
    
    def _validate_mod_data(self, mod_data: Dict[str, Any], mod: Dict[str, Any]) -> bool:
        """
        Validate mod data against schemas.
        
        Args:
            mod_data: The mod data to validate
            mod: The mod metadata
            
        Returns:
            True if valid, False otherwise
        """
        # For now, just do basic validation
        # In a real implementation, this would use JSON Schema validation
        
        # Check state changes format
        for change in mod_data.get("state_changes", []):
            if not isinstance(change, dict) or "key" not in change or "value" not in change:
                logger.warning(f"Invalid state change in mod '{mod['id']}'")
                return False
        
        # TODO: Add more validation for regions, factions, and NPCs
        
        return True
    
    def _execute_mod_scripts(self, script_paths: List[str], world_state: Dict[str, Any]) -> bool:
        """
        Execute mod Python scripts.
        
        Args:
            script_paths: List of script paths to execute
            world_state: The world state to modify
            
        Returns:
            True if all scripts executed successfully, False otherwise
        """
        for script_path in script_paths:
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location("mod_script", script_path)
                if not spec or not spec.loader:
                    logger.error(f"Failed to load script spec: {script_path}")
                    return False
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if the module has an apply function
                if not hasattr(module, "apply"):
                    logger.warning(f"Script {script_path} has no apply function, skipping")
                    continue
                
                # Execute the apply function
                result = module.apply(world_state)
                if not result:
                    logger.warning(f"Script {script_path} apply function returned False")
                    return False
                
            except Exception as e:
                logger.error(f"Error executing script {script_path}: {str(e)}")
                return False
        
        return True
    
    def _apply_state_changes(self, state_changes: List[Dict[str, Any]], world_state: Dict[str, Any]) -> None:
        """
        Apply state changes to the world state.
        
        Args:
            state_changes: List of state changes
            world_state: The world state to modify
        """
        for change in state_changes:
            key = change["key"]
            value = change["value"]
            
            # Get the path components
            path_components = key.split('.')
            
            # Navigate to the parent object
            current = world_state
            for i, component in enumerate(path_components[:-1]):
                if component not in current:
                    current[component] = {}
                current = current[component]
            
            # Set the value
            current[path_components[-1]] = value
    
    def _apply_regions(self, regions: List[Dict[str, Any]], world_state: Dict[str, Any]) -> None:
        """
        Apply region definitions to the world state.
        
        Args:
            regions: List of region definitions
            world_state: The world state to modify
        """
        if "regions" not in world_state:
            world_state["regions"] = {}
            
        for region in regions:
            region_id = region["id"]
            
            # Skip if region already exists and overwrite is not set
            if region_id in world_state["regions"] and not region.get("overwrite", False):
                logger.info(f"Region '{region_id}' already exists, skipping")
                continue
                
            # Add or replace the region
            world_state["regions"][region_id] = region
    
    def _apply_factions(self, factions: List[Dict[str, Any]], world_state: Dict[str, Any]) -> None:
        """
        Apply faction definitions to the world state.
        
        Args:
            factions: List of faction definitions
            world_state: The world state to modify
        """
        if "factions" not in world_state:
            world_state["factions"] = {}
            
        for faction in factions:
            faction_id = faction["id"]
            
            # Skip if faction already exists and overwrite is not set
            if faction_id in world_state["factions"] and not faction.get("overwrite", False):
                logger.info(f"Faction '{faction_id}' already exists, skipping")
                continue
                
            # Add or replace the faction
            world_state["factions"][faction_id] = faction
    
    def _apply_npcs(self, npcs: List[Dict[str, Any]], world_state: Dict[str, Any]) -> None:
        """
        Apply NPC definitions to the world state.
        
        Args:
            npcs: List of NPC definitions
            world_state: The world state to modify
        """
        if "npcs" not in world_state:
            world_state["npcs"] = {}
            
        for npc in npcs:
            npc_id = npc["id"]
            
            # Skip if NPC already exists and overwrite is not set
            if npc_id in world_state["npcs"] and not npc.get("overwrite", False):
                logger.info(f"NPC '{npc_id}' already exists, skipping")
                continue
                
            # Add or replace the NPC
            world_state["npcs"][npc_id] = npc

@router.get("/sync/status", response_model=SyncStatus)
async def get_sync_status():
    """Get the current status of mod synchronization"""
    return sync_state

@router.post("/sync/start")
async def start_sync():
    """Start the mod synchronization process"""
    if sync_state.in_progress:
        raise HTTPException(status_code=400, detail="Synchronization already in progress")
    
    # Reset state
    sync_state.in_progress = True
    sync_state.success = None
    sync_state.conflicts = []
    
    # Perform sync in background task to allow request to return
    asyncio.create_task(perform_sync())
    
    return {"status": "Synchronization started"}

async def perform_sync():
    """Perform the actual mod synchronization"""
    logger.info("Starting mod synchronization")
    
    try:
        # Load all mods from the mods directory
        await load_all_mods()
        
        # Detect conflicts
        conflicts = await detect_conflicts()
        sync_state.conflicts = conflicts
        
        # Auto-resolve conflicts where possible
        resolved_conflicts = await auto_resolve_conflicts(conflicts)
        
        # Update conflicts list with unresolved ones
        sync_state.conflicts = [c for c in conflicts if c not in resolved_conflicts]
        
        # Update sync state
        sync_state.in_progress = False
        sync_state.success = True
        sync_state.last_sync = datetime.now()
        
        # Notify connected clients
        await notify_clients({
            "type": "sync_completed",
            "success": True,
            "unresolved_conflicts": len(sync_state.conflicts)
        })
        
        logger.info(f"Mod synchronization completed successfully with {len(sync_state.conflicts)} unresolved conflicts")
    
    except Exception as e:
        logger.error(f"Error during mod synchronization: {str(e)}")
        sync_state.in_progress = False
        sync_state.success = False
        sync_state.last_sync = datetime.now()
        
        # Notify connected clients
        await notify_clients({
            "type": "sync_completed",
            "success": False,
            "error": str(e)
        })

async def load_all_mods():
    """Load all mod information from the mods directory"""
    logger.info(f"Loading mods from {MOD_BASE_DIR}")
    mod_registry.clear()
    
    if not MOD_BASE_DIR.exists():
        logger.warning(f"Mod directory {MOD_BASE_DIR} does not exist")
        return
    
    # Scan all directories in the mods folder
    for mod_dir in MOD_BASE_DIR.iterdir():
        if not mod_dir.is_dir():
            continue
        
        # Look for mod_info.json in the mod directory
        mod_info_path = mod_dir / "mod_info.json"
        if not mod_info_path.exists():
            logger.warning(f"No mod_info.json found in {mod_dir}")
            continue
        
        try:
            # Load the mod info
            with open(mod_info_path, "r") as f:
                mod_data = json.load(f)
            
            # Create ModInfo object
            mod_info = ModInfo(
                id=mod_data.get("id", mod_dir.name),
                name=mod_data.get("name", mod_dir.name),
                version=mod_data.get("version", "1.0.0"),
                description=mod_data.get("description"),
                author=mod_data.get("author"),
                load_priority=mod_data.get("load_priority", 100)
            )
            
            # Parse dependencies
            if "dependencies" in mod_data:
                for dep in mod_data["dependencies"]:
                    mod_info.dependencies.append(
                        ModDependency(
                            id=dep["id"],
                            version=dep.get("version"),
                            required=dep.get("required", True)
                        )
                    )
            
            # Parse incompatibilities
            if "incompatibilities" in mod_data:
                for incompat in mod_data["incompatibilities"]:
                    mod_info.incompatibilities.append(
                        ModIncompatibility(
                            id=incompat["id"],
                            version_range=incompat.get("version_range")
                        )
                    )
            
            # Add to registry
            mod_registry[mod_info.id] = mod_info
            active_mods.add(mod_info.id)
            
            logger.info(f"Loaded mod: {mod_info.name} (ID: {mod_info.id}, Version: {mod_info.version})")
        
        except Exception as e:
            logger.error(f"Error loading mod from {mod_dir}: {str(e)}")

async def detect_conflicts() -> List[ModConflict]:
    """Detect all types of conflicts between mods"""
    conflicts = []
    
    # Check for circular dependencies
    circular_dep_conflicts = await detect_circular_dependencies()
    if circular_dep_conflicts:
        conflicts.extend(circular_dep_conflicts)
        logger.warning(f"Detected {len(circular_dep_conflicts)} circular dependency conflicts")
    
    # Check for missing dependencies
    missing_dep_conflicts = []
    for mod_id, mod_info in mod_registry.items():
        for dep in mod_info.dependencies:
            if dep.required and dep.id not in mod_registry:
                conflict = ModConflict(
                    entity_id=f"dependency/{mod_id}/{dep.id}",
                    conflicting_mods=[mod_id],
                    type=ConflictType.DEPENDENCY_MISSING,
                    description=f"Mod {mod_id} requires dependency {dep.id} which is not installed"
                )
                missing_dep_conflicts.append(conflict)
    
    if missing_dep_conflicts:
        conflicts.extend(missing_dep_conflicts)
        logger.warning(f"Detected {len(missing_dep_conflicts)} missing dependency conflicts")
    
    # Check for incompatible mods
    incompatible_conflicts = []
    for mod_id, mod_info in mod_registry.items():
        for incompat in mod_info.incompatibilities:
            if incompat.id in mod_registry:
                conflict = ModConflict(
                    entity_id=f"incompatibility/{mod_id}/{incompat.id}",
                    conflicting_mods=[mod_id, incompat.id],
                    type=ConflictType.INCOMPATIBLE_MODS,
                    description=f"Mod {mod_id} is incompatible with mod {incompat.id}"
                )
                incompatible_conflicts.append(conflict)
    
    if incompatible_conflicts:
        conflicts.extend(incompatible_conflicts)
        logger.warning(f"Detected {len(incompatible_conflicts)} incompatibility conflicts")
    
    # Check for entity conflicts
    entity_conflicts = await detect_entity_conflicts()
    if entity_conflicts:
        conflicts.extend(entity_conflicts)
        logger.warning(f"Detected {len(entity_conflicts)} entity override conflicts")
    
    return conflicts

async def detect_circular_dependencies() -> List[ModConflict]:
    """Detect circular dependencies in mod loading order"""
    visited = set()
    path = []
    conflicts = []
    
    def dfs_visit(mod_id, path=None):
        if path is None:
            path = []
            
        if mod_id in path:
            # Circular dependency detected
            cycle_path = path[path.index(mod_id):] + [mod_id]
            conflict = ModConflict(
                entity_id=f"circular_dependency/{'_'.join(cycle_path)}",
                conflicting_mods=cycle_path,
                type=ConflictType.CIRCULAR_DEPENDENCY,
                description=f"Circular dependency detected: {' -> '.join(cycle_path)}"
            )
            conflicts.append(conflict)
            return
            
        if mod_id in visited:
            return
            
        visited.add(mod_id)
        path.append(mod_id)
        
        if mod_id in mod_registry:
            for dep in mod_registry[mod_id].dependencies:
                if dep.id in mod_registry:
                    dfs_visit(dep.id, path)
        
        path.pop()
    
    # Check each mod for circular dependencies
    for mod_id in mod_registry:
        if mod_id not in visited:
            dfs_visit(mod_id)
    
    return conflicts

async def detect_entity_conflicts() -> List[ModConflict]:
    """Detect conflicting entity definitions across mods"""
    # Map of entity ID to list of mods that define it
    entity_mods: Dict[str, List[str]] = {}
    conflicts = []
    
    # Scan each mod for entity definitions
    for mod_id, mod_info in mod_registry.items():
        mod_dir = MOD_BASE_DIR / mod_id
        
        # Look for entity definition files (JSON files in entities/ directory)
        entities_dir = mod_dir / "entities"
        if not entities_dir.exists() or not entities_dir.is_dir():
            continue
        
        for entity_file in entities_dir.glob("**/*.json"):
            try:
                # Parse entity definition
                with open(entity_file, "r") as f:
                    entity_data = json.load(f)
                
                # Extract entity ID
                entity_id = entity_data.get("id", entity_file.stem)
                
                # Record which mod defines this entity
                if entity_id not in entity_mods:
                    entity_mods[entity_id] = []
                entity_mods[entity_id].append(mod_id)
            except Exception as e:
                logger.error(f"Error parsing entity file {entity_file}: {str(e)}")
    
    # Find entities defined by multiple mods
    for entity_id, defining_mods in entity_mods.items():
        if len(defining_mods) > 1:
            # Create conflict
            conflict = ModConflict(
                entity_id=f"entity/{entity_id}",
                conflicting_mods=defining_mods,
                type=ConflictType.ENTITY_OVERRIDE,
                description=f"Entity {entity_id} is defined by multiple mods: {', '.join(defining_mods)}"
            )
            conflicts.append(conflict)
    
    return conflicts

async def auto_resolve_conflicts(conflicts: List[ModConflict]) -> List[ModConflict]:
    """Attempt to automatically resolve conflicts"""
    resolved_conflicts = []
    
    for conflict in conflicts:
        if conflict.type == ConflictType.ENTITY_OVERRIDE:
            # Attempt to resolve by load priority
            if await resolve_by_priority(conflict):
                resolved_conflicts.append(conflict)
        elif conflict.type == ConflictType.DEPENDENCY_MISSING:
            # Cannot auto-resolve missing dependencies
            pass
        elif conflict.type == ConflictType.INCOMPATIBLE_MODS:
            # Cannot auto-resolve incompatibilities
            pass
        elif conflict.type == ConflictType.CIRCULAR_DEPENDENCY:
            # Cannot auto-resolve circular dependencies
            pass
    
    return resolved_conflicts

async def resolve_by_priority(conflict: ModConflict) -> bool:
    """Resolve a conflict by using the mod with highest priority"""
    if conflict.type != ConflictType.ENTITY_OVERRIDE:
        return False
    
    # Find mod with highest priority (lowest priority number)
    highest_priority_mod = None
    highest_priority = float('inf')
    
    for mod_id in conflict.conflicting_mods:
        if mod_id in mod_registry:
            priority = mod_registry[mod_id].load_priority
            if priority < highest_priority:
                highest_priority = priority
                highest_priority_mod = mod_id
    
    if not highest_priority_mod:
        return False
    
    # Example: apply the resolution
    # In a real implementation, this would modify the loaded entity data
    logger.info(f"Auto-resolved conflict {conflict.entity_id} by using mod {highest_priority_mod} (priority {highest_priority})")
    
    # Notify connected clients
    await notify_clients({
        "type": "conflict_resolved",
        "entity_id": conflict.entity_id,
        "resolution": "priority",
        "selected_mod": highest_priority_mod
    })
    
    return True

@router.post("/sync/resolve")
async def resolve_conflict(resolution: ConflictResolutionRequest):
    """Manually resolve a conflict"""
    # Find the conflict
    conflict = next((c for c in sync_state.conflicts if c.entity_id == resolution.conflict_id), None)
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    # Apply resolution
    success = False
    if resolution.resolution_strategy == ConflictResolutionStrategy.USE_HIGHEST_PRIORITY:
        if not resolution.mod_to_use:
            raise HTTPException(status_code=400, detail="Must specify mod_to_use for USE_HIGHEST_PRIORITY strategy")
        
        if resolution.mod_to_use not in conflict.conflicting_mods:
            raise HTTPException(status_code=400, detail="Selected mod is not part of the conflict")
        
        # Implementation: prefer the specified mod
        logger.info(f"Resolving conflict {conflict.entity_id} by using mod {resolution.mod_to_use}")
        success = True
    
    elif resolution.resolution_strategy == ConflictResolutionStrategy.MERGE_DATA:
        # Merge data from conflicting mods
        success = await merge_conflicted_data(conflict)
    
    elif resolution.resolution_strategy == ConflictResolutionStrategy.DISABLE_MOD:
        if not resolution.mod_to_use:
            raise HTTPException(status_code=400, detail="Must specify mod_to_use (as the mod to disable) for DISABLE_MOD strategy")
        
        # Disable the specified mod for this conflict
        success = await disable_mod(conflict, resolution.mod_to_use)
    
    elif resolution.resolution_strategy == ConflictResolutionStrategy.IGNORE_CONFLICT:
        # Simply mark as resolved
        logger.info(f"Ignoring conflict {conflict.entity_id}")
        success = True
    
    if success:
        # Remove conflict from the list
        sync_state.conflicts = [c for c in sync_state.conflicts if c.entity_id != conflict.entity_id]
        
        # Notify connected clients
        await notify_clients({
            "type": "conflict_resolved",
            "entity_id": conflict.entity_id,
            "resolution": resolution.resolution_strategy.value,
            "selected_mod": resolution.mod_to_use
        })
        
        return {"status": "Conflict resolved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to resolve conflict")

async def merge_conflicted_data(conflict: ModConflict) -> bool:
    """Merge data from conflicting mods"""
    if conflict.type != ConflictType.ENTITY_OVERRIDE:
        return False
    
    # Extract entity ID
    entity_parts = conflict.entity_id.split("/")
    if len(entity_parts) < 2:
        return False
    
    entity_id = entity_parts[1]
    
    # Load entity data from each conflicting mod
    entity_data = {}
    
    for mod_id in conflict.conflicting_mods:
        mod_dir = MOD_BASE_DIR / mod_id
        entity_paths = list(mod_dir.glob(f"entities/**/{entity_id}.json"))
        
        if not entity_paths:
            continue
        
        try:
            with open(entity_paths[0], "r") as f:
                mod_entity_data = json.load(f)
                
            if not entity_data:
                # First mod's data used as base
                entity_data = mod_entity_data
            else:
                # Merge subsequent mod data
                entity_data = await deep_merge(entity_data, mod_entity_data)
        
        except Exception as e:
            logger.error(f"Error merging entity data from {mod_id}: {str(e)}")
            return False
    
    # Save merged entity data to a conflict resolution directory
    resolution_dir = MOD_BASE_DIR / "_resolved_conflicts"
    os.makedirs(resolution_dir, exist_ok=True)
    
    with open(resolution_dir / f"{entity_id}.json", "w") as f:
        json.dump(entity_data, f, indent=2)
    
    logger.info(f"Merged entity data for {entity_id} from mods: {', '.join(conflict.conflicting_mods)}")
    return True

async def deep_merge(target: dict, source: dict) -> dict:
    """Deep merge two dictionaries, with source values taking precedence"""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            await deep_merge(target[key], value)
        else:
            target[key] = value
    
    return target

async def disable_mod(conflict: ModConflict, mod_to_disable: str) -> bool:
    """Disable a mod for this specific conflict"""
    if mod_to_disable not in conflict.conflicting_mods:
        return False
    
    # Remove mod from active mods for this specific entity/conflict
    logger.info(f"Disabling mod {mod_to_disable} for conflict {conflict.entity_id}")
    
    # In a real implementation, this would update the mod loading configuration
    # For this example, we'll just log it
    
    return True

@router.websocket("/sync/ws")
async def websocket_sync_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time mod synchronization updates"""
    await websocket.accept()
    sync_connections.append(websocket)
    
    try:
        # Send current status on connection
        await websocket.send_json({
            "type": "sync_status",
            "in_progress": sync_state.in_progress,
            "success": sync_state.success,
            "unresolved_conflicts": len(sync_state.conflicts)
        })
        
        # Keep connection open until client disconnects
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            # Process client commands if needed
    
    except WebSocketDisconnect:
        # Remove disconnected clients
        if websocket in sync_connections:
            sync_connections.remove(websocket)

async def notify_clients(message: dict):
    """Send notification to all connected websocket clients"""
    disconnected = []
    
    for connection in sync_connections:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.append(connection)
    
    # Clean up disconnected clients
    for connection in disconnected:
        if connection in sync_connections:
            sync_connections.remove(connection)

@router.get("/optimized-load-order")
async def get_optimized_load_order():
    """Calculate an optimized mod loading order based on dependencies"""
    if not mod_registry:
        return {"load_order": []}
    
    # Topological sort for load order
    visited = set()
    temp_marks = set()  # For cycle detection
    order = []
    
    async def visit(mod_id):
        if mod_id in temp_marks:
            # Cycle detected
            return False
        
        if mod_id in visited or mod_id not in mod_registry:
            return True
        
        temp_marks.add(mod_id)
        
        # Process dependencies first
        for dep in mod_registry[mod_id].dependencies:
            if dep.id in mod_registry:
                success = await visit(dep.id)
                if not success:
                    return False
        
        # Mark as visited and add to order
        temp_marks.remove(mod_id)
        visited.add(mod_id)
        order.append({
            "id": mod_id,
            "name": mod_registry[mod_id].name,
            "priority": mod_registry[mod_id].load_priority
        })
        return True
    
    # Process each mod
    for mod_id in mod_registry:
        if mod_id not in visited:
            success = await visit(mod_id)
            if not success:
                return {"error": "Circular dependency detected", "partial_order": order}
    
    # Sort by load priority within topological constraints
    # (This is a simplified approach; a real implementation would need to respect
    # the topological ordering while adjusting for priority)
    priority_groups = {}
    for mod in order:
        priority = mod["priority"]
        if priority not in priority_groups:
            priority_groups[priority] = []
        priority_groups[priority].append(mod)
    
    # Rebuild order by priority
    final_order = []
    for priority in sorted(priority_groups.keys()):
        final_order.extend(priority_groups[priority])
    
    return {"load_order": final_order}

@router.get("/conflict-report")
async def generate_conflict_report():
    """Generate a detailed report of all detected mod conflicts"""
    if not sync_state.conflicts:
        return {"message": "No conflicts detected", "conflicts": []}
    
    # Group conflicts by type
    conflicts_by_type = {}
    for conflict in sync_state.conflicts:
        if conflict.type not in conflicts_by_type:
            conflicts_by_type[conflict.type] = []
        
        # Build detailed conflict info
        conflict_info = {
            "id": conflict.entity_id,
            "description": conflict.description,
            "mods": []
        }
        
        for mod_id in conflict.conflicting_mods:
            if mod_id in mod_registry:
                mod_info = mod_registry[mod_id]
                conflict_info["mods"].append({
                    "id": mod_id,
                    "name": mod_info.name,
                    "version": mod_info.version,
                    "priority": mod_info.load_priority
                })
            else:
                conflict_info["mods"].append({
                    "id": mod_id,
                    "name": mod_id,
                    "version": "unknown",
                    "priority": 999
                })
        
        conflicts_by_type[conflict.type].append(conflict_info)
    
    # Build final report
    report = {
        "total_conflicts": len(sync_state.conflicts),
        "types": [t.value for t in conflicts_by_type.keys()],
        "conflicts_by_type": {t.value: conflicts for t, conflicts in conflicts_by_type.items()}
    }
    
    return report 