#!/usr/bin/env python3
"""
Example script demonstrating the log retention and rotation features.

This script shows how to use the log retention and rotation capabilities
provided by the app.core.logging.retention module, including customizing
retention periods, working with different rotation strategies, and using
legal holds.

To try different log retention settings, run with environment variables:
- For size-based rotation: LOG_ROTATION_TRIGGER=size LOG_MAX_SIZE_BYTES=1024 python examples/log_retention_example.py
- For time-based rotation: LOG_ROTATION_TRIGGER=time LOG_ROTATION_INTERVAL=hourly python examples/log_retention_example.py
- For hybrid rotation: LOG_ROTATION_TRIGGER=hybrid python examples/log_retention_example.py
- For custom retention periods: LOG_LOG_TYPES_RETENTION=error:monthly,debug:hourly python examples/log_retention_example.py

To enable legal hold functionality:
- LOG_LEGAL_HOLD_ENABLED=true python examples/log_retention_example.py
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path

# Import the logging system
from app.core.logging import (
    get_logger,
    RetentionConfig,
    RetentionPeriod,
    RotationTrigger,
    retention_config,
    setup_retention,
    enforce_retention_policy,
    place_on_legal_hold,
    remove_from_legal_hold,
    update_retention_configuration
)

# Set environment variables to enable file logging if not already set
if "LOG_FILE_ENABLED" not in os.environ:
    os.environ["LOG_FILE_ENABLED"] = "true"

# Set log file paths for different log types
log_dir = Path("logs/retention_example")
log_dir.mkdir(parents=True, exist_ok=True)

# Create loggers for different log types
app_logger = get_logger("app")
error_logger = get_logger("error")
security_logger = get_logger("security")
debug_logger = get_logger("debug")

# Configure file handlers with different file paths for demonstration
for name, logger in [
    ("app", app_logger),
    ("error", error_logger),
    ("security", security_logger),
    ("debug", debug_logger)
]:
    # Remove existing handlers
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    
    # Add a new file handler
    file_path = log_dir / f"{name}.log"
    handler = logging.FileHandler(str(file_path))
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    # Apply retention and rotation settings
    setup_retention(logger)

def print_retention_config():
    """Print the current retention configuration."""
    print("\n=== Current Retention Configuration ===")
    print(f"Retention Enabled: {retention_config.retention_enabled}")
    print(f"Default Retention Period: {retention_config.default_retention_period.value} "
          f"({RetentionPeriod.get_days(retention_config.default_retention_period)} days)")
    print(f"Rotation Trigger: {retention_config.rotation_trigger.value}")
    print(f"Max Size: {retention_config.max_size_bytes / 1024:.1f} KB")
    print(f"Backup Count: {retention_config.backup_count}")
    print(f"Rotation Interval: {retention_config.rotation_interval}")
    print(f"Compression Enabled: {retention_config.compression_enabled}")
    
    if retention_config.log_types_retention:
        print("\nLog Type Specific Retention Periods:")
        for log_type, period in retention_config.log_types_retention.items():
            print(f"  {log_type}: {period}")
    
    if retention_config.legal_hold_enabled:
        print("\nLegal Hold Enabled")
        if retention_config.legal_hold_tags:
            print(f"Legal Hold Tags: {', '.join(retention_config.legal_hold_tags)}")
    
    print("=======================================")

def generate_log_entries(count=100, delay=0.01):
    """Generate a series of log entries across different loggers."""
    print(f"\nGenerating {count} log entries...")
    
    for i in range(count):
        # Cycle between different log types and levels
        if i % 4 == 0:
            app_logger.info(f"Application info message #{i}: Normal application event")
        elif i % 4 == 1:
            error_logger.error(f"Error message #{i}: Something went wrong", 
                              extra={"error_code": i % 10, "source": "example"})
        elif i % 4 == 2:
            security_logger.warning(f"Security warning #{i}: Unusual access pattern detected", 
                                  extra={"ip": f"192.168.1.{i % 255}", "user_id": f"user_{i}"})
        else:
            debug_logger.debug(f"Debug message #{i}: Detailed debugging information", 
                              extra={"trace_id": f"TRACE-{i}", "duration_ms": i * 2.5})
        
        # Add small delay to ensure log files grow gradually
        if delay > 0:
            time.sleep(delay)

def demonstrate_rotation():
    """Demonstrate log file rotation."""
    print("\n=== Demonstrating Log Rotation ===")
    
    if retention_config.rotation_trigger == RotationTrigger.SIZE:
        print(f"Using SIZE-based rotation (max {retention_config.max_size_bytes / 1024:.1f} KB)")
        # Generate enough logs to trigger rotation
        generate_log_entries(500, 0) 
    
    elif retention_config.rotation_trigger == RotationTrigger.TIME:
        print(f"Using TIME-based rotation (interval: {retention_config.rotation_interval})")
        print("For demonstration purposes, manually creating a rotation scenario...")
        
        # Since we can't easily wait for a time-based rotation in an example,
        # we'll simulate it by generating logs, then manually rotating
        generate_log_entries(50, 0)
        
        # Find all file handlers in the security logger and force a rollover if possible
        rotated = False
        for handler in security_logger.handlers:
            if hasattr(handler, 'doRollover'):
                handler.doRollover()
                rotated = True
                print("Manually triggered rotation for demonstration purposes")
                break
        
        if not rotated:
            print("Could not manually trigger rotation (handler doesn't support doRollover)")
    
    else:  # HYBRID
        print(f"Using HYBRID rotation (size or time, whichever comes first)")
        generate_log_entries(200, 0)
        
        # Try to manually rotate one logger for demonstration
        for handler in app_logger.handlers:
            if hasattr(handler, 'doRollover'):
                handler.doRollover()
                print("Manually triggered rotation for demonstration purposes")
                break
    
    print("\nCheck the logs directory for rotated log files")
    list_log_files()

def demonstrate_legal_hold():
    """Demonstrate legal hold functionality."""
    if not retention_config.legal_hold_enabled:
        print("\n=== Legal Hold Demonstration Skipped (Not Enabled) ===")
        print("To enable, set environment variable: LOG_LEGAL_HOLD_ENABLED=true")
        return
    
    print("\n=== Demonstrating Legal Hold ===")
    
    # Generate some logs first
    generate_log_entries(20, 0)
    
    # Put security logs on legal hold
    print("\nPlacing security logs on legal hold...")
    count = place_on_legal_hold("security*.log", log_dir)
    print(f"Placed {count} files on legal hold")
    
    # List files to show the change
    list_log_files()
    
    # Try to enforce retention policy (should skip legal hold files)
    print("\nEnforcing retention policy (legal hold files should be protected)...")
    enforce_retention_policy(log_dir)
    
    # List files to show the files are still there
    list_log_files()
    
    # Remove from legal hold
    print("\nRemoving files from legal hold...")
    count = remove_from_legal_hold("*security*.log", log_dir)
    print(f"Removed {count} files from legal hold")
    
    # List files to show the change
    list_log_files()

def list_log_files():
    """List all log files in the example directory."""
    print("\nCurrent log files:")
    for file_path in sorted(log_dir.glob("*")):
        size_kb = file_path.stat().st_size / 1024
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {file_path.name} ({size_kb:.1f} KB, modified: {mtime})")

def demonstrate_custom_retention():
    """Demonstrate custom retention periods for different log types."""
    print("\n=== Demonstrating Custom Retention Periods ===")
    
    # Update retention configuration to use custom periods
    original_config = retention_config.log_types_retention.copy()
    
    update_retention_configuration(
        log_types_retention={
            "error": RetentionPeriod.MONTHLY.value,
            "debug": RetentionPeriod.HOURLY.value,
            "app": RetentionPeriod.WEEKLY.value,
            "security": f"{RetentionPeriod.CUSTOM.value}:60"  # Custom 60 days
        }
    )
    
    print("Updated retention periods:")
    for log_type, period in retention_config.log_types_retention.items():
        retention_period, custom_days = retention_config.get_retention_period(log_type)
        days = RetentionPeriod.get_days(retention_period, custom_days)
        print(f"  {log_type}: {period} ({days} days)")
    
    # Create some log files with different timestamps to demonstrate
    print("\nCreating some old log files for demonstration...")
    now = time.time()
    
    # Create an "old" debug log file (past retention period)
    old_debug = log_dir / "debug.old.log"
    with open(old_debug, "w") as f:
        f.write("Old debug log - should be deleted by retention policy\n")
    
    # Set modification time to 2 days ago (past hourly retention)
    os.utime(old_debug, (now, now - 2 * 86400))
    
    # Create an "old" error log file (within retention period)
    old_error = log_dir / "error.old.log"
    with open(old_error, "w") as f:
        f.write("Old error log - should be kept by retention policy\n")
    
    # Set modification time to 15 days ago (within monthly retention)
    os.utime(old_error, (now, now - 15 * 86400))
    
    # List files to show what we created
    list_log_files()
    
    # Enforce retention policy
    print("\nEnforcing retention policy...")
    enforce_retention_policy(log_dir)
    
    # List files to show what was kept/deleted
    list_log_files()
    
    # Restore original configuration
    update_retention_configuration(log_types_retention=original_config)

def main():
    """Main demonstration function."""
    print("Log Retention and Rotation Example")
    print("==================================")
    
    # Print current configuration
    print_retention_config()
    
    # Demonstrate log rotation
    demonstrate_rotation()
    
    # Demonstrate custom retention periods for different log types
    demonstrate_custom_retention()
    
    # Demonstrate legal hold functionality
    demonstrate_legal_hold()
    
    print("\nExample completed. Check the logs directory for generated files.")

if __name__ == "__main__":
    main() 