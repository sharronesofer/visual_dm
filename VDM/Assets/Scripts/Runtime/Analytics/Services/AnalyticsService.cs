using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;
using VDM.Runtime.Analytics.Models;
using VDM.Runtime.Core.Services;
using VDM.Runtime.Services.Http;


namespace VDM.Runtime.Analytics.Services
{
    /// <summary>
    /// Analytics service for frontend-backend communication and data management
    /// </summary>
    public class AnalyticsService : MonoBehaviour, ISystemService
    {
        [Header("Configuration")]
        [SerializeField] private string baseUrl = "http://localhost:8000/api/analytics";
        [SerializeField] private float refreshInterval = 5.0f;
        [SerializeField] private int maxEventBuffer = 1000;
        [SerializeField] private bool enableRealTimeMonitoring = true;

        [Header("Performance Monitoring")]
        [SerializeField] private bool trackFrameRate = true;
        [SerializeField] private bool trackMemoryUsage = true;
        [SerializeField] private bool trackNetworkLatency = true;

        // Events for UI components to subscribe to
        public static event Action<AnalyticsEvent> OnEventRecorded;
        public static event Action<PerformanceMetrics> OnPerformanceUpdated;
        public static event Action<List<SystemHealthStatus>> OnSystemHealthUpdated;
        public static event Action<DashboardData> OnDashboardDataUpdated;

        // Private fields
        private HttpService httpService;
        private List<AnalyticsEvent> eventBuffer;
        private PerformanceMetrics currentMetrics;
        private List<SystemHealthStatus> systemStatuses;
        private DashboardData dashboardData;
        private float lastRefreshTime;
        private bool isInitialized;

        // Singleton pattern
        public static AnalyticsService Instance { get; private set; }

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                Initialize();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        /// <summary>
        /// Initialize the analytics service
        /// </summary>
        public void Initialize()
        {
            if (isInitialized) return;

            httpService = FindObjectOfType<HttpService>();
            if (httpService == null)
            {
                Debug.LogError("AnalyticsService: HttpService not found!");
                return;
            }

            eventBuffer = new List<AnalyticsEvent>();
            currentMetrics = new PerformanceMetrics();
            systemStatuses = new List<SystemHealthStatus>();
            dashboardData = new DashboardData();

            // Initialize system health monitoring
            InitializeSystemHealthMonitoring();

            isInitialized = true;
            Debug.Log("AnalyticsService initialized successfully");
        }

        private void Update()
        {
            if (!isInitialized) return;

            // Update performance metrics
            if (trackFrameRate || trackMemoryUsage)
            {
                UpdatePerformanceMetrics();
            }

            // Refresh dashboard data periodically
            if (Time.time - lastRefreshTime >= refreshInterval)
            {
                RefreshDashboardData();
                lastRefreshTime = Time.time;
            }
        }

        /// <summary>
        /// Record an analytics event
        /// </summary>
        public void RecordEvent(AnalyticsEventType eventType, Dictionary<string, object> data = null)
        {
            var analyticsEvent = new AnalyticsEvent
            {
                eventType = eventType,
                sessionId = SystemInfo.deviceUniqueIdentifier,
                worldId = GetCurrentWorldId(),
                data = data ?? new Dictionary<string, object>()
            };

            RecordEvent(analyticsEvent);
        }

        /// <summary>
        /// Record an analytics event
        /// </summary>
        public void RecordEvent(AnalyticsEvent analyticsEvent)
        {
            if (!isInitialized) return;

            // Add to buffer
            eventBuffer.Add(analyticsEvent);
            if (eventBuffer.Count > maxEventBuffer)
            {
                eventBuffer.RemoveAt(0);
            }

            // Notify subscribers
            OnEventRecorded?.Invoke(analyticsEvent);

            // Send to backend
            SendEventToBackend(analyticsEvent);
        }

        /// <summary>
        /// Get recent events for dashboard
        /// </summary>
        public List<AnalyticsEvent> GetRecentEvents(int count = 50)
        {
            var recent = new List<AnalyticsEvent>();
            int startIndex = Mathf.Max(0, eventBuffer.Count - count);
            for (int i = startIndex; i < eventBuffer.Count; i++)
            {
                recent.Add(eventBuffer[i]);
            }
            return recent;
        }

        /// <summary>
        /// Get current performance metrics
        /// </summary>
        public PerformanceMetrics GetCurrentMetrics()
        {
            return currentMetrics;
        }

        /// <summary>
        /// Get system health status
        /// </summary>
        public List<SystemHealthStatus> GetSystemHealth()
        {
            return systemStatuses;
        }

        /// <summary>
        /// Generate analytics report
        /// </summary>
        public async Task<AnalyticsReport> GenerateReport(DateTime startDate, DateTime endDate)
        {
            try
            {
                var requestData = new Dictionary<string, object>
                {
                    ["start_date"] = startDate.ToString("yyyy-MM-dd"),
                    ["end_date"] = endDate.ToString("yyyy-MM-dd")
                };

                var response = await httpService.PostAsync($"{baseUrl}/reports/generate", requestData);
                
                if (response.IsSuccess)
                {
                    return JsonUtility.FromJson<AnalyticsReport>(response.Data);
                }
                else
                {
                    Debug.LogError($"Failed to generate analytics report: {response.Error}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating analytics report: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get user behavior analytics
        /// </summary>
        public async Task<UserBehaviorData> GetUserBehaviorData(string userId = null)
        {
            try
            {
                userId = userId ?? SystemInfo.deviceUniqueIdentifier;
                var response = await httpService.GetAsync($"{baseUrl}/users/{userId}/behavior");
                
                if (response.IsSuccess)
                {
                    return JsonUtility.FromJson<UserBehaviorData>(response.Data);
                }
                else
                {
                    Debug.LogError($"Failed to get user behavior data: {response.Error}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting user behavior data: {ex.Message}");
                return null;
            }
        }

        private void UpdatePerformanceMetrics()
        {
            if (trackFrameRate)
            {
                currentMetrics.averageFrameRate = 1.0f / Time.deltaTime;
            }

            if (trackMemoryUsage)
            {
                currentMetrics.memoryUsage = (float)GC.GetTotalMemory(false) / (1024 * 1024); // MB
            }

            if (trackNetworkLatency && httpService != null)
            {
                currentMetrics.networkLatency = httpService.GetAverageLatency();
            }

            currentMetrics.lastUpdated = DateTime.UtcNow;

            // Notify subscribers
            OnPerformanceUpdated?.Invoke(currentMetrics);
        }

        private void InitializeSystemHealthMonitoring()
        {
            // Initialize health status for all systems
            var systemNames = new[]
            {
                "Analytics", "Arc", "AuthUser", "Character", "Combat", "Crafting",
                "Data", "Dialogue", "Diplomacy", "Economy", "Equipment", "Events",
                "Faction", "Inventory", "Llm", "Loot", "Magic", "Memory", "Motif",
                "Npc", "Poi", "Population", "Quest", "Region", "Religion", "Rumor",
                "Storage", "Time", "WorldGeneration", "WorldState"
            };

            foreach (var systemName in systemNames)
            {
                systemStatuses.Add(new SystemHealthStatus
                {
                    systemName = systemName,
                    healthLevel = HealthLevel.Healthy,
                    status = "Online",
                    lastCheck = DateTime.UtcNow,
                    uptime = 100.0f
                });
            }
        }

        private async void RefreshDashboardData()
        {
            if (!enableRealTimeMonitoring) return;

            dashboardData.recentEvents = GetRecentEvents(20);
            dashboardData.currentMetrics = currentMetrics;
            dashboardData.lastRefresh = DateTime.UtcNow;

            // Update system health
            await UpdateSystemHealth();

            // Notify subscribers
            OnDashboardDataUpdated?.Invoke(dashboardData);
        }

        private async Task UpdateSystemHealth()
        {
            try
            {
                var response = await httpService.GetAsync($"{baseUrl}/health");
                if (response.IsSuccess)
                {
                    var healthData = JsonUtility.FromJson<List<SystemHealthStatus>>(response.Data);
                    if (healthData != null)
                    {
                        systemStatuses = healthData;
                        OnSystemHealthUpdated?.Invoke(systemStatuses);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to update system health: {ex.Message}");
            }
        }

        private async void SendEventToBackend(AnalyticsEvent analyticsEvent)
        {
            try
            {
                var eventData = JsonUtility.ToJson(analyticsEvent);
                await httpService.PostAsync($"{baseUrl}/events", eventData);
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to send analytics event to backend: {ex.Message}");
            }
        }

        private string GetCurrentWorldId()
        {
            // This would typically come from a world manager or session service
            return "default_world_" + SystemInfo.deviceUniqueIdentifier;
        }

        public void Cleanup()
        {
            isInitialized = false;
            eventBuffer?.Clear();
        }

        private void OnDestroy()
        {
            Cleanup();
        }
    }
} 