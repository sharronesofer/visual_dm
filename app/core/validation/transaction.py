"""
Transaction system for ensuring ACID properties in game actions.
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import logging
import uuid
import json
import time
import traceback
from datetime import datetime
from flask import request, jsonify, current_app, g
from app.core.api.error_handling.exceptions import ValidationError, APIError
from app.core.database import db

class TransactionLogger:
    """Logger for transaction data."""
    
    def __init__(self, app=None):
        """Initialize transaction logger."""
        self.logger = logging.getLogger('transaction')
        self.setup_logger()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the logger with a Flask app."""
        handler = logging.FileHandler(app.config.get('TRANSACTION_LOG_PATH', 'transactions.log'))
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(app.config.get('TRANSACTION_LOG_LEVEL', logging.INFO))
    
    def setup_logger(self):
        """Set up the transaction logger."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_start(self, transaction_id: str, action_type: str, user_id: str, data: Dict[str, Any]):
        """Log transaction start.
        
        Args:
            transaction_id: Transaction ID
            action_type: Type of action being performed
            user_id: User ID
            data: Request data
        """
        self.logger.info(
            f"TRANSACTION START | ID: {transaction_id} | Type: {action_type} | User: {user_id} | "
            f"Data: {json.dumps(data, default=str)}"
        )
    
    def log_success(self, transaction_id: str, action_type: str, user_id: str, result: Dict[str, Any]):
        """Log transaction success.
        
        Args:
            transaction_id: Transaction ID
            action_type: Type of action being performed
            user_id: User ID
            result: Result data
        """
        self.logger.info(
            f"TRANSACTION SUCCESS | ID: {transaction_id} | Type: {action_type} | User: {user_id} | "
            f"Result: {json.dumps(result, default=str)}"
        )
    
    def log_failure(self, transaction_id: str, action_type: str, user_id: str, error: str):
        """Log transaction failure.
        
        Args:
            transaction_id: Transaction ID
            action_type: Type of action being performed
            user_id: User ID
            error: Error message
        """
        self.logger.error(
            f"TRANSACTION FAILURE | ID: {transaction_id} | Type: {action_type} | User: {user_id} | "
            f"Error: {error}"
        )
    
    def log_rollback(self, transaction_id: str, action_type: str, user_id: str, error: str):
        """Log transaction rollback.
        
        Args:
            transaction_id: Transaction ID
            action_type: Type of action being performed
            user_id: User ID
            error: Error message
        """
        self.logger.warning(
            f"TRANSACTION ROLLBACK | ID: {transaction_id} | Type: {action_type} | User: {user_id} | "
            f"Error: {error}"
        )

# Global transaction logger
transaction_logger = TransactionLogger()

class TransactionContext:
    """Context for managing database transactions."""
    
    def __init__(self, action_type: str, user_id: str, data: Dict[str, Any]):
        """Initialize transaction context.
        
        Args:
            action_type: Type of action being performed
            user_id: User ID
            data: Request data
        """
        self.transaction_id = str(uuid.uuid4())
        self.action_type = action_type
        self.user_id = user_id
        self.data = data
        self.start_time = time.time()
        self.success = False
        self.result = None
        self.error = None
    
    def __enter__(self):
        """Enter transaction context."""
        transaction_logger.log_start(self.transaction_id, self.action_type, self.user_id, self.data)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        if exc_type is not None:
            # Transaction failed
            error_msg = str(exc_val)
            if isinstance(exc_val, APIError):
                error_msg = f"{exc_val.code}: {exc_val.message}"
            
            transaction_logger.log_failure(self.transaction_id, self.action_type, self.user_id, error_msg)
            db.session.rollback()
            transaction_logger.log_rollback(self.transaction_id, self.action_type, self.user_id, error_msg)
        elif self.success:
            # Transaction successful
            transaction_logger.log_success(self.transaction_id, self.action_type, self.user_id, self.result or {})
            db.session.commit()
        else:
            # Transaction failed without exception
            transaction_logger.log_failure(self.transaction_id, self.action_type, self.user_id, self.error or "Unknown error")
            db.session.rollback()
            transaction_logger.log_rollback(self.transaction_id, self.action_type, self.user_id, self.error or "Unknown error")
        
        return False  # Let exceptions propagate

def transaction(action_type: str):
    """
    Decorator for wrapping request handlers in a transaction.
    
    Args:
        action_type: Type of action being performed
        
    Returns:
        Decorated function
    
    Usage:
        @app.route('/resources', methods=['POST'])
        @transaction('create_resource')
        def create_resource():
            # All database operations here are within a transaction
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Get user ID from context
                user_id = str(g.current_user.id) if hasattr(g, 'current_user') and g.current_user else request.remote_addr
                
                # Get request data
                if request.is_json:
                    data = request.get_json(force=True) or {}
                else:
                    data = dict(request.args)
                
                # Start transaction
                with TransactionContext(action_type, user_id, data) as tx:
                    result = f(*args, **kwargs)
                    
                    # Store result in transaction context
                    if isinstance(result, tuple) and len(result) >= 2:
                        # Result is (response, status_code[, headers])
                        response_data = result[0]
                        if hasattr(response_data, 'get_json'):
                            # Response is a Flask response object
                            tx.result = response_data.get_json()
                        elif isinstance(response_data, dict):
                            # Response is a dict
                            tx.result = response_data
                    
                    # Mark transaction as successful
                    tx.success = True
                    
                    return result
                
            except Exception as e:
                # Log unexpected exceptions
                if not isinstance(e, APIError):
                    current_app.logger.error(f"Transaction error: {str(e)}\n{traceback.format_exc()}")
                
                # Re-raise exception to be handled by Flask error handlers
                raise
        
        return decorated
    return decorator 