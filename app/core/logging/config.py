"""
Centralized Logging Configuration Module.

This module provides a standardized logging configuration system that supports
different formats based on environment, configurable via environment variables,
and ensures consistent field inclusion across all log entries.
"""

import os
import sys
import json
import logging
from enum import Enum, auto
from typing import Dict, Any, Optional, List, Union
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform colored terminal output
colorama.init()

# Define log levels enum that maps to Python's standard logging levels
class LogLevel(str, Enum):
    """Standard log levels with string representations for configuration."""
    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warn"
    ERROR = "error"
    CRITICAL = "critical"
    
    @classmethod
    def from_string(cls, level_str: str) -> int:
        """Convert string log level to logging module constant."""
        level_map = {
            cls.DEBUG: logging.DEBUG,
            cls.INFO: logging.INFO,
            cls.WARNING: logging.WARNING,
            cls.ERROR: logging.ERROR,
            cls.CRITICAL: logging.CRITICAL
        }
        
        normalized = level_str.lower()
        if normalized in level_map:
            return level_map[normalized]
        
        # Default to INFO if invalid level provided
        return logging.INFO

class LogFormat(str, Enum):
    """Log format types supported by the configuration."""
    JSON = "json"
    PRETTY = "pretty"
    
    @classmethod
    def from_string(cls, format_str: str) -> 'LogFormat':
        """Convert string format to enum value with validation."""
        normalized = format_str.lower()
        for fmt in cls:
            if normalized == fmt.value:
                return fmt
                
        # Default to JSON if invalid format provided
        return cls.JSON

class ColorScheme:
    """Color scheme for pretty log formatting."""
    LEVEL_COLORS = {
        LogLevel.DEBUG: Fore.CYAN,
        LogLevel.INFO: Fore.GREEN,
        LogLevel.WARNING: Fore.YELLOW,
        LogLevel.ERROR: Fore.RED,
        LogLevel.CRITICAL: Fore.RED + Style.BRIGHT
    }
    
    FIELD_NAME_COLOR = Fore.BLUE
    TIMESTAMP_COLOR = Fore.MAGENTA
    RESET = Style.RESET_ALL
    
    @classmethod
    def colorize_level(cls, level: str) -> str:
        """Apply color to a log level string."""
        level_lower = level.lower()
        for log_level, color in cls.LEVEL_COLORS.items():
            if level_lower == log_level.value:
                return f"{color}{level.upper()}{cls.RESET}"
        return level.upper()  # No color if level unknown

class LoggingConfig:
    """Centralized logging configuration manager."""
    
    def __init__(self, env_prefix: str = "LOG_"):
        """
        Initialize logging configuration from environment variables.
        
        Args:
            env_prefix: Prefix for environment variables used for configuration
        """
        self.env_prefix = env_prefix
        self._config = {}
        self._load_from_env()
        
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Core logging settings
        self._config["level"] = self._get_env("LEVEL", LogLevel.INFO.value)
        self._config["format"] = self._get_env("FORMAT", LogFormat.JSON.value)
        self._config["colorize"] = self._parse_bool(self._get_env("COLORIZE", "true"))
        
        # File logging settings
        self._config["file_enabled"] = self._parse_bool(self._get_env("FILE_ENABLED", "false"))
        self._config["file_path"] = self._get_env("FILE_PATH", "logs/app.log")
        self._config["max_bytes"] = int(self._get_env("MAX_BYTES", "10485760"))  # 10MB
        self._config["backup_count"] = int(self._get_env("BACKUP_COUNT", "5"))
        
        # Console logging settings
        self._config["console_enabled"] = self._parse_bool(self._get_env("CONSOLE_ENABLED", "true"))
        
        # Required fields for all log entries
        self._config["required_fields"] = [
            "timestamp", "level", "message", "logger_name"
        ]
        
        # Additional metadata fields
        additional_fields = self._get_env("ADDITIONAL_FIELDS", "")
        if additional_fields:
            self._config["additional_fields"] = [f.strip() for f in additional_fields.split(",")]
        else:
            self._config["additional_fields"] = []
            
    def _get_env(self, name: str, default: str) -> str:
        """Get environment variable with prefix."""
        return os.environ.get(f"{self.env_prefix}{name}", default)
    
    def _parse_bool(self, value: str) -> bool:
        """Parse string boolean value from environment variable."""
        return value.lower() in ("true", "yes", "1", "y", "t")
    
    @property
    def level(self) -> int:
        """Get the configured log level as a logging module constant."""
        return LogLevel.from_string(self._config["level"])
    
    @property
    def format(self) -> LogFormat:
        """Get the configured log format."""
        return LogFormat.from_string(self._config["format"])
    
    @property
    def colorize(self) -> bool:
        """Get whether logs should be colorized (for pretty format)."""
        return self._config["colorize"]
    
    @property
    def file_enabled(self) -> bool:
        """Get whether file logging is enabled."""
        return self._config["file_enabled"]
    
    @property
    def file_path(self) -> str:
        """Get the log file path."""
        return self._config["file_path"]
    
    @property
    def max_bytes(self) -> int:
        """Get the maximum log file size in bytes."""
        return self._config["max_bytes"]
    
    @property
    def backup_count(self) -> int:
        """Get the number of backup log files to keep."""
        return self._config["backup_count"]
    
    @property
    def console_enabled(self) -> bool:
        """Get whether console logging is enabled."""
        return self._config["console_enabled"]
    
    @property
    def required_fields(self) -> List[str]:
        """Get the list of required fields for all log entries."""
        return self._config["required_fields"]
    
    @property
    def additional_fields(self) -> List[str]:
        """Get the list of additional metadata fields for log entries."""
        return self._config["additional_fields"]
    
    def as_dict(self) -> Dict[str, Any]:
        """Get the configuration as a dictionary."""
        return self._config.copy()
    
    def update(self, **kwargs) -> None:
        """Update configuration with provided values."""
        for key, value in kwargs.items():
            if key in self._config:
                self._config[key] = value

# Create JSON formatter for production environments
class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""
    
    def __init__(self, config: LoggingConfig):
        """Initialize with logging configuration."""
        super().__init__()
        self.config = config
        
    def format(self, record: logging.LogRecord) -> str:
        """Format LogRecord as JSON string."""
        log_data = {
            # Required fields
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger_name": record.name,
            
            # Standard fields
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Add extra fields from record
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_data.update(record.extra)
            
        # Add any additional fields from record attributes
        for field in self.config.additional_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)
                
        return json.dumps(log_data)

# Create colorized formatter for development environments
class ColorizedFormatter(logging.Formatter):
    """Pretty formatter with color support for development environments."""
    
    def __init__(self, config: LoggingConfig):
        """Initialize with logging configuration."""
        super().__init__()
        self.config = config
        self.use_colors = config.colorize and sys.stdout.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format LogRecord as a human-readable string with optional colors."""
        # Format timestamp
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        if self.use_colors:
            timestamp = f"{ColorScheme.TIMESTAMP_COLOR}{timestamp}{ColorScheme.RESET}"
        
        # Format level with color
        level = record.levelname.upper()
        if self.use_colors:
            level = ColorScheme.colorize_level(record.levelname.lower())
        
        # Format basic log message
        message = record.getMessage()
        formatted = f"{timestamp} | {level} | {record.name} - {message}"
        
        # Add exception information if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            formatted += f"\n{exc_text}"
            
        # Add extra fields if present
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            extra_str = "\n"
            for key, value in sorted(record.extra.items()):
                # Skip non-scalar values for readability
                if isinstance(value, (str, int, float, bool)) or value is None:
                    field_name = key
                    if self.use_colors:
                        field_name = f"{ColorScheme.FIELD_NAME_COLOR}{key}{ColorScheme.RESET}"
                    extra_str += f"  {field_name}: {value}\n"
                elif isinstance(value, (list, dict)) and len(str(value)) < 50:
                    # Include short lists/dicts
                    field_name = key
                    if self.use_colors:
                        field_name = f"{ColorScheme.FIELD_NAME_COLOR}{key}{ColorScheme.RESET}"
                    extra_str += f"  {field_name}: {value}\n"
                else:
                    # Just indicate complex type
                    field_name = key
                    if self.use_colors:
                        field_name = f"{ColorScheme.FIELD_NAME_COLOR}{key}{ColorScheme.RESET}"
                    value_type = type(value).__name__
                    extra_str += f"  {field_name}: <{value_type}>\n"
                    
            formatted += extra_str
                
        return formatted

def get_formatter(format_type: Optional[LogFormat] = None) -> logging.Formatter:
    """
    Get a formatter based on the specified format type.
    
    Args:
        format_type: Format type (JSON or PRETTY)
        
    Returns:
        Configured formatter instance
    """
    format_type = format_type or logging_config.format
    
    if format_type == LogFormat.JSON:
        return JsonFormatter(logging_config)
    else:
        return ColorizedFormatter(logging_config)

# Define a global logging configuration
logging_config = LoggingConfig()

def configure_logger(logger: logging.Logger, config: Optional[LoggingConfig] = None) -> None:
    """
    Configure a logger with the specified configuration.
    
    Args:
        logger: Logger instance to configure
        config: Logging configuration (uses global if None)
    """
    config = config or logging_config
    
    # Set the log level
    logger.setLevel(config.level)
    
    # Clear any existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    
    # Add console handler if enabled
    if config.console_enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(get_formatter(config.format))
        logger.addHandler(console_handler)
    
    # Add file handler if enabled
    if config.file_enabled:
        # Create directory for log file if it doesn't exist
        log_dir = os.path.dirname(config.file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler
        file_handler = logging.FileHandler(config.file_path)
        file_handler.setFormatter(get_formatter(LogFormat.JSON))  # Always use JSON for files
        logger.addHandler(file_handler)
        
        # Add retention and rotation if the module is available
        try:
            from app.core.logging.retention import setup_retention
            setup_retention(logger)
        except ImportError:
            # Retention module not available, continue without it
            pass
    
    # Don't propagate to parent loggers to avoid duplicate logs
    logger.propagate = False

def update_configuration(**kwargs) -> None:
    """
    Update the global logging configuration.
    
    Args:
        **kwargs: Configuration parameters to update
    """
    logging_config.update(**kwargs)
    
    # Update the root logger with the new configuration
    root_logger = logging.getLogger()
    configure_logger(root_logger, logging_config) 