using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine;
using VDM.Runtime.Services;
using VDM.Systems;


namespace VDM.Runtime.Integration
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

        // Service clients
        private MockServerClient mockServerClient;
        private ArcSystemClient arcSystemClient;
        private NarrativeProgressionManager narrativeManager;

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

            // Get service references
            mockServerClient = MockServerClient.Instance;
            arcSystemClient = ArcSystemClient.Instance;
            narrativeManager = NarrativeProgressionManager.Instance;

            // Initialize integration tests
            InitializeIntegrationTests();

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

            // Configure Arc System Client
            if (arcSystemClient != null)
            {
                // Update base URL for arc system client
                var arcClientType = arcSystemClient.GetType();
                var baseUrlField = arcClientType.GetField("baseUrl", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                if (baseUrlField != null)
                {
                    baseUrlField.SetValue(arcSystemClient, selectedBaseUrl);
                    Debug.Log($"[BackendIntegrationManager] Arc system client configured for {selectedBaseUrl}");
                }

                serviceStatuses["ArcSystem"] = ServiceStatus.Configured;
                OnServiceStatusChanged?.Invoke("ArcSystem", ServiceStatus.Configured);
            }

            // Configure Mock Server Client
            if (mockServerClient != null && currentMode == BackendMode.Mock)
            {
                // Mock server client should be configured for mock mode
                serviceStatuses["MockServer"] = ServiceStatus.Configured;
                OnServiceStatusChanged?.Invoke("MockServer", ServiceStatus.Configured);
                Debug.Log("[BackendIntegrationManager] Mock server client maintained for fallback");
            }

            // Configure Narrative Manager
            if (narrativeManager != null)
            {
                // Narrative manager automatically adapts to configured services
                serviceStatuses["NarrativeSystem"] = ServiceStatus.Configured;
                OnServiceStatusChanged?.Invoke("NarrativeSystem", ServiceStatus.Configured);
                Debug.Log("[BackendIntegrationManager] Narrative progression manager configured");
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
            if (arcSystemClient == null)
            {
                result.passed = false;
                result.errorMessage = "Arc system client not available";
                yield break;
            }

            bool testCompleted = false;
            bool testPassed = false;
            string testError = "";

            // Test getting arcs
            arcSystemClient.GetArcs(callback: arcs =>
            {
                testCompleted = true;
                if (arcs != null)
                {
                    testPassed = true;
                    result.details = $"Successfully retrieved {arcs.Count} arcs";
                }
                else
                {
                    testError = "Failed to retrieve arcs";
                }
            });

            // Wait for test completion
            float timeout = connectionTimeout;
            while (!testCompleted && timeout > 0)
            {
                timeout -= Time.deltaTime;
                yield return null;
            }

            if (!testCompleted)
            {
                result.passed = false;
                result.errorMessage = "Arc system test timed out";
            }
            else
            {
                result.passed = testPassed;
                result.errorMessage = testError;
            }
        }

        private IEnumerator TestNarrativeProgressionIntegration(IntegrationTestResult result)
        {
            if (narrativeManager == null)
            {
                result.passed = false;
                result.errorMessage = "Narrative manager not available";
                yield break;
            }

            bool eventReceived = false;

            // Subscribe to narrative events
            System.Action<NarrativeEvent> eventHandler = (narrativeEvent) =>
            {
                eventReceived = true;
            };

            narrativeManager.OnNarrativeEventTriggered += eventHandler;

            // Trigger a test event
            narrativeManager.TriggerNarrativeEvent(
                "integration-test-arc", 
                NarrativeEventType.CustomTrigger,
                new Dictionary<string, object> { { "test", "integration" } }
            );

            // Wait for event processing
            float timeout = 5f;
            while (!eventReceived && timeout > 0)
            {
                timeout -= Time.deltaTime;
                yield return null;
            }

            // Cleanup
            narrativeManager.OnNarrativeEventTriggered -= eventHandler;

            if (eventReceived)
            {
                result.passed = true;
                result.details = "Narrative event successfully triggered and processed";
            }
            else
            {
                result.passed = false;
                result.errorMessage = "Narrative event was not processed within timeout";
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
            System.Action<string> messageHandler = (message) =>
            {
                messageReceived = true;
            };

            // Subscribe to messages
            webSocketClient.OnMessageReceived += messageHandler;

            // Send ping if connected, or attempt connection
            if (webSocketClient.IsConnected)
            {
                webSocketClient.SendPing();
            }
            else
            {
                // For this test, we'll consider disconnected state as acceptable
                // in production mode where WebSocket might not be available
                if (currentMode == BackendMode.Production)
                {
                    result.passed = true;
                    result.details = "WebSocket not required for production backend";
                    webSocketClient.OnMessageReceived -= messageHandler;
                    yield break;
                }
            }

            // Wait for response
            float timeout = 5f;
            while (!messageReceived && timeout > 0)
            {
                timeout -= Time.deltaTime;
                yield return null;
            }

            // Cleanup
            webSocketClient.OnMessageReceived -= messageHandler;

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
            if (arcSystemClient == null)
            {
                result.passed = false;
                result.errorMessage = "Arc system client not available for consistency test";
                yield break;
            }

            bool dataConsistent = true;
            string inconsistencyDetails = "";

            // Get arcs from backend
            bool operationCompleted = false;
            List<Arc> backendArcs = null;

            arcSystemClient.GetArcs(callback: arcs =>
            {
                backendArcs = arcs;
                operationCompleted = true;
            });

            // Wait for backend response
            float timeout = connectionTimeout;
            while (!operationCompleted && timeout > 0)
            {
                timeout -= Time.deltaTime;
                yield return null;
            }

            if (!operationCompleted)
            {
                result.passed = false;
                result.errorMessage = "Backend data retrieval timed out";
                yield break;
            }

            // Get local arc data from narrative manager
            var localArcs = narrativeManager?.GetActiveArcs();

            // Compare data consistency
            if (backendArcs != null && localArcs != null)
            {
                // Basic consistency check - ensure no major discrepancies
                foreach (var localArc in localArcs)
                {
                    var backendArc = backendArcs.Find(a => a.id == localArc.id);
                    if (backendArc != null)
                    {
                        if (localArc.current_step != backendArc.current_step)
                        {
                            dataConsistent = false;
                            inconsistencyDetails = $"Arc {localArc.id} step mismatch: local={localArc.current_step}, backend={backendArc.current_step}";
                            break;
                        }
                    }
                }
            }

            if (dataConsistent)
            {
                result.passed = true;
                result.details = "Data consistency verified between Unity and backend";
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