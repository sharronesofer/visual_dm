"""
Log Retention and Rotation Module.

This module provides standardized log retention policies and automated log rotation
across all services, using centralized configuration through environment variables.
It builds upon the existing centralized logging system to ensure logs are properly
rotated, compressed, and archived based on configurable policies.
"""

import os
import sys
import time
import gzip
import shutil
import fnmatch
import logging
import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
import logging.handlers

from app.core.logging.config import LoggingConfig

# Constants
DEFAULT_MAX_AGE_DAYS = 30
DEFAULT_MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
DEFAULT_BACKUP_COUNT = 5
DEFAULT_COMPRESSION_ENABLED = True
DEFAULT_COMPRESSION_LEVEL = 9  # Maximum compression
DEFAULT_ARCHIVE_DIR = "archives"


class RetentionPeriod(Enum):
    """Standard retention periods for log files."""
    HOURLY = "hourly"
    DAILY = "daily" 
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"  # For custom day-based retention
    
    @classmethod
    def get_days(cls, period: 'RetentionPeriod', custom_days: Optional[int] = None) -> int:
        """Convert retention period to days."""
        if period == cls.CUSTOM and custom_days is not None:
            return custom_days
            
        days_map = {
            cls.HOURLY: 1,     # Keep for 1 day
            cls.DAILY: 7,      # Keep for 1 week
            cls.WEEKLY: 30,    # Keep for ~1 month
            cls.MONTHLY: 90,   # Keep for ~3 months
            cls.QUARTERLY: 365,  # Keep for 1 year
            cls.YEARLY: 730,   # Keep for 2 years
        }
        
        return days_map.get(period, DEFAULT_MAX_AGE_DAYS)


class RotationTrigger(Enum):
    """Trigger types for log rotation."""
    SIZE = "size"
    TIME = "time"
    HYBRID = "hybrid"  # Rotate on either size or time, whichever comes first


class RetentionConfig:
    """Configuration for log retention and rotation policies."""
    
    def __init__(self, env_prefix: str = "LOG_"):
        """
        Initialize retention configuration from environment variables.
        
        Args:
            env_prefix: Prefix for environment variables used for configuration
        """
        self.env_prefix = env_prefix
        self._config = {}
        self._load_from_env()
        
    def _load_from_env(self) -> None:
        """Load retention configuration from environment variables."""
        # Retention settings
        self._config["retention_enabled"] = self._parse_bool(
            self._get_env("RETENTION_ENABLED", "true")
        )
        
        # Default retention period
        self._config["default_retention_period"] = self._get_env(
            "DEFAULT_RETENTION_PERIOD", RetentionPeriod.DAILY.value
        )
        self._config["default_custom_days"] = int(
            self._get_env("DEFAULT_CUSTOM_DAYS", str(DEFAULT_MAX_AGE_DAYS))
        )
        
        # Log type specific retention periods
        log_types_retention = self._get_env("LOG_TYPES_RETENTION", "")
        self._config["log_types_retention"] = {}
        if log_types_retention:
            for mapping in log_types_retention.split(","):
                if ":" in mapping:
                    log_type, period = mapping.split(":", 1)
                    self._config["log_types_retention"][log_type.strip()] = period.strip()
        
        # Rotation settings
        self._config["rotation_trigger"] = self._get_env(
            "ROTATION_TRIGGER", RotationTrigger.HYBRID.value
        )
        self._config["max_size_bytes"] = int(
            self._get_env("MAX_SIZE_BYTES", str(DEFAULT_MAX_SIZE_BYTES))
        )
        self._config["backup_count"] = int(
            self._get_env("BACKUP_COUNT", str(DEFAULT_BACKUP_COUNT))
        )
        self._config["rotation_interval"] = self._get_env("ROTATION_INTERVAL", "daily")
        
        # Time-based rotation at specific time
        self._config["rotation_time"] = self._get_env("ROTATION_TIME", "00:00")
        
        # Compression settings
        self._config["compression_enabled"] = self._parse_bool(
            self._get_env("COMPRESSION_ENABLED", str(DEFAULT_COMPRESSION_ENABLED))
        )
        self._config["compression_level"] = int(
            self._get_env("COMPRESSION_LEVEL", str(DEFAULT_COMPRESSION_LEVEL))
        )
        
        # Archive settings
        self._config["archive_dir"] = self._get_env("ARCHIVE_DIR", DEFAULT_ARCHIVE_DIR)
        self._config["archive_format"] = self._get_env(
            "ARCHIVE_FORMAT", "{base_name}.{timestamp}.{ext}.gz"
        )
        
        # Legal hold settings
        self._config["legal_hold_enabled"] = self._parse_bool(
            self._get_env("LEGAL_HOLD_ENABLED", "false")
        )
        self._config["legal_hold_tags"] = self._get_env("LEGAL_HOLD_TAGS", "").split(",")
        
    def _get_env(self, name: str, default: str) -> str:
        """Get environment variable with prefix."""
        return os.environ.get(f"{self.env_prefix}{name}", default)
    
    def _parse_bool(self, value: str) -> bool:
        """Parse string boolean value from environment variable."""
        return value.lower() in ("true", "yes", "1", "y", "t")
    
    @property
    def retention_enabled(self) -> bool:
        """Check if retention policies are enabled."""
        return self._config["retention_enabled"]
    
    @property
    def default_retention_period(self) -> RetentionPeriod:
        """Get the default retention period."""
        try:
            return RetentionPeriod(self._config["default_retention_period"])
        except (ValueError, KeyError):
            return RetentionPeriod.DAILY
    
    @property
    def default_custom_days(self) -> int:
        """Get the default custom retention days."""
        return self._config["default_custom_days"]
    
    @property
    def log_types_retention(self) -> Dict[str, str]:
        """Get retention periods by log type."""
        return self._config["log_types_retention"]
    
    def get_retention_period(self, log_type: str) -> Tuple[RetentionPeriod, Optional[int]]:
        """
        Get the retention period for a specific log type.
        
        Args:
            log_type: The type of log (e.g., 'error', 'access', 'security')
            
        Returns:
            Tuple of (RetentionPeriod, custom_days)
        """
        if log_type in self._config["log_types_retention"]:
            period_str = self._config["log_types_retention"][log_type]
            
            # Check for custom days format (e.g., "custom:90")
            if ":" in period_str:
                period_type, days = period_str.split(":", 1)
                if period_type.lower() == RetentionPeriod.CUSTOM.value:
                    try:
                        return RetentionPeriod.CUSTOM, int(days)
                    except ValueError:
                        pass
            
            # Try to parse as enum value
            try:
                return RetentionPeriod(period_str), None
            except ValueError:
                pass
                
        # Fall back to default
        return self.default_retention_period, self.default_custom_days
    
    @property
    def rotation_trigger(self) -> RotationTrigger:
        """Get the rotation trigger type."""
        try:
            return RotationTrigger(self._config["rotation_trigger"])
        except (ValueError, KeyError):
            return RotationTrigger.HYBRID
    
    @property
    def max_size_bytes(self) -> int:
        """Get the maximum log file size before rotation."""
        return self._config["max_size_bytes"]
    
    @property
    def backup_count(self) -> int:
        """Get the number of backup files to keep."""
        return self._config["backup_count"]
    
    @property
    def rotation_interval(self) -> str:
        """Get the time-based rotation interval."""
        return self._config["rotation_interval"]
    
    @property
    def rotation_time(self) -> str:
        """Get the specific time of day for rotation."""
        return self._config["rotation_time"]
    
    @property
    def compression_enabled(self) -> bool:
        """Check if compression is enabled for rotated logs."""
        return self._config["compression_enabled"]
    
    @property
    def compression_level(self) -> int:
        """Get the compression level for rotated logs."""
        return self._config["compression_level"]
    
    @property
    def archive_dir(self) -> str:
        """Get the directory for archived logs."""
        return self._config["archive_dir"]
    
    @property
    def archive_format(self) -> str:
        """Get the format string for archived log filenames."""
        return self._config["archive_format"]
    
    @property
    def legal_hold_enabled(self) -> bool:
        """Check if legal hold functionality is enabled."""
        return self._config["legal_hold_enabled"]
    
    @property
    def legal_hold_tags(self) -> List[str]:
        """Get the tags that trigger legal hold."""
        return [tag for tag in self._config["legal_hold_tags"] if tag]
    
    def as_dict(self) -> Dict[str, Any]:
        """Get the configuration as a dictionary."""
        return self._config.copy()
    
    def update(self, **kwargs) -> None:
        """Update configuration with provided values."""
        for key, value in kwargs.items():
            if key in self._config:
                self._config[key] = value


class RotatingFileHandlerWithCompression(logging.handlers.RotatingFileHandler):
    """Enhanced RotatingFileHandler with compression for rotated logs."""
    
    def __init__(
        self,
        filename: str,
        mode: str = 'a',
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: Optional[str] = None,
        delay: bool = False,
        compression_enabled: bool = True,
        compression_level: int = 9,
        archive_dir: Optional[str] = None,
        archive_format: Optional[str] = None
    ):
        """
        Initialize with standard parameters plus compression options.
        
        Args:
            filename: Log file path
            mode: File open mode (default: 'a' for append)
            maxBytes: Maximum file size before rotation (0 for no limit)
            backupCount: Number of backup files to keep
            encoding: File encoding
            delay: Delay file creation until first log
            compression_enabled: Whether to compress rotated logs
            compression_level: Compression level (1-9, 9 is highest)
            archive_dir: Directory for archived logs (None for same directory)
            archive_format: Format string for archived filenames
        """
        super().__init__(
            filename, mode, maxBytes, backupCount, encoding, delay
        )
        self.compression_enabled = compression_enabled
        self.compression_level = compression_level
        self.archive_dir = archive_dir
        self.archive_format = archive_format
    
    def rotation_filename(self, default_name: str) -> str:
        """
        Modify the rotation filename to use the archive directory and format if specified.
        
        Args:
            default_name: Default rotated filename from parent class
            
        Returns:
            Modified filename for rotated log
        """
        # If no archive directory or format, use parent implementation
        if not self.archive_dir or not self.archive_format:
            return super().rotation_filename(default_name)
        
        # Create archive directory if it doesn't exist
        archive_path = Path(self.baseFilename).parent / self.archive_dir
        archive_path.mkdir(parents=True, exist_ok=True)
        
        # Parse default name to get components
        base_path = Path(default_name)
        base_name = base_path.stem
        if "." in base_name:
            # Handle case where there's already a backup number
            parts = base_name.split(".")
            base_name = ".".join(parts[:-1])
        
        # Get timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Format archive filename
        archive_filename = self.archive_format.format(
            base_name=base_name,
            timestamp=timestamp,
            ext=base_path.suffix.lstrip(".") or "log"
        )
        
        # Return full archive path
        return str(archive_path / archive_filename)
    
    def doRollover(self) -> None:
        """
        Override doRollover to add compression after rotation.
        """
        # Call the parent implementation first
        super().doRollover()
        
        # If compression is enabled, compress the most recently rotated file
        if self.compression_enabled and self.backupCount > 0:
            # Get the most recently rotated file
            if self.archive_dir and self.archive_format:
                # Find the most recently created file in the archive directory
                archive_path = Path(self.baseFilename).parent / self.archive_dir
                if archive_path.exists():
                    rotated_files = list(archive_path.glob(f"*{Path(self.baseFilename).stem}*"))
                    if rotated_files:
                        # Sort by creation time, most recent first
                        rotated_files.sort(key=lambda p: p.stat().st_ctime, reverse=True)
                        source_path = str(rotated_files[0])
                        # Check if it's already compressed
                        if not source_path.endswith(".gz"):
                            target_path = f"{source_path}.gz"
                            self._compress_file(source_path, target_path)
            else:
                # Standard rotation - compress the first backup
                source_path = f"{self.baseFilename}.1"
                if os.path.exists(source_path):
                    target_path = f"{source_path}.gz"
                    self._compress_file(source_path, target_path)
    
    def _compress_file(self, source_path: str, target_path: str) -> None:
        """
        Compress a log file using gzip.
        
        Args:
            source_path: Path to the file to compress
            target_path: Path where compressed file should be saved
        """
        try:
            with open(source_path, 'rb') as f_in:
                with gzip.open(target_path, 'wb', compresslevel=self.compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # If compression successful, remove the original file
            os.remove(source_path)
        except Exception as e:
            # If compression fails, log error but don't crash
            sys.stderr.write(f"Error compressing log file {source_path}: {str(e)}\n")


# Create a global retention configuration instance
retention_config = RetentionConfig()


def configure_file_handler(
    handler: logging.FileHandler,
    config: Optional[RetentionConfig] = None
) -> logging.FileHandler:
    """
    Configure a file handler with retention and rotation settings.
    
    Args:
        handler: Existing file handler to configure
        config: Retention configuration (uses global if None)
        
    Returns:
        Configured handler (may be replaced with RotatingFileHandler)
    """
    config = config or retention_config
    
    # If rotation is not enabled, return the original handler
    if not config.retention_enabled:
        return handler
    
    # Get the base filename from the existing handler
    filename = handler.baseFilename
    
    # Determine log type from filename
    log_type = "default"
    base_name = os.path.basename(filename)
    for potential_type in ["error", "access", "security", "debug", "info"]:
        if potential_type in base_name.lower():
            log_type = potential_type
            break
    
    # Create a rotating file handler to replace the standard file handler
    rotating_handler = RotatingFileHandlerWithCompression(
        filename=filename,
        mode=handler.mode,
        maxBytes=config.max_size_bytes if config.rotation_trigger in [RotationTrigger.SIZE, RotationTrigger.HYBRID] else 0,
        backupCount=config.backup_count,
        encoding=handler.encoding,
        compression_enabled=config.compression_enabled,
        compression_level=config.compression_level,
        archive_dir=config.archive_dir if config.compression_enabled else None,
        archive_format=config.archive_format
    )
    
    # Copy formatter from original handler
    if handler.formatter:
        rotating_handler.setFormatter(handler.formatter)
    
    # Copy level from original handler
    rotating_handler.setLevel(handler.level)
    
    # If using time-based rotation, add a TimedRotatingFileHandler instead
    if config.rotation_trigger in [RotationTrigger.TIME, RotationTrigger.HYBRID]:
        # Determine rotation parameters based on interval
        interval_map = {
            "hourly": ("H", 1),
            "daily": ("midnight", 1),
            "weekly": ("W0", 1),
            "monthly": ("MIDNIGHT", 30),  # Approximate
        }
        
        when, interval = interval_map.get(config.rotation_interval.lower(), ("midnight", 1))
        
        # For specific time rotation, use midnight and then roll over at the specified time
        # This could be enhanced with a more sophisticated approach if needed
        
        # Create a timed rotating handler
        timed_handler = logging.handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            interval=interval,
            backupCount=config.backup_count,
            encoding=handler.encoding
        )
        
        # Copy formatter and level
        if handler.formatter:
            timed_handler.setFormatter(handler.formatter)
        timed_handler.setLevel(handler.level)
        
        # For hybrid approach, return both handlers in a list
        if config.rotation_trigger == RotationTrigger.HYBRID:
            return [rotating_handler, timed_handler]
        else:
            return timed_handler
    
    return rotating_handler


def setup_retention(logger: logging.Logger, config: Optional[RetentionConfig] = None) -> None:
    """
    Set up retention and rotation for all file handlers on a logger.
    
    Args:
        logger: The logger to configure
        config: Retention configuration (uses global if None)
    """
    config = config or retention_config
    
    if not config.retention_enabled:
        return
    
    # Find and replace any file handlers
    for i, handler in enumerate(logger.handlers):
        if isinstance(handler, logging.FileHandler) and not isinstance(
            handler, (logging.handlers.RotatingFileHandler, logging.handlers.TimedRotatingFileHandler)
        ):
            # Configure the file handler with retention settings
            new_handler = configure_file_handler(handler, config)
            
            # Replace the handler
            logger.removeHandler(handler)
            if isinstance(new_handler, list):
                # For hybrid approach with multiple handlers
                for h in new_handler:
                    logger.addHandler(h)
            else:
                logger.addHandler(new_handler)


def enforce_retention_policy(
    log_dir: Union[str, Path], 
    config: Optional[RetentionConfig] = None
) -> None:
    """
    Enforce retention policy by removing expired log files.
    
    Args:
        log_dir: Directory containing log files
        config: Retention configuration (uses global if None)
    """
    config = config or retention_config
    
    if not config.retention_enabled:
        return
    
    log_dir = Path(log_dir)
    if not log_dir.exists() or not log_dir.is_dir():
        return
    
    # Get current time for age calculations
    now = time.time()
    
    # Process all log files in the directory and subdirectories
    for root, _, files in os.walk(str(log_dir)):
        for filename in files:
            # Skip non-log files
            if not (filename.endswith('.log') or 
                    filename.endswith('.gz') or 
                    filename.endswith('.zip')):
                continue
            
            file_path = Path(root) / filename
            
            # Skip files on legal hold if enabled
            if config.legal_hold_enabled and any(
                tag in str(file_path) for tag in config.legal_hold_tags
            ):
                continue
            
            # Determine log type from filename
            log_type = "default"
            for potential_type in ["error", "access", "security", "debug", "info"]:
                if potential_type in filename.lower():
                    log_type = potential_type
                    break
            
            # Get retention period for this log type
            retention_period, custom_days = config.get_retention_period(log_type)
            max_age_days = RetentionPeriod.get_days(retention_period, custom_days)
            max_age_seconds = max_age_days * 86400  # Convert days to seconds
            
            # Check file age
            file_age_seconds = now - os.path.getmtime(file_path)
            if file_age_seconds > max_age_seconds:
                try:
                    os.remove(file_path)
                except Exception as e:
                    sys.stderr.write(f"Error removing expired log file {file_path}: {str(e)}\n")


def place_on_legal_hold(file_pattern: str, log_dir: Union[str, Path]) -> int:
    """
    Place log files matching a pattern on legal hold.
    
    Args:
        file_pattern: Glob pattern for files to place on hold
        log_dir: Directory containing log files
        
    Returns:
        Number of files placed on legal hold
    """
    if not retention_config.legal_hold_enabled:
        return 0
    
    log_dir = Path(log_dir)
    if not log_dir.exists() or not log_dir.is_dir():
        return 0
    
    count = 0
    for root, _, files in os.walk(str(log_dir)):
        for filename in files:
            if fnmatch.fnmatch(filename, file_pattern):
                file_path = Path(root) / filename
                # Rename file to include legal hold tag
                hold_tag = retention_config.legal_hold_tags[0] if retention_config.legal_hold_tags else "LEGAL_HOLD"
                new_path = file_path.with_name(f"{hold_tag}_{filename}")
                try:
                    os.rename(file_path, new_path)
                    count += 1
                except Exception as e:
                    sys.stderr.write(f"Error placing file on legal hold {file_path}: {str(e)}\n")
    
    return count


def remove_from_legal_hold(file_pattern: str, log_dir: Union[str, Path]) -> int:
    """
    Remove log files matching a pattern from legal hold.
    
    Args:
        file_pattern: Glob pattern for files to remove from hold
        log_dir: Directory containing log files
        
    Returns:
        Number of files removed from legal hold
    """
    if not retention_config.legal_hold_enabled:
        return 0
    
    log_dir = Path(log_dir)
    if not log_dir.exists() or not log_dir.is_dir():
        return 0
    
    count = 0
    for root, _, files in os.walk(str(log_dir)):
        for filename in files:
            # Check if file is on legal hold
            is_on_hold = any(tag in filename for tag in retention_config.legal_hold_tags)
            if is_on_hold and fnmatch.fnmatch(filename, file_pattern):
                file_path = Path(root) / filename
                # Remove legal hold tag from filename
                for tag in retention_config.legal_hold_tags:
                    if tag in filename:
                        new_filename = filename.replace(f"{tag}_", "")
                        new_path = file_path.with_name(new_filename)
                        try:
                            os.rename(file_path, new_path)
                            count += 1
                            break
                        except Exception as e:
                            sys.stderr.write(f"Error removing file from legal hold {file_path}: {str(e)}\n")
    
    return count


def update_retention_configuration(**kwargs) -> None:
    """
    Update the global retention configuration.
    
    Args:
        **kwargs: Configuration parameters to update
    """
    retention_config.update(**kwargs) 