using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using VDM.Runtime.Core.Services;
using VDM.Runtime.Services.Http;
using VDM.Runtime.Services.WebSocket;

namespace VDM.Tests.Integration
{
    /// <summary>
    /// Demo controller that showcases all performance optimization components working together.
    /// Provides real-time UI feedback and stress testing capabilities.
    /// </summary>
    public class PerformanceDemoController : MonoBehaviour
    {
        [Header("Performance Components")]
        [SerializeField] private PerformanceMonitor _performanceMonitor;
        [SerializeField] private CacheManager _cacheManager;
        [SerializeField] private OptimizedHttpClient _httpClient;
        [SerializeField] private OptimizedWebSocketClient _webSocketClient;
        
        [Header("UI Elements")]
        [SerializeField] private Text _fpsText;
        [SerializeField] private Text _memoryText;
        [SerializeField] private Text _systemCountText;
        [SerializeField] private Text _cacheStatsText;
        [SerializeField] private Text _httpStatsText;
        [SerializeField] private Text _webSocketStatsText;
        [SerializeField] private Text _alertsText;
        [SerializeField] private ScrollRect _alertsScrollRect;
        
        [Header("Demo Controls")]
        [SerializeField] private Button _stressTestButton;
        [SerializeField] private Button _clearCacheButton;
        [SerializeField] private Button _triggerAlertButton;
        [SerializeField] private Button _resetMetricsButton;
        [SerializeField] private Slider _systemLoadSlider;
        [SerializeField] private Toggle _enableMonitoringToggle;
        
        [Header("Stress Test Settings")]
        [SerializeField] private int _stressTestDuration = 10;
        [SerializeField] private int _stressTestIntensity = 100;
        [SerializeField] private bool _stressTestRunning = false;
        
        private List<string> _alertHistory = new List<string>();
        private bool _uiInitialized = false;
        
        #region Unity Lifecycle
        
        private void Start()
        {
            InitializeDemo();
            StartCoroutine(UpdateUI());
        }
        
        private void OnDestroy()
        {
            StopAllCoroutines();
            UnsubscribeFromEvents();
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeDemo()
        {
            // Find performance components if not assigned
            if (_performanceMonitor == null)
                _performanceMonitor = FindObjectOfType<PerformanceMonitor>();
            if (_cacheManager == null)
                _cacheManager = FindObjectOfType<CacheManager>();
            if (_httpClient == null)
                _httpClient = FindObjectOfType<OptimizedHttpClient>();
            if (_webSocketClient == null)
                _webSocketClient = FindObjectOfType<OptimizedWebSocketClient>();
            
            // Create components if they don't exist
            if (_performanceMonitor == null)
                _performanceMonitor = gameObject.AddComponent<PerformanceMonitor>();
            if (_cacheManager == null)
                _cacheManager = gameObject.AddComponent<CacheManager>();
            if (_httpClient == null)
                _httpClient = gameObject.AddComponent<OptimizedHttpClient>();
            if (_webSocketClient == null)
                _webSocketClient = gameObject.AddComponent<OptimizedWebSocketClient>();
            
            // Subscribe to events
            SubscribeToEvents();
            
            // Setup UI controls
            SetupUIControls();
            
            _uiInitialized = true;
            
            Debug.Log("[PerformanceDemoController] Demo initialized successfully");
        }
        
        private void SubscribeToEvents()
        {
            if (_performanceMonitor != null)
            {
                _performanceMonitor.OnPerformanceAlert += OnPerformanceAlert;
                _performanceMonitor.OnMetricsUpdated += OnMetricsUpdated;
            }
            
            if (_httpClient != null)
            {
                _httpClient.OnRequestCompleted += OnHttpRequestCompleted;
                _httpClient.OnRequestFailed += OnHttpRequestFailed;
            }
            
            if (_cacheManager != null)
            {
                _cacheManager.OnCacheHit += OnCacheHit;
                _cacheManager.OnCacheMiss += OnCacheMiss;
            }
        }
        
        private void UnsubscribeFromEvents()
        {
            if (_performanceMonitor != null)
            {
                _performanceMonitor.OnPerformanceAlert -= OnPerformanceAlert;
                _performanceMonitor.OnMetricsUpdated -= OnMetricsUpdated;
            }
            
            if (_httpClient != null)
            {
                _httpClient.OnRequestCompleted -= OnHttpRequestCompleted;
                _httpClient.OnRequestFailed -= OnHttpRequestFailed;
            }
            
            if (_cacheManager != null)
            {
                _cacheManager.OnCacheHit -= OnCacheHit;
                _cacheManager.OnCacheMiss -= OnCacheMiss;
            }
        }
        
        private void SetupUIControls()
        {
            if (_stressTestButton != null)
                _stressTestButton.onClick.AddListener(StartStressTest);
            
            if (_clearCacheButton != null)
                _clearCacheButton.onClick.AddListener(ClearCache);
            
            if (_triggerAlertButton != null)
                _triggerAlertButton.onClick.AddListener(TriggerTestAlert);
            
            if (_resetMetricsButton != null)
                _resetMetricsButton.onClick.AddListener(ResetMetrics);
            
            if (_systemLoadSlider != null)
                _systemLoadSlider.onValueChanged.AddListener(OnSystemLoadChanged);
            
            if (_enableMonitoringToggle != null)
                _enableMonitoringToggle.onValueChanged.AddListener(OnMonitoringToggleChanged);
        }
        
        #endregion
        
        #region UI Updates
        
        private IEnumerator UpdateUI()
        {
            while (true)
            {
                if (_uiInitialized)
                {
                    UpdatePerformanceUI();
                    UpdateCacheUI();
                    UpdateHttpUI();
                    UpdateWebSocketUI();
                }
                
                yield return new WaitForSeconds(0.5f); // Update UI every 500ms
            }
        }
        
        private void UpdatePerformanceUI()
        {
            if (_performanceMonitor == null) return;
            
            var metrics = _performanceMonitor.GetCurrentMetrics();
            
            if (_fpsText != null)
            {
                _fpsText.text = $"FPS: {metrics.FPS:F1}";
                _fpsText.color = metrics.FPS >= 60 ? Color.green : metrics.FPS >= 30 ? Color.yellow : Color.red;
            }
            
            if (_memoryText != null)
            {
                _memoryText.text = $"Memory: {metrics.MemoryUsageMB:F0} MB";
                _memoryText.color = metrics.MemoryUsageMB < 1024 ? Color.green : 
                                   metrics.MemoryUsageMB < 2048 ? Color.yellow : Color.red;
            }
            
            if (_systemCountText != null)
            {
                _systemCountText.text = $"Active Systems: {metrics.SystemCount}";
            }
        }
        
        private void UpdateCacheUI()
        {
            if (_cacheManager == null || _cacheStatsText == null) return;
            
            var stats = _cacheManager.GetStatistics();
            var cacheText = $"Cache: {stats.TotalItems} items\n" +
                           $"Hit Rate: {stats.HitRate:P1}\n" +
                           $"Memory: {stats.TotalMemoryUsage / (1024 * 1024):F1} MB";
            
            _cacheStatsText.text = cacheText;
        }
        
        private void UpdateHttpUI()
        {
            if (_httpClient == null || _httpStatsText == null) return;
            
            var stats = _httpClient.GetStatistics();
            var httpText = $"HTTP: {stats.TotalRequests} requests\n" +
                          $"Success Rate: {stats.SuccessRate:P1}\n" +
                          $"Cache Hit Rate: {stats.CacheHitRate:P1}\n" +
                          $"Active: {stats.ActiveConnections}";
            
            _httpStatsText.text = httpText;
        }
        
        private void UpdateWebSocketUI()
        {
            if (_webSocketClient == null || _webSocketStatsText == null) return;
            
            var stats = _webSocketClient.GetStatistics();
            var wsText = $"WebSocket: {stats.MessagesSent} sent\n" +
                        $"Received: {stats.MessagesReceived}\n" +
                        $"Queued: {stats.QueuedMessages}\n" +
                        $"Success Rate: {stats.MessageSuccessRate:P1}";
            
            _webSocketStatsText.text = wsText;
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnPerformanceAlert(PerformanceAlert alert)
        {
            var alertMessage = $"[{alert.Timestamp:HH:mm:ss}] {alert.Level}: {alert.Title} - {alert.Message}";
            _alertHistory.Add(alertMessage);
            
            // Keep only last 20 alerts
            if (_alertHistory.Count > 20)
            {
                _alertHistory.RemoveAt(0);
            }
            
            UpdateAlertsUI();
            
            Debug.Log($"[PerformanceDemoController] Alert: {alertMessage}");
        }
        
        private void OnMetricsUpdated(PerformanceMetrics metrics)
        {
            // Performance metrics are updated - UI will catch this in the update loop
        }
        
        private void OnHttpRequestCompleted(VDM.Runtime.Services.Http.HttpRequest request, VDM.Runtime.Services.Http.HttpResponse response)
        {
            Debug.Log($"[PerformanceDemoController] HTTP request completed: {request.Endpoint} in {response.ResponseTime:F2}ms");
        }
        
        private void OnHttpRequestFailed(VDM.Runtime.Services.Http.HttpRequest request, string error)
        {
            Debug.LogWarning($"[PerformanceDemoController] HTTP request failed: {request.Endpoint} - {error}");
        }
        
        private void OnCacheHit(string key, object data)
        {
            Debug.Log($"[PerformanceDemoController] Cache hit: {key}");
        }
        
        private void OnCacheMiss(string key)
        {
            Debug.Log($"[PerformanceDemoController] Cache miss: {key}");
        }
        
        #endregion
        
        #region UI Control Handlers
        
        private void StartStressTest()
        {
            if (!_stressTestRunning)
            {
                StartCoroutine(RunStressTest());
            }
        }
        
        private void ClearCache()
        {
            _cacheManager?.ClearCache();
            AddAlert("Cache cleared manually", AlertLevel.Info);
        }
        
        private void TriggerTestAlert()
        {
            // Trigger a test performance alert
            _performanceMonitor?.TrackMemoryUsage("TestAlert", 3L * 1024 * 1024 * 1024); // 3GB to trigger critical alert
        }
        
        private void ResetMetrics()
        {
            _performanceMonitor?.ResetMetrics();
            _alertHistory.Clear();
            UpdateAlertsUI();
            AddAlert("Metrics reset", AlertLevel.Info);
        }
        
        private void OnSystemLoadChanged(float value)
        {
            // Adjust system load simulation based on slider
            var intensity = Mathf.RoundToInt(value * 100);
            StartCoroutine(SimulateSystemLoad(intensity));
        }
        
        private void OnMonitoringToggleChanged(bool enabled)
        {
            // Toggle monitoring on/off
            if (_performanceMonitor != null)
            {
                _performanceMonitor.enabled = enabled;
            }
        }
        
        #endregion
        
        #region Stress Testing
        
        private IEnumerator RunStressTest()
        {
            _stressTestRunning = true;
            AddAlert($"Stress test started ({_stressTestDuration}s)", AlertLevel.Info);
            
            if (_stressTestButton != null)
            {
                _stressTestButton.interactable = false;
                var originalText = _stressTestButton.GetComponentInChildren<Text>();
                if (originalText != null)
                    originalText.text = "Running...";
            }
            
            var startTime = Time.time;
            var testData = new List<object>();
            
            while (Time.time - startTime < _stressTestDuration)
            {
                // CPU stress - system activity tracking
                for (int i = 0; i < _stressTestIntensity; i++)
                {
                    _performanceMonitor?.TrackSystemActivity($"StressTest{i % 10}", 
                        Random.Range(1f, 50f), Random.Range(100, 5000));
                }
                
                // Memory stress - cache operations
                for (int i = 0; i < _stressTestIntensity / 2; i++)
                {
                    var data = new { id = i, data = new byte[Random.Range(1024, 10240)], timestamp = Time.time };
                    testData.Add(data);
                    _cacheManager?.Set($"stress-{i}-{Time.time}", data);
                }
                
                // Network stress - HTTP requests
                for (int i = 0; i < 5; i++)
                {
                    _httpClient?.Get($"/api/stress-test/{i}", null, null);
                }
                
                // WebSocket stress - message sending
                for (int i = 0; i < 10; i++)
                {
                    _webSocketClient?.SendMessage("stress-test", new { id = i, timestamp = Time.time });
                }
                
                yield return new WaitForSeconds(0.1f);
            }
            
            // Cleanup
            testData.Clear();
            System.GC.Collect();
            
            _stressTestRunning = false;
            AddAlert("Stress test completed", AlertLevel.Info);
            
            if (_stressTestButton != null)
            {
                _stressTestButton.interactable = true;
                var originalText = _stressTestButton.GetComponentInChildren<Text>();
                if (originalText != null)
                    originalText.text = "Start Stress Test";
            }
        }
        
        private IEnumerator SimulateSystemLoad(int intensity)
        {
            // Simulate varying system load
            for (int i = 0; i < intensity; i++)
            {
                _performanceMonitor?.TrackSystemActivity("LoadSimulation", 
                    Random.Range(1f, 20f), Random.Range(256, 2048));
                
                if (i % 10 == 0)
                    yield return null; // Yield every 10 operations
            }
        }
        
        #endregion
        
        #region Utility Methods
        
        private void UpdateAlertsUI()
        {
            if (_alertsText != null)
            {
                _alertsText.text = string.Join("\n", _alertHistory.ToArray());
                
                // Auto-scroll to bottom
                if (_alertsScrollRect != null)
                {
                    Canvas.ForceUpdateCanvases();
                    _alertsScrollRect.verticalNormalizedPosition = 0f;
                }
            }
        }
        
        private void AddAlert(string message, AlertLevel level)
        {
            var alert = new PerformanceAlert
            {
                Title = "Demo",
                Message = message,
                Level = level,
                Timestamp = System.DateTime.Now,
                SystemSource = "DemoController"
            };
            
            OnPerformanceAlert(alert);
        }
        
        #endregion
        
        #region Public API
        
        public void StartPerformanceBenchmark()
        {
            StartCoroutine(RunPerformanceBenchmark());
        }
        
        private IEnumerator RunPerformanceBenchmark()
        {
            AddAlert("Performance benchmark started", AlertLevel.Info);
            
            // Run the same benchmarks as the test suite
            yield return StartCoroutine(BenchmarkFPS());
            yield return StartCoroutine(BenchmarkMemory());
            yield return StartCoroutine(BenchmarkAPI());
            
            AddAlert("Performance benchmark completed", AlertLevel.Info);
        }
        
        private IEnumerator BenchmarkFPS()
        {
            var fpsHistory = new List<float>();
            var duration = 5f;
            var startTime = Time.time;
            
            while (Time.time - startTime < duration)
            {
                var metrics = _performanceMonitor.GetCurrentMetrics();
                fpsHistory.Add(metrics.FPS);
                yield return new WaitForSeconds(0.1f);
            }
            
            var avgFPS = fpsHistory.Count > 0 ? fpsHistory.Average() : 0f;
            var minFPS = fpsHistory.Count > 0 ? fpsHistory.Min() : 0f;
            
            AddAlert($"FPS Benchmark - Avg: {avgFPS:F1}, Min: {minFPS:F1}", 
                avgFPS >= 60 ? AlertLevel.Info : AlertLevel.Warning);
        }
        
        private IEnumerator BenchmarkMemory()
        {
            var initialMemory = _performanceMonitor.GetCurrentMetrics().MemoryUsageMB;
            
            // Create memory load
            var testObjects = new List<object>();
            for (int i = 0; i < 1000; i++)
            {
                testObjects.Add(new byte[1024]);
                if (i % 100 == 0) yield return null;
            }
            
            var peakMemory = _performanceMonitor.GetCurrentMetrics().MemoryUsageMB;
            
            // Cleanup
            testObjects.Clear();
            System.GC.Collect();
            yield return new WaitForSeconds(1f);
            
            var finalMemory = _performanceMonitor.GetCurrentMetrics().MemoryUsageMB;
            
            AddAlert($"Memory Benchmark - Peak: {peakMemory}MB, Final: {finalMemory}MB", 
                peakMemory < 2048 ? AlertLevel.Info : AlertLevel.Warning);
        }
        
        private IEnumerator BenchmarkAPI()
        {
            var requestCount = 5;
            var startTime = Time.time;
            
            for (int i = 0; i < requestCount; i++)
            {
                _httpClient.Get($"/api/benchmark/{i}", null, null);
                yield return new WaitForSeconds(0.2f);
            }
            
            var totalTime = (Time.time - startTime) * 1000f; // Convert to ms
            var avgTime = totalTime / requestCount;
            
            AddAlert($"API Benchmark - Avg Response: {avgTime:F2}ms", 
                avgTime < 200 ? AlertLevel.Info : AlertLevel.Warning);
        }
        
        #endregion
    }
} 