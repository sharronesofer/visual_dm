#!/usr/bin/env python3
"""
Example script demonstrating the usage of the centralized logging system.

This script shows how to use the different logging features provided by 
the app.core.logging module, including basic logging, specialized logging functions,
and performance measurement.

To try different log formats, run with environment variables:
- For JSON format: LOG_FORMAT=json python examples/logging_example.py
- For pretty format: LOG_FORMAT=pretty python examples/logging_example.py
- For pretty format with colors: LOG_FORMAT=pretty LOG_COLORIZE=true python examples/logging_example.py

To enable file logging:
- LOG_FILE_ENABLED=true LOG_FILE_PATH=./example.log python examples/logging_example.py
"""

import os
import time
import random
import logging
from datetime import datetime
from typing import Dict, Any, List

# Import the logging system
from app.core.logging import (
    get_logger,
    log_request,
    log_error,
    log_performance,
    log_security_event,
    log_database_operation,
    update_configuration,
    LogLevel,
    LogFormat
)

# Get a logger for this module
logger = get_logger(__name__)

@log_performance
def slow_operation(iterations: int = 1000000) -> int:
    """A deliberately slow operation to demonstrate performance logging."""
    result = 0
    for i in range(iterations):
        result += i
    return result

@log_performance(threshold_ms=10, level=logging.WARNING)
def sometimes_slow_operation(iterations: int = 10000) -> int:
    """
    An operation that is sometimes slow to demonstrate the threshold feature.
    Only logs if execution time exceeds the threshold.
    """
    # Random sleep to sometimes exceed threshold
    if random.random() < 0.5:
        time.sleep(0.02)  # 20ms, above threshold
    
    result = 0
    for i in range(iterations):
        result += i
    return result

def simulate_database_queries() -> None:
    """Simulate database operations to demonstrate database operation logging."""
    collections = ["users", "posts", "comments", "products"]
    operations = ["query", "insert", "update", "delete"]
    
    for _ in range(5):
        collection = random.choice(collections)
        operation = random.choice(operations)
        
        # Simulate operation time
        start_time = time.time()
        time.sleep(random.uniform(0.01, 0.05))
        duration = time.time() - start_time
        
        # Generate random document ID for some operations
        document_id = None
        if operation in ["update", "delete"]:
            document_id = f"{random.randint(1000, 9999)}"
            
        # Generate random affected count for some operations
        affected_count = None
        if operation in ["query", "update", "delete"]:
            affected_count = random.randint(1, 100)
            
        # Generate random query for some operations
        query = None
        if operation in ["query", "update", "delete"]:
            statuses = ["active", "inactive", "pending", "archived"]
            query = {"status": random.choice(statuses)}
        
        # Log the database operation
        log_database_operation(
            operation=operation,
            collection=collection,
            query=query,
            document_id=document_id,
            duration=duration,
            affected_count=affected_count
        )

def simulate_http_requests() -> None:
    """Simulate HTTP requests to demonstrate request logging."""
    methods = ["GET", "POST", "PUT", "DELETE"]
    paths = ["/api/users", "/api/products", "/api/orders", "/api/settings"]
    status_codes = [200, 201, 400, 401, 403, 404, 500]
    
    for _ in range(5):
        method = random.choice(methods)
        path = random.choice(paths)
        status_code = random.choice(status_codes)
        
        # Simulate request time
        duration = random.uniform(0.05, 0.5)
        
        # Generate random user ID and request ID
        user_id = f"user_{random.randint(1000, 9999)}"
        request_id = f"req_{random.randint(10000, 99999)}"
        ip_address = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
        
        # Log the request
        log_request(
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            user_id=user_id,
            request_id=request_id,
            ip_address=ip_address
        )

def simulate_security_events() -> None:
    """Simulate security events to demonstrate security event logging."""
    event_types = ["login_attempt", "password_reset", "access_denied", "permission_change"]
    
    for _ in range(5):
        event_type = random.choice(event_types)
        user_id = f"user_{random.randint(1000, 9999)}"
        ip_address = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
        success = random.random() < 0.7  # 70% success rate
        
        # Create message based on event type and success
        if event_type == "login_attempt":
            message = f"{'Successful' if success else 'Failed'} login attempt"
            details = {
                "method": random.choice(["password", "oauth", "2fa"]),
                "attempts": random.randint(1, 5) if not success else 1
            }
        elif event_type == "password_reset":
            message = f"Password {'reset successfully' if success else 'reset failed'}"
            details = {
                "method": random.choice(["email", "sms", "security_questions"]),
                "reset_token_used": success
            }
        elif event_type == "access_denied":
            success = False  # Access denied is always a failure
            message = "Access denied to protected resource"
            details = {
                "resource": random.choice(["admin_panel", "user_data", "payment_info"]),
                "reason": random.choice(["insufficient_permissions", "invalid_token", "expired_session"])
            }
        else:  # permission_change
            message = f"User permissions {'changed' if success else 'change failed'}"
            details = {
                "old_role": random.choice(["user", "editor", "admin"]),
                "new_role": random.choice(["user", "editor", "admin"]),
                "changed_by": f"admin_{random.randint(100, 999)}"
            }
        
        # Log the security event
        log_security_event(
            event_type=event_type,
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            success=success,
            details=details
        )

def simulate_errors() -> None:
    """Simulate errors to demonstrate error logging."""
    error_types = [
        (ValueError, "Invalid value provided"),
        (KeyError, "Missing required key"),
        (TypeError, "Type mismatch in operation"),
        (ZeroDivisionError, "Division by zero"),
        (IndexError, "Index out of range")
    ]
    
    for error_class, message in error_types:
        # Create an error instance
        error = error_class(message)
        
        # Generate random context
        context = {
            "timestamp": datetime.now().isoformat(),
            "component": random.choice(["auth", "database", "api", "processing"]),
            "operation": random.choice(["read", "write", "update", "delete"]),
            "user_id": f"user_{random.randint(1000, 9999)}" if random.random() < 0.7 else None
        }
        
        # Log the error
        log_error(
            error=error,
            message=f"An error occurred: {message}",
            context=context
        )

def basic_logging_demo() -> None:
    """Demonstrate basic logging with different levels and context."""
    # Log messages with different levels
    logger.debug("This is a debug message")
    logger.info("This is an information message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Log with additional context
    user_data = {
        "user_id": "user_1234",
        "username": "example_user",
        "email": "user@example.com",
        "roles": ["user", "editor"]
    }
    
    logger.info(
        f"User {user_data['username']} logged in", 
        extra={
            "user_id": user_data["user_id"],
            "email": user_data["email"],
            "roles": user_data["roles"],
            "login_time": datetime.now().isoformat()
        }
    )
    
    # Log structured data
    order_data = {
        "order_id": "order_5678",
        "user_id": "user_1234",
        "items": [
            {"id": "item_1", "name": "Product 1", "price": 29.99, "quantity": 2},
            {"id": "item_2", "name": "Product 2", "price": 49.99, "quantity": 1}
        ],
        "total": 109.97,
        "status": "placed"
    }
    
    logger.info(
        f"Order {order_data['order_id']} placed by user {order_data['user_id']}",
        extra={
            "order_id": order_data["order_id"],
            "user_id": order_data["user_id"],
            "total": order_data["total"],
            "item_count": sum(item["quantity"] for item in order_data["items"]),
            "status": order_data["status"]
        }
    )

def configuration_demo() -> None:
    """Demonstrate programmatic configuration updates."""
    # Show initial configuration
    logger.info("Logging with initial configuration")
    
    # Update configuration to pretty format
    update_configuration(format=LogFormat.PRETTY.value, colorize=True)
    logger.info("Logging with pretty format and colors enabled")
    
    # Update configuration to JSON format
    update_configuration(format=LogFormat.JSON.value)
    logger.info("Logging with JSON format")
    
    # Update log level
    update_configuration(level=LogLevel.DEBUG.value)
    logger.debug("This debug message should now be visible with updated log level")

def main() -> None:
    """Run the logging examples."""
    print("Centralized Logging System Example")
    print("==================================")
    print(f"Current log format: {os.environ.get('LOG_FORMAT', 'default (json)')}")
    print(f"Colorize enabled: {os.environ.get('LOG_COLORIZE', 'default (true)')}")
    print(f"File logging enabled: {os.environ.get('LOG_FILE_ENABLED', 'default (false)')}")
    if os.environ.get('LOG_FILE_ENABLED', '').lower() in ('true', 'yes', '1', 'y', 't'):
        print(f"Log file path: {os.environ.get('LOG_FILE_PATH', 'default (logs/app.log)')}")
    print()
    
    print("1. Basic Logging Demo")
    basic_logging_demo()
    print("Done\n")
    
    print("2. Performance Logging Demo")
    slow_operation(100000)
    for _ in range(5):
        sometimes_slow_operation()
    print("Done\n")
    
    print("3. Database Operation Logging Demo")
    simulate_database_queries()
    print("Done\n")
    
    print("4. HTTP Request Logging Demo")
    simulate_http_requests()
    print("Done\n")
    
    print("5. Security Event Logging Demo")
    simulate_security_events()
    print("Done\n")
    
    print("6. Error Logging Demo")
    simulate_errors()
    print("Done\n")
    
    print("7. Configuration Update Demo")
    configuration_demo()
    print("Done\n")
    
    print("Example completed. Check the console output or log file for results.")

if __name__ == "__main__":
    main() 