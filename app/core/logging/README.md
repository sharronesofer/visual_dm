# Centralized Logging System

This module provides a standardized logging configuration system for Visual DM that supports:
- Different log formats based on environment (JSON in production, colorized in development)
- Configuration via environment variables
- Consistent field inclusion across all log entries
- Enhanced context and metadata support

## Basic Usage

```python
from app.core.logging import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Log messages with different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Log with additional context
logger.info("User logged in", extra={"user_id": "12345", "ip_address": "192.168.1.1"})
```

## Specialized Logging Functions

The module provides specialized logging functions for common scenarios:

```python
from app.core.logging import log_request, log_error, log_performance, log_security_event, log_database_operation

# Log HTTP requests
log_request(
    method="GET",
    path="/api/users",
    status_code=200,
    duration=0.153,
    user_id="user123",
    request_id="req-456",
    ip_address="192.168.1.1"
)

# Log errors with context
try:
    # Some operation that might fail
    result = 1 / 0
except Exception as e:
    log_error(
        error=e,
        message="Division operation failed",
        context={"operation": "division", "operands": [1, 0]}
    )

# Log security events
log_security_event(
    event_type="login_attempt",
    message="Failed login attempt",
    user_id="user123",
    ip_address="192.168.1.1",
    success=False,
    details={"reason": "invalid_password", "attempts": 3}
)

# Log database operations
log_database_operation(
    operation="query",
    collection="users",
    query={"status": "active"},
    duration=0.045,
    affected_count=25
)
```

## Performance Logging Decorator

Use the `log_performance` decorator to log function execution time:

```python
from app.core.logging import log_performance

# Basic usage
@log_performance
def my_function():
    # Function code here
    pass

# With parameters
@log_performance(threshold_ms=100, level=logging.WARNING)
def expensive_operation():
    # Function code here
    pass
```

## Flask Integration

For Flask applications, use the Flask integration module:

```python
from flask import Flask
from app.core.logging.flask_integration import configure_flask_logging, log_flask_view

# Configure Flask logging
app = Flask(__name__)
configure_flask_logging(app)

# Log view function execution
@app.route('/api/resource')
@log_flask_view
def get_resource():
    # View function code here
    return {"status": "success"}
```

## Environment Configuration

The logging system can be configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Log level (`debug`, `info`, `warn`, `error`, `critical`) | `info` |
| `LOG_FORMAT` | Log format (`json`, `pretty`) | `json` |
| `LOG_COLORIZE` | Colorize logs in pretty format | `true` |
| `LOG_FILE_ENABLED` | Enable file logging | `false` |
| `LOG_FILE_PATH` | Path to log file | `logs/app.log` |
| `LOG_MAX_BYTES` | Maximum log file size before rotation | `10485760` (10MB) |
| `LOG_BACKUP_COUNT` | Number of backup log files to keep | `5` |
| `LOG_CONSOLE_ENABLED` | Enable console logging | `true` |
| `LOG_ADDITIONAL_FIELDS` | Additional fields to include in all logs | `` |

## Log Formats

### JSON Format (Production)

JSON format is used by default in production environments, producing structured logs:

```json
{
  "timestamp": "2023-05-12T15:42:33.123Z",
  "level": "info",
  "message": "User logged in",
  "logger_name": "auth.service",
  "module": "service",
  "function": "login_user",
  "line": 42,
  "process_id": 12345,
  "thread_id": 140735272926208,
  "user_id": "user123",
  "ip_address": "192.168.1.1"
}
```

### Pretty Format (Development)

Pretty format is used in development environments, producing human-readable logs with optional colorization:

```
2023-05-12 15:42:33 [INFO] auth.service: User logged in [user_id=user123, ip_address=192.168.1.1]
```

## Programmatic Configuration

You can programmatically update the logging configuration:

```python
from app.core.logging import update_configuration

# Update specific configuration values
update_configuration(
    level="debug",
    format="pretty",
    colorize=True,
    file_enabled=True,
    file_path="custom_logs/app.log"
)
``` 