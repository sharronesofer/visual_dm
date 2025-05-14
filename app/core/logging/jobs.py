"""
Log Retention Scheduled Jobs Module.

This module provides scheduled jobs that enforce log retention policies
and handle log rotation based on the centralized retention configuration.
These jobs can be integrated with the application's task scheduler.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, List, Union

from app.core.logging.retention import (
    retention_config,
    enforce_retention_policy
)

# Set up a logger for this module
logger = logging.getLogger(__name__)

def enforce_retention_job(
    log_dirs: Optional[List[Union[str, Path]]] = None,
    recursive: bool = True
) -> int:
    """
    Scheduled job to enforce log retention policies across specified directories.
    
    Args:
        log_dirs: List of log directories to process (default: configured log directory)
        recursive: Whether to process subdirectories recursively
        
    Returns:
        Number of files processed
    """
    processed_count = 0
    
    try:
        # If no directories specified, use the configured log directory
        if not log_dirs:
            # Get the configured log directory from environment or default
            config_log_dir = os.environ.get("LOG_FILE_PATH", "logs")
            log_dirs = [Path(config_log_dir).parent]
        
        # Process each directory
        for log_dir in log_dirs:
            log_dir_path = Path(log_dir)
            
            # Process the main directory
            logger.info(f"Enforcing retention policy on directory: {log_dir_path}")
            enforce_retention_policy(log_dir_path, retention_config)
            processed_count += 1
            
            # Process subdirectories if recursive is enabled
            if recursive:
                for subdir in log_dir_path.glob("**/"):
                    if subdir != log_dir_path:  # Skip the parent directory
                        logger.debug(f"Processing subdirectory: {subdir}")
                        enforce_retention_policy(subdir, retention_config)
                        processed_count += 1
        
        logger.info(f"Retention policy enforcement completed: {processed_count} directories processed")
        return processed_count
        
    except Exception as e:
        logger.error(f"Error enforcing retention policy: {str(e)}")
        return 0

def check_archive_disk_space(
    archive_dir: Optional[Union[str, Path]] = None,
    threshold_percent: float = 90.0
) -> bool:
    """
    Check if the archive directory has sufficient disk space.
    
    Args:
        archive_dir: Directory to check (default: configured archive directory)
        threshold_percent: Warning threshold as a percentage of disk usage
        
    Returns:
        True if disk space is below threshold, False if above threshold
    """
    try:
        # If no directory specified, use the configured archive directory
        if not archive_dir:
            log_dir = os.environ.get("LOG_FILE_PATH", "logs")
            archive_dir = Path(log_dir).parent / retention_config.archive_dir
        
        # Ensure the directory exists
        archive_path = Path(archive_dir)
        if not archive_path.exists():
            archive_path.mkdir(parents=True, exist_ok=True)
        
        # Get disk usage statistics
        if sys.platform == "win32":
            # On Windows, use ctypes to get free space
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(str(archive_path)),
                None,
                ctypes.pointer(total_bytes),
                ctypes.pointer(free_bytes)
            )
            
            free_space = free_bytes.value
            total_space = total_bytes.value
        else:
            # On Unix-like systems, use os.statvfs
            stats = os.statvfs(archive_path)
            free_space = stats.f_frsize * stats.f_bavail
            total_space = stats.f_frsize * stats.f_blocks
        
        # Calculate usage percentage
        if total_space > 0:
            used_percent = 100.0 * (total_space - free_space) / total_space
        else:
            used_percent = 0.0
        
        # Log the result
        logger.info(f"Archive disk usage: {used_percent:.1f}% (threshold: {threshold_percent:.1f}%)")
        
        # Check against threshold
        if used_percent >= threshold_percent:
            logger.warning(f"Archive disk usage above threshold: {used_percent:.1f}% >= {threshold_percent:.1f}%")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking archive disk space: {str(e)}")
        return False

def cleanup_orphaned_rotated_logs(
    log_dir: Optional[Union[str, Path]] = None,
    max_age_days: int = 30
) -> int:
    """
    Clean up orphaned rotated log files that might have been missed by the normal retention process.
    
    Args:
        log_dir: Directory to scan for orphaned logs (default: configured log directory)
        max_age_days: Maximum age for orphaned files before deletion
        
    Returns:
        Number of files cleaned up
    """
    try:
        # If no directory specified, use the configured log directory
        if not log_dir:
            log_dir = os.environ.get("LOG_FILE_PATH", "logs")
        
        # Convert to Path object
        log_dir_path = Path(log_dir)
        if not log_dir_path.exists():
            logger.warning(f"Log directory does not exist: {log_dir_path}")
            return 0
        
        # Find archive directories
        archive_dirs = [
            log_dir_path / retention_config.archive_dir,  # Main archive directory
            *log_dir_path.glob(f"**/{retention_config.archive_dir}")  # Nested archive directories
        ]
        
        # Add the main log directory for rotated but not archived logs
        archive_dirs.append(log_dir_path)
        
        # Current time for age comparison
        now = time.time()
        max_age_seconds = max_age_days * 86400  # Convert days to seconds
        
        # Files to clean up
        cleanup_count = 0
        
        # Process each archive directory
        for archive_dir in archive_dirs:
            if not archive_dir.exists():
                continue
                
            logger.debug(f"Scanning directory for orphaned logs: {archive_dir}")
            
            # Look for rotated log files based on common patterns
            for pattern in ["*.log.*", "*.gz", "*.zip", "*.[0-9]", "*.[0-9][0-9]*"]:
                for file_path in archive_dir.glob(pattern):
                    # Skip directories
                    if file_path.is_dir():
                        continue
                    
                    # Check if file is orphaned (older than max age)
                    file_age_seconds = now - file_path.stat().st_mtime
                    if file_age_seconds > max_age_seconds:
                        logger.info(f"Cleaning up orphaned log file: {file_path} (age: {file_age_seconds / 86400:.1f} days)")
                        try:
                            os.remove(file_path)
                            cleanup_count += 1
                        except Exception as e:
                            logger.error(f"Error removing orphaned log file {file_path}: {str(e)}")
        
        logger.info(f"Orphaned log cleanup completed: {cleanup_count} files removed")
        return cleanup_count
        
    except Exception as e:
        logger.error(f"Error cleaning up orphaned rotated logs: {str(e)}")
        return 0

def run_maintenance_tasks() -> bool:
    """
    Run all maintenance tasks for log retention and rotation.
    
    Returns:
        True if all tasks completed successfully, False otherwise
    """
    success = True
    
    try:
        # Check disk space first
        if not check_archive_disk_space():
            logger.warning("Disk space check failed, but continuing with other maintenance tasks")
            success = False
        
        # Enforce retention policies
        if enforce_retention_job() == 0:
            logger.warning("No directories processed during retention enforcement")
            success = False
        
        # Clean up orphaned logs
        if cleanup_orphaned_rotated_logs() < 0:
            logger.warning("Error during orphaned log cleanup")
            success = False
        
        return success
        
    except Exception as e:
        logger.error(f"Error running maintenance tasks: {str(e)}")
        return False 