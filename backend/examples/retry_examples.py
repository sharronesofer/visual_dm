import asyncio
import random
import time
from typing import Optional

import aiohttp
import requests
from backend.utils.retry import retry, retry_sync, retry_async, RetryOptions
from backend.utils.logger import Logger

# Get the logger
logger = Logger.get_instance(__name__)

# Example 1: Using retry as a decorator for synchronous functions
@retry_sync(max_attempts=3, initial_delay_ms=100, max_delay_ms=1000)
def fetch_data_sync(url: str) -> dict:
    """
    Fetch data from an API synchronously with auto retry.
    Will retry up to 3 times with exponential backoff if the request fails.
    """
    logger.info(f"Fetching data from {url}")
    response = requests.get(url, timeout=5)
    
    # Raise exception for non-2xx responses
    response.raise_for_status()
    
    return response.json()

# Example 2: Using retry as a decorator for asynchronous functions
@retry_async(max_attempts=5, initial_delay_ms=200, max_delay_ms=3000)
async def fetch_data_async(url: str, session: Optional[aiohttp.ClientSession] = None) -> dict:
    """
    Fetch data from an API asynchronously with auto retry.
    Will retry up to 5 times with exponential backoff if the request fails.
    """
    logger.info(f"Async fetching data from {url}")
    
    # Create a new session if one wasn't provided
    if session is None:
        async with aiohttp.ClientSession() as session:
            return await _perform_fetch(url, session)
    else:
        return await _perform_fetch(url, session)

async def _perform_fetch(url: str, session: aiohttp.ClientSession) -> dict:
    """Helper function to perform the actual fetch."""
    async with session.get(url, timeout=5) as response:
        if response.status >= 400:
            response.raise_for_status()
        return await response.json()

# Example 3: Using retry with custom options and specific exceptions
def simulate_transient_failure(chance_of_failure: float = 0.7):
    """Simulate a function that sometimes fails with transient errors."""
    if random.random() < chance_of_failure:
        error_type = random.choice([
            ConnectionError("Connection refused"),
            TimeoutError("Request timed out"),
            requests.exceptions.RequestException("Server error")
        ])
        logger.error(f"Operation failed with error: {str(error_type)}")
        raise error_type
    
    logger.info("Operation succeeded")
    return {"status": "success", "data": "valuable data"}

def get_data_with_retry():
    """Get data using the retry mechanism with custom options."""
    retry_options = RetryOptions(
        max_attempts=4,
        initial_delay_ms=250,
        max_delay_ms=2000,
        factor=2.5,
        jitter=True,
        retryable_exceptions=[ConnectionError, TimeoutError, requests.exceptions.RequestException],
        on_retry=lambda attempt, exception: logger.warn(f"Retry attempt {attempt} after error: {str(exception)}")
    )
    
    # Using retry function directly
    result = retry_sync(retry_options=retry_options)(simulate_transient_failure)(0.7)
    return result

# Example 4: Using retry for async functions with direct configuration
async def process_data_with_retry(data_id: str) -> dict:
    """Process data with retry, demonstrating manual async retry configuration."""
    retry_options = RetryOptions(
        max_attempts=3,
        initial_delay_ms=100,
        max_delay_ms=1000,
        on_retry=lambda attempt, ex: logger.warn(f"Retry {attempt} for ID {data_id}: {str(ex)}")
    )
    
    async def _process():
        # Simulate processing that might fail
        await asyncio.sleep(0.1)
        if random.random() < 0.5:
            raise ValueError(f"Processing failed for ID {data_id}")
        return {"id": data_id, "processed": True, "timestamp": time.time()}
    
    # Using the retry function directly with an async function
    return await retry_async(retry_options=retry_options)(_process)()

# Example usage
def main():
    try:
        # Example 1: Sync function with decorator
        data = fetch_data_sync("https://jsonplaceholder.typicode.com/posts/1")
        logger.info(f"Received data: {data}")
    except Exception as e:
        logger.error(f"Failed to fetch data: {str(e)}")
    
    # Example 3: Function with direct retry configuration
    try:
        result = get_data_with_retry()
        logger.info(f"Successfully got data with retry: {result}")
    except Exception as e:
        logger.error(f"All retry attempts failed: {str(e)}")

async def async_main():
    # Example 2: Async function with decorator
    try:
        data = await fetch_data_async("https://jsonplaceholder.typicode.com/posts/1")
        logger.info(f"Received async data: {data}")
    except Exception as e:
        logger.error(f"Failed to fetch async data: {str(e)}")
    
    # Example 4: Async function with direct retry configuration
    try:
        for i in range(3):
            result = await process_data_with_retry(f"data-{i}")
            logger.info(f"Processed data {i}: {result}")
    except Exception as e:
        logger.error(f"Processing failed after retries: {str(e)}")

if __name__ == "__main__":
    # Run synchronous examples
    main()
    
    # Run asynchronous examples
    asyncio.run(async_main()) 