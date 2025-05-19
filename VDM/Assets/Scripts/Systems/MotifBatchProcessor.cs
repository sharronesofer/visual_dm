using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading.Tasks;
using UnityEngine;

namespace VisualDM.Systems.MotifSystem
{
    /// <summary>
    /// Batches motif updates for efficient processing, with debouncing and priority.
    /// </summary>
    public class MotifBatchProcessor
    {
        private readonly List<(Motif motif, int priority)> _pending = new();
        private bool _processing = false;
        private float _debounceMs = 100f;
        private Stopwatch _timer = new Stopwatch();
        public int LastBatchSize { get; private set; }
        public long LastBatchMs { get; private set; }
        private int _consecutiveFailures = 0;
        private const int CircuitBreakerThreshold = 5;
        private bool _circuitBreakerTripped = false;

        public void Enqueue(Motif motif, int priority = 0)
        {
            _pending.Add((motif, priority));
            if (!_processing)
                DebounceAndProcess();
        }

        private async void DebounceAndProcess()
        {
            _processing = true;
            await Task.Delay((int)_debounceMs);
            await ProcessBatch();
            _processing = false;
        }

        private void HandleError(Exception ex, string context)
        {
            _consecutiveFailures++;
            VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, $"MotifBatchProcessor error in {context}", context);
            VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            if (_consecutiveFailures >= CircuitBreakerThreshold)
            {
                _circuitBreakerTripped = true;
                Debug.LogError($"[MotifBatchProcessor] Circuit breaker tripped after {_consecutiveFailures} consecutive failures.");
            }
        }

        private void ResetCircuitBreaker()
        {
            _consecutiveFailures = 0;
            _circuitBreakerTripped = false;
        }

        /// <summary>
        /// Processes a batch of motifs. Skips invalid motifs and logs errors. Skips processing if circuit breaker is tripped.
        /// </summary>
        /// <param name="motifs">The motifs to process.</param>
        public void ProcessBatch(List<Motif> motifs)
        {
            if (_circuitBreakerTripped)
            {
                UnityEngine.Debug.LogWarning("MotifBatchProcessor: Circuit breaker tripped. Skipping batch processing.");
                return;
            }
            foreach (var motif in motifs)
            {
                try
                {
                    // Data integrity check
                    if (!MotifValidator.ValidateMotif(motif))
                    {
                        VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError($"MotifBatchProcessor: Invalid motif in batch: {motif?.Theme ?? "<null>"}", "MotifBatchProcessor.ProcessBatch");
                        VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                        continue;
                    }
                    // TODO: Save motif, update cache, etc.
                }
                catch (Exception ex)
                {
                    HandleError(ex, $"ProcessBatch motif {motif?.Theme ?? "<null>"}");
                }
            }
        }

        private async Task ProcessBatch()
        {
            if (_circuitBreakerTripped)
            {
                Debug.LogWarning("[MotifBatchProcessor] Circuit breaker is tripped. Skipping batch processing.");
                return;
            }
            _timer.Restart();
            if (_pending.Count == 0) return;
            _pending.Sort((a, b) => b.priority.CompareTo(a.priority));
            var batch = new List<Motif>(_pending.Count);
            foreach (var (motif, _) in _pending)
                batch.Add(motif);
            _pending.Clear();
            LastBatchSize = batch.Count;
            try
            {
                await MotifAsyncWorker.Instance.Queue.Enqueue(() => Task.Run(() =>
                {
                    int failed = 0;
                    foreach (var motif in batch)
                    {
                        try
                        {
                            // Data integrity check
                            if (!MotifValidator.ValidateMotif(motif))
                            {
                                VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError($"MotifBatchProcessor: Invalid motif in batch: {motif?.Theme ?? "<null>"}", "MotifBatchProcessor.ProcessBatch");
                                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                                continue;
                            }
                            // TODO: Save motif, update cache, etc.
                        }
                        catch (Exception ex)
                        {
                            failed++;
                            HandleError(ex, $"ProcessBatch motif: {motif?.Theme}");
                        }
                    }
                    if (failed == batch.Count)
                    {
                        HandleError(new Exception("All motif updates in batch failed."), "ProcessBatch");
                    }
                }));
                ResetCircuitBreaker();
            }
            catch (Exception ex)
            {
                HandleError(ex, "ProcessBatch");
            }
            _timer.Stop();
            LastBatchMs = _timer.ElapsedMilliseconds;
            Debug.Log($"[MotifBatchProcessor] Processed batch of {LastBatchSize} motifs in {LastBatchMs}ms");
        }
    }
}