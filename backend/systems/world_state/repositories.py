"""
World State Repositories - Data Persistence Layer

Implements the repository pattern for world state data with JSON schema validation
and hierarchical storage following the Development Bible requirements.
"""

import json
import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import logging

from backend.systems.world_state.manager import WorldStateRepository, RegionalSnapshot, HistoricalSummary
from backend.systems.world_state.world_types import WorldState, WorldStateChange

logger = logging.getLogger(__name__)


class JSONFileWorldStateRepository(WorldStateRepository):
    """
    JSON file-based implementation of WorldStateRepository with schema validation.
    Follows hierarchical storage structure and implements all temporal versioning features.
    """
    
    def __init__(self, base_path: str = "data/systems/world_state"):
        self.base_path = Path(base_path)
        self.schemas_path = self.base_path / "schemas"
        self.snapshots_path = self.base_path / "snapshots"
        self.summaries_path = self.base_path / "summaries"
        self.state_file = self.base_path / "current_state.json"
        self.changes_file = self.base_path / "changes.json"
        
        # Create directory structure
        self._ensure_directories()
        
        # Load schemas for validation
        self.schemas = self._load_schemas()
        
        # File locks for thread safety
        self._file_locks = {}
    
    def _ensure_directories(self):
        """Create necessary directory structure"""
        for path in [self.base_path, self.schemas_path, self.snapshots_path, self.summaries_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_lock(self, file_path: str) -> asyncio.Lock:
        """Get or create a file-specific lock"""
        if file_path not in self._file_locks:
            self._file_locks[file_path] = asyncio.Lock()
        return self._file_locks[file_path]
    
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load JSON schemas for validation"""
        schemas = {}
        
        # Default schemas if files don't exist
        default_schemas = {
            "world_state": {
                "type": "object",
                "required": ["id", "name", "created_at", "updated_at"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"},
                    "current_time": {"type": "string", "format": "date-time"},
                    "game_day": {"type": "integer", "minimum": 1},
                    "season": {"type": "string", "enum": ["spring", "summer", "autumn", "winter"]},
                    "year": {"type": "integer", "minimum": 1},
                    "state_variables": {"type": "object"},
                    "regions": {"type": "object"},
                    "global_resources": {"type": "object"},
                    "regional_resources": {"type": "object"},
                    "faction_relations": {"type": "object"},
                    "territorial_control": {"type": "object"},
                    "active_effects": {"type": "array"},
                    "recent_events": {"type": "array"},
                    "change_history": {"type": "array"},
                    "weather": {"type": "object"},
                    "environmental_conditions": {"type": "object"},
                    "metadata": {"type": "object"}
                }
            },
            "regional_snapshot": {
                "type": "object",
                "required": ["region_id", "timestamp", "local_state", "global_context", "snapshot_id"],
                "properties": {
                    "region_id": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "local_state": {"type": "object"},
                    "global_context": {"type": "object"},
                    "snapshot_id": {"type": "string"},
                    "metadata": {"type": "object"}
                }
            },
            "historical_summary": {
                "type": "object",
                "required": ["summary_id", "period_start", "period_end", "period_type", "regions_affected"],
                "properties": {
                    "summary_id": {"type": "string"},
                    "period_start": {"type": "string", "format": "date-time"},
                    "period_end": {"type": "string", "format": "date-time"},
                    "period_type": {"type": "string", "enum": ["daily", "weekly", "monthly", "quarterly", "yearly"]},
                    "regions_affected": {"type": "array", "items": {"type": "string"}},
                    "summary_text": {"type": "string"},
                    "key_changes": {"type": "array"},
                    "original_change_count": {"type": "integer", "minimum": 0},
                    "compression_ratio": {"type": "number", "minimum": 0, "maximum": 1},
                    "metadata": {"type": "object"}
                }
            },
            "world_state_change": {
                "type": "object",
                "required": ["id", "timestamp", "change_type", "state_key", "new_value"],
                "properties": {
                    "id": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "change_type": {"type": "string", "enum": ["created", "updated", "deleted", "merged", "calculated"]},
                    "state_key": {"type": "string"},
                    "old_value": {},
                    "new_value": {},
                    "region": {"type": "string"},
                    "category": {"type": "string"},
                    "entity_id": {"type": ["string", "null"]},
                    "reason": {"type": ["string", "null"]},
                    "custom_data": {"type": ["object", "null"]}
                }
            }
        }
        
        # Load from files or use defaults
        for schema_name, default_schema in default_schemas.items():
            schema_file = self.schemas_path / f"{schema_name}.json"
            if schema_file.exists():
                try:
                    with open(schema_file, 'r') as f:
                        schemas[schema_name] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load schema {schema_name}: {e}. Using default.")
                    schemas[schema_name] = default_schema
                    # Save default schema
                    self._save_schema(schema_name, default_schema)
            else:
                schemas[schema_name] = default_schema
                # Save default schema
                self._save_schema(schema_name, default_schema)
        
        return schemas
    
    def _save_schema(self, schema_name: str, schema: Dict):
        """Save a schema to file"""
        schema_file = self.schemas_path / f"{schema_name}.json"
        try:
            with open(schema_file, 'w') as f:
                json.dump(schema, f, indent=2)
            logger.info(f"Saved schema {schema_name}")
        except Exception as e:
            logger.error(f"Failed to save schema {schema_name}: {e}")
    
    def _validate_data(self, data: Dict, schema_name: str) -> bool:
        """Validate data against JSON schema"""
        try:
            # Simple validation - in production, use jsonschema library
            schema = self.schemas.get(schema_name, {})
            required_fields = schema.get('required', [])
            
            # Check required fields
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing required field '{field}' in {schema_name}")
                    return False
            
            # Basic type checking for critical fields
            properties = schema.get('properties', {})
            for field, value in data.items():
                if field in properties:
                    field_schema = properties[field]
                    expected_type = field_schema.get('type')
                    
                    if expected_type == 'string' and not isinstance(value, str):
                        if value is not None:  # Allow null for nullable fields
                            logger.error(f"Field '{field}' should be string, got {type(value)}")
                            return False
                    elif expected_type == 'integer' and not isinstance(value, int):
                        if value is not None:
                            logger.error(f"Field '{field}' should be integer, got {type(value)}")
                            return False
                    elif expected_type == 'object' and not isinstance(value, dict):
                        if value is not None:
                            logger.error(f"Field '{field}' should be object, got {type(value)}")
                            return False
                    elif expected_type == 'array' and not isinstance(value, list):
                        if value is not None:
                            logger.error(f"Field '{field}' should be array, got {type(value)}")
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Schema validation error for {schema_name}: {e}")
            return False
    
    async def save_state(self, state: WorldState) -> bool:
        """Save complete world state with schema validation"""
        lock = self._get_file_lock(str(self.state_file))
        async with lock:
            try:
                # Convert to dict for serialization
                state_dict = state.dict()
                
                # Validate against schema
                if not self._validate_data(state_dict, 'world_state'):
                    logger.error("World state failed schema validation")
                    return False
                
                # Create backup of existing state
                if self.state_file.exists():
                    backup_file = self.state_file.with_suffix('.json.backup')
                    self.state_file.rename(backup_file)
                
                # Save new state
                with open(self.state_file, 'w') as f:
                    json.dump(state_dict, f, indent=2, default=str)
                
                logger.info("World state saved successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to save world state: {e}")
                # Restore backup if save failed
                backup_file = self.state_file.with_suffix('.json.backup')
                if backup_file.exists():
                    backup_file.rename(self.state_file)
                return False
    
    async def load_state(self) -> Optional[WorldState]:
        """Load current world state"""
        lock = self._get_file_lock(str(self.state_file))
        async with lock:
            try:
                if not self.state_file.exists():
                    logger.info("No existing world state file found")
                    return None
                
                with open(self.state_file, 'r') as f:
                    state_dict = json.load(f)
                
                # Validate loaded data
                if not self._validate_data(state_dict, 'world_state'):
                    logger.error("Loaded world state failed schema validation")
                    return None
                
                # Convert datetime strings back to datetime objects
                for date_field in ['created_at', 'updated_at', 'current_time']:
                    if date_field in state_dict and isinstance(state_dict[date_field], str):
                        state_dict[date_field] = datetime.fromisoformat(state_dict[date_field])
                
                # Convert change history
                if 'change_history' in state_dict:
                    for change in state_dict['change_history']:
                        if 'timestamp' in change and isinstance(change['timestamp'], str):
                            change['timestamp'] = datetime.fromisoformat(change['timestamp'])
                
                state = WorldState(**state_dict)
                logger.info("World state loaded successfully")
                return state
                
            except Exception as e:
                logger.error(f"Failed to load world state: {e}")
                return None
    
    async def save_snapshot(self, snapshot: RegionalSnapshot) -> bool:
        """Save a regional snapshot"""
        try:
            # Create region-specific directory
            region_dir = self.snapshots_path / snapshot.region_id
            region_dir.mkdir(exist_ok=True)
            
            # Create filename with timestamp
            timestamp_str = snapshot.timestamp.strftime('%Y%m%d_%H%M%S')
            filename = f"snapshot_{timestamp_str}_{snapshot.snapshot_id}.json"
            file_path = region_dir / filename
            
            # Convert to dict
            snapshot_dict = {
                'region_id': snapshot.region_id,
                'timestamp': snapshot.timestamp.isoformat(),
                'local_state': snapshot.local_state,
                'global_context': snapshot.global_context,
                'snapshot_id': snapshot.snapshot_id,
                'metadata': snapshot.metadata
            }
            
            # Validate against schema
            if not self._validate_data(snapshot_dict, 'regional_snapshot'):
                logger.error(f"Snapshot {snapshot.snapshot_id} failed schema validation")
                return False
            
            lock = self._get_file_lock(str(file_path))
            async with lock:
                with open(file_path, 'w') as f:
                    json.dump(snapshot_dict, f, indent=2, default=str)
            
            logger.info(f"Snapshot saved: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save snapshot {snapshot.snapshot_id}: {e}")
            return False
    
    async def load_snapshots(
        self, 
        region_id: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[RegionalSnapshot]:
        """Load snapshots for a region within a time range"""
        try:
            region_dir = self.snapshots_path / region_id
            if not region_dir.exists():
                return []
            
            snapshots = []
            for file_path in region_dir.glob("snapshot_*.json"):
                try:
                    with open(file_path, 'r') as f:
                        snapshot_dict = json.load(f)
                    
                    # Convert timestamp
                    timestamp = datetime.fromisoformat(snapshot_dict['timestamp'])
                    
                    # Check if in time range
                    if start_time <= timestamp <= end_time:
                        snapshot = RegionalSnapshot(
                            region_id=snapshot_dict['region_id'],
                            timestamp=timestamp,
                            local_state=snapshot_dict['local_state'],
                            global_context=snapshot_dict['global_context'],
                            snapshot_id=snapshot_dict['snapshot_id'],
                            metadata=snapshot_dict['metadata']
                        )
                        snapshots.append(snapshot)
                        
                except Exception as e:
                    logger.warning(f"Failed to load snapshot from {file_path}: {e}")
                    continue
            
            # Sort by timestamp
            snapshots.sort(key=lambda s: s.timestamp)
            return snapshots
            
        except Exception as e:
            logger.error(f"Failed to load snapshots for region {region_id}: {e}")
            return []
    
    async def save_summary(self, summary: HistoricalSummary) -> bool:
        """Save a historical summary"""
        try:
            # Create period-specific directory
            period_dir = self.summaries_path / summary.period_type
            period_dir.mkdir(exist_ok=True)
            
            # Create filename with period dates
            start_str = summary.period_start.strftime('%Y%m%d')
            end_str = summary.period_end.strftime('%Y%m%d')
            filename = f"summary_{start_str}_{end_str}_{summary.summary_id}.json"
            file_path = period_dir / filename
            
            # Convert to dict
            summary_dict = {
                'summary_id': summary.summary_id,
                'period_start': summary.period_start.isoformat(),
                'period_end': summary.period_end.isoformat(),
                'period_type': summary.period_type,
                'regions_affected': summary.regions_affected,
                'summary_text': summary.summary_text,
                'key_changes': summary.key_changes,
                'original_change_count': summary.original_change_count,
                'compression_ratio': summary.compression_ratio,
                'metadata': summary.metadata
            }
            
            # Validate against schema
            if not self._validate_data(summary_dict, 'historical_summary'):
                logger.error(f"Summary {summary.summary_id} failed schema validation")
                return False
            
            lock = self._get_file_lock(str(file_path))
            async with lock:
                with open(file_path, 'w') as f:
                    json.dump(summary_dict, f, indent=2, default=str)
            
            logger.info(f"Summary saved: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save summary {summary.summary_id}: {e}")
            return False
    
    async def load_summaries(
        self, 
        period_type: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[HistoricalSummary]:
        """Load historical summaries"""
        try:
            period_dir = self.summaries_path / period_type
            if not period_dir.exists():
                return []
            
            summaries = []
            for file_path in period_dir.glob("summary_*.json"):
                try:
                    with open(file_path, 'r') as f:
                        summary_dict = json.load(f)
                    
                    # Convert timestamps
                    period_start = datetime.fromisoformat(summary_dict['period_start'])
                    period_end = datetime.fromisoformat(summary_dict['period_end'])
                    
                    # Check if overlaps with requested time range
                    if (period_start <= end_time and period_end >= start_time):
                        summary = HistoricalSummary(
                            summary_id=summary_dict['summary_id'],
                            period_start=period_start,
                            period_end=period_end,
                            period_type=summary_dict['period_type'],
                            regions_affected=summary_dict['regions_affected'],
                            summary_text=summary_dict['summary_text'],
                            key_changes=summary_dict['key_changes'],
                            original_change_count=summary_dict['original_change_count'],
                            compression_ratio=summary_dict['compression_ratio'],
                            metadata=summary_dict['metadata']
                        )
                        summaries.append(summary)
                        
                except Exception as e:
                    logger.warning(f"Failed to load summary from {file_path}: {e}")
                    continue
            
            # Sort by period start
            summaries.sort(key=lambda s: s.period_start)
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to load summaries for period {period_type}: {e}")
            return []
    
    async def delete_changes_before(self, timestamp: datetime) -> int:
        """Delete change records before timestamp"""
        try:
            if not self.changes_file.exists():
                return 0
            
            lock = self._get_file_lock(str(self.changes_file))
            async with lock:
                # Load existing changes
                with open(self.changes_file, 'r') as f:
                    changes = json.load(f)
                
                # Filter out old changes
                initial_count = len(changes)
                filtered_changes = []
                
                for change in changes:
                    change_time = datetime.fromisoformat(change['timestamp'])
                    if change_time >= timestamp:
                        filtered_changes.append(change)
                
                # Save filtered changes
                with open(self.changes_file, 'w') as f:
                    json.dump(filtered_changes, f, indent=2, default=str)
                
                deleted_count = initial_count - len(filtered_changes)
                logger.info(f"Deleted {deleted_count} old change records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to delete old changes: {e}")
            return 0
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get information about available schemas"""
        return {
            'schemas': list(self.schemas.keys()),
            'schema_path': str(self.schemas_path),
            'version': '1.0.0'
        }
    
    async def update_schema(self, schema_name: str, new_schema: Dict) -> bool:
        """Update a schema (for schema evolution)"""
        try:
            # Validate the new schema is well-formed
            if 'type' not in new_schema:
                logger.error("Schema must have a 'type' field")
                return False
            
            # Save the new schema
            self._save_schema(schema_name, new_schema)
            
            # Update in-memory schemas
            self.schemas[schema_name] = new_schema
            
            logger.info(f"Schema {schema_name} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update schema {schema_name}: {e}")
            return False


# Export the repository class
__all__ = ["JSONFileWorldStateRepository"] 