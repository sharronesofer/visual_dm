"""Circuit breaker implementation for search operations."""

import time
import logging
from typing import Optional, Callable, Any, Dict
from functools import wraps
from threading import Lock
from datetime import datetime, timedelta

from .config import SEARCH_SETTINGS
from .exceptions import CircuitBreakerError

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker for protecting search operations."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        half_open_timeout: int = 30
    ):
        """Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            reset_timeout: Seconds to wait before attempting reset
            half_open_timeout: Seconds to wait in half-open state
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
        self.lock = Lock()
        
    def __call__(self, func: Callable) -> Callable:
        """Decorator for protecting functions with circuit breaker.
        
        Args:
            func: Function to protect
            
        Returns:
            Protected function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                if self.state == "open":
                    if self._should_reset():
                        self._half_open()
                    else:
                        raise CircuitBreakerError(
                            f"Circuit breaker is open. "
                            f"Reset in {self._time_to_reset()} seconds."
                        )
                        
                try:
                    result = func(*args, **kwargs)
                    if self.state == "half-open":
                        self._close()
                    return result
                    
                except Exception as e:
                    self._handle_failure()
                    raise e
                    
        return wrapper
        
    def _handle_failure(self) -> None:
        """Handle a failure by incrementing counter and possibly opening circuit."""
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failures} failures"
            )
            
    def _should_reset(self) -> bool:
        """Check if enough time has passed to reset circuit.
        
        Returns:
            Whether circuit should be reset
        """
        if not self.last_failure_time:
            return True
            
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.reset_timeout
        
    def _time_to_reset(self) -> int:
        """Calculate seconds until circuit can be reset.
        
        Returns:
            Seconds until reset
        """
        if not self.last_failure_time:
            return 0
            
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0, self.reset_timeout - int(elapsed))
        
    def _half_open(self) -> None:
        """Transition to half-open state."""
        self.state = "half-open"
        self.failures = 0
        logger.info("Circuit breaker entering half-open state")
        
    def _close(self) -> None:
        """Close the circuit."""
        self.state = "closed"
        self.failures = 0
        self.last_failure_time = None
        logger.info("Circuit breaker closed")
        
    def get_state(self) -> Dict[str, Any]:
        """Get current state of circuit breaker.
        
        Returns:
            State information
        """
        return {
            "state": self.state,
            "failures": self.failures,
            "last_failure": self.last_failure_time,
            "time_to_reset": self._time_to_reset() if self.state == "open" else 0
        }

# Create circuit breaker instance with settings from config
search_breaker = CircuitBreaker(
    failure_threshold=5,
    reset_timeout=60,
    half_open_timeout=30
) if SEARCH_SETTINGS["circuit_breaker"]["enabled"] else None 