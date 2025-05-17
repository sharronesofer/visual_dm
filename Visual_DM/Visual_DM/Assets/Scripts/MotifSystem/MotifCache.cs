using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;

namespace VisualDM.MotifSystem
{
    /// <summary>
    /// Thread-safe, event-driven in-memory cache for Motif data.
    /// </summary>
    public class MotifCache
    {
        private static int _capacity = 128;
        public static int Capacity { get => _capacity; set => _capacity = Mathf.Max(8, value); }

        private readonly LinkedList<string> _lruList = new();
        private readonly Dictionary<string, Motif> _cache = new();
        private readonly Dictionary<string, DateTime> _expiry = new();
        private readonly object _lock = new();
        private TimeSpan _defaultTtl = TimeSpan.FromMinutes(10);

        public int Count { get { lock (_lock) { return _cache.Count; } } }
        public int HitCount { get; private set; }
        public int MissCount { get; private set; }

        public MotifCache()
        {
            MotifEventDispatcher.OnStateChanged += OnMotifEvent;
            MotifEventDispatcher.OnTriggered += OnMotifEvent;
        }

        /// <summary>
        /// Adds or updates a motif in the cache with an optional time-to-live.
        /// </summary>
        /// <param name="theme">The motif theme key.</param>
        /// <param name="motif">The motif to cache.</param>
        /// <param name="ttl">Optional time-to-live for the cache entry.</param>
        public void Set(string theme, Motif motif, TimeSpan? ttl = null)
        {
            try
            {
                if (string.IsNullOrEmpty(theme) || motif == null)
                    throw new ArgumentException("Theme and motif must be non-null.");
                lock (_lock)
                {
                    if (_cache.ContainsKey(theme))
                    {
                        _lruList.Remove(theme);
                    }
                    else if (_cache.Count >= Capacity)
                    {
                        var oldest = _lruList.Last.Value;
                        _lruList.RemoveLast();
                        _cache.Remove(oldest);
                        _expiry.Remove(oldest);
                    }
                    _cache[theme] = motif;
                    _lruList.AddFirst(theme);
                    _expiry[theme] = DateTime.UtcNow + (ttl ?? _defaultTtl);
                }
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifCache.Set failed", "MotifCache.Set");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
        }

        /// <summary>
        /// Retrieves a motif from the cache by theme. Returns null if not found or expired.
        /// </summary>
        /// <param name="theme">The motif theme key.</param>
        /// <returns>The cached motif or null.</returns>
        public Motif Get(string theme)
        {
            try
            {
                if (string.IsNullOrEmpty(theme)) return null;
                lock (_lock)
                {
                    if (_cache.TryGetValue(theme, out var motif))
                    {
                        if (_expiry[theme] < DateTime.UtcNow)
                        {
                            _cache.Remove(theme);
                            _lruList.Remove(theme);
                            _expiry.Remove(theme);
                            MissCount++;
                            return null;
                        }
                        // Data integrity check
                        if (motif == null || string.IsNullOrEmpty(motif.Theme))
                        {
                            _cache.Remove(theme);
                            _lruList.Remove(theme);
                            _expiry.Remove(theme);
                            MissCount++;
                            VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError("MotifCache: Corrupt motif data detected on get.", "MotifCache.Get");
                            VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                            return null;
                        }
                        _lruList.Remove(theme);
                        _lruList.AddFirst(theme);
                        HitCount++;
                        return motif;
                    }
                    MissCount++;
                    return null;
                }
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifCache.Get failed", "MotifCache.Get");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return null;
            }
        }

        /// <summary>
        /// Removes a motif from the cache by theme.
        /// </summary>
        /// <param name="theme">The motif theme key.</param>
        public void Invalidate(string theme)
        {
            try
            {
                if (string.IsNullOrEmpty(theme)) return;
                lock (_lock)
                {
                    _cache.Remove(theme);
                    _lruList.Remove(theme);
                    _expiry.Remove(theme);
                }
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifCache.Invalidate failed", "MotifCache.Invalidate");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
        }

        /// <summary>
        /// Removes all motifs from the cache.
        /// </summary>
        public void InvalidateAll()
        {
            try
            {
                lock (_lock)
                {
                    _cache.Clear();
                    _lruList.Clear();
                    _expiry.Clear();
                }
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifCache.InvalidateAll failed", "MotifCache.InvalidateAll");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
        }

        /// <summary>
        /// Warms the cache with a set of motifs.
        /// </summary>
        /// <param name="motifs">The motifs to cache.</param>
        public void WarmCache(IEnumerable<Motif> motifs)
        {
            try
            {
                foreach (var motif in motifs)
                {
                    Set(motif.Theme, motif);
                }
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifCache.WarmCache failed", "MotifCache.WarmCache");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
        }

        private void OnMotifEvent(MotifEventBase evt)
        {
            if (evt is MotifStateChangedEvent stateEvt)
            {
                Invalidate(stateEvt.Motif.Theme);
            }
            else if (evt is MotifTriggeredEvent trigEvt)
            {
                Invalidate(trigEvt.Motif.Theme);
            }
        }
    }
}