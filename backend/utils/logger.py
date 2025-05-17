import logging
import json
import sys
import os
import asyncio
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any, Union, List
from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warn'
    ERROR = 'error'
    CRITICAL = 'critical'

class LogHandler:
    def handle(self, entry: Dict[str, Any]) -> None:
        pass

class ConsoleLogHandler(LogHandler):
    def handle(self, entry: Dict[str, Any]) -> None:
        level = entry.get('level', 'info')
        message = entry.get('message', '')
        timestamp = entry.get('timestamp', '')
        context = entry.get('context')
        error = entry.get('error')
        
        formatted_message = f"[{timestamp}] [{level.upper()}] {message}"
        
        if context:
            formatted_message += f" {json.dumps(context)}"
            
        log_function = getattr(sys.stdout, 'write')
        if level in ['error', 'critical']:
            log_function = getattr(sys.stderr, 'write')
            
        log_function(formatted_message + '\n')
        if error:
            log_function(f"{error}\n")

class JsonLogHandler(LogHandler):
    def __init__(self, file_path: str = 'logs/app.log', max_bytes: int = 10485760, backup_count: int = 5):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
        
    def handle(self, entry: Dict[str, Any]) -> None:
        json_line = json.dumps(entry) + '\n'
        self.handler.stream.write(json_line)
        self.handler.stream.flush()

class AsyncLogHandler(LogHandler):
    def __init__(self, handler: LogHandler):
        self.handler = handler
        self.queue = asyncio.Queue()
        self.running = False
        self.worker_task = None
        
    async def worker(self):
        while self.running:
            try:
                entry = await self.queue.get()
                if entry is None:  # Sentinel to stop the worker
                    break
                self.handler.handle(entry)
                self.queue.task_done()
            except Exception as e:
                print(f"Error in async log worker: {e}")
                
    def handle(self, entry: Dict[str, Any]) -> None:
        if not self.running:
            self.start()
        asyncio.create_task(self.queue.put(entry))
        
    def start(self):
        if not self.running:
            self.running = True
            self.worker_task = asyncio.create_task(self.worker())
            
    def stop(self):
        if self.running:
            self.running = False
            asyncio.create_task(self.queue.put(None))  # Send sentinel

class Logger:
    _instance: Optional['Logger'] = None

    def __init__(self, 
                 level: Union[LogLevel, str] = LogLevel.INFO, 
                 prefix: str = '', 
                 metadata: Optional[Dict[str, Any]] = None,
                 enable_console: bool = True,
                 enable_json: bool = False,
                 enable_async: bool = False,
                 json_log_path: str = 'logs/app.log',
                 custom_handlers: Optional[List[LogHandler]] = None):
        
        self.level = level if isinstance(level, LogLevel) else getattr(LogLevel, level.upper(), LogLevel.INFO)
        self.prefix = prefix
        self.metadata = metadata or {}
        self.handlers = []
        
        # Configure handlers
        if enable_console:
            self.handlers.append(ConsoleLogHandler())
            
        if enable_json:
            json_handler = JsonLogHandler(file_path=json_log_path)
            self.handlers.append(json_handler)
            
        if custom_handlers:
            self.handlers.extend(custom_handlers)
            
        # Wrap handlers with async if requested
        if enable_async:
            self.handlers = [AsyncLogHandler(h) for h in self.handlers]
        
        # Set up standard Python logger for compatibility
        self._logger = logging.getLogger(prefix or 'root')
        self._set_log_level(self.level)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.propagate = False

    @classmethod
    def get_instance(cls, **kwargs) -> 'Logger':
        if cls._instance is None:
            cls._instance = Logger(**kwargs)
        return cls._instance

    def child(self, prefix: str, metadata: Optional[Dict[str, Any]] = None) -> 'Logger':
        child_prefix = f"{self.prefix}:{prefix}" if self.prefix else prefix
        child_metadata = {**self.metadata, **(metadata or {})}
        
        # Create a new logger but keep the same handlers
        child_logger = Logger(
            level=self.level, 
            prefix=child_prefix, 
            metadata=child_metadata,
            enable_console=False,  # Don't add default handlers
            enable_json=False,
            enable_async=False
        )
        
        # Copy the handlers
        child_logger.handlers = self.handlers
        
        return child_logger

    def add_handler(self, handler: LogHandler) -> None:
        """Add a custom log handler"""
        self.handlers.append(handler)
        
    def remove_handler(self, handler: LogHandler) -> None:
        """Remove a log handler"""
        if handler in self.handlers:
            self.handlers.remove(handler)

    def _create_entry(self, level: Union[LogLevel, str], message: str, context: Any = None, error: Optional[Exception] = None) -> Dict[str, Any]:
        level_str = level.value if isinstance(level, LogLevel) else level
        
        entry = {
            'level': level_str,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'prefix': self.prefix
        }
        
        # Add context data if provided
        if context:
            if isinstance(context, dict):
                entry['context'] = context
            else:
                entry['context'] = {'data': str(context)}
                
        # Add metadata from logger
        if self.metadata:
            entry['metadata'] = self.metadata
            
        # Add error information if provided
        if error:
            entry['error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': getattr(error, '__traceback__', None)
            }
            
        return entry

    def log(self, level: Union[LogLevel, str], message: str, context: Any = None, error: Optional[Exception] = None) -> None:
        """Generic logging method that handles any log level"""
        # Skip if log level is below current threshold
        level_obj = level if isinstance(level, LogLevel) else getattr(LogLevel, level.upper(), LogLevel.INFO)
        current_level_obj = self.level if isinstance(self.level, LogLevel) else getattr(LogLevel, self.level.upper(), LogLevel.INFO)
        
        level_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        if level_order.index(level_obj) < level_order.index(current_level_obj):
            return
            
        # Create log entry
        entry = self._create_entry(level, message, context, error)
        
        # Send to handlers
        for handler in self.handlers:
            try:
                handler.handle(entry)
            except Exception as e:
                print(f"Error in log handler: {e}")

    def debug(self, message: str, context: Any = None) -> None:
        self.log(LogLevel.DEBUG, message, context)

    def info(self, message: str, context: Any = None) -> None:
        self.log(LogLevel.INFO, message, context)

    def warn(self, message: str, context: Any = None) -> None:
        self.log(LogLevel.WARNING, message, context)

    def error(self, message: str, error: Optional[Exception] = None, context: Any = None) -> None:
        self.log(LogLevel.ERROR, message, context, error)
        
    def critical(self, message: str, error: Optional[Exception] = None, context: Any = None) -> None:
        self.log(LogLevel.CRITICAL, message, context, error)

    def set_level(self, level: Union[LogLevel, str]) -> None:
        """Set the minimum log level"""
        self.level = level if isinstance(level, LogLevel) else getattr(LogLevel, level.upper(), LogLevel.INFO)
        self._set_log_level(self.level)

    def get_level(self) -> Union[LogLevel, str]:
        """Get the current log level"""
        return self.level

    def _set_log_level(self, level: Union[LogLevel, str]) -> None:
        """Set the standard Python logger level for compatibility"""
        level_str = level.value if isinstance(level, LogLevel) else level
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warn': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        self._logger.setLevel(level_map.get(level_str, logging.INFO))

    def shutdown(self) -> None:
        """Properly shutdown the logger, closing async handlers"""
        for handler in self.handlers:
            if hasattr(handler, 'stop'):
                handler.stop()

# Default logger instance with console output
logger = Logger.get_instance(enable_console=True) 