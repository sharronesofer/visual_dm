using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System.IO.Compression;
using System.IO;
using System.Linq;
using System.Text;
using System;
using UnityEngine.Networking;
using UnityEngine;


namespace VDM.Runtime.Services
{
    /// <summary>
    /// Optimized HTTP client with connection pooling, caching, compression, and delta updates
    /// Provides enhanced performance for Unity-backend communication
    /// </summary>
    public class OptimizedHTTPClient : BaseHTTPClient
    {
        [Header("Performance Optimization")]
        [SerializeField] private bool enableConnectionPooling = true;
        [SerializeField] private bool enableCompression = true;
        [SerializeField] private bool enableLocalCaching = true;
        [SerializeField] private bool enableDeltaUpdates = true;
        [SerializeField] private int maxConcurrentRequests = 10;
        [SerializeField] private float cacheExpirationTime = 300f; // 5 minutes

        [Header("Compression Settings")]
        [SerializeField] private int compressionThreshold = 1024; // Compress data larger than 1KB
        [SerializeField] private CompressionLevel compressionLevel = System.IO.Compression.CompressionLevel.Optimal;

        [Header("Connection Pool Settings")]
        [SerializeField] private int maxConnectionsPerEndpoint = 5;
        [SerializeField] private float connectionTimeout = 10f;
        [SerializeField] private float keepAliveTime = 30f;

        // Connection pooling
        private Dictionary<string, Queue<UnityWebRequest>> connectionPool = new Dictionary<string, Queue<UnityWebRequest>>();
        private Dictionary<string, int> activeConnections = new Dictionary<string, int>();
        private Dictionary<UnityWebRequest, string> requestToEndpoint = new Dictionary<UnityWebRequest, string>();

        // Local caching
        private Dictionary<string, CacheEntry> cache = new Dictionary<string, CacheEntry>();
        private Dictionary<string, string> dataChecksums = new Dictionary<string, string>();

        // Delta tracking for efficient updates
        private Dictionary<string, object> lastDataState = new Dictionary<string, object>();

        // Request queue for managing concurrent requests
        private Queue<RequestQueueItem> requestQueue = new Queue<RequestQueueItem>();
        private int activeRequestCount = 0;

        protected override string GetClientName() => "OptimizedHTTPClient";

        protected override void InitializeClient()
        {
            base.InitializeClient();

            if (enableLocalCaching)
            {
                StartCoroutine(CacheCleanupRoutine());
            }

            if (enableConnectionPooling)
            {
                StartCoroutine(ConnectionPoolMaintenanceRoutine());
            }

            // Add compression support to default headers
            if (enableCompression)
            {
                defaultHeaders["Accept-Encoding"] = "gzip, deflate";
            }
        }

        #region Optimized HTTP Methods

        /// <summary>
        /// Optimized GET request with caching and pooling
        /// </summary>
        protected IEnumerator OptimizedGetRequestCoroutine(string endpoint, Action<bool, string> callback, bool useCache = true, int retryCount = 0)
        {
            string cacheKey = $"GET:{endpoint}";

            // Check cache first
            if (enableLocalCaching && useCache && IsValidCacheEntry(cacheKey))
            {
                var cachedEntry = cache[cacheKey];
                callback?.Invoke(true, cachedEntry.data);
                yield break;
            }

            // Queue request if we're at max concurrent requests
            if (activeRequestCount >= maxConcurrentRequests)
            {
                yield return QueueRequest(new RequestQueueItem
                {
                    method = "GET",
                    endpoint = endpoint,
                    callback = callback,
                    retryCount = retryCount
                });
                yield break;
            }

            activeRequestCount++;
            
            UnityWebRequest request = GetPooledRequest(endpoint, "GET");
            if (request == null)
            {
                request = UnityWebRequest.Get($"{baseUrl}{endpoint}");
            }

            SetOptimizedHeaders(request);
            request.timeout = (int)requestTimeout;

            yield return request.SendWebRequest();

            bool success = request.result == UnityWebRequest.Result.Success;
            string response = success ? request.downloadHandler.text : null;

            if (success)
            {
                // Handle compressed response
                if (enableCompression && request.GetResponseHeader("Content-Encoding") != null)
                {
                    response = DecompressResponse(request.downloadHandler.data);
                }

                // Cache successful response
                if (enableLocalCaching && useCache)
                {
                    CacheResponse(cacheKey, response);
                }

                LogRequest("GET", endpoint, success);
                callback?.Invoke(success, response);
            }
            else if (retryCount < maxRetryAttempts)
            {
                if (debugLogging)
                    Debug.LogWarning($"[{GetClientName()}] GET {endpoint} failed, retrying... ({retryCount + 1}/{maxRetryAttempts})");
                
                yield return new WaitForSeconds(Mathf.Pow(2, retryCount)); // Exponential backoff
                yield return OptimizedGetRequestCoroutine(endpoint, callback, useCache, retryCount + 1);
            }
            else
            {
                LogRequest("GET", endpoint, success, request.error);
                callback?.Invoke(false, null);
                OnError?.Invoke($"GET {endpoint} failed: {request.error}");
            }

            ReturnRequestToPool(request);
            activeRequestCount--;

            // Process queued requests
            ProcessRequestQueue();
        }

        /// <summary>
        /// Optimized POST request with compression and delta updates
        /// </summary>
        protected IEnumerator OptimizedPostRequestCoroutine(string endpoint, object data, Action<bool, string> callback, bool useDelta = true, int retryCount = 0)
        {
            // Queue request if we're at max concurrent requests
            if (activeRequestCount >= maxConcurrentRequests)
            {
                yield return QueueRequest(new RequestQueueItem
                {
                    method = "POST",
                    endpoint = endpoint,
                    data = data,
                    callback = callback,
                    retryCount = retryCount
                });
                yield break;
            }

            activeRequestCount++;

            // Prepare data for sending
            object dataToSend = data;
            bool isDelta = false;

            // Apply delta optimization if enabled
            if (enableDeltaUpdates && useDelta)
            {
                var deltaData = CreateDeltaUpdate(endpoint, data);
                if (deltaData != null)
                {
                    dataToSend = deltaData;
                    isDelta = true;
                }
                else
                {
                    // Store current state for future delta calculations
                    lastDataState[endpoint] = data;
                }
            }

            string jsonData = JsonConvert.SerializeObject(dataToSend);
            byte[] bodyData = null;

            // Apply compression if data is large enough
            if (enableCompression && jsonData.Length > compressionThreshold)
            {
                bodyData = CompressData(jsonData);
            }
            else
            {
                bodyData = Encoding.UTF8.GetBytes(jsonData);
            }

            UnityWebRequest request = GetPooledRequest(endpoint, "POST");
            if (request == null)
            {
                request = new UnityWebRequest($"{baseUrl}{endpoint}", "POST");
                request.downloadHandler = new DownloadHandlerBuffer();
            }

            request.uploadHandler = new UploadHandlerRaw(bodyData);
            SetOptimizedHeaders(request);
            
            if (enableCompression && jsonData.Length > compressionThreshold)
            {
                request.SetRequestHeader("Content-Encoding", "gzip");
            }

            if (isDelta)
            {
                request.SetRequestHeader("X-Delta-Update", "true");
            }

            request.timeout = (int)requestTimeout;

            yield return request.SendWebRequest();

            bool success = request.result == UnityWebRequest.Result.Success;
            string response = success ? request.downloadHandler.text : null;

            if (success)
            {
                // Handle compressed response
                if (enableCompression && request.GetResponseHeader("Content-Encoding") != null)
                {
                    response = DecompressResponse(request.downloadHandler.data);
                }

                // Update state tracking for successful delta updates
                if (enableDeltaUpdates && success && !isDelta)
                {
                    lastDataState[endpoint] = data;
                }

                LogRequest("POST", endpoint, success);
                callback?.Invoke(success, response);
            }
            else if (retryCount < maxRetryAttempts)
            {
                if (debugLogging)
                    Debug.LogWarning($"[{GetClientName()}] POST {endpoint} failed, retrying... ({retryCount + 1}/{maxRetryAttempts})");
                
                yield return new WaitForSeconds(Mathf.Pow(2, retryCount)); // Exponential backoff
                yield return OptimizedPostRequestCoroutine(endpoint, data, callback, useDelta, retryCount + 1);
            }
            else
            {
                LogRequest("POST", endpoint, success, request.error);
                callback?.Invoke(false, null);
                OnError?.Invoke($"POST {endpoint} failed: {request.error}");
            }

            ReturnRequestToPool(request);
            activeRequestCount--;

            // Process queued requests
            ProcessRequestQueue();
        }

        #endregion

        #region Connection Pooling

        private UnityWebRequest GetPooledRequest(string endpoint, string method)
        {
            if (!enableConnectionPooling) return null;

            string poolKey = GetPoolKey(endpoint);
            
            if (connectionPool.TryGetValue(poolKey, out Queue<UnityWebRequest> pool) && pool.Count > 0)
            {
                var request = pool.Dequeue();
                
                // Reset request for reuse
                if (request.downloadHandler != null)
                {
                    request.downloadHandler.Dispose();
                }
                if (request.uploadHandler != null)
                {
                    request.uploadHandler.Dispose();
                }

                request.downloadHandler = new DownloadHandlerBuffer();
                request.method = method;
                
                return request;
            }

            return null;
        }

        private void ReturnRequestToPool(UnityWebRequest request)
        {
            if (!enableConnectionPooling) return;

            string endpoint = requestToEndpoint.TryGetValue(request, out string ep) ? ep : "";
            string poolKey = GetPoolKey(endpoint);

            if (!connectionPool.TryGetValue(poolKey, out Queue<UnityWebRequest> pool))
            {
                pool = new Queue<UnityWebRequest>();
                connectionPool[poolKey] = pool;
            }

            // Only pool if we haven't exceeded the limit
            if (pool.Count < maxConnectionsPerEndpoint)
            {
                pool.Enqueue(request);
                requestToEndpoint[request] = endpoint;
            }
            else
            {
                request.Dispose();
            }

            // Update active connection count
            if (activeConnections.TryGetValue(poolKey, out int count))
            {
                activeConnections[poolKey] = Math.Max(0, count - 1);
            }
        }

        private string GetPoolKey(string endpoint)
        {
            // Extract base endpoint for pooling (remove query parameters)
            int queryIndex = endpoint.IndexOf('?');
            return queryIndex > 0 ? endpoint.Substring(0, queryIndex) : endpoint;
        }

        private IEnumerator ConnectionPoolMaintenanceRoutine()
        {
            while (true)
            {
                yield return new WaitForSeconds(keepAliveTime);

                // Clean up old connections
                var keysToRemove = new List<string>();
                foreach (var kvp in connectionPool)
                {
                    var pool = kvp.Value;
                    while (pool.Count > 0)
                    {
                        var request = pool.Dequeue();
                        request.Dispose();
                    }

                    if (pool.Count == 0)
                    {
                        keysToRemove.Add(kvp.Key);
                    }
                }

                foreach (var key in keysToRemove)
                {
                    connectionPool.Remove(key);
                    activeConnections.Remove(key);
                }
            }
        }

        #endregion

        #region Caching

        private bool IsValidCacheEntry(string key)
        {
            if (!cache.TryGetValue(key, out CacheEntry entry))
                return false;

            return Time.time < entry.expirationTime;
        }

        private void CacheResponse(string key, string data)
        {
            cache[key] = new CacheEntry
            {
                data = data,
                expirationTime = Time.time + cacheExpirationTime,
                checksum = CalculateChecksum(data)
            };
        }

        private IEnumerator CacheCleanupRoutine()
        {
            while (true)
            {
                yield return new WaitForSeconds(60f); // Clean up every minute

                var keysToRemove = new List<string>();
                foreach (var kvp in cache)
                {
                    if (Time.time >= kvp.Value.expirationTime)
                    {
                        keysToRemove.Add(kvp.Key);
                    }
                }

                foreach (var key in keysToRemove)
                {
                    cache.Remove(key);
                }
            }
        }

        #endregion

        #region Compression

        private byte[] CompressData(string data)
        {
            byte[] inputBytes = Encoding.UTF8.GetBytes(data);
            
            using (var outputStream = new MemoryStream())
            {
                using (var gzipStream = new GZipStream(outputStream, compressionLevel))
                {
                    gzipStream.Write(inputBytes, 0, inputBytes.Length);
                }
                return outputStream.ToArray();
            }
        }

        private string DecompressResponse(byte[] compressedData)
        {
            using (var inputStream = new MemoryStream(compressedData))
            using (var gzipStream = new GZipStream(inputStream, CompressionMode.Decompress))
            using (var outputStream = new MemoryStream())
            {
                gzipStream.CopyTo(outputStream);
                return Encoding.UTF8.GetString(outputStream.ToArray());
            }
        }

        #endregion

        #region Delta Updates

        private object CreateDeltaUpdate(string endpoint, object newData)
        {
            if (!lastDataState.TryGetValue(endpoint, out object lastData))
                return null;

            // Simple delta implementation - in a real scenario, you'd want more sophisticated diffing
            var deltaChanges = new Dictionary<string, object>();
            var newDataDict = JsonConvert.DeserializeObject<Dictionary<string, object>>(JsonConvert.SerializeObject(newData));
            var lastDataDict = JsonConvert.DeserializeObject<Dictionary<string, object>>(JsonConvert.SerializeObject(lastData));

            foreach (var kvp in newDataDict)
            {
                if (!lastDataDict.TryGetValue(kvp.Key, out object lastValue) || 
                    !JsonConvert.SerializeObject(kvp.Value).Equals(JsonConvert.SerializeObject(lastValue)))
                {
                    deltaChanges[kvp.Key] = kvp.Value;
                }
            }

            return deltaChanges.Count > 0 ? new { delta = true, changes = deltaChanges } : null;
        }

        #endregion

        #region Request Queue Management

        private IEnumerator QueueRequest(RequestQueueItem item)
        {
            requestQueue.Enqueue(item);
            
            // Wait until we can process this request
            while (activeRequestCount >= maxConcurrentRequests)
            {
                yield return new WaitForSeconds(0.1f);
            }

            // Process the request if it's still in queue (might have been processed already)
            if (requestQueue.Count > 0 && requestQueue.Peek() == item)
            {
                requestQueue.Dequeue();
                
                if (item.method == "GET")
                {
                    yield return OptimizedGetRequestCoroutine(item.endpoint, item.callback, true, item.retryCount);
                }
                else if (item.method == "POST")
                {
                    yield return OptimizedPostRequestCoroutine(item.endpoint, item.data, item.callback, true, item.retryCount);
                }
            }
        }

        private void ProcessRequestQueue()
        {
            if (requestQueue.Count > 0 && activeRequestCount < maxConcurrentRequests)
            {
                StartCoroutine(ProcessNextQueuedRequest());
            }
        }

        private IEnumerator ProcessNextQueuedRequest()
        {
            if (requestQueue.Count > 0)
            {
                var item = requestQueue.Dequeue();
                
                if (item.method == "GET")
                {
                    yield return OptimizedGetRequestCoroutine(item.endpoint, item.callback, true, item.retryCount);
                }
                else if (item.method == "POST")
                {
                    yield return OptimizedPostRequestCoroutine(item.endpoint, item.data, item.callback, true, item.retryCount);
                }
            }
        }

        #endregion

        #region Helper Methods

        private void SetOptimizedHeaders(UnityWebRequest request)
        {
            SetHeaders(request);
            
            // Add performance-oriented headers
            request.SetRequestHeader("Connection", "keep-alive");
            request.SetRequestHeader("Cache-Control", "max-age=300");
        }

        private string CalculateChecksum(string data)
        {
            // Simple checksum for cache validation
            return data.GetHashCode().ToString();
        }

        #endregion

        #region Public API

        /// <summary>
        /// Optimized GET request with caching
        /// </summary>
        public void GetOptimized(string endpoint, Action<bool, string> callback, bool useCache = true)
        {
            if (!isInitialized)
                InitializeClient();

            StartCoroutine(OptimizedGetRequestCoroutine(endpoint, callback, useCache));
        }

        /// <summary>
        /// Optimized POST request with compression and delta updates
        /// </summary>
        public void PostOptimized(string endpoint, object data, Action<bool, string> callback, bool useDelta = true)
        {
            if (!isInitialized)
                InitializeClient();

            StartCoroutine(OptimizedPostRequestCoroutine(endpoint, data, callback, useDelta));
        }

        /// <summary>
        /// Clear cache manually
        /// </summary>
        public void ClearCache()
        {
            cache.Clear();
            dataChecksums.Clear();
        }

        /// <summary>
        /// Get performance statistics
        /// </summary>
        public NetworkPerformanceStats GetPerformanceStats()
        {
            return new NetworkPerformanceStats
            {
                cacheHitRatio = cache.Count > 0 ? (float)cache.Count / (cache.Count + 1) : 0f,
                activeConnections = activeRequestCount,
                queuedRequests = requestQueue.Count,
                cachedItems = cache.Count,
                pooledConnections = connectionPool.Values.Sum(pool => pool.Count)
            };
        }

        #endregion

        #region Data Classes

        [System.Serializable]
        private class CacheEntry
        {
            public string data;
            public float expirationTime;
            public string checksum;
        }

        private class RequestQueueItem
        {
            public string method;
            public string endpoint;
            public object data;
            public Action<bool, string> callback;
            public int retryCount;
        }

        [System.Serializable]
        public class NetworkPerformanceStats
        {
            public float cacheHitRatio;
            public int activeConnections;
            public int queuedRequests;
            public int cachedItems;
            public int pooledConnections;
        }

        #endregion

        protected virtual void OnDestroy()
        {
            // Clean up connection pools
            foreach (var pool in connectionPool.Values)
            {
                while (pool.Count > 0)
                {
                    pool.Dequeue().Dispose();
                }
            }

            base.OnDestroy();
        }
    }
} 