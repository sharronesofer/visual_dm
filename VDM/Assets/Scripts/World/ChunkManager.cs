using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
{
    /// <summary>
    /// Manages grid chunks, including loading, unloading, and caching.
    /// </summary>
    public class ChunkManager
    {
        private readonly int chunkSize;
        private readonly Dictionary<Vector2Int, GridChunk> loadedChunks = new();
        private readonly HashSet<Vector2Int> cachedChunks = new();
        private readonly int cacheLimit = 64; // Example cache size

        public ChunkManager(int chunkSize)
        {
            this.chunkSize = chunkSize;
        }

        /// <summary>
        /// Gets the chunk containing the given world position, loading it if necessary.
        /// </summary>
        public GridChunk GetOrLoadChunk(Vector2 worldPosition)
        {
            Vector2Int chunkCoord = WorldToChunkCoord(worldPosition);
            if (!loadedChunks.TryGetValue(chunkCoord, out var chunk))
            {
                chunk = LoadChunk(chunkCoord);
                loadedChunks[chunkCoord] = chunk;
                CacheChunk(chunkCoord);
            }
            return chunk;
        }

        /// <summary>
        /// Converts a world position to chunk coordinates.
        /// </summary>
        public Vector2Int WorldToChunkCoord(Vector2 worldPosition)
        {
            int x = Mathf.FloorToInt(worldPosition.x / chunkSize);
            int y = Mathf.FloorToInt(worldPosition.y / chunkSize);
            return new Vector2Int(x, y);
        }

        /// <summary>
        /// Loads a chunk at the given chunk coordinates.
        /// </summary>
        private GridChunk LoadChunk(Vector2Int chunkCoord)
        {
            // TODO: Load from disk/network or create new
            return new GridChunk(chunkCoord, chunkSize);
        }

        /// <summary>
        /// Unloads a chunk at the given chunk coordinates.
        /// </summary>
        public void UnloadChunk(Vector2Int chunkCoord)
        {
            loadedChunks.Remove(chunkCoord);
            cachedChunks.Remove(chunkCoord);
        }

        /// <summary>
        /// Caches the chunk and evicts old chunks if over limit.
        /// </summary>
        private void CacheChunk(Vector2Int chunkCoord)
        {
            cachedChunks.Add(chunkCoord);
            if (cachedChunks.Count > cacheLimit)
            {
                // Simple eviction: remove oldest
                var toRemove = new List<Vector2Int>(cachedChunks)[0];
                UnloadChunk(toRemove);
            }
        }
    }
} 