"""
World State Manager - Business Logic Interface

Provides a comprehensive business logic interface for world state management
with temporal versioning, regional historical reconstruction, and hierarchical
batch summarization following the Development Bible requirements.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict
from uuid import uuid4
import logging

from backend.systems.world_state.world_types import (
    StateChangeType,
    WorldRegion,
    StateCategory,
    WorldStateChange,
    WorldState
)

logger = logging.getLogger(__name__)


@dataclass
class RegionalSnapshot:
    """Snapshot of world state for a specific region at a point in time"""
    region_id: str
    timestamp: datetime
    local_state: Dict[str, Any]
    global_context: Dict[str, Any]  # Important global state at this time
    snapshot_id: str
    metadata: Dict[str, Any]


@dataclass
class HistoricalSummary:
    """Summary of historical changes over a time period"""
    summary_id: str
    period_start: datetime
    period_end: datetime
    period_type: str  # 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    regions_affected: List[str]
    summary_text: str
    key_changes: List[Dict[str, Any]]
    original_change_count: int
    compression_ratio: float
    metadata: Dict[str, Any]


class SnapshotLevel(Enum):
    """Hierarchical levels for historical data retention"""
    HOURLY = "hourly"
    DAILY = "daily" 
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class WorldStateRepository:
    """Protocol for world state data persistence"""
    
    async def save_state(self, state: WorldState) -> bool:
        """Save complete world state"""
        raise NotImplementedError
    
    async def load_state(self) -> Optional[WorldState]:
        """Load current world state"""
        raise NotImplementedError
    
    async def save_snapshot(self, snapshot: RegionalSnapshot) -> bool:
        """Save a regional snapshot"""
        raise NotImplementedError
    
    async def load_snapshots(self, region_id: str, start_time: datetime, end_time: datetime) -> List[RegionalSnapshot]:
        """Load snapshots for a region within a time range"""
        raise NotImplementedError
    
    async def save_summary(self, summary: HistoricalSummary) -> bool:
        """Save a historical summary"""
        raise NotImplementedError
    
    async def load_summaries(self, period_type: str, start_time: datetime, end_time: datetime) -> List[HistoricalSummary]:
        """Load historical summaries"""
        raise NotImplementedError
    
    async def delete_changes_before(self, timestamp: datetime) -> int:
        """Delete change records before timestamp"""
        raise NotImplementedError


class WorldStateManager:
    """
    Comprehensive world state manager with temporal versioning, regional history,
    thread safety, and hierarchical batch summarization.
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __init__(self, repository: Optional[WorldStateRepository] = None):
        if WorldStateManager._instance is not None:
            raise Exception("WorldStateManager is a singleton. Use get_instance()")
        
        self.repository = repository
        self.current_state = WorldState()
        
        # Thread safety
        self._read_write_lock = asyncio.RWLock() if hasattr(asyncio, 'RWLock') else asyncio.Lock()
        self._snapshot_lock = asyncio.Lock()
        
        # Regional state tracking
        self.regional_states: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.regional_snapshots: Dict[str, List[RegionalSnapshot]] = defaultdict(list)
        
        # Historical summarization configuration
        self.summarization_schedule = {
            SnapshotLevel.DAILY: {'frequency_days': 1, 'retention_days': 7},
            SnapshotLevel.WEEKLY: {'frequency_days': 7, 'retention_days': 28},
            SnapshotLevel.MONTHLY: {'frequency_days': 28, 'retention_days': 90},
            SnapshotLevel.QUARTERLY: {'frequency_days': 90, 'retention_days': 365},
            SnapshotLevel.YEARLY: {'frequency_days': 365, 'retention_days': 730}
        }
        
        # Batch summarization tracking
        self.last_summarization: Dict[SnapshotLevel, datetime] = {}
        self.summarization_enabled = True
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[callable]] = defaultdict(list)
        
        WorldStateManager._instance = self
    
    @classmethod
    async def get_instance(cls, repository: Optional[WorldStateRepository] = None) -> 'WorldStateManager':
        """Get singleton instance with thread safety"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(repository)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton for testing"""
        cls._instance = None
    
    # ===== CORE STATE OPERATIONS =====
    
    async def get_state(self, key: str, region_id: Optional[str] = None, default: Any = None) -> Any:
        """Get state variable with concurrent read support"""
        async with self._read_write_lock:
            if region_id:
                return self.regional_states.get(region_id, {}).get(key, default)
            return self.current_state.get_state_variable(key, default)
    
    async def set_state(
        self, 
        key: str, 
        value: Any, 
        region_id: Optional[str] = None,
        category: StateCategory = StateCategory.OTHER,
        reason: Optional[str] = None
    ) -> None:
        """Set state variable with exclusive write and change tracking"""
        async with self._read_write_lock:
            old_value = await self.get_state(key, region_id)
            
            # Update state
            if region_id:
                if region_id not in self.regional_states:
                    self.regional_states[region_id] = {}
                self.regional_states[region_id][key] = value
            else:
                self.current_state.set_state_variable(key, value)
            
            # Record change
            change = WorldStateChange(
                change_type=StateChangeType.UPDATED,
                state_key=key,
                old_value=old_value,
                new_value=value,
                region=WorldRegion.GLOBAL if not region_id else WorldRegion.CENTRAL,  # TODO: Map region_id to WorldRegion
                category=category,
                entity_id=region_id,
                reason=reason
            )
            
            self.current_state.change_history.append(change)
            
            # Trigger events
            await self._trigger_event('state_changed', {
                'key': key,
                'old_value': old_value,
                'new_value': value,
                'region_id': region_id,
                'change': change
            })
            
            # Auto-snapshot if significant change
            if await self._should_auto_snapshot(change):
                await self._create_auto_snapshot(region_id or 'global', change)
    
    async def query_state(
        self, 
        query: Dict[str, Any], 
        region_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query state with filtering support"""
        async with self._read_write_lock:
            results = {}
            
            category_filter = query.get('category')
            key_pattern = query.get('key_pattern', '')
            time_range = query.get('time_range')
            
            # Get state source
            if region_id:
                source_state = self.regional_states.get(region_id, {})
            else:
                source_state = self.current_state.state_variables
            
            # Apply filters
            for key, value in source_state.items():
                if key_pattern and key_pattern not in key:
                    continue
                
                # Category filtering (if we have metadata about categories)
                if category_filter:
                    # TODO: Implement category metadata tracking
                    pass
                
                results[key] = value
            
            return results
    
    # ===== TEMPORAL VERSIONING & SNAPSHOTS =====
    
    async def create_snapshot(
        self, 
        region_id: str, 
        include_global_context: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RegionalSnapshot:
        """Create a timestamped snapshot of regional state"""
        async with self._snapshot_lock:
            timestamp = datetime.utcnow()
            
            # Get regional state
            local_state = self.regional_states.get(region_id, {}).copy()
            
            # Get relevant global context
            global_context = {}
            if include_global_context:
                # Include important global state that affects this region
                global_context = {
                    'global_time': self.current_state.current_time,
                    'season': self.current_state.season,
                    'year': self.current_state.year,
                    'active_global_effects': [
                        effect for effect in self.current_state.active_effects 
                        if not hasattr(effect, 'region') or effect.region == region_id
                    ]
                }
            
            snapshot = RegionalSnapshot(
                region_id=region_id,
                timestamp=timestamp,
                local_state=local_state,
                global_context=global_context,
                snapshot_id=str(uuid4()),
                metadata=metadata or {}
            )
            
            # Store snapshot
            self.regional_snapshots[region_id].append(snapshot)
            
            # Persist if repository available
            if self.repository:
                await self.repository.save_snapshot(snapshot)
            
            await self._trigger_event('snapshot_created', {
                'snapshot': snapshot,
                'region_id': region_id
            })
            
            return snapshot
    
    async def rollback_to_snapshot(
        self, 
        region_id: str, 
        snapshot_id: str,
        atomic: bool = True
    ) -> bool:
        """Rollback regional state to a specific snapshot"""
        async with self._read_write_lock:
            # Find snapshot
            snapshot = None
            for snap in self.regional_snapshots.get(region_id, []):
                if snap.snapshot_id == snapshot_id:
                    snapshot = snap
                    break
            
            if not snapshot:
                logger.error(f"Snapshot {snapshot_id} not found for region {region_id}")
                return False
            
            try:
                if atomic:
                    # Atomic rollback: backup current state first
                    backup_snapshot = await self.create_snapshot(
                        region_id, 
                        metadata={'type': 'rollback_backup', 'original_snapshot': snapshot_id}
                    )
                
                # Restore regional state
                self.regional_states[region_id] = snapshot.local_state.copy()
                
                # Optionally restore global context
                if snapshot.global_context:
                    for key, value in snapshot.global_context.items():
                        if key in ['global_time', 'season', 'year']:
                            setattr(self.current_state, key, value)
                
                # Record rollback change
                change = WorldStateChange(
                    change_type=StateChangeType.UPDATED,
                    state_key=f"region_{region_id}_state",
                    old_value="<complex_state>",
                    new_value="<rolled_back_state>",
                    region=WorldRegion.CENTRAL,  # TODO: Map region_id
                    category=StateCategory.OTHER,
                    entity_id=region_id,
                    reason=f"Rollback to snapshot {snapshot_id}"
                )
                
                self.current_state.change_history.append(change)
                
                await self._trigger_event('state_rolled_back', {
                    'region_id': region_id,
                    'snapshot_id': snapshot_id,
                    'timestamp': snapshot.timestamp
                })
                
                return True
                
            except Exception as e:
                logger.error(f"Rollback failed for region {region_id}: {str(e)}")
                return False
    
    async def get_historical_state(
        self, 
        region_id: str, 
        timestamp: datetime,
        reconstruct_global: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Reconstruct historical state for a region at a specific timestamp"""
        async with self._read_write_lock:
            # Find the closest snapshot before the timestamp
            relevant_snapshots = [
                snap for snap in self.regional_snapshots.get(region_id, [])
                if snap.timestamp <= timestamp
            ]
            
            if not relevant_snapshots:
                return None
            
            # Get the closest snapshot
            base_snapshot = max(relevant_snapshots, key=lambda s: s.timestamp)
            
            # Start with the snapshot state
            reconstructed_state = base_snapshot.local_state.copy()
            
            # Apply changes that occurred between snapshot and target timestamp
            relevant_changes = [
                change for change in self.current_state.change_history
                if (change.entity_id == region_id and 
                    base_snapshot.timestamp <= change.timestamp <= timestamp)
            ]
            
            # Apply changes chronologically
            for change in sorted(relevant_changes, key=lambda c: c.timestamp):
                if change.state_key in reconstructed_state:
                    reconstructed_state[change.state_key] = change.new_value
            
            result = {
                'regional_state': reconstructed_state,
                'timestamp': timestamp,
                'base_snapshot_id': base_snapshot.snapshot_id,
                'changes_applied': len(relevant_changes)
            }
            
            # Include global context if requested
            if reconstruct_global and base_snapshot.global_context:
                result['global_context'] = base_snapshot.global_context
            
            return result
    
    # ===== HIERARCHICAL BATCH SUMMARIZATION =====
    
    async def process_batch_summarization(self, force: bool = False) -> Dict[str, int]:
        """Process hierarchical batch summarization on schedule"""
        if not self.summarization_enabled and not force:
            return {}
        
        results = {}
        now = datetime.utcnow()
        
        # Check each summarization level
        for level in SnapshotLevel:
            config = self.summarization_schedule[level]
            last_run = self.last_summarization.get(level, datetime.min)
            frequency = timedelta(days=config['frequency_days'])
            
            if force or (now - last_run) >= frequency:
                count = await self._summarize_period(level, config)
                results[level.value] = count
                self.last_summarization[level] = now
        
        return results
    
    async def _summarize_period(self, level: SnapshotLevel, config: Dict[str, Any]) -> int:
        """Summarize a specific time period"""
        now = datetime.utcnow()
        frequency_days = config['frequency_days']
        retention_days = config['retention_days']
        
        # Define the period to summarize
        period_end = now - timedelta(days=frequency_days)
        period_start = period_end - timedelta(days=frequency_days)
        
        logger.info(f"Summarizing {level.value} period: {period_start} to {period_end}")
        
        # Collect changes from this period
        relevant_changes = [
            change for change in self.current_state.change_history
            if period_start <= change.timestamp <= period_end
        ]
        
        if not relevant_changes:
            return 0
        
        # Group changes by region
        changes_by_region = defaultdict(list)
        for change in relevant_changes:
            region = change.entity_id or 'global'
            changes_by_region[region].append(change)
        
        # Create summary for each region
        summaries_created = 0
        for region_id, region_changes in changes_by_region.items():
            summary = await self._create_period_summary(
                region_id, level, period_start, period_end, region_changes
            )
            
            if self.repository:
                await self.repository.save_summary(summary)
            
            summaries_created += 1
        
        # Clean up old detailed records if retention period exceeded
        cleanup_threshold = now - timedelta(days=retention_days)
        if self.repository:
            deleted_count = await self.repository.delete_changes_before(cleanup_threshold)
            logger.info(f"Cleaned up {deleted_count} old change records for {level.value}")
        
        return summaries_created
    
    async def _create_period_summary(
        self,
        region_id: str,
        level: SnapshotLevel,
        period_start: datetime,
        period_end: datetime,
        changes: List[WorldStateChange]
    ) -> HistoricalSummary:
        """Create a summary for a specific period and region"""
        
        # Analyze changes
        key_changes = []
        categories_affected = set()
        
        for change in changes:
            categories_affected.add(change.category.value)
            
            if self._is_significant_change(change):
                key_changes.append({
                    'timestamp': change.timestamp.isoformat(),
                    'type': change.change_type.value,
                    'key': change.state_key,
                    'category': change.category.value,
                    'reason': change.reason
                })
        
        # Generate summary text (simple version - could use LLM for better summaries)
        summary_text = self._generate_summary_text(region_id, level, categories_affected, len(changes))
        
        compression_ratio = len(key_changes) / len(changes) if changes else 0
        
        return HistoricalSummary(
            summary_id=str(uuid4()),
            period_start=period_start,
            period_end=period_end,
            period_type=level.value,
            regions_affected=[region_id],
            summary_text=summary_text,
            key_changes=key_changes,
            original_change_count=len(changes),
            compression_ratio=compression_ratio,
            metadata={
                'categories_affected': list(categories_affected),
                'created_at': datetime.utcnow().isoformat()
            }
        )
    
    def _generate_summary_text(
        self, 
        region_id: str, 
        level: SnapshotLevel, 
        categories: set, 
        change_count: int
    ) -> str:
        """Generate human-readable summary text"""
        category_list = ', '.join(categories) if categories else 'no specific categories'
        
        return (f"During this {level.value} period, region {region_id} experienced "
                f"{change_count} state changes affecting {category_list}. "
                f"Summary generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}.")
    
    def _is_significant_change(self, change: WorldStateChange) -> bool:
        """Determine if a change is significant enough to preserve in summaries"""
        # High-importance categories
        important_categories = {
            StateCategory.POLITICAL, 
            StateCategory.MILITARY, 
            StateCategory.QUEST
        }
        
        if change.category in important_categories:
            return True
        
        # Large value changes
        if isinstance(change.new_value, (int, float)) and isinstance(change.old_value, (int, float)):
            if abs(change.new_value - change.old_value) > 100:  # Arbitrary threshold
                return True
        
        return False
    
    # ===== EVENT SYSTEM =====
    
    async def subscribe_to_events(self, event_type: str, callback: callable):
        """Subscribe to world state events"""
        self.event_callbacks[event_type].append(callback)
    
    async def unsubscribe_from_events(self, event_type: str, callback: callable):
        """Unsubscribe from world state events"""
        if callback in self.event_callbacks[event_type]:
            self.event_callbacks[event_type].remove(callback)
    
    async def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Trigger events for subscribers"""
        for callback in self.event_callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error in event callback for {event_type}: {str(e)}")
    
    # ===== HELPER METHODS =====
    
    async def _should_auto_snapshot(self, change: WorldStateChange) -> bool:
        """Determine if a change warrants an automatic snapshot"""
        # Snapshot on important category changes
        important_categories = {
            StateCategory.POLITICAL,
            StateCategory.MILITARY,
            StateCategory.QUEST
        }
        
        return change.category in important_categories
    
    async def _create_auto_snapshot(self, region_id: str, triggering_change: WorldStateChange):
        """Create an automatic snapshot triggered by a significant change"""
        metadata = {
            'type': 'auto_snapshot',
            'triggered_by_change': triggering_change.id,
            'change_category': triggering_change.category.value
        }
        
        await self.create_snapshot(region_id, metadata=metadata)
    
    async def get_summary_for_period(
        self, 
        start_time: datetime, 
        end_time: datetime, 
        region_id: Optional[str] = None
    ) -> List[HistoricalSummary]:
        """Get historical summaries for a time period"""
        if not self.repository:
            return []
        
        summaries = []
        for level in SnapshotLevel:
            level_summaries = await self.repository.load_summaries(
                level.value, start_time, end_time
            )
            
            if region_id:
                level_summaries = [
                    s for s in level_summaries 
                    if region_id in s.regions_affected
                ]
            
            summaries.extend(level_summaries)
        
        return sorted(summaries, key=lambda s: s.period_start)
    
    # ===== TICK PROCESSING =====
    
    async def process_tick(self) -> None:
        """Process a world state tick with summarization"""
        # Update world time
        self.current_state.current_time = datetime.utcnow()
        
        # Process expired effects
        expired_effects = self.current_state.remove_expired_effects()
        for effect in expired_effects:
            await self._trigger_event('effect_expired', {'effect': effect})
        
        # Check for scheduled summarization
        if self.summarization_enabled:
            results = await self.process_batch_summarization()
            if results:
                logger.info(f"Batch summarization completed: {results}")
        
        # Trigger tick event
        await self._trigger_event('tick_processed', {
            'timestamp': self.current_state.current_time,
            'expired_effects_count': len(expired_effects)
        })
    
    # ===== PERSISTENCE =====
    
    async def save_to_repository(self) -> bool:
        """Save current state to repository"""
        if not self.repository:
            return False
        
        try:
            return await self.repository.save_state(self.current_state)
        except Exception as e:
            logger.error(f"Failed to save state to repository: {str(e)}")
            return False
    
    async def load_from_repository(self) -> bool:
        """Load state from repository"""
        if not self.repository:
            return False
        
        try:
            loaded_state = await self.repository.load_state()
            if loaded_state:
                self.current_state = loaded_state
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load state from repository: {str(e)}")
            return False


# Export classes
__all__ = [
    "WorldStateManager",
    "RegionalSnapshot", 
    "HistoricalSummary",
    "SnapshotLevel",
    "WorldStateRepository"
] 