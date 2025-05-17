import asyncio
import time
from unittest import mock
import pytest
from backend.utils.retry import retry, retry_sync, retry_async, RetryOptions
from backend.utils.logger import Logger

# Mock logger to test logging behavior
@pytest.fixture
def mock_logger():
    with mock.patch.object(Logger, 'get_instance') as mock_get_instance:
        mock_logger = mock.MagicMock()
        mock_get_instance.return_value = mock_logger
        yield mock_logger

class TestRetryableError(Exception):
    """Exception that should trigger a retry."""
    pass

class NonRetryableError(Exception):
    """Exception that should not trigger a retry."""
    pass

class TestRetry:
    """Test suite for the retry mechanisms."""

    def test_retry_sync_success_first_try(self, mock_logger):
        """Test that a function that succeeds on first try returns the result."""
        def test_func():
            return "success"
        
        result = retry_sync(test_func)
        assert result == "success"
        mock_logger.info.assert_not_called()

    def test_retry_sync_success_after_failures(self, mock_logger):
        """Test that a function that succeeds after failures returns the result."""
        counter = 0
        
        def test_func():
            nonlocal counter
            counter += 1
            if counter < 3:
                raise TestRetryableError("Temporary error")
            return "success"
        
        result = retry_sync(test_func)
        assert result == "success"
        assert counter == 3
        assert mock_logger.info.call_count == 2

    def test_retry_sync_max_attempts_exceeded(self, mock_logger):
        """Test that max_attempts limit is respected."""
        counter = 0
        
        def test_func():
            nonlocal counter
            counter += 1
            raise TestRetryableError("Persistent error")
        
        options = RetryOptions(max_attempts=3)
        
        with pytest.raises(TestRetryableError, match="Persistent error"):
            retry_sync(test_func, options)
            
        assert counter == 3
        assert mock_logger.info.call_count == 2
        assert mock_logger.warn.call_count == 1

    def test_retry_sync_exception_filtering(self, mock_logger):
        """Test that exception filtering works as expected."""
        counter = 0
        
        def test_func():
            nonlocal counter
            counter += 1
            if counter == 1:
                raise TestRetryableError("Retryable error")
            elif counter == 2:
                raise NonRetryableError("Non-retryable error")
            return "success"
        
        options = RetryOptions(
            retryable_exceptions=[TestRetryableError],
            max_attempts=5
        )
        
        with pytest.raises(NonRetryableError, match="Non-retryable error"):
            retry_sync(test_func, options)
            
        assert counter == 2
        assert mock_logger.info.call_count == 2  # One for retry, one for non-retryable

    def test_retry_sync_callback(self):
        """Test that on_retry callback is called correctly."""
        counter = 0
        callback_counter = 0
        callback_errors = []
        
        def on_retry(attempt, error):
            nonlocal callback_counter
            callback_counter += 1
            callback_errors.append(error)
        
        def test_func():
            nonlocal counter
            counter += 1
            if counter < 3:
                raise TestRetryableError(f"Error {counter}")
            return "success"
        
        options = RetryOptions(on_retry=on_retry)
        
        result = retry_sync(test_func, options)
        
        assert result == "success"
        assert counter == 3
        assert callback_counter == 2
        assert all(isinstance(e, TestRetryableError) for e in callback_errors)
        assert str(callback_errors[0]) == "Error 1"
        assert str(callback_errors[1]) == "Error 2"

    @pytest.mark.asyncio
    async def test_retry_async_success_first_try(self, mock_logger):
        """Test that an async function that succeeds on first try returns the result."""
        async def test_func():
            return "success"
        
        result = await retry_async(test_func)
        assert result == "success"
        mock_logger.info.assert_not_called()

    @pytest.mark.asyncio
    async def test_retry_async_success_after_failures(self, mock_logger):
        """Test that an async function that succeeds after failures returns the result."""
        counter = 0
        
        async def test_func():
            nonlocal counter
            counter += 1
            if counter < 3:
                raise TestRetryableError("Temporary error")
            return "success"
        
        result = await retry_async(test_func)
        assert result == "success"
        assert counter == 3
        assert mock_logger.info.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_async_max_attempts_exceeded(self, mock_logger):
        """Test that max_attempts limit is respected for async functions."""
        counter = 0
        
        async def test_func():
            nonlocal counter
            counter += 1
            raise TestRetryableError("Persistent error")
        
        options = RetryOptions(max_attempts=3)
        
        with pytest.raises(TestRetryableError, match="Persistent error"):
            await retry_async(test_func, options)
            
        assert counter == 3
        assert mock_logger.info.call_count == 2
        assert mock_logger.warn.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_async_exception_filtering(self, mock_logger):
        """Test that exception filtering works as expected for async functions."""
        counter = 0
        
        async def test_func():
            nonlocal counter
            counter += 1
            if counter == 1:
                raise TestRetryableError("Retryable error")
            elif counter == 2:
                raise NonRetryableError("Non-retryable error")
            return "success"
        
        options = RetryOptions(
            retryable_exceptions=[TestRetryableError],
            max_attempts=5
        )
        
        with pytest.raises(NonRetryableError, match="Non-retryable error"):
            await retry_async(test_func, options)
            
        assert counter == 2
        assert mock_logger.info.call_count == 2  # One for retry, one for non-retryable

    def test_decorator_sync(self, mock_logger):
        """Test that the decorator works with sync functions."""
        counter = 0
        
        @retry(max_attempts=3)
        def test_func():
            nonlocal counter
            counter += 1
            if counter < 3:
                raise TestRetryableError("Temporary error")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert counter == 3
        assert mock_logger.info.call_count == 2

    @pytest.mark.asyncio
    async def test_decorator_async(self, mock_logger):
        """Test that the decorator works with async functions."""
        counter = 0
        
        @retry(max_attempts=3)
        async def test_func():
            nonlocal counter
            counter += 1
            if counter < 3:
                raise TestRetryableError("Temporary error")
            return "success"
        
        result = await test_func()
        assert result == "success"
        assert counter == 3
        assert mock_logger.info.call_count == 2

    def test_decorator_parameterized(self, mock_logger):
        """Test that the decorator works with parameters."""
        counter = 0
        
        @retry(
            max_attempts=2,
            initial_delay_ms=10,
            max_delay_ms=100,
            factor=2.0,
            jitter=False,
            retryable_exceptions=[TestRetryableError]
        )
        def test_func():
            nonlocal counter
            counter += 1
            if counter < 2:
                raise TestRetryableError("Temporary error")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert counter == 2
        assert mock_logger.info.call_count == 1

    def test_exponential_backoff(self):
        """Test that the exponential backoff timing works as expected."""
        counter = 0
        sleep_times = []
        
        # Mock sleep function to record times
        def mock_sleep(seconds):
            sleep_times.append(seconds)
        
        with mock.patch('time.sleep', mock_sleep):
            def test_func():
                nonlocal counter
                counter += 1
                if counter <= 3:
                    raise TestRetryableError(f"Error {counter}")
                return "success"
            
            options = RetryOptions(
                max_attempts=4,
                initial_delay_ms=100,
                max_delay_ms=1000,
                factor=2.0,
                jitter=False  # Disable jitter for predictable timing
            )
            
            result = retry_sync(test_func, options)
            
            assert result == "success"
            assert counter == 4
            
            # Convert to seconds for comparison with mocked sleep calls
            expected_delays = [0.1, 0.2, 0.4]
            
            assert len(sleep_times) == 3
            for actual, expected in zip(sleep_times, expected_delays):
                assert abs(actual - expected) < 0.001

    @pytest.mark.asyncio
    async def test_jitter(self):
        """Test that jitter adds randomness to the delay."""
        # We'll run multiple tests and check that we get different delays
        delays = set()
        
        for _ in range(10):
            counter = 0
            
            async def test_func():
                nonlocal counter
                counter += 1
                if counter == 1:
                    raise TestRetryableError("Error")
                return "success"
            
            # Mock sleep function and capture the delay
            async def mock_sleep(seconds):
                delays.add(seconds)
            
            with mock.patch('asyncio.sleep', mock_sleep):
                options = RetryOptions(
                    max_attempts=2,
                    initial_delay_ms=100,
                    jitter=True
                )
                
                await retry_async(test_func, options)
        
        # With jitter, we should have multiple different delay values
        assert len(delays) > 1 