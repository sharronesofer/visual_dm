# Retry Mechanisms Documentation

This document provides comprehensive guidance on using the retry mechanisms implemented in both Python (backend) and C# (Unity client) codebases.

## Table of Contents

- [Overview](#overview)
- [Python Retry Implementation](#python-retry-implementation)
  - [Features](#python-features)
  - [Usage Patterns](#python-usage-patterns)
  - [Best Practices](#python-best-practices)
  - [Examples](#python-examples)
- [C# Unity Retry Implementation](#c-unity-retry-implementation)
  - [Features](#csharp-features)
  - [Usage Patterns](#csharp-usage-patterns)
  - [Best Practices](#csharp-best-practices)
  - [Examples](#csharp-examples)
- [Common Retry Strategy Considerations](#common-retry-strategy-considerations)

## Overview

Transient failures are common in distributed systems, including network timeouts, temporary service unavailability, and rate limiting. Implementing retry mechanisms with exponential backoff helps build resilient applications that can recover from these failures automatically.

Our implementations provide:

- Configurable retry policies with exponential backoff
- Support for synchronous and asynchronous operations
- Jitter to prevent "thundering herd" problems
- Comprehensive logging
- Exception filtering

## Python Retry Implementation

The Python retry mechanism is implemented in `backend/utils/retry.py`.

### Python Features

- **Decorators**: Use as function decorators for both sync and async functions
- **Exponential Backoff**: Configurable initial delay, maximum delay, and multiplier
- **Jitter**: Random delay variations to prevent synchronized retries
- **Exception Filtering**: Specify which exceptions should trigger retries
- **Retry Callbacks**: Custom logic executed on each retry attempt
- **Logging Integration**: Built-in logging of retry attempts and results
- **Type Annotations**: Full typing support for better IDE integration

### Python Usage Patterns

#### 1. Decorator Syntax

```python
# Simple decorator with default settings
@retry_sync()
def fetch_data():
    # Function that might fail

# Customized decorator for async functions
@retry_async(max_attempts=5, initial_delay_ms=200, jitter=True)
async def process_data():
    # Async function that might fail
```

#### 2. Manual Configuration

```python
# Create custom retry options
retry_options = RetryOptions(
    max_attempts=4,
    initial_delay_ms=250,
    max_delay_ms=2000,
    factor=2.5,
    jitter=True,
    retryable_exceptions=[ConnectionError, TimeoutError]
)

# Apply to a function
result = retry_sync(retry_options=retry_options)(my_function)(*args, **kwargs)

# For async functions
result = await retry_async(retry_options=retry_options)(my_async_function)(*args, **kwargs)
```

### Python Best Practices

1. **Be Selective About Retried Exceptions**: Only retry for exceptions that represent transient failures.

   ```python
   @retry_sync(retryable_exceptions=[ConnectionError, TimeoutError, requests.exceptions.RequestException])
   def fetch_api_data():
       # ...
   ```

2. **Use Appropriate Timeouts**: Ensure your function calls have appropriate timeouts so retries don't wait indefinitely.

   ```python
   @retry_sync(max_attempts=3)
   def fetch_with_timeout():
       return requests.get(url, timeout=5)  # Set a 5 second timeout
   ```

3. **Log Retry Attempts**: Use the on_retry callback for visibility into retries.

   ```python
   def log_retry(attempt, exception):
       logger.warning(f"Retry attempt {attempt} after error: {str(exception)}")
   
   @retry_sync(on_retry=log_retry)
   def operation():
       # ...
   ```

4. **Avoid Retrying Non-Idempotent Operations**: Be careful when retrying operations that aren't idempotent (e.g., POST requests that create resources).

5. **Configure Appropriate Backoff**: Use longer delays for operations that might take longer to recover.

   ```python
   # For database operations that might need more time to recover
   @retry_sync(initial_delay_ms=1000, max_delay_ms=10000, factor=2.0)
   def database_operation():
       # ...
   ```

### Python Examples

See `backend/examples/retry_examples.py` for complete examples, including:

1. Synchronous HTTP requests with retry
2. Asynchronous API calls with retry
3. Custom retry configurations
4. Exception filtering examples

## C# Unity Retry Implementation

The C# retry mechanism for Unity is implemented in `UnityClient/Assets/Scripts/Core/Utils/RetryPolicy.cs`.

### CSharp Features

- **Policy-Based Design**: Create reusable retry policies
- **Sync and Async Support**: Works with synchronous methods, Tasks, and UniTasks
- **Exponential Backoff**: Configurable backoff parameters
- **Jitter**: Optional randomization of delays
- **Cancellation Support**: Integration with CancellationToken
- **Exception Filtering**: Specify which exception types should trigger retries
- **Extension Methods**: Convenient syntax for retrying operations
- **Serializable Options**: Configure retry options in the Unity Inspector
- **Logging Integration**: Comprehensive logging

### CSharp Usage Patterns

#### 1. Using RetryPolicy Object

```csharp
// Create a retry policy
var options = new RetryOptions { MaxAttempts = 3, InitialDelayMs = 100 };
var policy = new RetryPolicy(options, logger);

// Synchronous operations
int result = policy.Execute(() => RiskyOperation());

// Asynchronous operations
string data = await policy.ExecuteAsync(() => FetchDataAsync(url));

// UniTask operations
PlayerData player = await policy.ExecuteUniTask(() => LoadPlayerDataAsync(id));
```

#### 2. Using Extension Methods

```csharp
// Create retry options
var options = new RetryOptions { MaxAttempts = 3, InitialDelayMs = 100 };

// Apply to synchronous functions
int result = GetNumber.WithRetry(options);

// Apply to Task-based methods
string data = await FetchDataAsync.WithRetryAsync(options);

// Apply to UniTask-based methods
float damage = await CalculateDamageAsync.WithRetryUniTask(options);
```

### CSharp Best Practices

1. **Share Retry Policies**: Create and reuse policies for similar operations.

   ```csharp
   // Create once and reuse
   private readonly RetryPolicy _networkPolicy;
   private readonly RetryPolicy _databasePolicy;
   
   public Service(Logger logger)
   {
       _networkPolicy = new RetryPolicy(new RetryOptions { MaxAttempts = 3 }, logger);
       _databasePolicy = new RetryPolicy(new RetryOptions { MaxAttempts = 5, InitialDelayMs = 500 }, logger);
   }
   ```

2. **Use Cancellation Tokens**: Allow operations to be cancelled, especially for UI interactions.

   ```csharp
   // Creating a cancellation token
   var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5)); // 5-second timeout
   
   try
   {
       var result = await _policy.ExecuteAsync(() => LongRunningTaskAsync(), cts.Token);
   }
   catch (OperationCanceledException)
   {
       // Handle cancellation
   }
   ```

3. **Configure for Specific Exception Types**: Only retry specific exceptions.

   ```csharp
   var options = new RetryOptions
   {
       MaxAttempts = 3,
       RetryableExceptions = new[] { typeof(NetworkException), typeof(TimeoutException) }
   };
   ```

4. **Use SerializeField for Configuration**: In MonoBehaviours, expose retry options for configuration in the editor.

   ```csharp
   [SerializeField] private RetryOptions _apiRetryOptions = new RetryOptions
   {
       MaxAttempts = 3,
       InitialDelayMs = 200,
       MaxDelayMs = 2000
   };
   ```

5. **Prefer UniTask for Unity**: Use UniTask-based methods for Unity coroutine compatibility.

   ```csharp
   // Better for Unity's main thread operations
   PlayerData data = await _policy.ExecuteUniTask(() => LoadPlayerDataAsync(id));
   ```

### CSharp Examples

See `UnityClient/Assets/Scripts/Examples/RetryPolicyExample.cs` for complete examples, including:

1. Synchronous operations with retry
2. Async operations with Task and UniTask
3. Cancellation support
4. Extension method usage
5. Exception filtering

## Common Retry Strategy Considerations

Regardless of language, consider these principles when implementing retry logic:

1. **Identify Idempotent Operations**: Only automatically retry operations that can be safely repeated.

2. **Consider Retry Budgets**: Limit the total number of retries across your system to prevent cascading failures.

3. **Monitor Retry Rates**: High retry rates might indicate underlying issues that need addressing.

4. **Use Circuit Breakers**: Consider implementing circuit breakers for services that are consistently failing.

5. **Apply Appropriate Backoff**: 
   - Short delays (100-500ms) for quick transient issues
   - Medium delays (500-2000ms) for network issues
   - Longer delays (2-10 seconds) for service outages

6. **Add Jitter**: Always use jitter in production to prevent synchronized retries.

7. **Test Retry Logic**: Simulate failures to ensure your retry mechanism works as expected.

8. **Document Retry Policies**: Make your retry policies explicit and document them for your team.

---

By implementing these retry mechanisms consistently, we improve the resilience and reliability of our application across both the backend and client components. 