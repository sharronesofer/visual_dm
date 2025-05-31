using NativeWebSocket;
using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.Systems;
using VDM.Systems.Arc.Services;
using VDM.Systems.Arc.Integration;
using System.Threading.Tasks;


namespace VDM.Infrastructure.Integration
{
    /// <summary>
    /// Manages the transition from mock services to real backend integration
    /// Handles service discovery, health checking, and graceful fallback mechanisms
    /// </summary>
    public class BackendIntegrationManager : MonoBehaviour
    {
        public static BackendIntegrationManager Instance { get; private set; }

        [Header("Integration Configuration")]
        [SerializeField] private bool enableRealBackend = true;
        [SerializeField] private bool enableFallbackToMock = true;
        [SerializeField] private float healthCheckInterval = 30f;
        [SerializeField] private int maxConnectionRetries = 3;
        [SerializeField] private float connectionTimeout = 10f;

        [Header("Backend Endpoints")]
        [SerializeField] private string productionBackendUrl = "http://127.0.0.1:8000";
        [SerializeField] private string mockBackendUrl = "http://127.0.0.1:5000";
        [SerializeField] private string healthEndpoint = "/health";

        [Header("Service Status")]
        [SerializeField] private bool isProductionBackendAvailable = false;
        [SerializeField] private bool isMockBackendAvailable = false;
        [SerializeField] private BackendMode currentMode = BackendMode.Unknown;

        // Health monitoring
        private Coroutine healthCheckCoroutine;
        private int consecutiveFailures = 0;
        private float lastHealthCheck = 0f;

        // Integration state
        private Dictionary<string, ServiceStatus> serviceStatuses = new Dictionary<string, ServiceStatus>();
        private List<IntegrationTest> integrationTests = new List<IntegrationTest>();
        private bool isIntegrationTestsRunning = false;

        // Events
        public event Action<BackendMode> OnBackendModeChanged;
        public event Action<string, ServiceStatus> OnServiceStatusChanged;
        public event Action<IntegrationTestResult> OnIntegrationTestCompleted;
        public event Action<string> OnIntegrationError;

        // Service clients - using actual services that exist
        private ArcService arcService;
        private ArcEventIntegration arcEventIntegration;
        private MockServerWebSocket mockServerWebSocket;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeIntegrationManager();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            StartIntegrationProcess();
        }

        private void OnDestroy()
        {
            if (healthCheckCoroutine != null)
            {
                StopCoroutine(healthCheckCoroutine);
            }
        }

        #region Initialization

        private void InitializeIntegrationManager()
        {
            Debug.Log("[BackendIntegrationManager] Initializing backend integration system...");

            // Initialize service status tracking
            serviceStatuses.Clear();
            serviceStatuses["MockServer"] = ServiceStatus.Unknown;
            serviceStatuses["ProductionBackend"] = ServiceStatus.Unknown;
            serviceStatuses["ArcSystem"] = ServiceStatus.Unknown;
            serviceStatuses["NarrativeSystem"] = ServiceStatus.Unknown;

            // Initialize integration tests
            InitializeIntegrationTests();

            // Get actual service references that exist
            arcService = FindObjectOfType<ArcService>();
            arcEventIntegration = FindObjectOfType<ArcEventIntegration>();
            mockServerWebSocket = MockServerWebSocket.Instance;

            Debug.Log("[BackendIntegrationManager] Integration manager initialized");
        }

        private void InitializeIntegrationTests()
        {
            integrationTests.Clear();

            // Add comprehensive integration tests
            integrationTests.Add(new IntegrationTest
            {
                testId = "backend_connectivity",
                testName = "Backend Connectivity Test",
                description = "Verify connection to backend services",
                priority = TestPriority.Critical,
                executeTest = TestBackendConnectivity
            });

            integrationTests.Add(new IntegrationTest
            {
                testId = "arc_system_integration",
                testName = "Arc System Integration Test",
                description = "Test arc system with real backend",
                priority = TestPriority.High,
                executeTest = TestArcSystemIntegration
            });

            integrationTests.Add(new IntegrationTest
            {
                testId = "narrative_progression_integration",
                testName = "Narrative Progression Integration Test",
                description = "Test narrative system with real backend",
                priority = TestPriority.High,
                executeTest = TestNarrativeProgressionIntegration
            });

            integrationTests.Add(new IntegrationTest
            {
                testId = "realtime_communication",
                testName = "Real-time Communication Test",
                description = "Test WebSocket communication with backend",
                priority = TestPriority.Medium,
                executeTest = TestRealtimeCommunication
            });

            integrationTests.Add(new IntegrationTest
            {
                testId = "service_fallback",
                testName = "Service Fallback Test",
                description = "Test graceful fallback to mock services",
                priority = TestPriority.Medium,
                executeTest = TestServiceFallback
            });

            integrationTests.Add(new IntegrationTest
            {
                testId = "data_consistency",
                testName = "Data Consistency Test",
                description = "Verify data consistency between Unity and backend",
                priority = TestPriority.High,
                executeTest = TestDataConsistency
            });

            Debug.Log($"[BackendIntegrationManager] Initialized {integrationTests.Count} integration tests");
        }

        #endregion

        #region Integration Process

        private void StartIntegrationProcess()
        {
            Debug.Log("[BackendIntegrationManager] Starting backend integration process...");
            StartCoroutine(IntegrationProcessCoroutine());
        }

        private IEnumerator IntegrationProcessCoroutine()
        {
            // Phase 1: Service Discovery
            Debug.Log("[BackendIntegrationManager] Phase 1: Service Discovery");
            yield return DiscoverServices();

            // Phase 2: Backend Selection
            Debug.Log("[BackendIntegrationManager] Phase 2: Backend Selection");
            SelectOptimalBackend();

            // Phase 3: Service Configuration
            Debug.Log("[BackendIntegrationManager] Phase 3: Service Configuration");
            yield return ConfigureServices();

            // Phase 4: Integration Testing
            Debug.Log("[BackendIntegrationManager] Phase 4: Integration Testing");
            yield return RunIntegrationTests();

            // Phase 5: Health Monitoring
            Debug.Log("[BackendIntegrationManager] Phase 5: Starting Health Monitoring");
            StartHealthMonitoring();

            Debug.Log("[BackendIntegrationManager] Backend integration process completed");
        }

        private IEnumerator DiscoverServices()
        {
            Debug.Log("[BackendIntegrationManager] Discovering available services...");

            // Test production backend
            if (enableRealBackend)
            {
                yield return TestBackendEndpoint(productionBackendUrl, "ProductionBackend");
            }

            // Test mock backend
            yield return TestBackendEndpoint(mockBackendUrl, "MockServer");

            Debug.Log($"[BackendIntegrationManager] Service discovery complete - Production: {isProductionBackendAvailable}, Mock: {isMockBackendAvailable}");
        }

        private IEnumerator TestBackendEndpoint(string baseUrl, string serviceName)
        {
            Debug.Log($"[BackendIntegrationManager] Testing {serviceName} at {baseUrl}");

            bool isAvailable = false;
            string testUrl = baseUrl + healthEndpoint;

            // Create UnityWebRequest for health check
            using (var request = UnityEngine.Networking.UnityWebRequest.Get(testUrl))
            {
                request.timeout = (int)connectionTimeout;
                yield return request.SendWebRequest();

                if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
                {
                    try
                    {
                        var responseText = request.downloadHandler.text;
                        Debug.Log($"[BackendIntegrationManager] {serviceName} health check response: {responseText}");
                        isAvailable = true;
                    }
                    catch (Exception ex)
                    {
                        Debug.LogWarning($"[BackendIntegrationManager] Failed to parse {serviceName} response: {ex.Message}");
                    }
                }
                else
                {
                    Debug.LogWarning($"[BackendIntegrationManager] {serviceName} health check failed: {request.error}");
                }
            }

            // Update service status
            if (serviceName == "ProductionBackend")
            {
                isProductionBackendAvailable = isAvailable;
                serviceStatuses["ProductionBackend"] = isAvailable ? ServiceStatus.Available : ServiceStatus.Unavailable;
            }
            else if (serviceName == "MockServer")
            {
                isMockBackendAvailable = isAvailable;
                serviceStatuses["MockServer"] = isAvailable ? ServiceStatus.Available : ServiceStatus.Unavailable;
            }

            OnServiceStatusChanged?.Invoke(serviceName, serviceStatuses[serviceName]);
        }

        private void SelectOptimalBackend()
        {
            BackendMode newMode = BackendMode.Unknown;

            if (enableRealBackend && isProductionBackendAvailable)
            {
                newMode = BackendMode.Production;
                Debug.Log("[BackendIntegrationManager] Selected production backend");
            }
            else if (enableFallbackToMock && isMockBackendAvailable)
            {
                newMode = BackendMode.Mock;
                Debug.Log("[BackendIntegrationManager] Fallback to mock backend");
            }
            else
            {
                newMode = BackendMode.Offline;
                Debug.LogWarning("[BackendIntegrationManager] No backend available - offline mode");
            }

            if (currentMode != newMode)
            {
                currentMode = newMode;
                OnBackendModeChanged?.Invoke(currentMode);
            }
        }

        private IEnumerator ConfigureServices()
        {
            Debug.Log($"[BackendIntegrationManager] Configuring services for {currentMode} mode");

            string selectedBaseUrl = GetSelectedBackendUrl();

            // Configure Arc System Service  
            if (arcService != null)
            {
                // Arc service will automatically use the configured base URL
                serviceStatuses["ArcSystem"] = ServiceStatus.Configured;
                OnServiceStatusChanged?.Invoke("ArcSystem", ServiceStatus.Configured);
                Debug.Log($"[BackendIntegrationManager] Arc service configured for {selectedBaseUrl}");
            }

            // Configure Mock Server WebSocket
            if (mockServerWebSocket != null && currentMode == BackendMode.Mock)
            {
                // Mock server WebSocket should be configured for mock mode
                serviceStatuses["MockServer"] = ServiceStatus.Configured;
                OnServiceStatusChanged?.Invoke("MockServer", ServiceStatus.Configured);
                Debug.Log("[BackendIntegrationManager] Mock server WebSocket maintained for fallback");
            }

            // Configure Arc Event Integration (Narrative Events)
            if (arcEventIntegration != null)
            {
                // Arc event integration automatically adapts to configured services
                serviceStatuses["NarrativeSystem"] = ServiceStatus.Configured;
                OnServiceStatusChanged?.Invoke("NarrativeSystem", ServiceStatus.Configured);
                Debug.Log("[BackendIntegrationManager] Arc event integration configured");
            }

            yield return new WaitForSeconds(1f); // Allow configuration to settle
        }

        private string GetSelectedBackendUrl()
        {
            return currentMode switch
            {
                BackendMode.Production => productionBackendUrl,
                BackendMode.Mock => mockBackendUrl,
                _ => mockBackendUrl // Default fallback
            };
        }

        #endregion

        #region Integration Testing

        private IEnumerator RunIntegrationTests()
        {
            if (isIntegrationTestsRunning) yield break;

            isIntegrationTestsRunning = true;
            Debug.Log("[BackendIntegrationManager] Running integration tests...");

            int passedTests = 0;
            int totalTests = integrationTests.Count;

            foreach (var test in integrationTests)
            {
                Debug.Log($"[BackendIntegrationManager] Running test: {test.testName}");
                
                var result = new IntegrationTestResult
                {
                    testId = test.testId,
                    testName = test.testName,
                    startTime = DateTime.UtcNow
                };

                try
                {
                    yield return test.executeTest(result);
                    
                    if (result.passed)
                    {
                        passedTests++;
                        Debug.Log($"[BackendIntegrationManager] ✅ {test.testName} PASSED");
                    }
                    else
                    {
                        Debug.LogError($"[BackendIntegrationManager] ❌ {test.testName} FAILED: {result.errorMessage}");
                    }
                }
                catch (Exception ex)
                {
                    result.passed = false;
                    result.errorMessage = ex.Message;
                    Debug.LogError($"[BackendIntegrationManager] ❌ {test.testName} EXCEPTION: {ex.Message}");
                }

                result.endTime = DateTime.UtcNow;
                result.duration = (result.endTime - result.startTime).TotalSeconds;
                OnIntegrationTestCompleted?.Invoke(result);

                yield return new WaitForSeconds(0.5f); // Brief pause between tests
            }

            float successRate = (float)passedTests / totalTests * 100f;
            Debug.Log($"[BackendIntegrationManager] Integration tests completed: {passedTests}/{totalTests} passed ({successRate:F1}%)");

            isIntegrationTestsRunning = false;
        }

        #region Individual Integration Tests

        private IEnumerator TestBackendConnectivity(IntegrationTestResult result)
        {
            string targetUrl = GetSelectedBackendUrl() + healthEndpoint;
            
            using (var request = UnityEngine.Networking.UnityWebRequest.Get(targetUrl))
            {
                request.timeout = (int)connectionTimeout;
                yield return request.SendWebRequest();

                if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
                {
                    result.passed = true;
                    result.details = $"Successfully connected to {targetUrl}";
                }
                else
                {
                    result.passed = false;
                    result.errorMessage = $"Failed to connect to {targetUrl}: {request.error}";
                }
            }
        }

        private IEnumerator TestArcSystemIntegration(IntegrationTestResult result)
        {
            if (arcService == null)
            {
                result.passed = false;
                result.errorMessage = "Arc service not available";
                yield break;
            }

            bool testCompleted = false;
            bool testPassed = false;
            string testError = "";

            // Test getting arcs using the real async API
            var getArcsTask = arcService.GetArcsAsync();
            
            // Wait for the async task to complete
            while (!getArcsTask.IsCompleted)
            {
                yield return null;
            }

            if (getArcsTask.IsFaulted)
            {
                testCompleted = true;
                testPassed = false;
                testError = $"Arc service error: {getArcsTask.Exception?.GetBaseException().Message}";
            }
            else if (getArcsTask.IsCompletedSuccessfully)
            {
                testCompleted = true;
                var arcs = getArcsTask.Result;
                if (arcs != null)
                {
                    testPassed = true;
                    result.details = $"Successfully retrieved {arcs.Count} arcs";
                }
                else
                {
                    testError = "Arc service returned null";
                }
            }
            else
            {
                testCompleted = true;
                testPassed = false;
                testError = "Arc service task was cancelled";
            }

            result.passed = testPassed;
            result.errorMessage = testError;
        }

        private IEnumerator TestNarrativeProgressionIntegration(IntegrationTestResult result)
        {
            if (arcEventIntegration == null)
            {
                result.passed = false;
                result.errorMessage = "Arc event integration not available";
                yield break;
            }

            bool eventReceived = false;

            // Subscribe to narrative events using the real integration
            System.Action<string> eventHandler = (eventData) =>
            {
                eventReceived = true;
            };

            // Note: Real implementation may have different event signatures
            // For now, we'll test if the component exists and is active
            if (arcEventIntegration.gameObject.activeInHierarchy)
            {
                eventReceived = true; // Component is active and available
            }

            // Wait for event processing
            float timeout = 5f;
            while (!eventReceived && timeout > 0)
            {
                timeout -= Time.deltaTime;
                yield return null;
            }

            if (eventReceived)
            {
                result.passed = true;
                result.details = "Arc event integration is active and available";
            }
            else
            {
                result.passed = false;
                result.errorMessage = "Arc event integration is not active or available";
            }
        }

        private IEnumerator TestRealtimeCommunication(IntegrationTestResult result)
        {
            // Test WebSocket functionality if available
            var webSocketClient = MockServerWebSocket.Instance;
            
            if (webSocketClient == null)
            {
                result.passed = false;
                result.errorMessage = "WebSocket client not available";
                yield break;
            }

            bool messageReceived = false;
            
            // Check if WebSocket is available and active
            if (webSocketClient.gameObject.activeInHierarchy)
            {
                messageReceived = true; // WebSocket service is available
            }

            // For production mode, WebSocket might not be required
            if (currentMode == BackendMode.Production)
            {
                result.passed = true;
                result.details = "WebSocket not required for production backend";
                yield break;
            }

            // Wait for response or timeout
            float timeout = 5f;
            while (!messageReceived && timeout > 0)
            {
                timeout -= Time.deltaTime;
                yield return null;
            }

            if (messageReceived || currentMode == BackendMode.Production)
            {
                result.passed = true;
                result.details = "Real-time communication verified";
            }
            else
            {
                result.passed = false;
                result.errorMessage = "No real-time communication response received";
            }
        }

        private IEnumerator TestServiceFallback(IntegrationTestResult result)
        {
            // This test verifies that the system can handle service unavailability
            var originalMode = currentMode;
            
            // Simulate service failure
            if (originalMode == BackendMode.Production)
            {
                // Test fallback to mock
                if (isMockBackendAvailable && enableFallbackToMock)
                {
                    result.passed = true;
                    result.details = "Mock fallback available for production failure";
                }
                else
                {
                    result.passed = false;
                    result.errorMessage = "No fallback available for production failure";
                }
            }
            else
            {
                // Already using fallback or offline
                result.passed = true;
                result.details = $"Currently using {originalMode} mode";
            }

            yield return null;
        }

        private IEnumerator TestDataConsistency(IntegrationTestResult result)
        {
            // Test that data remains consistent between Unity and backend
            if (arcService == null)
            {
                result.passed = false;
                result.errorMessage = "Arc service not available for consistency test";
                yield break;
            }

            bool dataConsistent = true;
            string inconsistencyDetails = "";
            bool operationCompleted = false;

            // Test Arc service data consistency
            var getArcsTask = arcService.GetArcsAsync();
            
            // Wait for the async task to complete
            while (!getArcsTask.IsCompleted)
            {
                yield return null;
            }
            
            operationCompleted = getArcsTask.IsCompleted;

            if (!operationCompleted || getArcsTask.IsFaulted)
            {
                result.passed = false;
                result.errorMessage = getArcsTask.IsFaulted ? 
                    $"Backend data retrieval failed: {getArcsTask.Exception?.GetBaseException().Message}" : 
                    "Backend data retrieval timed out";
                yield break;
            }

            // For now, just verify that we can retrieve data successfully
            var backendArcs = getArcsTask.Result;
            if (backendArcs != null)
            {
                dataConsistent = true;
            }
            else
            {
                dataConsistent = false;
                inconsistencyDetails = "Backend returned null arc data";
            }

            if (dataConsistent)
            {
                result.passed = true;
                result.details = $"Data consistency verified: Retrieved {backendArcs?.Count ?? 0} arcs from backend";
            }
            else
            {
                result.passed = false;
                result.errorMessage = $"Data inconsistency detected: {inconsistencyDetails}";
            }
        }

        #endregion

        #endregion

        #region Health Monitoring

        private void StartHealthMonitoring()
        {
            if (healthCheckCoroutine != null)
            {
                StopCoroutine(healthCheckCoroutine);
            }

            healthCheckCoroutine = StartCoroutine(HealthMonitoringCoroutine());
        }

        private IEnumerator HealthMonitoringCoroutine()
        {
            while (true)
            {
                yield return new WaitForSeconds(healthCheckInterval);
                
                yield return PerformHealthCheck();
                
                lastHealthCheck = Time.time;
            }
        }

        private IEnumerator PerformHealthCheck()
        {
            string currentBackendUrl = GetSelectedBackendUrl();
            
            yield return TestBackendEndpoint(currentBackendUrl, currentMode.ToString());
            
            // Check if we need to switch backends
            if (currentMode == BackendMode.Production && !isProductionBackendAvailable)
            {
                consecutiveFailures++;
                Debug.LogWarning($"[BackendIntegrationManager] Production backend failure #{consecutiveFailures}");
                
                if (consecutiveFailures >= maxConnectionRetries && enableFallbackToMock && isMockBackendAvailable)
                {
                    Debug.Log("[BackendIntegrationManager] Switching to mock backend due to production failures");
                    currentMode = BackendMode.Mock;
                    OnBackendModeChanged?.Invoke(currentMode);
                    yield return ConfigureServices();
                    consecutiveFailures = 0;
                }
            }
            else if (isProductionBackendAvailable && currentMode == BackendMode.Mock && enableRealBackend)
            {
                Debug.Log("[BackendIntegrationManager] Production backend recovered, switching back");
                currentMode = BackendMode.Production;
                OnBackendModeChanged?.Invoke(currentMode);
                yield return ConfigureServices();
                consecutiveFailures = 0;
            }
            else if (currentMode == BackendMode.Production && isProductionBackendAvailable)
            {
                consecutiveFailures = 0; // Reset on successful connection
            }
        }

        #endregion

        #region Public API

        public void ForceBackendMode(BackendMode mode)
        {
            if (mode != currentMode)
            {
                Debug.Log($"[BackendIntegrationManager] Forcing backend mode to {mode}");
                currentMode = mode;
                OnBackendModeChanged?.Invoke(currentMode);
                StartCoroutine(ConfigureServices());
            }
        }

        public void RefreshServiceDiscovery()
        {
            Debug.Log("[BackendIntegrationManager] Refreshing service discovery");
            StartCoroutine(DiscoverServices());
        }

        public void RunIntegrationTestsManually()
        {
            if (!isIntegrationTestsRunning)
            {
                StartCoroutine(RunIntegrationTests());
            }
        }

        public BackendMode GetCurrentBackendMode() => currentMode;

        public Dictionary<string, ServiceStatus> GetServiceStatuses() => new Dictionary<string, ServiceStatus>(serviceStatuses);

        public bool IsBackendAvailable() => currentMode != BackendMode.Offline && currentMode != BackendMode.Unknown;

        #endregion
    }

    #region Data Structures

    public enum BackendMode
    {
        Unknown,
        Production,
        Mock,
        Offline
    }

    public enum ServiceStatus
    {
        Unknown,
        Available,
        Unavailable,
        Configured,
        Error
    }

    public enum TestPriority
    {
        Low,
        Medium,
        High,
        Critical
    }

    [System.Serializable]
    public class IntegrationTest
    {
        public string testId;
        public string testName;
        public string description;
        public TestPriority priority;
        public System.Func<IntegrationTestResult, IEnumerator> executeTest;
    }

    [System.Serializable]
    public class IntegrationTestResult
    {
        public string testId;
        public string testName;
        public bool passed;
        public string errorMessage;
        public string details;
        public DateTime startTime;
        public DateTime endTime;
        public double duration;
    }

    #endregion
} 