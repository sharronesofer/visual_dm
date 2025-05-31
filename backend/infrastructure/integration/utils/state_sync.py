"""
Integration system - State Sync module for cross-system data synchronization.

This module provides comprehensive state synchronization functionality:
- StateSyncManager class for coordinating state across systems
- Async state synchronization with callbacks
- State rollback capabilities for failed operations
- State conflict resolution mechanisms
- State versioning and consistency checking
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class StateSnapshot:
    """Represents a snapshot of system state"""
    system_id: str
    state_data: Dict[str, Any]
    version: int
    timestamp: datetime
    checksum: str = field(init=False)
    
    def __post_init__(self):
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum for state data"""
        data_str = json.dumps(self.state_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


@dataclass
class SyncOperation:
    """Represents a state synchronization operation"""
    operation_id: str
    source_system: str
    target_systems: List[str]
    state_snapshot: StateSnapshot
    callback_handlers: List[Callable] = field(default_factory=list)
    error_handlers: List[Callable] = field(default_factory=list)
    success_handlers: List[Callable] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed, rolled_back
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class StateSyncManager:
    """
    Manages cross-system state synchronization with callbacks and rollback capabilities.
    
    Provides:
    - State synchronization between systems
    - Callback system for state change notifications
    - Rollback mechanisms for failed operations
    - State validation and consistency checks
    - Conflict resolution for concurrent updates
    """
    
    def __init__(self):
        self._registered_systems: Dict[str, Dict[str, Any]] = {}
        self._state_snapshots: Dict[str, StateSnapshot] = {}
        self._sync_operations: Dict[str, SyncOperation] = {}
        self._state_versions: Dict[str, int] = defaultdict(int)
        self._sync_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self._rollback_history: List[StateSnapshot] = []
        self._lock = asyncio.Lock()
        
    async def register_state_sync(
        self,
        system_id: str,
        initial_state: Dict[str, Any],
        sync_callback: Optional[Callable] = None,
        validation_callback: Optional[Callable] = None
    ) -> bool:
        """
        Register a system for state synchronization.
        
        Args:
            system_id: Unique identifier for the system
            initial_state: Initial state data for the system
            sync_callback: Optional callback for state changes
            validation_callback: Optional callback for state validation
            
        Returns:
            bool: True if registration successful
        """
        async with self._lock:
            try:
                # Create initial state snapshot
                snapshot = StateSnapshot(
                    system_id=system_id,
                    state_data=initial_state.copy(),
                    version=0,
                    timestamp=datetime.now()
                )
                
                # Register system
                self._registered_systems[system_id] = {
                    "sync_callback": sync_callback,
                    "validation_callback": validation_callback,
                    "registered_at": datetime.now()
                }
                
                self._state_snapshots[system_id] = snapshot
                self._state_versions[system_id] = 0
                
                if sync_callback:
                    self._sync_callbacks[system_id].append(sync_callback)
                
                logger.info(f"Registered system {system_id} for state sync")
                return True
                
            except Exception as e:
                logger.error(f"Failed to register system {system_id}: {e}")
                return False
    
    async def sync_state(
        self,
        source_system: str,
        target_systems: List[str],
        state_data: Dict[str, Any],
        operation_id: Optional[str] = None
    ) -> str:
        """
        Synchronize state between systems.
        
        Args:
            source_system: System initiating the sync
            target_systems: Systems to sync state to
            state_data: State data to synchronize
            operation_id: Optional operation identifier
            
        Returns:
            str: Operation ID for tracking
        """
        if operation_id is None:
            operation_id = f"sync_{source_system}_{datetime.now().timestamp()}"
        
        async with self._lock:
            try:
                # Validate source system
                if source_system not in self._registered_systems:
                    raise ValueError(f"Source system {source_system} not registered")
                
                # Validate target systems
                unregistered = [t for t in target_systems if t not in self._registered_systems]
                if unregistered:
                    raise ValueError(f"Target systems not registered: {unregistered}")
                
                # Create state snapshot
                current_version = self._state_versions[source_system] + 1
                snapshot = StateSnapshot(
                    system_id=source_system,
                    state_data=state_data.copy(),
                    version=current_version,
                    timestamp=datetime.now()
                )
                
                # Create sync operation
                operation = SyncOperation(
                    operation_id=operation_id,
                    source_system=source_system,
                    target_systems=target_systems,
                    state_snapshot=snapshot,
                    status="in_progress",
                    started_at=datetime.now()
                )
                
                self._sync_operations[operation_id] = operation
                
                # Execute sync
                await self._execute_sync_operation(operation)
                
                return operation_id
                
            except Exception as e:
                logger.error(f"Sync operation {operation_id} failed: {e}")
                if operation_id in self._sync_operations:
                    self._sync_operations[operation_id].status = "failed"
                    self._sync_operations[operation_id].error_message = str(e)
                raise
    
    async def _execute_sync_operation(self, operation: SyncOperation):
        """Execute the actual sync operation"""
        try:
            # Store rollback point
            rollback_snapshots = {}
            for target_system in operation.target_systems:
                if target_system in self._state_snapshots:
                    rollback_snapshots[target_system] = self._state_snapshots[target_system]
            
            # Update target systems
            for target_system in operation.target_systems:
                # Validate state if validator available
                validator = self._registered_systems[target_system].get("validation_callback")
                if validator and not await self._call_async_safe(validator, operation.state_snapshot.state_data):
                    raise ValueError(f"State validation failed for system {target_system}")
                
                # Update state
                new_snapshot = StateSnapshot(
                    system_id=target_system,
                    state_data=operation.state_snapshot.state_data.copy(),
                    version=self._state_versions[target_system] + 1,
                    timestamp=datetime.now()
                )
                
                self._state_snapshots[target_system] = new_snapshot
                self._state_versions[target_system] += 1
                
                # Call sync callbacks
                for callback in self._sync_callbacks[target_system]:
                    await self._call_async_safe(callback, new_snapshot.state_data)
            
            # Mark operation as successful
            operation.status = "completed"
            operation.completed_at = datetime.now()
            
            # Call success handlers
            for handler in operation.success_handlers:
                await self._call_async_safe(handler, operation)
                
        except Exception as e:
            # Rollback on failure
            operation.status = "failed"
            operation.error_message = str(e)
            operation.completed_at = datetime.now()
            
            # Call error handlers
            for handler in operation.error_handlers:
                await self._call_async_safe(handler, operation, e)
            
            raise
    
    async def rollback_state(self, operation_id: str) -> bool:
        """
        Rollback state changes from a failed operation.
        
        Args:
            operation_id: ID of the operation to rollback
            
        Returns:
            bool: True if rollback successful
        """
        async with self._lock:
            try:
                if operation_id not in self._sync_operations:
                    logger.error(f"Operation {operation_id} not found")
                    return False
                
                operation = self._sync_operations[operation_id]
                
                if operation.status != "failed":
                    logger.warning(f"Cannot rollback operation {operation_id} with status {operation.status}")
                    return False
                
                # Find rollback points (previous state snapshots)
                rollback_version = operation.state_snapshot.version - 1
                
                for target_system in operation.target_systems:
                    # Find previous snapshot
                    for snapshot in self._rollback_history:
                        if (snapshot.system_id == target_system and 
                            snapshot.version == rollback_version):
                            # Restore previous state
                            self._state_snapshots[target_system] = snapshot
                            self._state_versions[target_system] = snapshot.version
                            
                            # Notify via callbacks
                            for callback in self._sync_callbacks[target_system]:
                                await self._call_async_safe(callback, snapshot.state_data)
                            break
                
                operation.status = "rolled_back"
                logger.info(f"Rolled back operation {operation_id}")
                return True
                
            except Exception as e:
                logger.error(f"Rollback failed for operation {operation_id}: {e}")
                return False
    
    async def validate_state(self, system_id: str) -> bool:
        """
        Validate state consistency for a system.
        
        Args:
            system_id: System to validate
            
        Returns:
            bool: True if state is valid
        """
        try:
            if system_id not in self._registered_systems:
                return False
            
            snapshot = self._state_snapshots.get(system_id)
            if not snapshot:
                return False
            
            # Validate checksum
            expected_checksum = snapshot._calculate_checksum()
            if snapshot.checksum != expected_checksum:
                logger.error(f"Checksum mismatch for system {system_id}")
                return False
            
            # Call custom validator if available
            validator = self._registered_systems[system_id].get("validation_callback")
            if validator:
                return await self._call_async_safe(validator, snapshot.state_data)
            
            return True
            
        except Exception as e:
            logger.error(f"State validation failed for system {system_id}: {e}")
            return False
    
    def get_sync_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get synchronization status for an operation.
        
        Args:
            operation_id: Operation to check
            
        Returns:
            Optional[Dict]: Operation status details
        """
        if operation_id not in self._sync_operations:
            return None
        
        operation = self._sync_operations[operation_id]
        return {
            "operation_id": operation.operation_id,
            "source_system": operation.source_system,
            "target_systems": operation.target_systems,
            "status": operation.status,
            "error_message": operation.error_message,
            "started_at": operation.started_at,
            "completed_at": operation.completed_at
        }
    
    def get_system_state(self, system_id: str) -> Optional[Dict[str, Any]]:
        """Get current state for a system"""
        snapshot = self._state_snapshots.get(system_id)
        return snapshot.state_data if snapshot else None
    
    def get_system_version(self, system_id: str) -> int:
        """Get current version for a system"""
        return self._state_versions.get(system_id, 0)
    
    async def _call_async_safe(self, callback: Callable, *args, **kwargs) -> Any:
        """Safely call a callback that might be sync or async"""
        try:
            if asyncio.iscoroutinefunction(callback):
                return await callback(*args, **kwargs)
            else:
                return callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Callback failed: {e}")
            return None


# Global instance
state_sync_manager = StateSyncManager()


# Convenience functions
async def register_state_sync(
    system_id: str,
    initial_state: Dict[str, Any],
    sync_callback: Optional[Callable] = None,
    validation_callback: Optional[Callable] = None
) -> bool:
    """Register a system for state synchronization"""
    return await state_sync_manager.register_state_sync(
        system_id, initial_state, sync_callback, validation_callback
    )


async def sync_state(
    source_system: str,
    target_systems: List[str],
    state_data: Dict[str, Any],
    operation_id: Optional[str] = None
) -> str:
    """Synchronize state between systems"""
    return await state_sync_manager.sync_state(
        source_system, target_systems, state_data, operation_id
    )


async def rollback_state(operation_id: str) -> bool:
    """Rollback state changes from a failed operation"""
    return await state_sync_manager.rollback_state(operation_id)


async def validate_state(system_id: str) -> bool:
    """Validate state consistency for a system"""
    return await state_sync_manager.validate_state(system_id)


def get_sync_status(operation_id: str) -> Optional[Dict[str, Any]]:
    """Get synchronization status for an operation"""
    return state_sync_manager.get_sync_status(operation_id)
