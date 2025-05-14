"""
Database transaction management system with rollback support.
"""

import logging
import sqlite3
from typing import Dict, Any, Optional, List, Callable, Set
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    """Transaction data structure."""
    id: str
    start_time: datetime
    operations: List[Dict[str, Any]]
    status: str  # 'pending', 'committed', 'rolled_back'
    error: Optional[Exception] = None

class TransactionManager:
    """Manages database transactions with rollback support."""
    
    def __init__(self, db_path: str):
        """Initialize the transaction manager.
        
        Args:
            db_path: Path to the SQLite database
        """
        try:
            self.db_path = db_path
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            
            # Transaction tracking
            self.active_transactions: Dict[str, Transaction] = {}
            self.savepoints: Dict[str, str] = {}
            
            # Enable foreign key constraints
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            logger.info("Transaction manager initialized")
            
        except Exception as e:
            handle_component_error(
                "TransactionManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    @contextmanager
    def transaction(self, transaction_id: Optional[str] = None):
        """Context manager for database transactions.
        
        Args:
            transaction_id: Optional transaction ID
            
        Yields:
            Transaction object
        """
        transaction = None
        try:
            # Start transaction
            transaction = self.begin_transaction(transaction_id)
            yield transaction
            
            # Commit if no exceptions
            self.commit_transaction(transaction.id)
            
        except Exception as e:
            if transaction:
                # Rollback on exception
                self.rollback_transaction(transaction.id)
            raise
            
    def begin_transaction(self, transaction_id: Optional[str] = None) -> Transaction:
        """Begin a new transaction.
        
        Args:
            transaction_id: Optional transaction ID
            
        Returns:
            Transaction object
        """
        try:
            # Generate transaction ID if not provided
            if not transaction_id:
                transaction_id = f"tx-{datetime.now().timestamp()}"
                
            # Check for existing transaction
            if transaction_id in self.active_transactions:
                raise ValueError(f"Transaction {transaction_id} already exists")
                
            # Create savepoint
            savepoint = f"sp_{transaction_id}"
            self.cursor.execute(f"SAVEPOINT {savepoint}")
            self.savepoints[transaction_id] = savepoint
            
            # Create transaction
            transaction = Transaction(
                id=transaction_id,
                start_time=datetime.now(),
                operations=[],
                status="pending"
            )
            
            self.active_transactions[transaction_id] = transaction
            logger.info(f"Started transaction {transaction_id}")
            
            return transaction
            
        except Exception as e:
            handle_component_error(
                "TransactionManager",
                "begin_transaction",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def commit_transaction(self, transaction_id: str) -> None:
        """Commit a transaction.
        
        Args:
            transaction_id: Transaction ID
        """
        try:
            if transaction_id not in self.active_transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
                
            transaction = self.active_transactions[transaction_id]
            
            # Release savepoint
            savepoint = self.savepoints[transaction_id]
            self.cursor.execute(f"RELEASE SAVEPOINT {savepoint}")
            
            # Commit changes
            self.connection.commit()
            
            # Update transaction status
            transaction.status = "committed"
            logger.info(f"Committed transaction {transaction_id}")
            
            # Clean up
            del self.active_transactions[transaction_id]
            del self.savepoints[transaction_id]
            
        except Exception as e:
            handle_component_error(
                "TransactionManager",
                "commit_transaction",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def rollback_transaction(self, transaction_id: str) -> None:
        """Rollback a transaction.
        
        Args:
            transaction_id: Transaction ID
        """
        try:
            if transaction_id not in self.active_transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
                
            transaction = self.active_transactions[transaction_id]
            
            # Rollback to savepoint
            savepoint = self.savepoints[transaction_id]
            self.cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
            
            # Update transaction status
            transaction.status = "rolled_back"
            logger.info(f"Rolled back transaction {transaction_id}")
            
            # Clean up
            del self.active_transactions[transaction_id]
            del self.savepoints[transaction_id]
            
        except Exception as e:
            handle_component_error(
                "TransactionManager",
                "rollback_transaction",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def execute_in_transaction(
        self,
        query: str,
        params: tuple = (),
        transaction_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute a query within a transaction.
        
        Args:
            query: SQL query
            params: Query parameters
            transaction_id: Optional transaction ID
            
        Returns:
            Query results
        """
        try:
            # Start transaction if not provided
            if not transaction_id:
                with self.transaction() as transaction:
                    self.cursor.execute(query, params)
                    return [dict(row) for row in self.cursor.fetchall()]
                    
            # Use existing transaction
            if transaction_id not in self.active_transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
                
            transaction = self.active_transactions[transaction_id]
            
            # Execute query
            self.cursor.execute(query, params)
            
            # Track operation
            transaction.operations.append({
                "query": query,
                "params": params,
                "timestamp": datetime.now()
            })
            
            return [dict(row) for row in self.cursor.fetchall()]
            
        except Exception as e:
            handle_component_error(
                "TransactionManager",
                "execute_in_transaction",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def get_transaction_status(self, transaction_id: str) -> Optional[str]:
        """Get transaction status.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction status if found, None otherwise
        """
        try:
            transaction = self.active_transactions.get(transaction_id)
            return transaction.status if transaction else None
            
        except Exception as e:
            handle_component_error(
                "TransactionManager",
                "get_transaction_status",
                e,
                ErrorSeverity.ERROR
            )
            return None
            
    def cleanup(self) -> None:
        """Clean up transaction manager resources."""
        try:
            # Rollback any active transactions
            for transaction_id in list(self.active_transactions.keys()):
                self.rollback_transaction(transaction_id)
                
            # Close database connection
            self.cursor.close()
            self.connection.close()
            
            logger.info("Transaction manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "TransactionManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 