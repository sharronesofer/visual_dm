using System;
using System.Collections.Generic;
using Systems.Integration;
using UnityEngine;

namespace VisualDM.MotifSystem
{
    /// <summary>
    /// Manages a pool of Motifs, including active motifs, history, rotation, and validation.
    /// </summary>
    [Serializable]
    public class MotifPool
    {
        public List<Motif> ActiveMotifs { get; private set; }
        public List<string> MotifHistory { get; private set; }
        public DateTime LastRotated { get; private set; }
        public string Version { get; private set; }
        private MotifPool _snapshot;
        private MotifCache _cache = new MotifCache();
        private MotifBatchProcessor _batchProcessor = new MotifBatchProcessor();
        private int _consecutiveFailures = 0;
        private const int CircuitBreakerThreshold = 5;
        private bool _circuitBreakerTripped = false;

        public MotifPool(List<Motif> activeMotifs = null, List<string> motifHistory = null, DateTime? lastRotated = null, string version = "1.0.0")
        {
            ActiveMotifs = activeMotifs ?? new List<Motif>();
            MotifHistory = motifHistory ?? new List<string>();
            LastRotated = lastRotated ?? DateTime.UtcNow;
            Version = version;
        }

        public ValidationResult Validate()
        {
            var result = new ValidationResult { IsValid = true };
            if (ActiveMotifs == null || ActiveMotifs.Count == 0)
            {
                result.IsValid = false;
                result.Errors.Add("At least one active motif is required.");
            }
            foreach (var motif in ActiveMotifs)
            {
                var motifResult = motif.Validate();
                if (!motifResult.IsValid)
                {
                    result.IsValid = false;
                    result.Errors.AddRange(motifResult.Errors);
                }
            }
            return result;
        }

        private void HandleError(Exception ex, string context)
        {
            _consecutiveFailures++;
            VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, $"MotifPool error in {context}", context, GetSystemState());
            VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            if (_consecutiveFailures >= CircuitBreakerThreshold)
            {
                _circuitBreakerTripped = true;
                Debug.LogError($"[MotifPool] Circuit breaker tripped after {_consecutiveFailures} consecutive failures.");
            }
        }

        private void ResetCircuitBreaker()
        {
            _consecutiveFailures = 0;
            _circuitBreakerTripped = false;
        }

        private string GetSystemState()
        {
            return $"ActiveMotifs: {ActiveMotifs?.Count ?? 0}, MotifHistory: {MotifHistory?.Count ?? 0}, LastRotated: {LastRotated}, Version: {Version}";
        }

        /// <summary>
        /// Retrieves a motif from the pool by theme. Returns null if not found, invalid, or circuit breaker is tripped.
        /// </summary>
        /// <param name="theme">The motif theme key.</param>
        /// <returns>The motif or null.</returns>
        public Motif GetMotif(string theme)
        {
            if (_circuitBreakerTripped)
            {
                UnityEngine.Debug.LogWarning("MotifPool: Circuit breaker tripped. Skipping GetMotif.");
                return null;
            }
            try
            {
                if (string.IsNullOrEmpty(theme)) return null;
                var motif = _cache.Get(theme);
                if (motif != null)
                {
                    Debug.Log($"[MotifPool] Cache hit for motif '{theme}'");
                    ResetCircuitBreaker();
                    // Data integrity check
                    if (!MotifValidator.ValidateMotif(motif))
                    {
                        VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError($"MotifPool: Invalid motif returned: {motif?.Theme ?? "<null>"}", "MotifPool.GetMotif");
                        VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                        return null;
                    }
                    return motif;
                }
                // Fallback: search in ActiveMotifs
                motif = ActiveMotifs.Find(m => m.Theme == theme);
                if (motif != null)
                {
                    Debug.Log($"[MotifPool] Cache miss, found motif '{theme}' in ActiveMotifs. Caching.");
                    _cache.Set(theme, motif);
                    ResetCircuitBreaker();
                    // Data integrity check
                    if (!MotifValidator.ValidateMotif(motif))
                    {
                        VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError($"MotifPool: Invalid motif returned: {motif?.Theme ?? "<null>"}", "MotifPool.GetMotif");
                        VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                        return null;
                    }
                }
                else
                {
                    Debug.LogWarning($"[MotifPool] Motif '{theme}' not found in cache or ActiveMotifs.");
                }
                return motif;
            }
            catch (Exception ex)
            {
                HandleError(ex, "GetMotif");
                return null;
            }
        }

        public void UpdateMotif(Motif motif, int priority = 0)
        {
            if (_circuitBreakerTripped)
            {
                Debug.LogWarning("[MotifPool] Circuit breaker is tripped. Skipping UpdateMotif.");
                return;
            }
            try
            {
                Debug.Log($"[MotifPool] Updating motif '{motif.Theme}' (priority {priority})");
                _cache.Set(motif.Theme, motif);
                _batchProcessor.Enqueue(motif, priority);
                ResetCircuitBreaker();
            }
            catch (Exception ex)
            {
                HandleError(ex, $"UpdateMotif({motif?.Theme})");
            }
        }

        public void TickAll(Action<Motif> onExpire = null)
        {
            if (_circuitBreakerTripped)
            {
                Debug.LogWarning("[MotifPool] Circuit breaker is tripped. Skipping TickAll.");
                return;
            }
            try
            {
                Debug.Log("[MotifPool] TickAll: incrementing entropy and updating motifs");
                var expired = new List<Motif>();
                foreach (var motif in ActiveMotifs)
                {
                    try
                    {
                        motif.IncrementEntropy();
                        if (motif.NeedsRotation())
                            expired.Add(motif);
                        // Update cache and batch for each motif
                        UpdateMotif(motif);
                    }
                    catch (Exception ex)
                    {
                        HandleError(ex, $"TickAll motif: {motif?.Theme}");
                    }
                }
                if (expired.Count > 0 && onExpire != null)
                {
                    foreach (var motif in expired)
                    {
                        try { onExpire(motif); } catch (Exception ex) { HandleError(ex, $"TickAll onExpire: {motif?.Theme}"); }
                    }
                }
                Rotate();
                ResetCircuitBreaker();
            }
            catch (Exception ex)
            {
                HandleError(ex, "TickAll");
            }
        }

        /// <summary>
        /// Rotates motifs, using the chaos engine to determine chaos state and publish motif events.
        /// </summary>
        /// <param name="chaosEngine">The chaos engine for integration (optional).</param>
        public void Rotate(IChaosEngine chaosEngine = null)
        {
            if (_circuitBreakerTripped)
            {
                Debug.LogWarning("[MotifPool] Circuit breaker is tripped. Skipping Rotate.");
                return;
            }
            try
            {
                // Use IChaosEngine to determine chaos state
                bool chaos = false;
                if (chaosEngine == null)
                {
                    try
                    {
                        chaosEngine = ServiceLocator.Instance.Resolve<IChaosEngine>();
                    }
                    catch { /* Not registered, fallback to false */ }
                }
                if (chaosEngine != null)
                {
                    try { chaos = chaosEngine.GetChaosState()?.ChaosLevel > 0.5f; } catch { chaos = false; }
                }
                Debug.Log($"[MotifPool] Rotating motifs (chaos={chaos})");
                var active = new List<Motif>();
                foreach (var motif in ActiveMotifs)
                {
                    try
                    {
                        if (motif.NeedsRotation())
                            MotifHistory.Add(motif.Theme);
                        else
                            active.Add(motif);
                    }
                    catch (Exception ex)
                    {
                        HandleError(ex, $"Rotate motif: {motif?.Theme}");
                    }
                }
                while (active.Count < 3)
                {
                    try
                    {
                        var exclude = new HashSet<string>(active.ConvertAll(m => m.Theme));
                        exclude.UnionWith(MotifHistory);
                        var newMotif = MotifFactory.RollNewMotif(exclude, chaosEngine);
                        active.Add(newMotif);
                        MotifHistory.Add(newMotif.Theme);
                        // Add new motif to cache and batch
                        Debug.Log($"[MotifPool] Adding new motif '{newMotif.Theme}' to cache and batch (priority 1)");
                        UpdateMotif(newMotif, priority: 1);
                        // Publish motif event to ChaosEngine
                        try
                        {
                            if (chaosEngine != null)
                            {
                                var eventData = new MotifEventData
                                {
                                    MotifTheme = newMotif.Theme,
                                    IsChaosSource = newMotif.ChaosSource,
                                    EventType = "MotifRotated",
                                    Context = "Rotation"
                                };
                                chaosEngine.OnMotifEvent(eventData);
                            }
                        }
                        catch (Exception ex)
                        {
                            IntegrationLogger.Log($"[MotifPool] Failed to notify ChaosEngine: {ex.Message}", LogLevel.Warn, "MotifPool", "ChaosEngine", "MotifRotated", "Error");
                        }
                    }
                    catch (Exception ex)
                    {
                        HandleError(ex, "Rotate new motif");
                        // Attempt recovery: fallback to cached motif if possible
                        if (_cache.Count > 0)
                        {
                            foreach (var cached in _cache)
                            {
                                if (!active.Exists(m => m.Theme == cached.Key))
                                {
                                    active.Add(cached.Value);
                                    break;
                                }
                            }
                        }
                        else
                        {
                            Debug.LogError("[MotifPool] No motifs available for recovery during rotation.");
                            break;
                        }
                    }
                }
                ActiveMotifs = active;
                LastRotated = DateTime.UtcNow;
                ResetCircuitBreaker();
            }
            catch (Exception ex)
            {
                HandleError(ex, "Rotate");
            }
        }

        public void BeginTransaction()
        {
            _snapshot = this.MemberwiseClone() as MotifPool;
            // Deep copy lists
            _snapshot.ActiveMotifs = new List<Motif>(ActiveMotifs);
            _snapshot.MotifHistory = new List<string>(MotifHistory);
        }

        public void CommitTransaction()
        {
            _snapshot = null;
        }

        public void RollbackTransaction()
        {
            if (_snapshot != null)
            {
                ActiveMotifs = new List<Motif>(_snapshot.ActiveMotifs);
                MotifHistory = new List<string>(_snapshot.MotifHistory);
                LastRotated = _snapshot.LastRotated;
                Version = _snapshot.Version;
                _snapshot = null;
            }
        }

        /// <summary>
        /// Adds a motif to the pool. Skips if circuit breaker is tripped or motif is invalid.
        /// </summary>
        /// <param name="motif">The motif to add.</param>
        public void AddMotif(Motif motif)
        {
            if (_circuitBreakerTripped)
            {
                UnityEngine.Debug.LogWarning("MotifPool: Circuit breaker tripped. Skipping AddMotif.");
                return;
            }
            // Data integrity check
            if (!MotifValidator.ValidateMotif(motif))
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError($"MotifPool: Invalid motif added: {motif?.Theme ?? "<null>"}", "MotifPool.AddMotif");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return;
            }
            // ... existing add logic ...
        }
    }
}