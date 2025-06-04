"""
World State Services - Business Logic Layer

Provides comprehensive business logic services for world state management
with temporal versioning, regional state tracking, and historical reconstruction
following the Development Bible requirements.
"""

import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple, Callable
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import logging

from backend.systems.world_state.manager import (
    WorldStateManager, 
    RegionalSnapshot, 
    HistoricalSummary,
    SnapshotLevel
)
from backend.systems.world_state.repositories import JSONFileWorldStateRepository
from backend.systems.world_state.world_types import (
    WorldState,
    StateCategory,
    WorldRegion,
    StateChangeType,
    WorldStateChange
)

logger = logging.getLogger(__name__)


class WorldStateService:
    """
    High-level business logic service for world state operations.
    Provides a facade over the WorldStateManager with additional business rules.
    """
    
    def __init__(self, repository_path: Optional[str] = None):
        self.repository = JSONFileWorldStateRepository(
            repository_path or "data/systems/world_state"
        )
        self.manager: Optional[WorldStateManager] = None
        self._initialized = False
        self._event_listeners: Dict[str, List[Callable]] = {}
    
    async def initialize(self) -> bool:
        """Initialize the service and world state manager"""
        try:
            self.manager = await WorldStateManager.get_instance(self.repository)
            
            # Load existing state if available
            if await self.manager.load_from_repository():
                logger.info("Loaded existing world state from repository")
            else:
                logger.info("No existing world state found, starting fresh")
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WorldStateService: {e}")
            return False
    
    def _ensure_initialized(self):
        """Ensure service is initialized"""
        if not self._initialized or not self.manager:
            raise RuntimeError("WorldStateService not initialized. Call initialize() first.")
    
    # ===== CORE STATE OPERATIONS =====
    
    async def get_state_variable(
        self, 
        key: str, 
        region_id: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """Get a state variable value"""
        self._ensure_initialized()
        return await self.manager.get_state(key, region_id, default)
    
    async def set_state_variable(
        self,
        key: str,
        value: Any,
        region_id: Optional[str] = None,
        category: StateCategory = StateCategory.OTHER,
        reason: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """Set a state variable with business validation"""
        self._ensure_initialized()
        
        try:
            # Business validation
            if not self._validate_state_change(key, value, category):
                return False
            
            # Get old value for change event
            old_value = await self.manager.get_state(key, region_id, None)
            
            # Add user tracking to reason
            if user_id:
                reason = f"{reason or 'User action'} (by {user_id})"
            
            await self.manager.set_state(key, value, region_id, category, reason)
            
            # Emit state change event for WebSocket and integration
            await self._emit_state_changed(key, old_value, value, region_id, category, reason)
            
            # Auto-save if significant change
            if category in [StateCategory.POLITICAL, StateCategory.MILITARY, StateCategory.QUEST]:
                await self.save_state()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set state variable {key}: {e}")
            return False
    
    async def query_state(
        self, 
        category: Optional[StateCategory] = None,
        region_id: Optional[str] = None,
        key_pattern: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Query state variables with filtering"""
        self._ensure_initialized()
        
        query = {}
        if category:
            query['category'] = category
        if key_pattern:
            query['key_pattern'] = key_pattern
        if time_range:
            query['time_range'] = time_range
        
        return await self.manager.query_state(query, region_id)
    
    def _validate_state_change(self, key: str, value: Any, category: StateCategory) -> bool:
        """Validate state changes according to business rules"""
        # Business rule: Population cannot be negative
        if 'population' in key.lower() and isinstance(value, (int, float)) and value < 0:
            logger.error(f"Population values cannot be negative: {key} = {value}")
            return False
        
        # Business rule: Resources have upper limits
        if 'resource' in key.lower() and isinstance(value, (int, float)) and value > 1000000:
            logger.warning(f"Resource value very high, may indicate error: {key} = {value}")
        
        # Business rule: Certain keys require specific categories
        if key.startswith('faction.') and category != StateCategory.POLITICAL:
            logger.warning(f"Faction-related key should use POLITICAL category: {key}")
        
        return True
    
    async def _emit_state_changed(
        self, 
        key: str, 
        old_value: Any, 
        new_value: Any, 
        region_id: Optional[str], 
        category: StateCategory,
        reason: Optional[str]
    ):
        """Emit state change event to listeners"""
        event_data = {
            'key': key,
            'old_value': old_value,
            'new_value': new_value,
            'region_id': region_id,
            'category': category,
            'reason': reason,
            'timestamp': datetime.utcnow()
        }
        
        # Notify all listeners for 'state_changed' events
        listeners = self._event_listeners.get('state_changed', [])
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event_data)
                else:
                    listener(event_data)
            except Exception as e:
                logger.error(f"Error in state change listener: {e}")
    
    # ===== REGIONAL STATE MANAGEMENT =====
    
    async def create_region(
        self,
        region_id: str,
        initial_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a new region with initial state"""
        self._ensure_initialized()
        
        try:
            # Set initial regional state
            if initial_state:
                for key, value in initial_state.items():
                    await self.set_state_variable(
                        key, value, region_id, 
                        reason=f"Initial state for region {region_id}"
                    )
            
            # Create initial snapshot
            snapshot = await self.manager.create_snapshot(
                region_id, 
                metadata={"type": "region_creation", **(metadata or {})}
            )
            
            logger.info(f"Created region {region_id} with snapshot {snapshot.snapshot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create region {region_id}: {e}")
            return False
    
    async def get_region_state(self, region_id: str) -> Dict[str, Any]:
        """Get complete state for a region"""
        self._ensure_initialized()
        return await self.query_state(region_id=region_id)
    
    async def update_region_state(
        self,
        region_id: str,
        updates: Dict[str, Any],
        reason: Optional[str] = None,
        create_snapshot: bool = False
    ) -> bool:
        """Update multiple state variables for a region"""
        self._ensure_initialized()
        
        try:
            for key, value in updates.items():
                await self.set_state_variable(
                    key, value, region_id,
                    reason=reason or f"Bulk update for {region_id}"
                )
            
            if create_snapshot:
                await self.create_region_snapshot(region_id, {
                    "type": "bulk_update",
                    "update_count": len(updates)
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update region {region_id}: {e}")
            return False
    
    # ===== SNAPSHOT MANAGEMENT =====
    
    async def create_region_snapshot(
        self,
        region_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a snapshot of the current region state"""
        self._ensure_initialized()
        
        try:
            snapshot = await self.manager.create_snapshot(region_id, metadata)
            return snapshot.snapshot_id
        except Exception as e:
            logger.error(f"Failed to create snapshot for region {region_id}: {e}")
            return None
    
    async def list_region_snapshots(
        self,
        region_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List snapshots for a region"""
        self._ensure_initialized()
        
        try:
            snapshots = await self.manager.list_snapshots(
                region_id, start_time, end_time, limit
            )
            
            # Convert snapshots to dict format
            result = []
            for snapshot in snapshots:
                result.append({
                    'snapshot_id': snapshot.snapshot_id,
                    'timestamp': snapshot.timestamp,
                    'region_id': snapshot.region_id,
                    'state_hash': snapshot.state_hash,
                    'metadata': snapshot.metadata,
                    'data_size': len(str(snapshot.state_data))
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list snapshots for region {region_id}: {e}")
            return []
    
    async def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific snapshot by ID"""
        self._ensure_initialized()
        
        try:
            snapshot = await self.manager.get_snapshot(snapshot_id)
            if not snapshot:
                return None
            
            return {
                'snapshot_id': snapshot.snapshot_id,
                'timestamp': snapshot.timestamp,
                'region_id': snapshot.region_id,
                'state_hash': snapshot.state_hash,
                'metadata': snapshot.metadata,
                'state_data': snapshot.state_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get snapshot {snapshot_id}: {e}")
            return None
    
    async def rollback_region(
        self,
        region_id: str,
        snapshot_id: str,
        create_backup: bool = True
    ) -> bool:
        """Rollback a region to a previous snapshot"""
        self._ensure_initialized()
        
        try:
            if create_backup:
                await self.create_region_snapshot(region_id, {
                    "type": "pre_rollback_backup",
                    "rollback_target": snapshot_id
                })
            
            success = await self.manager.rollback_region(region_id, snapshot_id)
            
            if success:
                logger.info(f"Successfully rolled back region {region_id} to snapshot {snapshot_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rollback region {region_id} to snapshot {snapshot_id}: {e}")
            return False
    
    # ===== HISTORICAL OPERATIONS =====
    
    async def get_historical_state(
        self,
        region_id: str,
        timestamp: datetime,
        include_global: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get historical state at a specific timestamp"""
        self._ensure_initialized()
        
        try:
            state_data = await self.manager.get_historical_state(
                region_id, timestamp, include_global
            )
            return state_data
            
        except Exception as e:
            logger.error(f"Failed to get historical state for {region_id} at {timestamp}: {e}")
            return None
    
    async def force_summarization(self, level: Optional[SnapshotLevel] = None) -> Dict[str, int]:
        """Force creation of historical summaries"""
        self._ensure_initialized()
        
        try:
            summary_stats = await self.manager.force_summarization(level)
            logger.info(f"Summarization completed: {summary_stats}")
            return summary_stats
            
        except Exception as e:
            logger.error(f"Failed to force summarization: {e}")
            return {"error": str(e)}
    
    async def get_historical_summary(
        self,
        start_time: datetime,
        end_time: datetime,
        region_id: Optional[str] = None,
        period_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get historical summaries for a time period"""
        self._ensure_initialized()
        
        try:
            # Map period_type to SnapshotLevel
            level = None
            if period_type:
                level_map = {
                    'hour': SnapshotLevel.HOURLY,
                    'day': SnapshotLevel.DAILY,
                    'week': SnapshotLevel.WEEKLY,
                    'month': SnapshotLevel.MONTHLY
                }
                level = level_map.get(period_type.lower(), SnapshotLevel.DAILY)
            
            summaries = await self.manager.get_historical_summaries(
                start_time, end_time, region_id, level
            )
            
            # Convert to dict format
            result = []
            for summary in summaries:
                result.append({
                    'summary_id': summary.summary_id,
                    'level': summary.level.value,
                    'start_time': summary.start_time,
                    'end_time': summary.end_time,
                    'region_id': summary.region_id,
                    'snapshot_count': summary.snapshot_count,
                    'key_changes': summary.key_changes,
                    'summary_data': summary.summary_data
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get historical summary: {e}")
            return []
    
    # ===== EVENT RECORDING =====
    
    async def record_world_event(
        self,
        event_type: str,
        description: str,
        affected_regions: Optional[List[str]] = None,
        category: StateCategory = StateCategory.OTHER,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record a world event"""
        self._ensure_initialized()
        
        try:
            event_id = str(uuid4())
            
            # Store event data in state variables
            event_key = f"events.{event_id}"
            event_data = {
                "id": event_id,
                "event_type": event_type,
                "description": description,
                "timestamp": datetime.utcnow().isoformat(),
                "affected_regions": affected_regions or [],
                "category": category.value,
                "metadata": metadata or {}
            }
            
            await self.set_state_variable(
                event_key, event_data,
                category=category,
                reason=f"Recorded world event: {event_type}"
            )
            
            # Update recent events list
            recent_events = await self.get_state_variable("events.recent", default=[])
            if not isinstance(recent_events, list):
                recent_events = []
            
            recent_events.insert(0, event_data)
            # Keep only last 100 recent events
            recent_events = recent_events[:100]
            
            await self.set_state_variable(
                "events.recent", recent_events,
                category=StateCategory.OTHER,
                reason="Updated recent events list"
            )
            
            logger.info(f"Recorded world event {event_id}: {event_type}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to record world event: {e}")
            return ""
    
    # ===== EVENT SUBSCRIPTION =====
    
    async def subscribe_to_state_changes(
        self,
        callback: Callable,
        event_type: str = 'state_changed'
    ) -> bool:
        """Subscribe to state change events"""
        try:
            if event_type not in self._event_listeners:
                self._event_listeners[event_type] = []
            
            self._event_listeners[event_type].append(callback)
            logger.info(f"Added listener for {event_type} events")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to {event_type} events: {e}")
            return False
    
    async def unsubscribe_from_state_changes(
        self,
        callback: Callable,
        event_type: str = 'state_changed'
    ) -> bool:
        """Unsubscribe from state change events"""
        try:
            if event_type in self._event_listeners:
                if callback in self._event_listeners[event_type]:
                    self._event_listeners[event_type].remove(callback)
                    logger.info(f"Removed listener for {event_type} events")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {event_type} events: {e}")
            return False
    
    # ===== SYSTEM OPERATIONS =====
    
    async def save_state(self) -> bool:
        """Save current state to repository"""
        self._ensure_initialized()
        return await self.manager.save_to_repository()
    
    async def process_tick(self) -> Dict[str, Any]:
        """Process a game tick and return statistics"""
        self._ensure_initialized()
        
        try:
            tick_start = datetime.utcnow()
            
            # Update game time
            current_day = await self.get_state_variable("time.game_day", 1)
            await self.set_state_variable(
                "time.game_day", current_day + 1,
                category=StateCategory.OTHER,
                reason="Daily tick progression"
            )
            
            # Update last tick timestamp
            await self.set_state_variable(
                "time.last_tick", tick_start.isoformat(),
                category=StateCategory.OTHER,
                reason="Tick timestamp update"
            )
            
            # Force save after tick
            await self.save_state()
            
            tick_duration = (datetime.utcnow() - tick_start).total_seconds()
            
            return {
                "tick_start": tick_start.isoformat(),
                "duration_seconds": tick_duration,
                "changes_applied": 2,  # game_day and last_tick
                "events_generated": 0,
                "game_day": current_day + 1
            }
            
        except Exception as e:
            logger.error(f"Failed to process tick: {e}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        try:
            status = {
                "initialized": self._initialized,
                "manager_available": self.manager is not None,
                "repository_path": str(self.repository.base_path),
                "current_time": datetime.utcnow().isoformat()
            }
            
            if self._initialized and self.manager:
                status.update({
                    "total_regions": len(await self.manager.list_regions()),
                    "snapshot_count": await self._count_total_snapshots(),
                    "last_save": await self.get_state_variable("system.last_save"),
                    "event_listeners": len(self._event_listeners.get('state_changed', []))
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e), "initialized": False}
    
    async def _count_total_snapshots(self) -> int:
        """Count total snapshots across all regions"""
        try:
            regions = await self.manager.list_regions()
            total = 0
            for region_id in regions:
                snapshots = await self.list_region_snapshots(region_id, limit=1000)
                total += len(snapshots)
            return total
        except Exception:
            return 0
    
    async def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, int]:
        """Clean up old historical data"""
        self._ensure_initialized()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            cleanup_stats = await self.manager.cleanup_old_data(cutoff_date)
            
            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return {"error": str(e)}
    
    async def export_region_history(
        self,
        region_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Export region history for analysis or backup"""
        self._ensure_initialized()
        
        try:
            # Get snapshots
            snapshots = await self.list_region_snapshots(
                region_id, start_time, end_time
            )
            
            # Get historical summaries
            if start_time and end_time:
                summaries = await self.get_historical_summary(
                    start_time, end_time, region_id
                )
            else:
                summaries = []
            
            # Get current state
            current_state = await self.get_region_state(region_id)
            
            export_data = {
                "export_metadata": {
                    "region_id": region_id,
                    "export_time": datetime.utcnow().isoformat(),
                    "start_time": start_time.isoformat() if start_time else None,
                    "end_time": end_time.isoformat() if end_time else None,
                    "snapshot_count": len(snapshots),
                    "summary_count": len(summaries)
                },
                "current_state": current_state,
                "snapshots": snapshots,
                "historical_summaries": summaries
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export region history for {region_id}: {e}")
            return {"error": str(e)}


async def create_world_state_service(repository_path: Optional[str] = None) -> WorldStateService:
    """Factory function to create and initialize a world state service"""
    service = WorldStateService(repository_path)
    await service.initialize()
    return service


# Export the service class
__all__ = ["WorldStateService", "create_world_state_service"]
