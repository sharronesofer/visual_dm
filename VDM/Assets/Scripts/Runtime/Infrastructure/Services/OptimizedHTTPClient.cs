using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using VDM.Infrastructure.Services;
using System.IO.Compression;
using VDM.Infrastructure.Core;
using System.IO;

namespace VDM.Infrastructure.Services.Services.Http
{
    /// <summary>
    /// Optimized HTTP client with connection pooling, smart retry logic, and performance tracking.
    /// Designed for high-performance API communication with the VDM backend.
    /// </summary>
    public class OptimizedHttpClient : MonoBehaviour
    {
        [Header("Connection Configuration")]
        [SerializeField] private string _baseUrl = "http://localhost:8000";
        [SerializeField] private int _maxConcurrentRequests = 6;
        [SerializeField] private float _requestTimeout = 30f;
        [SerializeField] private int _connectionPoolSize = 10;
        [SerializeField] private bool _enableConnectionPooling = true;
        
        [Header("Retry Configuration")]
        [SerializeField] private int _maxRetryAttempts = 3;
        [SerializeField] private float _baseRetryDelay = 1f;
        [SerializeField] private float _maxRetryDelay = 30f;
        [SerializeField] private bool _enableExponentialBackoff = true;
        [SerializeField] private bool _enableJitter = true;
        
        [Header("Performance Optimization")]
        [SerializeField] private bool _enableRequestBatching = true;
        [SerializeField] private float _batchingDelay = 0.1f; // 100ms batching window
        [SerializeField] private int _maxBatchSize = 10;
        [SerializeField] private bool _enableGZipCompression = true;
        [SerializeField] private bool _enableCaching = true;
        
        [Header("Monitoring")]
        [SerializeField] private bool _enablePerformanceTracking = true;
        [SerializeField] private bool _enableDetailedLogging = false;
        
        // Connection management
        private Queue<UnityWebRequest> _connectionPool = new Queue<UnityWebRequest>();
        private HashSet<UnityWebRequest> _activeRequests = new HashSet<UnityWebRequest>();
        private Queue<HttpRequest> _requestQueue = new Queue<HttpRequest>();
        private List<HttpRequest> _batchedRequests = new List<HttpRequest>();
        
        // Performance tracking
        private PerformanceMonitor _performanceMonitor;
        private CacheManager _cacheManager;
        private HttpClientStatistics _statistics = new HttpClientStatistics();
        
        // Timing
        private float _lastBatchProcessTime = 0f;
        private Dictionary<UnityWebRequest, float> _requestStartTimes = new Dictionary<UnityWebRequest, float>();
        
        // Events
        public event Action<HttpRequest, HttpResponse> OnRequestCompleted;
        public event Action<HttpRequest, string> OnRequestFailed;
        public event Action<HttpClientStatistics> OnStatisticsUpdated;
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            InitializeHttpClient();
        }
        
        private void Start()
        {
            _performanceMonitor = FindObjectOfType<PerformanceMonitor>();
            _cacheManager = FindObjectOfType<CacheManager>();
            
            StartCoroutine(ProcessRequestQueue());
            
            if (_enableRequestBatching)
            {
                StartCoroutine(ProcessBatchedRequests());
            }
            
            StartCoroutine(PerformanceTrackingLoop());
        }
        
        private void OnDestroy()
        {
            StopAllCoroutines();
            CleanupConnections();
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeHttpClient()
        {
            // Pre-populate connection pool
            if (_enableConnectionPooling)
            {
                for (int i = 0; i < _connectionPoolSize; i++)
                {
                    var request = new UnityWebRequest();
                    _connectionPool.Enqueue(request);
                }
            }
            
            Debug.Log($"[OptimizedHttpClient] Initialized with {_connectionPoolSize} pooled connections");
        }
        
        #endregion
        
        #region Public API
        
        public void Get(string endpoint, Action<HttpResponse> onSuccess = null, Action<string> onError = null, 
                       Dictionary<string, string> headers = null, bool bypassCache = false)
        {
            var request = new HttpRequest
            {
                Method = HttpMethod.GET,
                Endpoint = endpoint,
                Headers = headers ?? new Dictionary<string, string>(),
                OnSuccess = onSuccess,
                OnError = onError,
                BypassCache = bypassCache,
                Timestamp = DateTime.Now
            };
            
            EnqueueRequest(request);
        }
        
        public void Post<T>(string endpoint, T data, Action<HttpResponse> onSuccess = null, Action<string> onError = null,
                           Dictionary<string, string> headers = null)
        {
            var request = new HttpRequest
            {
                Method = HttpMethod.POST,
                Endpoint = endpoint,
                Data = JsonUtility.ToJson(data),
                Headers = headers ?? new Dictionary<string, string>(),
                OnSuccess = onSuccess,
                OnError = onError,
                Timestamp = DateTime.Now
            };
            
            EnqueueRequest(request);
        }
        
        public void Put<T>(string endpoint, T data, Action<HttpResponse> onSuccess = null, Action<string> onError = null,
                          Dictionary<string, string> headers = null)
        {
            var request = new HttpRequest
            {
                Method = HttpMethod.PUT,
                Endpoint = endpoint,
                Data = JsonUtility.ToJson(data),
                Headers = headers ?? new Dictionary<string, string>(),
                OnSuccess = onSuccess,
                OnError = onError,
                Timestamp = DateTime.Now
            };
            
            EnqueueRequest(request);
        }
        
        public void Delete(string endpoint, Action<HttpResponse> onSuccess = null, Action<string> onError = null,
                          Dictionary<string, string> headers = null)
        {
            var request = new HttpRequest
            {
                Method = HttpMethod.DELETE,
                Endpoint = endpoint,
                Headers = headers ?? new Dictionary<string, string>(),
                OnSuccess = onSuccess,
                OnError = onError,
                Timestamp = DateTime.Now
            };
            
            EnqueueRequest(request);
        }
        
        public void Batch(List<HttpRequest> requests)
        {
            if (!_enableRequestBatching)
            {
                foreach (var request in requests)
                {
                    EnqueueRequest(request);
                }
                return;
            }
            
            _batchedRequests.AddRange(requests);
            Debug.Log($"[OptimizedHttpClient] Added {requests.Count} requests to batch");
        }
        
        #endregion
        
        #region Request Management
        
        private void EnqueueRequest(HttpRequest request)
        {
            // Check cache first for GET requests
            if (request.Method == HttpMethod.GET && _enableCaching && !request.BypassCache)
            {
                var cacheKey = GetCacheKey(request);
                var cachedResponse = _cacheManager?.Get<HttpResponse>(cacheKey, "API");
                
                if (cachedResponse != null)
                {
                    _statistics.CacheHits++;
                    request.OnSuccess?.Invoke(cachedResponse);
                    return;
                }
            }
            
            request.Id = Guid.NewGuid().ToString();
            _requestQueue.Enqueue(request);
            _statistics.TotalRequests++;
            
            if (_enableDetailedLogging)
            {
                Debug.Log($"[OptimizedHttpClient] Enqueued {request.Method} request to {request.Endpoint}");
            }
        }
        
        private IEnumerator ProcessRequestQueue()
        {
            while (true)
            {
                while (_requestQueue.Count > 0 && _activeRequests.Count < _maxConcurrentRequests)
                {
                    var request = _requestQueue.Dequeue();
                    StartCoroutine(ExecuteRequest(request));
                }
                
                yield return new WaitForSeconds(0.1f); // Check every 100ms
            }
        }
        
        private IEnumerator ProcessBatchedRequests()
        {
            while (true)
            {
                yield return new WaitForSeconds(_batchingDelay);
                
                if (_batchedRequests.Count > 0)
                {
                    var batch = _batchedRequests.Take(_maxBatchSize).ToList();
                    _batchedRequests.RemoveRange(0, batch.Count);
                    
                    StartCoroutine(ExecuteBatch(batch));
                }
            }
        }
        
        #endregion
        
        #region Request Execution
        
        private IEnumerator ExecuteRequest(HttpRequest request)
        {
            var attempts = 0;
            var delay = _baseRetryDelay;
            
            while (attempts <= _maxRetryAttempts)
            {
                var webRequest = CreateWebRequest(request);
                _activeRequests.Add(webRequest);
                _requestStartTimes[webRequest] = Time.time;
                
                yield return webRequest.SendWebRequest();
                
                var responseTime = (Time.time - _requestStartTimes[webRequest]) * 1000f; // Convert to ms
                _requestStartTimes.Remove(webRequest);
                _activeRequests.Remove(webRequest);
                
                // Track performance
                _performanceMonitor?.TrackAPICall(request.Endpoint, responseTime, 
                    webRequest.result == UnityWebRequest.Result.Success);
                
                if (webRequest.result == UnityWebRequest.Result.Success)
                {
                    var response = CreateResponse(webRequest, responseTime);
                    
                    // Cache successful GET responses
                    if (request.Method == HttpMethod.GET && _enableCaching)
                    {
                        var cacheKey = GetCacheKey(request);
                        _cacheManager?.Set(cacheKey, response, "API", 180f); // 3 minutes TTL
                    }
                    
                    _statistics.SuccessfulRequests++;
                    request.OnSuccess?.Invoke(response);
                    OnRequestCompleted?.Invoke(request, response);
                    
                    ReturnConnectionToPool(webRequest);
                    yield break;
                }
                
                attempts++;
                
                if (attempts <= _maxRetryAttempts && ShouldRetry(webRequest))
                {
                    _statistics.RetryAttempts++;
                    
                    if (_enableDetailedLogging)
                    {
                        Debug.LogWarning($"[OptimizedHttpClient] Retrying request {request.Id}, attempt {attempts}");
                    }
                    
                    ReturnConnectionToPool(webRequest);
                    
                    // Apply exponential backoff with jitter
                    if (_enableExponentialBackoff)
                    {
                        delay = Mathf.Min(_maxRetryDelay, delay * 2);
                    }
                    
                    if (_enableJitter)
                    {
                        delay += UnityEngine.Random.Range(0f, delay * 0.1f);
                    }
                    
                    yield return new WaitForSeconds(delay);
                }
                else
                {
                    _statistics.FailedRequests++;
                    var errorMessage = $"Request failed: {webRequest.error}";
                    request.OnError?.Invoke(errorMessage);
                    OnRequestFailed?.Invoke(request, errorMessage);
                    
                    ReturnConnectionToPool(webRequest);
                    yield break;
                }
            }
        }
        
        private IEnumerator ExecuteBatch(List<HttpRequest> batch)
        {
            var batchCoroutines = new List<Coroutine>();
            
            foreach (var request in batch)
            {
                batchCoroutines.Add(StartCoroutine(ExecuteRequest(request)));
            }
            
            // Wait for all requests in batch to complete
            foreach (var coroutine in batchCoroutines)
            {
                yield return coroutine;
            }
            
            _statistics.BatchesProcessed++;
            
            if (_enableDetailedLogging)
            {
                Debug.Log($"[OptimizedHttpClient] Completed batch of {batch.Count} requests");
            }
        }
        
        #endregion
        
        #region Web Request Management
        
        private UnityWebRequest CreateWebRequest(HttpRequest request)
        {
            UnityWebRequest webRequest;
            
            if (_enableConnectionPooling && _connectionPool.Count > 0)
            {
                webRequest = _connectionPool.Dequeue();
                webRequest.url = _baseUrl + request.Endpoint;
                webRequest.method = request.Method.ToString();
            }
            else
            {
                webRequest = new UnityWebRequest(_baseUrl + request.Endpoint, request.Method.ToString());
            }
            
            webRequest.timeout = (int)_requestTimeout;
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            
            // Set request body for POST/PUT
            if (!string.IsNullOrEmpty(request.Data))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(request.Data);
                webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
            }
            
            // Apply headers
            foreach (var header in request.Headers)
            {
                webRequest.SetRequestHeader(header.Key, header.Value);
            }
            
            // Default headers
            webRequest.SetRequestHeader("Content-Type", "application/json");
            webRequest.SetRequestHeader("Accept", "application/json");
            
            if (_enableGZipCompression)
            {
                webRequest.SetRequestHeader("Accept-Encoding", "gzip");
            }
            
            return webRequest;
        }
        
        private HttpResponse CreateResponse(UnityWebRequest webRequest, float responseTime)
        {
            return new HttpResponse
            {
                StatusCode = webRequest.responseCode,
                Text = webRequest.downloadHandler.text,
                Headers = webRequest.GetResponseHeaders(),
                IsSuccess = webRequest.result == UnityWebRequest.Result.Success,
                ResponseTime = responseTime,
                Timestamp = DateTime.Now
            };
        }
        
        private void ReturnConnectionToPool(UnityWebRequest webRequest)
        {
            if (_enableConnectionPooling && _connectionPool.Count < _connectionPoolSize)
            {
                // Reset the request for reuse
                webRequest.url = "";
                webRequest.method = "GET";
                webRequest.uploadHandler?.Dispose();
                webRequest.uploadHandler = null;
                webRequest.downloadHandler?.Dispose();
                webRequest.downloadHandler = new DownloadHandlerBuffer();
                
                _connectionPool.Enqueue(webRequest);
            }
            else
            {
                webRequest.Dispose();
            }
        }
        
        private bool ShouldRetry(UnityWebRequest webRequest)
        {
            // Retry on network errors and 5xx server errors
            return webRequest.result == UnityWebRequest.Result.ConnectionError ||
                   webRequest.result == UnityWebRequest.Result.ProtocolError && 
                   webRequest.responseCode >= 500;
        }
        
        #endregion
        
        #region Caching
        
        private string GetCacheKey(HttpRequest request)
        {
            var keyBuilder = new StringBuilder();
            keyBuilder.Append($"{request.Method}:{request.Endpoint}");
            
            // Include headers that affect response
            var relevantHeaders = new[] { "Authorization", "Accept-Language", "User-Agent" };
            foreach (var header in relevantHeaders)
            {
                if (request.Headers.ContainsKey(header))
                {
                    keyBuilder.Append($":{header}={request.Headers[header]}");
                }
            }
            
            return keyBuilder.ToString();
        }
        
        public void InvalidateCache(string pattern = null)
        {
            if (pattern == null)
            {
                _cacheManager?.ClearCategory("API");
            }
            else
            {
                _cacheManager?.InvalidatePattern(pattern);
            }
        }
        
        #endregion
        
        #region Performance Tracking
        
        private IEnumerator PerformanceTrackingLoop()
        {
            while (_enablePerformanceTracking)
            {
                yield return new WaitForSeconds(10f); // Update every 10 seconds
                
                UpdateStatistics();
                OnStatisticsUpdated?.Invoke(_statistics);
            }
        }
        
        private void UpdateStatistics()
        {
            _statistics.ActiveConnections = _activeRequests.Count;
            _statistics.PooledConnections = _connectionPool.Count;
            _statistics.QueuedRequests = _requestQueue.Count;
            _statistics.SuccessRate = _statistics.TotalRequests > 0 
                ? (float)_statistics.SuccessfulRequests / _statistics.TotalRequests : 0f;
            _statistics.CacheHitRate = (_statistics.SuccessfulRequests + _statistics.CacheHits) > 0
                ? (float)_statistics.CacheHits / (_statistics.SuccessfulRequests + _statistics.CacheHits) : 0f;
            _statistics.LastUpdated = DateTime.Now;
        }
        
        public HttpClientStatistics GetStatistics()
        {
            UpdateStatistics();
            return _statistics;
        }
        
        #endregion
        
        #region Cleanup
        
        private void CleanupConnections()
        {
            // Cancel all active requests
            foreach (var request in _activeRequests.ToList())
            {
                request.Abort();
                request.Dispose();
            }
            _activeRequests.Clear();
            
            // Dispose pooled connections
            while (_connectionPool.Count > 0)
            {
                var request = _connectionPool.Dequeue();
                request.Dispose();
            }
            
            Debug.Log("[OptimizedHttpClient] Cleaned up all connections");
        }
        
        #endregion
        
        #region Configuration
        
        public void SetBaseUrl(string baseUrl)
        {
            _baseUrl = baseUrl;
            Debug.Log($"[OptimizedHttpClient] Base URL updated to: {baseUrl}");
        }
        
        public void SetMaxConcurrentRequests(int maxRequests)
        {
            _maxConcurrentRequests = Mathf.Clamp(maxRequests, 1, 20);
            Debug.Log($"[OptimizedHttpClient] Max concurrent requests updated to: {_maxConcurrentRequests}");
        }
        
        public void SetRequestTimeout(float timeout)
        {
            _requestTimeout = Mathf.Clamp(timeout, 5f, 120f);
            Debug.Log($"[OptimizedHttpClient] Request timeout updated to: {_requestTimeout}s");
        }
        
        #endregion
        
        private void CompressData(byte[] data, Stream outputStream)
        {
            using (var gzipStream = new GZipStream(outputStream, System.IO.Compression.CompressionLevel.Fastest))
            {
                gzipStream.Write(data, 0, data.Length);
            }
        }
    }
    
    #region Data Classes
    
    [Serializable]
    public class HttpRequest
    {
        public string Id;
        public HttpMethod Method;
        public string Endpoint;
        public string Data;
        public Dictionary<string, string> Headers;
        public Action<HttpResponse> OnSuccess;
        public Action<string> OnError;
        public bool BypassCache;
        public DateTime Timestamp;
    }
    
    [Serializable]
    public class HttpResponse
    {
        public long StatusCode;
        public string Text;
        public Dictionary<string, string> Headers;
        public bool IsSuccess;
        public float ResponseTime;
        public DateTime Timestamp;
        
        public T FromJson<T>()
        {
            return JsonUtility.FromJson<T>(Text);
        }
    }
    
    [Serializable]
    public class HttpClientStatistics
    {
        public int TotalRequests;
        public int SuccessfulRequests;
        public int FailedRequests;
        public int RetryAttempts;
        public int CacheHits;
        public int BatchesProcessed;
        public int ActiveConnections;
        public int PooledConnections;
        public int QueuedRequests;
        public float SuccessRate;
        public float CacheHitRate;
        public DateTime LastUpdated;
    }
    
    public enum HttpMethod
    {
        GET,
        POST,
        PUT,
        DELETE,
        PATCH
    }
    
    #endregion
} 