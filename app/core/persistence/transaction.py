"""
Transaction system for atomic world state changes.

This module provides transaction support for making atomic changes to the world state,
allowing for batching operations and ensuring data consistency.
"""

import logging
from typing import Dict, List, Optional, Any, Set, Callable, TypeVar, Generic
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import traceback

from app.core.persistence.change_tracker import ChangeTracker, ChangeType, ChangeContext

logger = logging.getLogger(__name__)

T = TypeVar('T')

class TransactionStatus(str, Enum):
    """Status of a transaction."""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"

@dataclass
class Operation:
    """An operation within a transaction."""
    operation_type: str  # "create", "update", "delete"
    entity_type: str
    entity_id: str
    field_name: Optional[str] = None
    value: Any = None
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TransactionResult:
    """Result of a transaction."""
    success: bool
    transaction_id: str
    status: TransactionStatus
    affected_entities: List[Dict[str, Any]]
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class Transaction:
    """Represents a transaction for atomic world state changes."""
    
    def __init__(
        self,
        name: str,
        change_tracker: ChangeTracker,
        context: Optional[ChangeContext] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a transaction.
        
        Args:
            name: Name of the transaction
            change_tracker: ChangeTracker instance
            context: Change context information
            metadata: Additional metadata
        """
        self.transaction_id = str(uuid.uuid4())
        self.name = name
        self.change_tracker = change_tracker
        self.context = context or ChangeContext()
        self.metadata = metadata or {}
        
        # Transaction state
        self.status = TransactionStatus.PENDING
        self.operations: List[Operation] = []
        self.pre_state: Dict[str, Dict[str, Any]] = {}
        self.post_state: Dict[str, Dict[str, Any]] = {}
        self.error: Optional[Exception] = None
        
        # Track affected entities for efficient lookup
        self.affected_entities: Dict[str, Set[str]] = {}
        
        # Hooks
        self.pre_commit_hooks: List[Callable[['Transaction'], None]] = []
        self.post_commit_hooks: List[Callable[['Transaction'], None]] = []
        
        # Start timestamp
        self.start_time = datetime.utcnow().isoformat()
        self.end_time: Optional[str] = None
        
        logger.debug(f"Created transaction {self.transaction_id} ({name})")
    
    def add_operation(
        self,
        operation_type: str,
        entity_type: str,
        entity_id: str,
        field_name: Optional[str] = None,
        value: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an operation to the transaction.
        
        Args:
            operation_type: Type of operation
            entity_type: Type of entity
            entity_id: ID of entity
            field_name: Field name (for updates)
            value: Value to set
            metadata: Additional metadata
            
        Returns:
            Operation ID
        """
        if self.status != TransactionStatus.PENDING:
            raise ValueError(f"Cannot add operation to {self.status} transaction")
        
        # Create operation
        operation = Operation(
            operation_type=operation_type,
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            value=value,
            metadata=metadata or {}
        )
        
        # Add to operations list
        self.operations.append(operation)
        
        # Track affected entity
        self._track_affected_entity(entity_type, entity_id)
        
        logger.debug(f"Added {operation_type} operation to transaction {self.transaction_id}")
        return operation.operation_id
    
    def _track_affected_entity(self, entity_type: str, entity_id: str) -> None:
        """Track an affected entity for efficient lookup."""
        if entity_type not in self.affected_entities:
            self.affected_entities[entity_type] = set()
        self.affected_entities[entity_type].add(entity_id)
    
    def get_affected_entities(self) -> Dict[str, Set[str]]:
        """
        Get all affected entities.
        
        Returns:
            Dictionary mapping entity types to sets of entity IDs
        """
        return self.affected_entities
    
    def add_pre_commit_hook(self, hook: Callable[['Transaction'], None]) -> None:
        """
        Add a hook to run before committing the transaction.
        
        Args:
            hook: Function to call before commit
        """
        self.pre_commit_hooks.append(hook)
    
    def add_post_commit_hook(self, hook: Callable[['Transaction'], None]) -> None:
        """
        Add a hook to run after committing the transaction.
        
        Args:
            hook: Function to call after commit
        """
        self.post_commit_hooks.append(hook)
    
    def commit(self, world_state: Dict[str, Any]) -> TransactionResult:
        """
        Commit the transaction, applying all operations.
        
        Args:
            world_state: Current world state
            
        Returns:
            Result of the transaction
        """
        if self.status != TransactionStatus.PENDING:
            return TransactionResult(
                success=False,
                transaction_id=self.transaction_id,
                status=self.status,
                affected_entities=self._format_affected_entities(),
                error_message=f"Cannot commit {self.status} transaction"
            )
        
        try:
            # Run pre-commit hooks
            for hook in self.pre_commit_hooks:
                hook(self)
            
            # Save the pre-state of affected entities
            self._save_pre_state(world_state)
            
            # Apply all operations
            for operation in self.operations:
                self._apply_operation(operation, world_state)
            
            # Save the post-state of affected entities
            self._save_post_state(world_state)
            
            # Record changes
            self._record_changes()
            
            # Update status
            self.status = TransactionStatus.COMMITTED
            self.end_time = datetime.utcnow().isoformat()
            
            # Run post-commit hooks
            for hook in self.post_commit_hooks:
                hook(self)
            
            logger.info(f"Committed transaction {self.transaction_id} ({self.name})")
            
            return TransactionResult(
                success=True,
                transaction_id=self.transaction_id,
                status=self.status,
                affected_entities=self._format_affected_entities()
            )
        except Exception as e:
            self.status = TransactionStatus.FAILED
            self.error = e
            self.end_time = datetime.utcnow().isoformat()
            
            error_message = f"Transaction failed: {str(e)}"
            logger.error(f"{error_message}\n{traceback.format_exc()}")
            
            return TransactionResult(
                success=False,
                transaction_id=self.transaction_id,
                status=self.status,
                affected_entities=self._format_affected_entities(),
                error_message=error_message
            )
    
    def rollback(self, world_state: Dict[str, Any]) -> TransactionResult:
        """
        Roll back the transaction, reverting all changes.
        
        Args:
            world_state: Current world state
            
        Returns:
            Result of the rollback
        """
        if self.status not in [TransactionStatus.COMMITTED, TransactionStatus.PENDING]:
            return TransactionResult(
                success=False,
                transaction_id=self.transaction_id,
                status=self.status,
                affected_entities=self._format_affected_entities(),
                error_message=f"Cannot roll back {self.status} transaction"
            )
        
        try:
            # Restore pre-state
            for entity_type, entities in self.pre_state.items():
                if entity_type not in world_state:
                    world_state[entity_type] = {}
                
                for entity_id, entity_data in entities.items():
                    world_state[entity_type][entity_id] = entity_data
            
            # Update status
            self.status = TransactionStatus.ROLLED_BACK
            self.end_time = datetime.utcnow().isoformat()
            
            logger.info(f"Rolled back transaction {self.transaction_id} ({self.name})")
            
            return TransactionResult(
                success=True,
                transaction_id=self.transaction_id,
                status=self.status,
                affected_entities=self._format_affected_entities()
            )
        except Exception as e:
            error_message = f"Rollback failed: {str(e)}"
            logger.error(f"{error_message}\n{traceback.format_exc()}")
            
            return TransactionResult(
                success=False,
                transaction_id=self.transaction_id,
                status=self.status,
                affected_entities=self._format_affected_entities(),
                error_message=error_message
            )
    
    def _save_pre_state(self, world_state: Dict[str, Any]) -> None:
        """Save the pre-state of affected entities."""
        for entity_type, entity_ids in self.affected_entities.items():
            if entity_type not in self.pre_state:
                self.pre_state[entity_type] = {}
            
            if entity_type in world_state:
                for entity_id in entity_ids:
                    if entity_id in world_state[entity_type]:
                        # Deep copy the entity data
                        self.pre_state[entity_type][entity_id] = _deep_copy(world_state[entity_type][entity_id])
    
    def _save_post_state(self, world_state: Dict[str, Any]) -> None:
        """Save the post-state of affected entities."""
        for entity_type, entity_ids in self.affected_entities.items():
            if entity_type not in self.post_state:
                self.post_state[entity_type] = {}
            
            if entity_type in world_state:
                for entity_id in entity_ids:
                    if entity_id in world_state[entity_type]:
                        # Deep copy the entity data
                        self.post_state[entity_type][entity_id] = _deep_copy(world_state[entity_type][entity_id])
    
    def _apply_operation(self, operation: Operation, world_state: Dict[str, Any]) -> None:
        """Apply an operation to the world state."""
        # Ensure the entity type exists in the world state
        if operation.entity_type not in world_state:
            world_state[operation.entity_type] = {}
        
        if operation.operation_type == "create":
            # Create operation
            if operation.field_name:
                # Create/update a field
                if operation.entity_id not in world_state[operation.entity_type]:
                    world_state[operation.entity_type][operation.entity_id] = {}
                world_state[operation.entity_type][operation.entity_id][operation.field_name] = operation.value
            else:
                # Create an entity
                world_state[operation.entity_type][operation.entity_id] = operation.value
        elif operation.operation_type == "update":
            # Update operation
            if operation.entity_id not in world_state[operation.entity_type]:
                raise ValueError(f"Entity {operation.entity_id} not found in {operation.entity_type}")
            
            if operation.field_name:
                # Update a field
                world_state[operation.entity_type][operation.entity_id][operation.field_name] = operation.value
            else:
                # Update the entire entity
                world_state[operation.entity_type][operation.entity_id] = operation.value
        elif operation.operation_type == "delete":
            # Delete operation
            if operation.entity_id not in world_state[operation.entity_type]:
                raise ValueError(f"Entity {operation.entity_id} not found in {operation.entity_type}")
            
            if operation.field_name:
                # Delete a field
                if operation.field_name in world_state[operation.entity_type][operation.entity_id]:
                    del world_state[operation.entity_type][operation.entity_id][operation.field_name]
            else:
                # Delete the entire entity
                del world_state[operation.entity_type][operation.entity_id]
        else:
            raise ValueError(f"Unknown operation type: {operation.operation_type}")
    
    def _record_changes(self) -> None:
        """Record changes to the change tracker."""
        for operation in self.operations:
            change_type = ChangeType.CREATE if operation.operation_type == "create" else \
                          ChangeType.UPDATE if operation.operation_type == "update" else \
                          ChangeType.DELETE
            
            old_value = None
            if operation.entity_type in self.pre_state and operation.entity_id in self.pre_state[operation.entity_type]:
                if operation.field_name:
                    old_value = self.pre_state[operation.entity_type][operation.entity_id].get(operation.field_name)
                else:
                    old_value = self.pre_state[operation.entity_type][operation.entity_id]
            
            new_value = None
            if change_type != ChangeType.DELETE:
                if operation.entity_type in self.post_state and operation.entity_id in self.post_state[operation.entity_type]:
                    if operation.field_name:
                        new_value = self.post_state[operation.entity_type][operation.entity_id].get(operation.field_name)
                    else:
                        new_value = self.post_state[operation.entity_type][operation.entity_id]
            
            # Create change context
            context = ChangeContext(
                timestamp=datetime.utcnow().isoformat(),
                source=f"transaction:{self.transaction_id}",
                cause=self.name,
                metadata={
                    "transaction_id": self.transaction_id,
                    "transaction_name": self.name,
                    "operation_id": operation.operation_id,
                    **self.context.metadata
                }
            )
            
            # Record the change
            self.change_tracker.track_change(
                change_type=change_type,
                entity_type=operation.entity_type,
                entity_id=operation.entity_id,
                field_name=operation.field_name,
                old_value=old_value,
                new_value=new_value,
                context=context
            )
    
    def _format_affected_entities(self) -> List[Dict[str, Any]]:
        """Format affected entities for the transaction result."""
        result = []
        for entity_type, entity_ids in self.affected_entities.items():
            for entity_id in entity_ids:
                result.append({
                    "entity_type": entity_type,
                    "entity_id": entity_id
                })
        return result

class TransactionManager:
    """Manages transactions for world state changes."""
    
    def __init__(self, change_tracker: ChangeTracker):
        """
        Initialize the transaction manager.
        
        Args:
            change_tracker: ChangeTracker instance
        """
        self.change_tracker = change_tracker
        self.active_transactions: Dict[str, Transaction] = {}
        self.completed_transactions: Dict[str, Transaction] = {}
        self.max_completed_transactions = 100
    
    def create_transaction(
        self,
        name: str,
        context: Optional[ChangeContext] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            name: Name of the transaction
            context: Change context information
            metadata: Additional metadata
            
        Returns:
            Created transaction
        """
        transaction = Transaction(name, self.change_tracker, context, metadata)
        self.active_transactions[transaction.transaction_id] = transaction
        return transaction
    
    def commit_transaction(self, transaction_id: str, world_state: Dict[str, Any]) -> TransactionResult:
        """
        Commit a transaction.
        
        Args:
            transaction_id: ID of the transaction to commit
            world_state: Current world state
            
        Returns:
            Result of the transaction
        """
        if transaction_id not in self.active_transactions:
            return TransactionResult(
                success=False,
                transaction_id=transaction_id,
                status=TransactionStatus.FAILED,
                affected_entities=[],
                error_message=f"Transaction {transaction_id} not found"
            )
        
        transaction = self.active_transactions[transaction_id]
        result = transaction.commit(world_state)
        
        # Move to completed transactions
        del self.active_transactions[transaction_id]
        self.completed_transactions[transaction_id] = transaction
        
        # Trim completed transactions if needed
        if len(self.completed_transactions) > self.max_completed_transactions:
            oldest_id = min(self.completed_transactions.keys(), key=lambda k: self.completed_transactions[k].start_time)
            del self.completed_transactions[oldest_id]
        
        return result
    
    def rollback_transaction(self, transaction_id: str, world_state: Dict[str, Any]) -> TransactionResult:
        """
        Roll back a transaction.
        
        Args:
            transaction_id: ID of the transaction to roll back
            world_state: Current world state
            
        Returns:
            Result of the rollback
        """
        # Check active transactions first
        if transaction_id in self.active_transactions:
            transaction = self.active_transactions[transaction_id]
            result = transaction.rollback(world_state)
            
            # Move to completed transactions
            del self.active_transactions[transaction_id]
            self.completed_transactions[transaction_id] = transaction
            
            return result
        
        # Check completed transactions
        if transaction_id in self.completed_transactions:
            transaction = self.completed_transactions[transaction_id]
            return transaction.rollback(world_state)
        
        return TransactionResult(
            success=False,
            transaction_id=transaction_id,
            status=TransactionStatus.FAILED,
            affected_entities=[],
            error_message=f"Transaction {transaction_id} not found"
        )
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get a transaction by ID.
        
        Args:
            transaction_id: ID of the transaction
            
        Returns:
            Transaction if found, None otherwise
        """
        if transaction_id in self.active_transactions:
            return self.active_transactions[transaction_id]
        
        if transaction_id in self.completed_transactions:
            return self.completed_transactions[transaction_id]
        
        return None
    
    def get_active_transactions(self) -> Dict[str, Transaction]:
        """
        Get all active transactions.
        
        Returns:
            Dictionary of active transactions
        """
        return self.active_transactions
    
    def get_completed_transactions(self) -> Dict[str, Transaction]:
        """
        Get all completed transactions.
        
        Returns:
            Dictionary of completed transactions
        """
        return self.completed_transactions

def _deep_copy(obj: Any) -> Any:
    """Create a deep copy of an object."""
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy(x) for x in obj]
    elif isinstance(obj, set):
        return {_deep_copy(x) for x in obj}
    elif isinstance(obj, tuple):
        return tuple(_deep_copy(x) for x in obj)
    else:
        return obj  # Assume immutable 