using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

namespace VDM.Motifs
{
    /// <summary>
    /// Caches motifs for efficient local access, with TTL and background refresh.
    /// </summary>
    public class MotifCacheManager
    {
        private readonly MotifApiClient _apiClient;
        private readonly float _ttlSeconds;
        private readonly Dictionary<int, (Motif motif, DateTime expiry)> _motifById = new();
        private readonly Dictionary<string, (List<Motif> motifs, DateTime expiry)> _motifQueryCache = new();
        private readonly HashSet<int> _refreshing = new();

        public MotifCacheManager(MotifApiClient apiClient, float ttlSeconds = 60f)
        {
            _apiClient = apiClient;
            _ttlSeconds = ttlSeconds;
        }

        /// <summary>
        /// Get a motif by ID, using cache if valid.
        /// </summary>
        public async Task<Motif> GetMotifByIdAsync(int id)
        {
            if (_motifById.TryGetValue(id, out var entry) && entry.expiry > DateTime.UtcNow)
                return entry.motif;
            var motif = await _apiClient.GetMotifByIdAsync(id);
            _motifById[id] = (motif, DateTime.UtcNow.AddSeconds(_ttlSeconds));
            return motif;
        }

        /// <summary>
        /// Get motifs by query string, using cache if valid.
        /// </summary>
        public async Task<List<Motif>> GetMotifsAsync(string query = "")
        {
            if (_motifQueryCache.TryGetValue(query, out var entry) && entry.expiry > DateTime.UtcNow)
                return entry.motifs;
            var motifs = await _apiClient.GetMotifsAsync(query);
            _motifQueryCache[query] = (motifs, DateTime.UtcNow.AddSeconds(_ttlSeconds));
            // Cache by ID as well
            foreach (var motif in motifs)
                if (motif.Id.HasValue)
                    _motifById[motif.Id.Value] = (motif, DateTime.UtcNow.AddSeconds(_ttlSeconds));
            return motifs;
        }

        /// <summary>
        /// Invalidate a motif by ID.
        /// </summary>
        public void InvalidateMotif(int id)
        {
            _motifById.Remove(id);
        }

        /// <summary>
        /// Invalidate all cached motifs.
        /// </summary>
        public void InvalidateAll()
        {
            _motifById.Clear();
            _motifQueryCache.Clear();
        }

        /// <summary>
        /// Start background refresh for a motif by ID (if not already refreshing).
        /// </summary>
        public void StartBackgroundRefresh(int id, float refreshInterval = 30f)
        {
            if (_refreshing.Contains(id)) return;
            _refreshing.Add(id);
            Task.Run(async () =>
            {
                while (_refreshing.Contains(id))
                {
                    try
                    {
                        var motif = await _apiClient.GetMotifByIdAsync(id);
                        _motifById[id] = (motif, DateTime.UtcNow.AddSeconds(_ttlSeconds));
                    }
                    catch { /* log or ignore */ }
                    await Task.Delay(TimeSpan.FromSeconds(refreshInterval));
                }
            });
        }

        /// <summary>
        /// Stop background refresh for a motif by ID.
        /// </summary>
        public void StopBackgroundRefresh(int id)
        {
            _refreshing.Remove(id);
        }
    }
} 