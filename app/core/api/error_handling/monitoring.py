"""Error monitoring and logging utilities."""

import logging
import json
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ErrorMonitor:
    """Error monitoring and logging utility."""
    
    def __init__(
        self,
        log_dir: str = "logs/errors",
        max_log_size: int = 10 * 1024 * 1024,  # 10MB
        max_log_files: int = 10
    ):
        """Initialize error monitor.
        
        Args:
            log_dir: Directory for error logs
            max_log_size: Maximum size of each log file in bytes
            max_log_files: Maximum number of log files to keep
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_log_size = max_log_size
        self.max_log_files = max_log_files
        
        # Set up error log file
        self.current_log_file = self._get_current_log_file()
        self._rotate_logs_if_needed()
        
    def log_error(
        self,
        error: Exception,
        request_id: str,
        request_data: Dict[str, Any],
        user_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error details.
        
        Args:
            error: Exception that occurred
            request_id: Unique request identifier
            request_data: Request context data
            user_id: Optional user identifier
            extra_data: Additional error context
        """
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "request": {
                "method": request_data.get("method"),
                "path": request_data.get("path"),
                "headers": request_data.get("headers"),
                "query_params": request_data.get("query_params"),
                "client_ip": request_data.get("client_ip")
            }
        }
        
        if user_id:
            error_data["user_id"] = user_id
            
        if extra_data:
            error_data["extra"] = extra_data
            
        self._write_error_log(error_data)
        
        # Log to application logger as well
        logger.error(
            f"Error logged: {error_data['error_type']} - {error_data['error_message']}",
            extra={
                "request_id": request_id,
                "error_data": error_data
            }
        )
        
    def get_recent_errors(
        self,
        limit: int = 100,
        error_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> list:
        """Get recent error logs.
        
        Args:
            limit: Maximum number of errors to return
            error_type: Filter by error type
            start_time: Filter errors after this time
            end_time: Filter errors before this time
            
        Returns:
            List of error log entries
        """
        errors = []
        for log_file in sorted(self.log_dir.glob("*.log"), reverse=True):
            with log_file.open() as f:
                for line in f:
                    try:
                        error = json.loads(line)
                        
                        # Apply filters
                        if error_type and error["error_type"] != error_type:
                            continue
                            
                        error_time = datetime.fromisoformat(error["timestamp"])
                        if start_time and error_time < start_time:
                            continue
                        if end_time and error_time > end_time:
                            continue
                            
                        errors.append(error)
                        if len(errors) >= limit:
                            return errors
                            
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in error log: {line}")
                        continue
                        
        return errors
        
    def get_error_stats(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get error statistics.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            Error statistics
        """
        stats = {
            "total_errors": 0,
            "error_types": {},
            "error_paths": {},
            "error_users": {}
        }
        
        for log_file in self.log_dir.glob("*.log"):
            with log_file.open() as f:
                for line in f:
                    try:
                        error = json.loads(line)
                        error_time = datetime.fromisoformat(error["timestamp"])
                        
                        # Apply time filters
                        if start_time and error_time < start_time:
                            continue
                        if end_time and error_time > end_time:
                            continue
                            
                        # Update stats
                        stats["total_errors"] += 1
                        
                        error_type = error["error_type"]
                        stats["error_types"][error_type] = stats["error_types"].get(error_type, 0) + 1
                        
                        path = error["request"]["path"]
                        stats["error_paths"][path] = stats["error_paths"].get(path, 0) + 1
                        
                        if "user_id" in error:
                            user_id = error["user_id"]
                            stats["error_users"][user_id] = stats["error_users"].get(user_id, 0) + 1
                            
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in error log: {line}")
                        continue
                        
        return stats
        
    def _get_current_log_file(self) -> Path:
        """Get current log file path.
        
        Returns:
            Path to current log file
        """
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        return self.log_dir / f"error-{current_date}.log"
        
    def _rotate_logs_if_needed(self) -> None:
        """Rotate log files if needed."""
        if not self.current_log_file.exists():
            return
            
        if self.current_log_file.stat().st_size >= self.max_log_size:
            # Rotate current file
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            rotated_file = self.log_dir / f"error-{timestamp}.log"
            self.current_log_file.rename(rotated_file)
            
            # Remove old files if needed
            log_files = sorted(self.log_dir.glob("*.log"))
            while len(log_files) > self.max_log_files:
                log_files[0].unlink()
                log_files = log_files[1:]
                
    def _write_error_log(self, error_data: Dict[str, Any]) -> None:
        """Write error data to log file.
        
        Args:
            error_data: Error data to log
        """
        self._rotate_logs_if_needed()
        
        with self.current_log_file.open("a") as f:
            f.write(json.dumps(error_data) + "\n") 