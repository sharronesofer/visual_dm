using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

namespace VisualDM.World
{
    /// <summary>
    /// Handles asynchronous streaming of grid data, prioritizing chunks near the player/camera.
    /// </summary>
    public class GridStreamer : MonoBehaviour
    {
        private ChunkManager chunkManager;
        private Transform playerTransform;
        private float streamRadius = 64f;
        private int maxConcurrentLoads = 2;
        private HashSet<Vector2Int> loadingChunks = new();

        public void Initialize(ChunkManager chunkManager, Transform playerTransform, float streamRadius = 64f)
        {
            this.chunkManager = chunkManager;
            this.playerTransform = playerTransform;
            this.streamRadius = streamRadius;
        }

        /// <summary>
        /// Starts streaming grid chunks around the player asynchronously.
        /// </summary>
        public void StartStreaming()
        {
            StartCoroutine(StreamChunksCoroutine());
        }

        private IEnumerator StreamChunksCoroutine()
        {
            while (true)
            {
                Vector2 playerPos = playerTransform.position;
                List<Vector2Int> neededChunks = GetChunksInRadius(playerPos, streamRadius);
                int loads = 0;
                foreach (var chunkCoord in neededChunks)
                {
                    if (!loadingChunks.Contains(chunkCoord))
                    {
                        loadingChunks.Add(chunkCoord);
                        loads++;
                        if (loads > maxConcurrentLoads) break;
                        // Async load chunk
                        Task.Run(() => chunkManager.GetOrLoadChunk((Vector2)chunkCoord)).ContinueWith(_ =>
                        {
                            loadingChunks.Remove(chunkCoord);
                        });
                    }
                }
                yield return new WaitForSeconds(0.1f);
            }
        }

        /// <summary>
        /// Gets a list of chunk coordinates within the streaming radius.
        /// </summary>
        private List<Vector2Int> GetChunksInRadius(Vector2 center, float radius)
        {
            int chunkSize = 32; // TODO: Use actual chunk size
            int r = Mathf.CeilToInt(radius / chunkSize);
            Vector2Int centerChunk = chunkManager.WorldToChunkCoord(center);
            List<Vector2Int> result = new();
            for (int dx = -r; dx <= r; dx++)
            {
                for (int dy = -r; dy <= r; dy++)
                {
                    Vector2Int coord = new(centerChunk.x + dx, centerChunk.y + dy);
                    result.Add(coord);
                }
            }
            return result;
        }
    }
} 