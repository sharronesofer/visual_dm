# UniTask Integration Guide

This document provides guidelines for using [UniTask](https://github.com/Cysharp/UniTask) in the Visual DM project to handle asynchronous operations efficiently.

## Overview

UniTask is a powerful library that enables zero-allocation async/await integration in Unity, replacing standard C# Task with a more Unity-friendly implementation. The Visual DM project uses UniTask for all asynchronous operations, including:

- API requests and responses
- Scene loading and transitions
- Asset loading with Addressables
- Animation and tween operations
- Delayed execution and timers
- Input handling

## Core Utilities

The project provides several utility classes in the `VisualDM.Core.Utils` namespace to help with common UniTask patterns:

- **UniTaskUtils**: Core extension methods for timeout handling, retries, and other common operations
- **UniTaskProgress**: Progress reporting with aggregation support
- **UniTaskTween**: Tweening utilities for animations

## Best Practices

### 1. Basic Usage

```csharp
// Basic async method
private async UniTaskVoid DoSomethingAsync()
{
    // Use .Forget() for fire-and-forget operations
    // Don't use .Forget() if you need to handle exceptions!
    DoSomethingElseAsync().Forget();
    
    // Use await to wait for completion
    await UniTask.Delay(1000);
    
    // Return a value
    int result = await GetValueAsync();
}
```

### 2. Cancellation

Always support cancellation where appropriate:

```csharp
// Store a cancellation token source at the class level
private CancellationTokenSource _cts;

private void Awake()
{
    _cts = new CancellationTokenSource();
}

private void OnDestroy()
{
    // Always cancel and dispose CTS when done
    _cts.Cancel();
    _cts.Dispose();
}

private async UniTask LoadDataAsync(CancellationToken cancellationToken)
{
    // Pass the token to async operations
    await UniTask.Delay(1000, cancellationToken: cancellationToken);
    
    // Check for cancellation
    cancellationToken.ThrowIfCancellationRequested();
}
```

### 3. Timeout Handling

Use the timeout utilities for operations that might hang:

```csharp
// This will throw TimeoutException if the operation takes too long
await SomeOperationAsync()
    .WithTimeout(TimeSpan.FromSeconds(5), _cts.Token);

// This will return a default value instead of throwing
bool result = await SomeOperationAsync()
    .WithTimeoutOrDefault(TimeSpan.FromSeconds(5), defaultValue: false, _cts.Token);
```

### 4. Retry Logic

Use retry utilities for operations that might fail temporarily:

```csharp
// Retry the operation up to 3 times with exponential backoff
int result = await UniTaskUtils.WithRetry(
    async (ct) => await SomeOperationThatMightFailAsync(ct),
    maxRetries: 3,
    initialDelay: TimeSpan.FromSeconds(1),
    maxDelay: TimeSpan.FromSeconds(5),
    cancellationToken: _cts.Token
);
```

### 5. Progress Reporting

Use the progress utilities for long-running operations:

```csharp
// Create a progress object
var progress = new UniTaskProgress(
    progressAction: (value) => progressBar.value = value,
    messageAction: (msg) => statusText.text = msg
);

// Report progress directly
progress.Report(0.5f);
progress.ReportMessage("Loading assets...");

// Create child progress objects for sub-operations
var child1 = progress.CreateChild(0.7f, 0);     // First 70% of the overall progress
var child2 = progress.CreateChild(0.3f, 0.7f);  // Last 30% of the overall progress

// Pass the child progress to methods
await LoadFirstBatchAsync(child1);
await LoadSecondBatchAsync(child2);
```

### 6. Animation with Tweens

Use the tween utilities for smooth animations:

```csharp
// Fade a CanvasGroup
await UniTaskTween.FadeCanvasGroupAsync(
    canvasGroup,
    targetAlpha: 0f,
    duration: 1.0f, 
    UniTaskTween.EaseInOutQuad,
    progress: null,
    cancellationToken: _cts.Token
);

// Move a Transform
await UniTaskTween.MoveTransformAsync(
    transform,
    targetPosition,
    duration: 1.0f,
    useLocal: false,
    easingFunc: null,
    progress: null,
    cancellationToken: _cts.Token
);
```

### 7. Exception Handling

Always handle exceptions properly:

```csharp
try
{
    await SomeOperationAsync();
}
catch (OperationCanceledException)
{
    // Handle cancellation
    Debug.Log("Operation was canceled");
}
catch (TimeoutException)
{
    // Handle timeout
    Debug.Log("Operation timed out");
}
catch (Exception ex)
{
    // Handle other exceptions
    Debug.LogError($"Error: {ex.Message}");
}
```

### 8. Memory Considerations

UniTask is designed to be allocation-free, but there are some pitfalls:

- Using `.ContinueWith()` or lambda captures can cause allocations
- Excessive nesting of async methods can cause stack issues
- Use struct-based approaches where possible with `UniTask<T>`

## Example Code

An example implementation can be found in `UniTaskExample.cs` which demonstrates all the core patterns including timeouts, retries, progress reporting, and tweening.

## References

- [UniTask GitHub Repository](https://github.com/Cysharp/UniTask)
- [UniTask Documentation](https://github.com/Cysharp/UniTask/blob/master/README.md) 