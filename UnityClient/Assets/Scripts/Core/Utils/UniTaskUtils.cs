using System;
using System.Collections.Generic;
using System.Threading;
using Cysharp.Threading.Tasks;
using UnityEngine;
using VisualDM.Core;

namespace VisualDM.Core.Utils
{
    /// <summary>
    /// Provides utility methods and extensions for UniTask operations
    /// </summary>
    public static class UniTaskUtils
    {
        /// <summary>
        /// Default timeout duration for operations
        /// </summary>
        public static readonly TimeSpan DefaultTimeout = TimeSpan.FromSeconds(30);

        /// <summary>
        /// Executes a task with timeout handling
        /// </summary>
        public static async UniTask<T> WithTimeout<T>(this UniTask<T> task, TimeSpan timeout, CancellationToken cancellationToken = default)
        {
            try
            {
                return await task.Timeout(timeout, cancellationToken: cancellationToken);
            }
            catch (TimeoutException)
            {
                Logger.Error($"Operation timed out after {timeout.TotalSeconds} seconds");
                throw;
            }
        }

        /// <summary>
        /// Executes a task with timeout handling and a default value if timeout occurs
        /// </summary>
        public static async UniTask<T> WithTimeoutOrDefault<T>(this UniTask<T> task, TimeSpan timeout, T defaultValue, CancellationToken cancellationToken = default)
        {
            try
            {
                return await task.Timeout(timeout, cancellationToken: cancellationToken);
            }
            catch (TimeoutException)
            {
                Logger.Warning($"Operation timed out after {timeout.TotalSeconds} seconds, returning default value");
                return defaultValue;
            }
        }

        /// <summary>
        /// Retries an operation with exponential backoff
        /// </summary>
        public static async UniTask<T> WithRetry<T>(
            Func<CancellationToken, UniTask<T>> taskFactory, 
            int maxRetries = 3, 
            TimeSpan? initialDelay = null, 
            Func<Exception, int, bool> retryPredicate = null,
            CancellationToken cancellationToken = default)
        {
            var delay = initialDelay ?? TimeSpan.FromSeconds(1);
            Exception lastException = null;

            for (int attempt = 0; attempt <= maxRetries; attempt++)
            {
                try
                {
                    if (attempt > 0)
                    {
                        Logger.Info($"Retry attempt {attempt}/{maxRetries}");
                    }

                    return await taskFactory(cancellationToken);
                }
                catch (OperationCanceledException)
                {
                    throw; // Don't catch cancellation
                }
                catch (Exception ex)
                {
                    lastException = ex;
                    
                    // Check if we should retry this exception
                    if (retryPredicate != null && !retryPredicate(ex, attempt))
                    {
                        Logger.Warning($"Exception not eligible for retry: {ex.Message}");
                        throw;
                    }
                    
                    if (attempt >= maxRetries)
                    {
                        Logger.Error($"Operation failed after {maxRetries} retries: {ex.Message}");
                        throw;
                    }
                    
                    // Calculate delay with exponential backoff (2^attempt * initial delay)
                    var currentDelay = TimeSpan.FromMilliseconds(delay.TotalMilliseconds * Math.Pow(2, attempt));
                    
                    // Add jitter to avoid thundering herd problem
                    var jitteredDelay = currentDelay.TotalMilliseconds * (0.8 + (0.4 * UnityEngine.Random.value));
                    
                    Logger.Warning($"Operation failed, retrying in {jitteredDelay:0.00}ms: {ex.Message}");
                    await UniTask.Delay(TimeSpan.FromMilliseconds(jitteredDelay), cancellationToken: cancellationToken);
                }
            }
            
            // This should never be reached due to the throw in the last iteration
            throw lastException ?? new Exception("Operation failed");
        }

        /// <summary>
        /// Creates a cancellation token that combines a timeout with an existing token
        /// </summary>
        public static (CancellationToken token, CancellationTokenSource source) CreateTimeoutToken(
            TimeSpan timeout, 
            CancellationToken originalToken = default)
        {
            var timeoutSource = new CancellationTokenSource(timeout);
            var combinedSource = CancellationTokenSource.CreateLinkedTokenSource(originalToken, timeoutSource.Token);
            return (combinedSource.Token, combinedSource);
        }

        /// <summary>
        /// Runs multiple tasks in parallel with progress reporting
        /// </summary>
        public static async UniTask<IReadOnlyList<T>> WhenAll<T>(
            IEnumerable<UniTask<T>> tasks,
            IProgress<float> progress = null,
            CancellationToken cancellationToken = default)
        {
            var taskArray = tasks as UniTask<T>[] ?? new List<UniTask<T>>(tasks).ToArray();
            int completedCount = 0;
            var completionSource = new UniTaskCompletionSource<IReadOnlyList<T>>();
            var results = new T[taskArray.Length];

            if (taskArray.Length == 0)
            {
                return Array.Empty<T>();
            }

            for (int i = 0; i < taskArray.Length; i++)
            {
                int index = i;
                taskArray[i].ContinueWith(result =>
                {
                    try
                    {
                        results[index] = result;
                        completedCount++;
                        progress?.Report((float)completedCount / taskArray.Length);

                        if (completedCount >= taskArray.Length)
                        {
                            completionSource.TrySetResult(results);
                        }
                    }
                    catch (Exception ex)
                    {
                        completionSource.TrySetException(ex);
                    }
                }, cancellationToken);
            }

            return await completionSource.Task;
        }

        /// <summary>
        /// Executes a task and catches specific exceptions, returning a default value
        /// </summary>
        public static async UniTask<T> CatchException<T, TException>(
            this UniTask<T> task, 
            T defaultValue,
            Action<TException> onException = null,
            CancellationToken cancellationToken = default) where TException : Exception
        {
            try
            {
                return await task;
            }
            catch (TException ex)
            {
                onException?.Invoke(ex);
                return defaultValue;
            }
        }
    }
} 