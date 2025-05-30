# Error Handling Refactoring Guide

## Overview

This document details the refactoring of error handling patterns throughout the VDM codebase to reduce code duplication. We've enhanced the `ErrorHandlingService` with standardized utility methods that can be used across the codebase.

## Changes Made

1. **Enhanced ErrorHandlingService**
   - Added `TryExecute` and `TryExecute<T>` static methods
   - Added async variants `TryExecuteAsync` and `TryExecuteAsync<T>`
   - All methods provide standardized error logging, monitoring, and return value handling

2. **Refactored Examples**
   - `MotifEventDispatcher.PublishStateChanged` - Standardized synchronous error handling
   - `MotifEventDispatcher.PublishStateChangedAsync` - Standardized async error handling
   - `MotifTransactionManager.BeginTransaction` - Standardized functional error handling with return value

## Pattern Recognition

Look for these common error handling patterns that can be refactored:

### Pattern 1: Basic try/catch with logging
```csharp
try
{
    // Implementation
}
catch (Exception ex)
{
    VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "...", "...");
    VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
}
```

Replace with:
```csharp
VisualDM.Core.ErrorHandlingService.TryExecute(() => {
    // Implementation
}, "context", "User-friendly message");
```

### Pattern 2: try/catch with return value
```csharp
try
{
    // Implementation
    return result;
}
catch (Exception ex)
{
    VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "...", "...");
    VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
    return defaultValue;
}
```

Replace with:
```csharp
return VisualDM.Core.ErrorHandlingService.TryExecute<ReturnType>(() => {
    // Implementation
    return result;
}, "context", "User-friendly message", defaultValue);
```

### Pattern 3: Async try/catch
```csharp
try
{
    await SomeAsyncOperation();
    // More async implementation
}
catch (Exception ex)
{
    VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "...", "...");
    VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
}
```

Replace with:
```csharp
await VisualDM.Core.ErrorHandlingService.TryExecuteAsync(async () => {
    await SomeAsyncOperation();
    // More async implementation
}, "context", "User-friendly message");
```

### Pattern 4: Async try/catch with return value
```csharp
try
{
    var result = await SomeAsyncFunction();
    // More async implementation
    return result;
}
catch (Exception ex)
{
    VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "...", "...");
    VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
    return defaultValue;
}
```

Replace with:
```csharp
return await VisualDM.Core.ErrorHandlingService.TryExecuteAsync<ReturnType>(async () => {
    var result = await SomeAsyncFunction();
    // More async implementation
    return result;
}, "context", "User-friendly message", defaultValue);
```

## Search Strategies

Use these search patterns to find duplicated error handling code:

1. **Grep/Regex Search:**
   ```
   try\s*\{[\s\S]*?\}\s*catch\s*\(Exception[\s\S]*?ErrorHandlingService
   ```

2. **Key imports to check:**
   - `using VisualDM.Utilities;` followed by `ErrorHandlingService.Instance` usage
   - `LogException` method calls
   - `MonitoringManager.Instance?.IncrementErrorCount()` calls

3. **Files to prioritize:**
   - Service classes in `/Systems/` directory
   - Manager classes throughout the codebase
   - Event handlers and dispatchers

## Testing Guidelines

When refactoring error handling:

1. **Unit Tests:**
   - Verify the behavior matches original implementation
   - Ensure correct error messages and context are passed
   - Test both success and failure paths

2. **Ensure Error Details Are Preserved:**
   - Context string should identify the component + method
   - User message should be descriptive for end users
   - Default return values should match original behavior

3. **Maintain Special Cases:**
   - Some error handlers may have special logic (retries, specific cleanup)
   - Ensure these are maintained in the refactored version

## Tracking Progress

Maintain a checklist of files that have been refactored:

- [x] `ErrorHandlingService.cs` - Enhanced with utility methods
- [x] `MotifEventDispatcher.cs` - Refactored synchronous and async methods (PublishStateChanged, PublishStateChangedAsync, PublishTriggered, PublishTriggeredAsync)
- [x] `MotifTransactionManager.cs` - Refactored all methods (BeginTransaction, Commit, Rollback)
- [x] `MotifRuleEngine.cs` - Refactored nested error handling with multiple catch blocks (CompileRule, ParseRule)
- [x] `MotifValidator.cs` - Refactored ValidateMotif method
- [x] `MotifTriggerManager.cs` - Refactored EvaluateAndExecute and EvaluateAndExecuteAsync methods
- [ ] Remaining files in `/Systems/` directory
- [ ] Files in `/Core/` directory
- [ ] Files in `/UI/` directory
- [ ] Files in `/Inventory/` directory

## Next Steps

1. Continue refactoring error handling in order of priority:
   - High-usage service classes first
   - Performance-critical code second
   - UI and user-facing components last

2. Once error handling is consolidated, consider enhancing the service with:
   - Structured logging integration
   - Error aggregation and analytics
   - Custom exception types for domain-specific errors 