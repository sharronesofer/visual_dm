import pytest
import asyncio
from typing import Dict, List, Any, Optional, TypedDict, Tuple, Union, Callable, Awaitable

"""
This test file demonstrates various Python async function patterns and their correct syntax.
It serves as a reference for migrating from TypeScript's async/await patterns to Python.
These examples validate different ways to define async functions, work with async context managers,
and use proper type annotations.
"""

# Type definitions
class UserData(TypedDict):
    id: str
    name: str
    age: int

class ApiResponse(TypedDict):
    success: bool
    data: Optional[Any]
    error: Optional[str]

# Basic async function pattern
async def async_function() -> str:
    """Basic async function with return type annotation"""
    await asyncio.sleep(0.01)  # Simulate async operation
    return "Result"

# Async function with parameters
async def async_with_params(a: int, b: str, c: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Async function with parameters and return type annotation"""
    await asyncio.sleep(0.01)
    return {"a": a, "b": b, "c": c or {}}

# Async method in a class
class AsyncClass:
    def __init__(self, value: str):
        self.value = value
    
    async def async_method(self, param: int) -> str:
        """Async method with self parameter and return type"""
        await asyncio.sleep(0.01)
        return f"{self.value}_{param}"
    
    @classmethod
    async def async_class_method(cls, param: str) -> "AsyncClass":
        """Async class method with return type annotation"""
        await asyncio.sleep(0.01)
        return cls(param)
    
    @staticmethod
    async def async_static_method(a: int, b: int) -> int:
        """Async static method with return type annotation"""
        await asyncio.sleep(0.01)
        return a + b

# Async generator function
async def async_generator() -> AsyncGenerator[int, None]:
    """Async generator function with proper return type annotation"""
    for i in range(5):
        await asyncio.sleep(0.01)
        yield i

# Function that returns a coroutine
def returns_coroutine() -> Awaitable[str]:
    """Function that returns a coroutine object"""
    async def inner_coroutine() -> str:
        await asyncio.sleep(0.01)
        return "Inner result"
    
    return inner_coroutine()

# Async context manager
class AsyncContextManager:
    async def __aenter__(self) -> "AsyncContextManager":
        """Async enter method for context manager"""
        await asyncio.sleep(0.01)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async exit method for context manager"""
        await asyncio.sleep(0.01)
    
    async def operation(self) -> str:
        """Operation to perform within the context"""
        await asyncio.sleep(0.01)
        return "Context operation"

# Higher-order function with async
def higher_order_function(func: Callable[[str], Awaitable[str]]) -> Callable[[str], Awaitable[str]]:
    """Higher-order function that takes and returns an async function"""
    async def wrapper(param: str) -> str:
        print(f"Before calling {func.__name__}")
        result = await func(param)
        print(f"After calling {func.__name__}")
        return result
    return wrapper

# Decorated async function
@higher_order_function
async def decorated_async_function(param: str) -> str:
    """Async function with decorator"""
    await asyncio.sleep(0.01)
    return f"Processed {param}"

# Arrow function equivalent in Python (lambda with async)
async_lambda = lambda x: await asyncio.sleep(0.01) and f"Lambda result: {x}"

# Tests for the async patterns
@pytest.mark.asyncio
async def test_basic_async_function():
    """Test basic async function"""
    result = await async_function()
    assert result == "Result"

@pytest.mark.asyncio
async def test_async_with_params():
    """Test async function with parameters"""
    result = await async_with_params(1, "test", {"extra": "data"})
    assert result["a"] == 1
    assert result["b"] == "test"
    assert result["c"]["extra"] == "data"

@pytest.mark.asyncio
async def test_async_class_methods():
    """Test async methods in a class"""
    # Instance method
    obj = AsyncClass("value")
    result = await obj.async_method(42)
    assert result == "value_42"
    
    # Class method
    new_obj = await AsyncClass.async_class_method("new_value")
    assert isinstance(new_obj, AsyncClass)
    assert new_obj.value == "new_value"
    
    # Static method
    sum_result = await AsyncClass.async_static_method(2, 3)
    assert sum_result == 5

@pytest.mark.asyncio
async def test_async_generator():
    """Test async generator function"""
    results = []
    async for item in async_generator():
        results.append(item)
    assert results == [0, 1, 2, 3, 4]

@pytest.mark.asyncio
async def test_returns_coroutine():
    """Test function that returns a coroutine"""
    result = await returns_coroutine()
    assert result == "Inner result"

@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager"""
    async with AsyncContextManager() as manager:
        result = await manager.operation()
        assert result == "Context operation"

@pytest.mark.asyncio
async def test_higher_order_function():
    """Test higher-order function with async"""
    result = await decorated_async_function("data")
    assert result == "Processed data"

@pytest.mark.asyncio
async def test_async_lambda():
    """Test async lambda function (closest equivalent to arrow function)"""
    # Need to define it here since lambdas can't directly contain await
    async def execute_lambda(x):
        return await async_lambda(x)
    
    result = await execute_lambda("test")
    assert result == "Lambda result: test"

@pytest.mark.asyncio
async def test_parallel_execution():
    """Test parallel execution of async functions"""
    # Schedule three functions to run concurrently
    tasks = [
        async_function(),
        async_with_params(1, "test"),
        AsyncClass("value").async_method(42)
    ]
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    # Verify results
    assert results[0] == "Result"
    assert results[1]["a"] == 1
    assert results[2] == "value_42"

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in async functions"""
    async def raises_exception() -> None:
        await asyncio.sleep(0.01)
        raise ValueError("Test error")
    
    # Using try/except
    try:
        await raises_exception()
        assert False, "Exception was not raised"
    except ValueError as e:
        assert str(e) == "Test error"
    
    # Using asyncio.gather with return_exceptions=True
    results = await asyncio.gather(
        async_function(),
        raises_exception(),
        return_exceptions=True
    )
    
    assert results[0] == "Result"
    assert isinstance(results[1], ValueError)

# Run tests with: pytest -v backend/tests/test_async_function_patterns.py 