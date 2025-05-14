"""
Logging management system.
"""

import logging
import logging.handlers
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .error_handler import handle_component_error, ErrorSeverity

class LogContext:
    """Context manager for logging with additional context."""
    
    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        """Initialize log context.
        
        Args:
            logger: Logger instance
            context: Additional context to include in logs
        """
        self.logger = logger
        self.context = context
        self.old_context = {}
        
    def __enter__(self):
        """Enter context."""
        # Store old context
        self.old_context = getattr(self.logger, "context", {}).copy()
        
        # Update context
        current_context = getattr(self.logger, "context", {})
        current_context.update(self.context)
        setattr(self.logger, "context", current_context)
        
        return self.logger
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        # Restore old context
        setattr(self.logger, "context", self.old_context)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON-formatted log string
        """
        # Get basic log data
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add stack info if present
        if record.stack_info:
            log_data["stack_info"] = self.formatStack(record.stack_info)
            
        # Add custom context if present
        context = getattr(record, "context", {})
        if context:
            log_data["context"] = context
            
        return json.dumps(log_data)

class LoggingManager:
    """Manages application logging configuration."""
    
    def __init__(
        self,
        log_dir: str = "logs",
        log_level: int = logging.INFO,
        max_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ):
        """Initialize logging manager.
        
        Args:
            log_dir: Directory for log files
            log_level: Logging level
            max_size: Maximum size of log file in bytes
            backup_count: Number of backup files to keep
        """
        try:
            # Create log directory
            self.log_dir = Path(log_dir)
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Set up formatters
            json_formatter = JSONFormatter()
            
            # Set up handlers
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(json_formatter)
            console_handler.setLevel(log_level)
            
            # File handler for all logs
            all_logs_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / "app.log",
                maxBytes=max_size,
                backupCount=backup_count
            )
            all_logs_handler.setFormatter(json_formatter)
            all_logs_handler.setLevel(log_level)
            
            # File handler for errors
            error_logs_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / "error.log",
                maxBytes=max_size,
                backupCount=backup_count
            )
            error_logs_handler.setFormatter(json_formatter)
            error_logs_handler.setLevel(logging.ERROR)
            
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(log_level)
            
            # Remove existing handlers
            root_logger.handlers = []
            
            # Add handlers
            root_logger.addHandler(console_handler)
            root_logger.addHandler(all_logs_handler)
            root_logger.addHandler(error_logs_handler)
            
            # Store configuration
            self.log_level = log_level
            self.max_size = max_size
            self.backup_count = backup_count
            
            logging.info("Logging manager initialized")
            
        except Exception as e:
            handle_component_error(
                "LoggingManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def set_level(self, level: int) -> None:
        """Set logging level.
        
        Args:
            level: New logging level
        """
        try:
            self.log_level = level
            logging.getLogger().setLevel(level)
            
            logging.info(f"Logging level set to {level}")
            
        except Exception as e:
            handle_component_error(
                "LoggingManager",
                "set_level",
                e,
                ErrorSeverity.ERROR
            )
            
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger with specified name.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        try:
            logger = logging.getLogger(name)
            logger.context = {}  # Add context attribute
            return logger
            
        except Exception as e:
            handle_component_error(
                "LoggingManager",
                "get_logger",
                e,
                ErrorSeverity.ERROR
            )
            return logging.getLogger()  # Fallback to root logger
            
    def cleanup(self) -> None:
        """Clean up logging resources."""
        try:
            # Close all handlers
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
                
            logging.info("Logging manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "LoggingManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 