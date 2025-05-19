using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;
using UnityEngine;

namespace VisualDM.Systems.MotifSystem
{
    /// <summary>
    /// Thread-safe async queue for non-critical motif operations.
    /// </summary>
    public class MotifAsyncQueue
    {
        private readonly ConcurrentQueue<Func<Task>> _queue = new();
        private bool _processing = false;
        private int _retryLimit = 3;
        private int _consecutiveFailures = 0;
        private const int CircuitBreakerThreshold = 5;
        private bool _circuitBreakerTripped = false;

        /// <summary>
        /// Enqueues a motif for asynchronous processing. Skips if circuit breaker is tripped or motif is invalid.
        /// </summary>
        /// <param name="motif">The motif to enqueue.</param>
        public void Enqueue(Motif motif)
        {
            if (_circuitBreakerTripped)
            {
                UnityEngine.Debug.LogWarning("MotifAsyncQueue: Circuit breaker tripped. Skipping enqueue.");
                return;
            }
            // Data integrity check
            if (!MotifValidator.ValidateMotif(motif))
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError($"MotifAsyncQueue: Invalid motif enqueued: {motif?.Theme ?? "<null>"}", "MotifAsyncQueue.Enqueue");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return;
            }
            _queue.Enqueue(motifTask);
            ProcessQueue();
        }

        private void HandleError(Exception ex, string context)
        {
            _consecutiveFailures++;
            VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, $"MotifAsyncQueue error in {context}", context);
            VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            if (_consecutiveFailures >= CircuitBreakerThreshold)
            {
                _circuitBreakerTripped = true;
                Debug.LogError($"[MotifAsyncQueue] Circuit breaker tripped after {_consecutiveFailures} consecutive failures.");
            }
        }

        private void ResetCircuitBreaker()
        {
            _consecutiveFailures = 0;
            _circuitBreakerTripped = false;
        }

        private async void ProcessQueue()
        {
            if (_processing || _circuitBreakerTripped)
            {
                if (_circuitBreakerTripped)
                    Debug.LogWarning("[MotifAsyncQueue] Circuit breaker is tripped. Skipping queue processing.");
                return;
            }
            _processing = true;
            while (_queue.TryDequeue(out var taskFunc))
            {
                int attempts = 0;
                bool success = false;
                while (!success && attempts < _retryLimit)
                {
                    try
                    {
                        await taskFunc();
                        success = true;
                        ResetCircuitBreaker();
                    }
                    catch (Exception ex)
                    {
                        attempts++;
                        Debug.LogWarning($"[MotifAsyncQueue] Task failed (attempt {attempts}): {ex.Message}");
                        HandleError(ex, $"ProcessQueue task (attempt {attempts})");
                        await Task.Delay(100 * attempts);
                    }
                }
                if (!success)
                {
                    HandleError(new Exception("MotifAsyncQueue task failed all retries."), "ProcessQueue");
                }
            }
            _processing = false;
        }
    }

    /// <summary>
    /// MonoBehaviour worker to process motif async queue in background.
    /// </summary>
    public class MotifAsyncWorker : MonoBehaviour
    {
        public static MotifAsyncWorker Instance { get; private set; }
        public MotifAsyncQueue Queue { get; private set; } = new MotifAsyncQueue();

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
    }
}