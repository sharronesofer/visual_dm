from typing import Any
from enum import Enum


/**
 * Log levels in order of increasing severity
 */
class LogLevel(Enum):
    DEBUG = 'debug'
    INFO = 'info'
    WARN = 'warn'
    ERROR = 'error'