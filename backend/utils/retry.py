import asyncio
import functools
import random
import time
from typing import Callable, Any, Awaitable, Optional, Union, Type, List, TypeVar, cast

from backend.utils.logger import Logger

# Define generic return type
T = TypeVar('T')

class RetryOptions:
    """Configuration options for the retry mechanism."""
    
    def __init__(
        self,
        max_attempts: int = 5,
        initial_delay_ms: int = 100,
        max_delay_ms: int = 5000,
        factor: float = 2.0,
        jitter: bool = True,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
        logger: Optional[Logger] = None
    ):
        """Initialize retry options.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay_ms: Initial delay between retries in milliseconds
            max_delay_ms: Maximum delay between retries in milliseconds
            factor: Multiplicative factor for exponential backoff
            jitter: Whether to add randomness to delay times
            on_retry: Optional callback function called on each retry
            retryable_exceptions: List of exception types to retry on (retries on all exceptions if None)
            logger: Logger instance to use for logging retry attempts
        """
        self.max_attempts = max_attempts
        self.initial_delay_ms = initial_delay_ms
        self.max_delay_ms = max_delay_ms
        self.factor = factor
        self.jitter = jitter
        self.on_retry = on_retry
        self.retryable_exceptions = retryable_exceptions
        self.logger = logger or Logger.get_instance()


def _should_retry(exception: Exception, retryable_exceptions: Optional[List[Type[Exception]]]) -> bool:
    """Determine if the given exception should trigger a retry.
    
    Args:
        exception: The exception that was raised
        retryable_exceptions: List of exception types that are retryable
        
    Returns:
        True if the exception should trigger a retry, False otherwise
    """
    if retryable_exceptions is None:
        return True
    return any(isinstance(exception, exc_type) for exc_type in retryable_exceptions)


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    options: Optional[RetryOptions] = None
) -> T:
    """Retry an asynchronous function with exponential backoff.
    
    Args:
        fn: Async function to retry
        options: Retry configuration options
        
    Returns:
        The result of the function call
        
    Raises:
        The last exception raised by the function after all retry attempts fail
    """
    opts = options or RetryOptions()
    attempt = 0
    delay = opts.initial_delay_ms
    last_error = None
    
    while attempt < opts.max_attempts:
        try:
            return await fn()
        except Exception as err:
            last_error = err
            attempt += 1
            
            # Check if this exception should trigger a retry
            if not _should_retry(err, opts.retryable_exceptions):
                opts.logger.info(
                    f"Not retrying for non-retryable exception: {type(err).__name__}",
                    {"error": str(err)}
                )
                break
                
            if opts.on_retry:
                opts.on_retry(attempt, err)
                
            if attempt >= opts.max_attempts:
                opts.logger.warn(
                    f"Maximum retry attempts ({opts.max_attempts}) reached",
                    {"error": str(err), "attempt": attempt}
                )
                break
                
            sleep = delay
            if opts.jitter:
                # Add jitter of up to 25% of the delay
                jitter_amount = int(delay * 0.25)
                sleep = delay + random.randint(-jitter_amount, jitter_amount)
                sleep = max(1, sleep)  # Ensure positive delay
                
            opts.logger.info(
                f"Retry attempt {attempt}/{opts.max_attempts} failed, retrying in {sleep}ms",
                {"error": str(err), "attempt": attempt, "delay_ms": sleep}
            )
            
            await asyncio.sleep(sleep / 1000.0)
            delay = min(int(delay * opts.factor), opts.max_delay_ms)
            
    if last_error:
        raise last_error
    
    # This should be unreachable
    raise RuntimeError("Unexpected state in retry_async")


def retry_sync(
    fn: Callable[[], T],
    options: Optional[RetryOptions] = None
) -> T:
    """Retry a synchronous function with exponential backoff.
    
    Args:
        fn: Synchronous function to retry
        options: Retry configuration options
        
    Returns:
        The result of the function call
        
    Raises:
        The last exception raised by the function after all retry attempts fail
    """
    opts = options or RetryOptions()
    attempt = 0
    delay = opts.initial_delay_ms
    last_error = None
    
    while attempt < opts.max_attempts:
        try:
            return fn()
        except Exception as err:
            last_error = err
            attempt += 1
            
            # Check if this exception should trigger a retry
            if not _should_retry(err, opts.retryable_exceptions):
                opts.logger.info(
                    f"Not retrying for non-retryable exception: {type(err).__name__}",
                    {"error": str(err)}
                )
                break
                
            if opts.on_retry:
                opts.on_retry(attempt, err)
                
            if attempt >= opts.max_attempts:
                opts.logger.warn(
                    f"Maximum retry attempts ({opts.max_attempts}) reached",
                    {"error": str(err), "attempt": attempt}
                )
                break
                
            sleep = delay
            if opts.jitter:
                # Add jitter of up to 25% of the delay
                jitter_amount = int(delay * 0.25)
                sleep = delay + random.randint(-jitter_amount, jitter_amount)
                sleep = max(1, sleep)  # Ensure positive delay
                
            opts.logger.info(
                f"Retry attempt {attempt}/{opts.max_attempts} failed, retrying in {sleep}ms",
                {"error": str(err), "attempt": attempt, "delay_ms": sleep}
            )
            
            time.sleep(sleep / 1000.0)
            delay = min(int(delay * opts.factor), opts.max_delay_ms)
            
    if last_error:
        raise last_error
    
    # This should be unreachable
    raise RuntimeError("Unexpected state in retry_sync")


def retry(
    fn: Optional[Callable] = None,
    *,
    max_attempts: int = 5,
    initial_delay_ms: int = 100,
    max_delay_ms: int = 5000,
    factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[List[Type[Exception]]] = None,
    logger: Optional[Logger] = None
) -> Any:
    """Decorator for retrying functions with exponential backoff.
    
    Can be used as:
        @retry
        def my_function(): ...
        
        @retry(max_attempts=3, initial_delay_ms=200)
        def my_function(): ...
    
    Args:
        fn: The function to retry (used when decorator is called without args)
        max_attempts: Maximum number of retry attempts
        initial_delay_ms: Initial delay between retries in milliseconds
        max_delay_ms: Maximum delay between retries in milliseconds
        factor: Multiplicative factor for exponential backoff
        jitter: Whether to add randomness to delay times
        retryable_exceptions: List of exception types to retry on (retries on all exceptions if None)
        logger: Logger instance to use for logging retry attempts
        
    Returns:
        Decorated function with retry logic
    """
    # Create retry options from parameters
    options = RetryOptions(
        max_attempts=max_attempts,
        initial_delay_ms=initial_delay_ms,
        max_delay_ms=max_delay_ms,
        factor=factor,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
        logger=logger
    )
    
    # Handle case when decorator is called without arguments
    if fn is not None:
        @functools.wraps(fn)
        def wrapped_sync(*args, **kwargs):
            return retry_sync(lambda: fn(*args, **kwargs), options)
            
        @functools.wraps(fn)
        async def wrapped_async(*args, **kwargs):
            return await retry_async(lambda: fn(*args, **kwargs), options)
            
        # Determine if function is async or sync
        if asyncio.iscoroutinefunction(fn):
            return wrapped_async
        else:
            return wrapped_sync
    
    # Handle case when decorator is called with arguments
    def decorator(func):
        @functools.wraps(func)
        def wrapped_sync(*args, **kwargs):
            return retry_sync(lambda: func(*args, **kwargs), options)
            
        @functools.wraps(func)
        async def wrapped_async(*args, **kwargs):
            return await retry_async(lambda: func(*args, **kwargs), options)
            
        # Determine if function is async or sync
        if asyncio.iscoroutinefunction(func):
            return wrapped_async
        else:
            return wrapped_sync
            
    return decorator 