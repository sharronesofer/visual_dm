# TypeScript to C#/Python Migration Guide

## Overview

This document serves as the comprehensive guide for migrating the Visual DM codebase from TypeScript to a dual-language architecture with Python (backend) and C# (Unity frontend). All tasks related to this migration should reference this guide for standards, patterns, and implementation details.

## Architecture

### Target Architecture
- **Backend**: Python 3.9+ with FastAPI
- **Frontend**: Unity (C#) with UniTask for async operations
- **Communication**: JSON-based REST APIs

### Directory Structure
- **Backend**: `/backend/` directory with Python modules
- **Frontend**: `/Dreamforge/Dreamforge/Assets/Scripts/` directory with C# scripts
- **Tests**: 
  - Python: `/backend/tests/`
  - C#: `/Dreamforge/Dreamforge/Assets/Tests/`

## Migration Patterns

### TypeScript to Python Migration Patterns

#### Data Types
| TypeScript | Python |
|------------|--------|
| `interface` | `@dataclass` or Pydantic `BaseModel` |
| `enum` | Python `Enum` |
| `type` | Type annotations with `typing` module |
| `Array<T>` | `List[T]` |
| `Record<K, V>` | `Dict[K, V]` |
| `undefined/null` | `None` |
| `any` | `Any` |

#### Asynchronous Code
| TypeScript | Python |
|------------|--------|
| `async/await` | `async/await` with `asyncio` |
| `Promise<T>` | Python coroutines with return type `T` |
| `Promise.all()` | `asyncio.gather()` |
| `Promise.race()` | `asyncio.wait()` with `return_when=asyncio.FIRST_COMPLETED` |

#### Error Handling
| TypeScript | Python |
|------------|--------|
| `try/catch` | `try/except` |
| `throw new Error()` | `raise Exception()` |
| Custom errors | Custom exception classes |

### TypeScript to C# Migration Patterns

#### Data Types
| TypeScript | C# |
|------------|---|
| `interface` | `interface` or `class` |
| `enum` | `enum` |
| `type` | `class` or generic type constraints |
| `Array<T>` | `List<T>` or `T[]` |
| `Record<K, V>` | `Dictionary<K, V>` |
| `undefined/null` | `null` |
| `any` | `object` or generics |

#### Asynchronous Code
| TypeScript | C# (Unity) |
|------------|-------------|
| `async/await` | `async/await` with UniTask |
| `Promise<T>` | `UniTask<T>` |
| `Promise.all()` | `UniTask.WhenAll()` |
| `Promise.race()` | `UniTask.WhenAny()` |

#### Error Handling
| TypeScript | C# |
|------------|---|
| `try/catch` | `try/catch` |
| `throw new Error()` | `throw new Exception()` |
| Custom errors | Custom exception classes |

## Core System Migration Details

### Logger System
- Python implementation: Use Python's `logging` module with custom formatter
- C# implementation: Create a `Logger` class with static methods and Unity Debug integration
- Log levels should be consistent between implementations

```python
# Python example
import logging
from typing import Optional

class Logger:
    @classmethod
    def setup(cls, level: str = "INFO") -> None:
        numeric_level = getattr(logging, level.upper(), None)
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @classmethod
    def debug(cls, message: str, context: Optional[dict] = None) -> None:
        logging.debug(message, extra={"context": context or {}})
    
    @classmethod
    def info(cls, message: str, context: Optional[dict] = None) -> None:
        logging.info(message, extra={"context": context or {}})
    
    @classmethod
    def warning(cls, message: str, context: Optional[dict] = None) -> None:
        logging.warning(message, extra={"context": context or {}})
    
    @classmethod
    def error(cls, message: str, context: Optional[dict] = None) -> None:
        logging.error(message, extra={"context": context or {}})
```

```csharp
// C# example
using System;
using UnityEngine;

public static class Logger
{
    public enum LogLevel
    {
        Debug,
        Info,
        Warning,
        Error
    }
    
    public static LogLevel CurrentLogLevel { get; private set; } = LogLevel.Info;
    
    public static void SetLogLevel(LogLevel level)
    {
        CurrentLogLevel = level;
    }
    
    public static void Debug(string message, object context = null)
    {
        if (CurrentLogLevel <= LogLevel.Debug)
            UnityEngine.Debug.Log($"[DEBUG] {message} {FormatContext(context)}");
    }
    
    public static void Info(string message, object context = null)
    {
        if (CurrentLogLevel <= LogLevel.Info)
            UnityEngine.Debug.Log($"[INFO] {message} {FormatContext(context)}");
    }
    
    public static void Warning(string message, object context = null)
    {
        if (CurrentLogLevel <= LogLevel.Warning)
            UnityEngine.Debug.LogWarning($"[WARNING] {message} {FormatContext(context)}");
    }
    
    public static void Error(string message, object context = null)
    {
        if (CurrentLogLevel <= LogLevel.Error)
            UnityEngine.Debug.LogError($"[ERROR] {message} {FormatContext(context)}");
    }
    
    private static string FormatContext(object context)
    {
        if (context == null) return string.Empty;
        return $"Context: {JsonUtility.ToJson(context)}";
    }
}
```

### Event System
- Python: Use `TypedEventEmitter` pattern with type annotations
- C# (Unity): Implement `EventBus` with generic methods and strong typing

```python
# Python example
from typing import Dict, List, Any, Callable, TypeVar, Generic

T = TypeVar('T')

class TypedEventEmitter:
    def __init__(self):
        self._events: Dict[str, List[Callable]] = {}
    
    def on(self, event_name: str, callback: Callable[[T], Any]) -> None:
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(callback)
    
    def off(self, event_name: str, callback: Callable[[T], Any]) -> None:
        if event_name in self._events and callback in self._events[event_name]:
            self._events[event_name].remove(callback)
    
    def emit(self, event_name: str, data: T) -> None:
        if event_name in self._events:
            for callback in self._events[event_name]:
                callback(data)
```

```csharp
// C# example
using System;
using System.Collections.Generic;

public static class EventBus
{
    private static Dictionary<string, List<Delegate>> _events = new Dictionary<string, List<Delegate>>();
    
    public static void Subscribe<T>(string eventName, Action<T> handler)
    {
        if (!_events.ContainsKey(eventName))
            _events[eventName] = new List<Delegate>();
        
        _events[eventName].Add(handler);
    }
    
    public static void Unsubscribe<T>(string eventName, Action<T> handler)
    {
        if (_events.ContainsKey(eventName))
            _events[eventName].Remove(handler);
    }
    
    public static void Publish<T>(string eventName, T data)
    {
        if (!_events.ContainsKey(eventName))
            return;
            
        foreach (var handler in _events[eventName])
        {
            if (handler is Action<T> typedHandler)
                typedHandler(data);
        }
    }
    
    public static void Clear()
    {
        _events.Clear();
    }
}
```

### ID Generation System

```python
# Python example
import uuid
import time
from typing import Optional

class IDGenerator:
    @classmethod
    def generate(cls, prefix: Optional[str] = None) -> str:
        """Generate a unique ID with optional prefix."""
        unique_id = f"{int(time.time())}-{uuid.uuid4().hex[:12]}"
        return f"{prefix}-{unique_id}" if prefix else unique_id
```

```csharp
// C# example
using System;

public static class IDGenerator
{
    public static string Generate(string prefix = null)
    {
        string timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
        string uniquePart = Guid.NewGuid().ToString("N").Substring(0, 12);
        string uniqueId = $"{timestamp}-{uniquePart}";
        
        return string.IsNullOrEmpty(prefix) ? uniqueId : $"{prefix}-{uniqueId}";
    }
}
```

### Retry Mechanism with Exponential Backoff

```python
# Python example
import asyncio
import logging
from typing import TypeVar, Callable, Awaitable, Optional, List, Type, Dict, Any

T = TypeVar('T')

class RetryOptions:
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay_ms: int = 100,
        max_delay_ms: int = 5000,
        backoff_factor: float = 2.0,
        retry_exceptions: Optional[List[Type[Exception]]] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay_ms = base_delay_ms
        self.max_delay_ms = max_delay_ms
        self.backoff_factor = backoff_factor
        self.retry_exceptions = retry_exceptions or [Exception]

async def retry_async(
    fn: Callable[..., Awaitable[T]],
    options: Optional[RetryOptions] = None,
    **kwargs: Any
) -> T:
    """Retry an async function with exponential backoff."""
    opts = options or RetryOptions()
    last_exception = None
    
    for attempt in range(1, opts.max_attempts + 1):
        try:
            return await fn(**kwargs)
        except Exception as e:
            last_exception = e
            should_retry = any(isinstance(e, ex) for ex in opts.retry_exceptions)
            
            if not should_retry or attempt >= opts.max_attempts:
                raise
            
            delay_ms = min(
                opts.base_delay_ms * (opts.backoff_factor ** (attempt - 1)),
                opts.max_delay_ms
            )
            logging.warning(
                f"Retry attempt {attempt}/{opts.max_attempts} after {delay_ms}ms. "
                f"Error: {str(last_exception)}"
            )
            await asyncio.sleep(delay_ms / 1000)
    
    # This should never be reached due to the raise in the except block
    raise last_exception
```

```csharp
// C# example
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Cysharp.Threading.Tasks;
using UnityEngine;

public class RetryOptions
{
    public int MaxAttempts { get; set; } = 3;
    public int BaseDelayMs { get; set; } = 100;
    public int MaxDelayMs { get; set; } = 5000;
    public float BackoffFactor { get; set; } = 2.0f;
    public List<Type> RetryExceptions { get; set; } = new List<Type> { typeof(Exception) };
}

public static class RetryUtility
{
    public static async UniTask<T> RetryAsync<T>(Func<UniTask<T>> func, RetryOptions options = null)
    {
        options ??= new RetryOptions();
        Exception lastException = null;
        
        for (int attempt = 1; attempt <= options.MaxAttempts; attempt++)
        {
            try
            {
                return await func();
            }
            catch (Exception ex)
            {
                lastException = ex;
                bool shouldRetry = false;
                
                foreach (var exceptionType in options.RetryExceptions)
                {
                    if (exceptionType.IsInstanceOfType(ex))
                    {
                        shouldRetry = true;
                        break;
                    }
                }
                
                if (!shouldRetry || attempt >= options.MaxAttempts)
                    throw;
                
                int delayMs = Mathf.Min(
                    (int)(options.BaseDelayMs * Math.Pow(options.BackoffFactor, attempt - 1)),
                    options.MaxDelayMs
                );
                
                Debug.LogWarning($"Retry attempt {attempt}/{options.MaxAttempts} after {delayMs}ms. " +
                                $"Error: {lastException.Message}");
                
                await UniTask.Delay(delayMs);
            }
        }
        
        throw lastException;
    }
}
```

## Testing Patterns

### Python Testing
- Use pytest for unit and integration tests
- Use pytest-mock for mocking dependencies
- Use pytest-asyncio for testing async code
- Follow AAA pattern (Arrange, Act, Assert)

Example:
```python
import pytest
from unittest.mock import MagicMock, patch

from backend.utils.id import IDGenerator

def test_id_generator_with_prefix():
    # Arrange
    prefix = "test"
    
    # Act
    result = IDGenerator.generate(prefix)
    
    # Assert
    assert result.startswith(f"{prefix}-")
    assert len(result) > len(prefix) + 1

@pytest.mark.asyncio
async def test_retry_with_success():
    # Arrange
    mock_fn = MagicMock()
    mock_fn.return_value = pytest.asyncio.Future()
    mock_fn.return_value.set_result("success")
    
    # Act
    from backend.utils.retry import retry_async
    result = await retry_async(mock_fn)
    
    # Assert
    assert result == "success"
    mock_fn.assert_called_once()
```

### C# Testing
- Use Unity Test Framework with NUnit
- Create EditMode tests for non-MonoBehaviour classes
- Create PlayMode tests for MonoBehaviour components
- Use NSubstitute for mocking

Example:
```csharp
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using NSubstitute;

[TestFixture]
public class IDGeneratorTests
{
    [Test]
    public void Generate_WithPrefix_StartsWithPrefix()
    {
        // Arrange
        string prefix = "test";
        
        // Act
        string result = IDGenerator.Generate(prefix);
        
        // Assert
        Assert.IsTrue(result.StartsWith($"{prefix}-"));
        Assert.IsTrue(result.Length > prefix.Length + 1);
    }
}

[UnityTest]
public IEnumerator EventBus_PublishEvent_SubscribersReceiveEvent()
{
    // Arrange
    string eventName = "TestEvent";
    string testData = "TestData";
    bool eventReceived = false;
    
    EventBus.Subscribe<string>(eventName, (data) => {
        Assert.AreEqual(testData, data);
        eventReceived = true;
    });
    
    // Act
    EventBus.Publish(eventName, testData);
    
    // Wait a frame to ensure event processing
    yield return null;
    
    // Assert
    Assert.IsTrue(eventReceived);
    
    // Cleanup
    EventBus.Clear();
}
```

## Migration Checklist

For each component being migrated, ensure the following:

1. **Functionality**
   - All original functionality is preserved
   - Edge cases are handled correctly
   - API contracts are maintained

2. **Performance**
   - Performance is equal to or better than original implementation
   - Memory usage is reasonable
   - No performance regressions are introduced

3. **Testing**
   - Unit tests are implemented and passing
   - Integration tests verify component interactions
   - Edge cases are tested

4. **Documentation**
   - Code is well-documented with comments/docstrings
   - Public APIs have clear documentation
   - Usage examples are provided for complex features

5. **Code Quality**
   - Code follows language-specific conventions and best practices
   - No code duplication or unnecessary complexity
   - Proper error handling is implemented

## References

- [Python Language Style Guide (PEP 8)](https://peps.python.org/pep-0008/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Unity C# Coding Standards](https://docs.unity3d.com/Manual/CodingGuidelines.html)
- [UniTask Documentation](https://github.com/Cysharp/UniTask)
- [Migration Architecture Overview](diagrams/target_architecture.puml) 