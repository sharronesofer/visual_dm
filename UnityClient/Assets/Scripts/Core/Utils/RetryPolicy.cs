using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cysharp.Threading.Tasks;
using UnityEngine;
using Random = UnityEngine.Random;

namespace Core.Utils
{
    /// <summary>
    /// Configuration options for retry operations.
    /// </summary>
    [Serializable]
    public class RetryOptions
    {
        [Tooltip("Maximum number of retry attempts")]
        public int MaxAttempts = 5;

        [Tooltip("Initial delay between retries in milliseconds")]
        public int InitialDelayMs = 100;

        [Tooltip("Maximum delay between retries in milliseconds")]
        public int MaxDelayMs = 5000;

        [Tooltip("Multiplicative factor for exponential backoff")]
        public float Factor = 2.0f;

        [Tooltip("Whether to add randomness to delay times")]
        public bool Jitter = true;

        /// <summary>
        /// Types of exceptions that should trigger a retry.
        /// If empty, all exceptions will trigger retries.
        /// </summary>
        public Type[] RetryableExceptions { get; set; }
        
        /// <summary>
        /// Optional callback function that will be called when a retry is attempted.
        /// </summary>
        public Action<int, Exception> OnRetry { get; set; }
    }

    /// <summary>
    /// Handles retry operations with exponential backoff for both synchronous and asynchronous methods.
    /// </summary>
    public class RetryPolicy
    {
        private readonly RetryOptions _options;
        private readonly Logger _logger;

        /// <summary>
        /// Creates a new retry policy with the given options.
        /// </summary>
        /// <param name="options">The options to configure the retry behavior.</param>
        /// <param name="logger">The logger to use for logging retry attempts.</param>
        public RetryPolicy(RetryOptions options = null, Logger logger = null)
        {
            _options = options ?? new RetryOptions();
            _logger = logger ?? Logger.GetInstance();
        }

        /// <summary>
        /// Determines if the given exception should trigger a retry.
        /// </summary>
        /// <param name="exception">The exception to check.</param>
        /// <returns>True if this exception should trigger a retry, false otherwise.</returns>
        private bool ShouldRetry(Exception exception)
        {
            if (_options.RetryableExceptions == null || _options.RetryableExceptions.Length == 0)
            {
                return true;
            }

            foreach (var exceptionType in _options.RetryableExceptions)
            {
                if (exceptionType.IsInstanceOfType(exception))
                {
                    return true;
                }
            }

            return false;
        }

        /// <summary>
        /// Calculates the delay for a specific retry attempt.
        /// </summary>
        /// <param name="attempt">The current attempt number (1-based).</param>
        /// <returns>The delay in milliseconds.</returns>
        private int CalculateDelay(int attempt)
        {
            float delay = _options.InitialDelayMs * Mathf.Pow(_options.Factor, attempt - 1);
            delay = Mathf.Min(delay, _options.MaxDelayMs);
            
            if (_options.Jitter)
            {
                // Add jitter of up to 25% of the delay
                float jitterAmount = delay * 0.25f;
                delay += Random.Range(-jitterAmount, jitterAmount);
                delay = Mathf.Max(1, delay);  // Ensure positive delay
            }
            
            return Mathf.RoundToInt(delay);
        }

        /// <summary>
        /// Executes a function with retry logic.
        /// </summary>
        /// <typeparam name="T">Return type of the function.</typeparam>
        /// <param name="func">The function to execute.</param>
        /// <returns>The result of the function call.</returns>
        public T Execute<T>(Func<T> func)
        {
            int attempt = 1;
            Exception lastException = null;

            while (attempt <= _options.MaxAttempts)
            {
                try
                {
                    return func();
                }
                catch (Exception ex)
                {
                    lastException = ex;
                    
                    if (!ShouldRetry(ex))
                    {
                        _logger.Info($"Not retrying for non-retryable exception: {ex.GetType().Name}", new Dictionary<string, object> 
                        {
                            { "error", ex.Message }
                        });
                        throw;
                    }
                    
                    _options.OnRetry?.Invoke(attempt, ex);
                    
                    if (attempt >= _options.MaxAttempts)
                    {
                        _logger.Warn($"Maximum retry attempts ({_options.MaxAttempts}) reached", new Dictionary<string, object> 
                        {
                            { "error", ex.Message },
                            { "attempt", attempt }
                        });
                        throw;
                    }
                    
                    int delayMs = CalculateDelay(attempt);
                    
                    _logger.Info($"Retry attempt {attempt}/{_options.MaxAttempts} failed, retrying in {delayMs}ms", new Dictionary<string, object> 
                    {
                        { "error", ex.Message },
                        { "attempt", attempt },
                        { "delay_ms", delayMs }
                    });
                    
                    Thread.Sleep(delayMs);
                    attempt++;
                }
            }
            
            // This should be unreachable
            throw lastException ?? new InvalidOperationException("Unexpected state in retry logic");
        }

        /// <summary>
        /// Executes a function with retry logic and returns a Task.
        /// </summary>
        /// <typeparam name="T">Return type of the function.</typeparam>
        /// <param name="func">The function to execute.</param>
        /// <param name="cancellationToken">Cancellation token to cancel the operation.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
        public async Task<T> ExecuteAsync<T>(Func<Task<T>> func, CancellationToken cancellationToken = default)
        {
            int attempt = 1;
            Exception lastException = null;

            while (attempt <= _options.MaxAttempts)
            {
                try
                {
                    return await func();
                }
                catch (Exception ex)
                {
                    if (cancellationToken.IsCancellationRequested)
                    {
                        throw new OperationCanceledException("Operation was canceled", ex, cancellationToken);
                    }
                    
                    lastException = ex;
                    
                    if (!ShouldRetry(ex))
                    {
                        _logger.Info($"Not retrying for non-retryable exception: {ex.GetType().Name}", new Dictionary<string, object> 
                        {
                            { "error", ex.Message }
                        });
                        throw;
                    }
                    
                    _options.OnRetry?.Invoke(attempt, ex);
                    
                    if (attempt >= _options.MaxAttempts)
                    {
                        _logger.Warn($"Maximum retry attempts ({_options.MaxAttempts}) reached", new Dictionary<string, object> 
                        {
                            { "error", ex.Message },
                            { "attempt", attempt }
                        });
                        throw;
                    }
                    
                    int delayMs = CalculateDelay(attempt);
                    
                    _logger.Info($"Retry attempt {attempt}/{_options.MaxAttempts} failed, retrying in {delayMs}ms", new Dictionary<string, object> 
                    {
                        { "error", ex.Message },
                        { "attempt", attempt },
                        { "delay_ms", delayMs }
                    });
                    
                    await Task.Delay(delayMs, cancellationToken);
                    attempt++;
                }
            }
            
            // This should be unreachable
            throw lastException ?? new InvalidOperationException("Unexpected state in retry logic");
        }

        /// <summary>
        /// Executes a function with retry logic and returns a UniTask.
        /// </summary>
        /// <typeparam name="T">Return type of the function.</typeparam>
        /// <param name="func">The function to execute.</param>
        /// <param name="cancellationToken">Cancellation token to cancel the operation.</param>
        /// <returns>A UniTask representing the asynchronous operation.</returns>
        public async UniTask<T> ExecuteUniTask<T>(Func<UniTask<T>> func, CancellationToken cancellationToken = default)
        {
            int attempt = 1;
            Exception lastException = null;

            while (attempt <= _options.MaxAttempts)
            {
                try
                {
                    return await func();
                }
                catch (Exception ex)
                {
                    if (cancellationToken.IsCancellationRequested)
                    {
                        throw new OperationCanceledException("Operation was canceled", ex, cancellationToken);
                    }
                    
                    lastException = ex;
                    
                    if (!ShouldRetry(ex))
                    {
                        _logger.Info($"Not retrying for non-retryable exception: {ex.GetType().Name}", new Dictionary<string, object> 
                        {
                            { "error", ex.Message }
                        });
                        throw;
                    }
                    
                    _options.OnRetry?.Invoke(attempt, ex);
                    
                    if (attempt >= _options.MaxAttempts)
                    {
                        _logger.Warn($"Maximum retry attempts ({_options.MaxAttempts}) reached", new Dictionary<string, object> 
                        {
                            { "error", ex.Message },
                            { "attempt", attempt }
                        });
                        throw;
                    }
                    
                    int delayMs = CalculateDelay(attempt);
                    
                    _logger.Info($"Retry attempt {attempt}/{_options.MaxAttempts} failed, retrying in {delayMs}ms", new Dictionary<string, object> 
                    {
                        { "error", ex.Message },
                        { "attempt", attempt },
                        { "delay_ms", delayMs }
                    });
                    
                    await UniTask.Delay(delayMs, cancellationToken: cancellationToken);
                    attempt++;
                }
            }
            
            // This should be unreachable
            throw lastException ?? new InvalidOperationException("Unexpected state in retry logic");
        }
    }

    /// <summary>
    /// Extension methods for retry operations.
    /// </summary>
    public static class RetryExtensions
    {
        /// <summary>
        /// Retries the function with exponential backoff.
        /// </summary>
        /// <typeparam name="T">The return type of the function.</typeparam>
        /// <param name="func">The function to retry.</param>
        /// <param name="options">Options for retry behavior.</param>
        /// <returns>The result of the function call.</returns>
        public static T WithRetry<T>(this Func<T> func, RetryOptions options = null)
        {
            var policy = new RetryPolicy(options);
            return policy.Execute(func);
        }

        /// <summary>
        /// Retries the async function with exponential backoff.
        /// </summary>
        /// <typeparam name="T">The return type of the function.</typeparam>
        /// <param name="func">The async function to retry.</param>
        /// <param name="options">Options for retry behavior.</param>
        /// <param name="cancellationToken">Cancellation token to cancel the operation.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
        public static Task<T> WithRetryAsync<T>(this Func<Task<T>> func, RetryOptions options = null, CancellationToken cancellationToken = default)
        {
            var policy = new RetryPolicy(options);
            return policy.ExecuteAsync(func, cancellationToken);
        }

        /// <summary>
        /// Retries the UniTask function with exponential backoff.
        /// </summary>
        /// <typeparam name="T">The return type of the function.</typeparam>
        /// <param name="func">The UniTask function to retry.</param>
        /// <param name="options">Options for retry behavior.</param>
        /// <param name="cancellationToken">Cancellation token to cancel the operation.</param>
        /// <returns>A UniTask representing the asynchronous operation.</returns>
        public static UniTask<T> WithRetryUniTask<T>(this Func<UniTask<T>> func, RetryOptions options = null, CancellationToken cancellationToken = default)
        {
            var policy = new RetryPolicy(options);
            return policy.ExecuteUniTask(func, cancellationToken);
        }
    }
} 