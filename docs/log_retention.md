# Log Retention and Rotation System

This document describes the log retention and rotation policies implemented in the Visual DM project.

## Overview

The log retention system provides standardized log management across all services by:

1. Automatically rotating log files based on size or time
2. Compressing rotated logs to save disk space
3. Archiving logs according to configurable retention periods
4. Supporting different retention policies for different log types
5. Providing legal hold functionality for compliance requirements

This system builds upon the existing centralized logging configuration system and ensures that logs are properly managed throughout their lifecycle.

## Configuration

The log retention system is configured using environment variables with the `LOG_` prefix:

### Core Retention Settings

| Environment Variable | Description | Default |
|---|---|---|
| `LOG_RETENTION_ENABLED` | Enable/disable log retention | `true` |
| `LOG_DEFAULT_RETENTION_PERIOD` | Default retention period for all logs | `daily` |
| `LOG_DEFAULT_CUSTOM_DAYS` | Default retention days when using custom period | `30` |
| `LOG_LOG_TYPES_RETENTION` | Comma-separated mapping of log types to retention periods | `""` |

### Rotation Settings

| Environment Variable | Description | Default |
|---|---|---|
| `LOG_ROTATION_TRIGGER` | Rotation trigger type: `size`, `time`, or `hybrid` | `hybrid` |
| `LOG_MAX_SIZE_BYTES` | Maximum log file size before rotation | `10485760` (10MB) |
| `LOG_BACKUP_COUNT` | Number of backup files to keep | `5` |
| `LOG_ROTATION_INTERVAL` | Time-based rotation interval: `hourly`, `daily`, `weekly`, `monthly` | `daily` |
| `LOG_ROTATION_TIME` | Specific time of day for rotation (format: `HH:MM`) | `00:00` |

### Compression and Archiving

| Environment Variable | Description | Default |
|---|---|---|
| `LOG_COMPRESSION_ENABLED` | Enable/disable compression of rotated logs | `true` |
| `LOG_COMPRESSION_LEVEL` | Compression level (1-9) | `9` |
| `LOG_ARCHIVE_DIR` | Directory for archived logs | `archives` |
| `LOG_ARCHIVE_FORMAT` | Format string for archived filenames | `{base_name}.{timestamp}.{ext}.gz` |

### Legal Hold Settings

| Environment Variable | Description | Default |
|---|---|---|
| `LOG_LEGAL_HOLD_ENABLED` | Enable/disable legal hold functionality | `false` |
| `LOG_LEGAL_HOLD_TAGS` | Comma-separated list of tags that indicate legal hold | `""` |

## Retention Periods

The system supports the following standard retention periods:

| Period | Description | Default Retention Days |
|---|---|---|
| `hourly` | Short-term logs (e.g., debug logs) | 1 day |
| `daily` | Standard application logs | 7 days |
| `weekly` | Important operational logs | 30 days |
| `monthly` | Historical data for analysis | 90 days |
| `quarterly` | Compliance and audit logs | 365 days |
| `yearly` | Critical business records | 730 days |
| `custom` | User-defined retention period | Specified in days |

## Log Type Specific Retention

You can specify different retention periods for different log types using the `LOG_LOG_TYPES_RETENTION` environment variable. The format is a comma-separated list of `logType:retentionPeriod` pairs:

```
LOG_LOG_TYPES_RETENTION=error:monthly,debug:hourly,security:quarterly,audit:yearly
```

For custom retention periods, use the format `logType:custom:days`:

```
LOG_LOG_TYPES_RETENTION=error:monthly,security:custom:90,audit:custom:1825
```

## Rotation Strategies

The system supports three rotation strategies:

1. **Size-based rotation** (`LOG_ROTATION_TRIGGER=size`): Rotates logs when they reach a specified size limit.
2. **Time-based rotation** (`LOG_ROTATION_TRIGGER=time`): Rotates logs at specified intervals (hourly, daily, weekly, etc.).
3. **Hybrid rotation** (`LOG_ROTATION_TRIGGER=hybrid`): Rotates logs based on either size or time, whichever comes first.

## Scheduled Maintenance

The system includes scheduled jobs that:

1. Enforce retention policies by deleting expired logs
2. Check disk space usage in archive directories
3. Clean up orphaned rotated logs that might have been missed

These jobs can be scheduled using your application's task scheduler or a cron job:

```python
from app.core.logging.jobs import run_maintenance_tasks

# Run maintenance tasks
success = run_maintenance_tasks()
```

## Legal Hold

Legal hold functionality allows you to protect logs from automatic deletion:

```python
from app.core.logging import place_on_legal_hold, remove_from_legal_hold

# Place matching log files on legal hold
count = place_on_legal_hold("*security*.log", "logs/")

# Remove from legal hold when no longer needed
count = remove_from_legal_hold("*security*.log", "logs/")
```

## Integration with Existing Logging

The retention system integrates with the existing logging system:

```python
from app.core.logging import get_logger, setup_retention

# Get a logger
logger = get_logger("my_module")

# Ensure retention settings are applied
setup_retention(logger)
```

Most applications won't need to call `setup_retention` directly as it's automatically applied when configuring loggers through the centralized system.

## Example Usage

See the example script at `examples/log_retention_example.py` for a complete demonstration of the log retention and rotation features.

## Implementation Details

The log retention system is implemented in:

- `app/core/logging/retention.py`: Core retention logic and configuration
- `app/core/logging/jobs.py`: Scheduled maintenance jobs
- `app/core/logging/config.py`: Integration with existing logging configuration
- `app/core/logging/__init__.py`: Package initialization and API exports 