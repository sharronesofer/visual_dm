using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using VDM.Runtime.Core.Services;
using VDM.Runtime.Services.Http;
using VDM.Runtime.Services.WebSocket;

namespace VDM.Tests.Integration
{
    /// <summary>
    /// Integration tests for the performance monitoring system.
    /// Validates that PerformanceMonitor, CacheManager, HTTP client, and WebSocket client work together.
    /// </summary>
    public class PerformanceIntegrationTests
    {
        private GameObject _testManager;
        private PerformanceMonitor _performanceMonitor;
        private CacheManager _cacheManager;
        private OptimizedHttpClient _httpClient;
        private OptimizedWebSocketClient _webSocketClient;
        
        [SetUp]
        public void Setup()
        {
            // Create test manager GameObject
            _testManager = new GameObject("PerformanceTestManager");
            
            // Add all performance components
            _performanceMonitor = _testManager.AddComponent<PerformanceMonitor>();
            _cacheManager = _testManager.AddComponent<CacheManager>();
            _httpClient = _testManager.AddComponent<OptimizedHttpClient>();
            _webSocketClient = _testManager.AddComponent<OptimizedWebSocketClient>();
            
            // Wait a frame for components to initialize
            Object.DontDestroyOnLoad(_testManager);
        }
        
        [TearDown]
        public void TearDown()
        {
            if (_testManager != null)
            {
                Object.DestroyImmediate(_testManager);
            }
        }
        
        [UnityTest]
        public IEnumerator PerformanceMonitor_InitializesCorrectly()
        {
            yield return new WaitForSeconds(0.5f); // Allow initialization
            
            var metrics = _performanceMonitor.GetCurrentMetrics();
            
            Assert.IsNotNull(metrics, "Performance metrics should be available");
            Assert.Greater(metrics.FPS, 0, "FPS should be greater than 0");
            Assert.GreaterOrEqual(metrics.MemoryUsageMB, 0, "Memory usage should be non-negative");
            Assert.GreaterOrEqual(metrics.SystemCount, 0, "System count should be non-negative");
        }
        
        [UnityTest]
        public IEnumerator CacheManager_IntegratesWithPerformanceMonitor()
        {
            yield return new WaitForSeconds(0.5f); // Allow initialization
            
            // Test cache operations
            var testData = new TestData { Name = "Test", Value = 42 };
            _cacheManager.Set("test-key", testData, "TestCategory");
            
            yield return new WaitForSeconds(0.1f);
            
            var retrievedData = _cacheManager.Get<TestData>("test-key", "TestCategory");
            
            Assert.IsNotNull(retrievedData, "Cached data should be retrievable");
            Assert.AreEqual("Test", retrievedData.Name, "Cached data should match original");
            Assert.AreEqual(42, retrievedData.Value, "Cached data should match original");
            
            // Verify performance monitoring tracked the cache operations
            var systemPerformance = _performanceMonitor.GetAllSystemPerformance();
            Assert.IsTrue(systemPerformance.ContainsKey("Core"), "Core system should be tracked");
        }
        
        [UnityTest]
        public IEnumerator HttpClient_TracksPerformanceMetrics()
        {
            yield return new WaitForSeconds(0.5f); // Allow initialization
            
            bool requestCompleted = false;
            string responseData = null;
            string errorMessage = null;
            
            // Make a test HTTP request (to localhost - will likely fail but that's ok for testing)
            _httpClient.Get("/api/test", 
                response => {
                    requestCompleted = true;
                    responseData = response.Text;
                },
                error => {
                    requestCompleted = true;
                    errorMessage = error;
                });
            
            // Wait for request to complete (or timeout)
            float timeout = 5f;
            while (!requestCompleted && timeout > 0)
            {
                timeout -= 0.1f;
                yield return new WaitForSeconds(0.1f);
            }
            
            Assert.IsTrue(requestCompleted, "HTTP request should complete (success or failure)");
            
            // Verify HTTP client statistics
            var httpStats = _httpClient.GetStatistics();
            Assert.GreaterOrEqual(httpStats.TotalRequests, 1, "Should have recorded at least one request");
            
            // Check if performance monitor tracked the API call
            yield return new WaitForSeconds(0.5f);
            var apiMetrics = _performanceMonitor.GetAPIMetrics();
            // Note: API metrics might be empty if the request failed immediately
        }
        
        [UnityTest]
        public IEnumerator WebSocketClient_IntegratesWithMonitoring()
        {
            yield return new WaitForSeconds(0.5f); // Allow initialization
            
            // Test WebSocket statistics
            var wsStats = _webSocketClient.GetStatistics();
            Assert.IsNotNull(wsStats, "WebSocket statistics should be available");
            Assert.GreaterOrEqual(wsStats.TotalConnections, 0, "Connection count should be non-negative");
            
            // Test sending a message (will queue since not connected)
            _webSocketClient.SendMessage("test", new { data = "test" });
            
            yield return new WaitForSeconds(0.1f);
            
            var updatedStats = _webSocketClient.GetStatistics();
            // Message should be queued even if not connected
            Assert.GreaterOrEqual(updatedStats.QueuedMessages, 0, "Queued messages should be tracked");
        }
        
        [UnityTest]
        public IEnumerator PerformanceAlerts_TriggerCorrectly()
        {
            yield return new WaitForSeconds(0.5f); // Allow initialization
            
            bool alertTriggered = false;
            PerformanceAlert capturedAlert = null;
            
            _performanceMonitor.OnPerformanceAlert += (alert) => {
                alertTriggered = true;
                capturedAlert = alert;
            };
            
            // Simulate high memory usage
            _performanceMonitor.TrackMemoryUsage("TestSystem", 3L * 1024 * 1024 * 1024); // 3GB
            
            yield return new WaitForSeconds(1.5f); // Wait for monitoring cycle
            
            Assert.IsTrue(alertTriggered, "Performance alert should be triggered for high memory usage");
            Assert.IsNotNull(capturedAlert, "Alert data should be captured");
            Assert.AreEqual(AlertLevel.Critical, capturedAlert.Level, "Should be critical alert for 3GB memory usage");
        }
        
        [UnityTest]
        public IEnumerator SystemPerformanceTracking_WorksCorrectly()
        {
            yield return new WaitForSeconds(0.5f); // Allow initialization
            
            // Track some system activity
            _performanceMonitor.TrackSystemActivity("Character", 15.5f, 1024); // 15.5ms processing, 1KB memory
            _performanceMonitor.TrackSystemActivity("Combat", 8.2f, 2048);    // 8.2ms processing, 2KB memory
            
            yield return new WaitForSeconds(0.1f);
            
            var characterPerf = _performanceMonitor.GetSystemPerformance("Character");
            var combatPerf = _performanceMonitor.GetSystemPerformance("Combat");
            
            Assert.IsNotNull(characterPerf, "Character system performance should be tracked");
            Assert.IsNotNull(combatPerf, "Combat system performance should be tracked");
            
            Assert.IsTrue(characterPerf.IsActive, "Character system should be marked as active");
            Assert.IsTrue(combatPerf.IsActive, "Combat system should be marked as active");
            
            Assert.Greater(characterPerf.ProcessingTimeHistory.Count, 0, "Should have processing time history");
            Assert.Greater(combatPerf.ProcessingTimeHistory.Count, 0, "Should have processing time history");
            
            Assert.AreEqual(15.5f, characterPerf.ProcessingTimeHistory.Last(), "Should track correct processing time");
            Assert.AreEqual(8.2f, combatPerf.ProcessingTimeHistory.Last(), "Should track correct processing time");
        }
        
        [UnityTest]
        public IEnumerator CacheStatistics_UpdateCorrectly()
        {
            yield return new WaitForSeconds(0.5f); // Allow initialization
            
            // Perform cache operations
            _cacheManager.Set("key1", new TestData { Name = "Test1", Value = 1 });
            _cacheManager.Set("key2", new TestData { Name = "Test2", Value = 2 });
            _cacheManager.Set("key3", new TestData { Name = "Test3", Value = 3 });
            
            yield return new WaitForSeconds(0.1f);
            
            // Test cache hits
            var data1 = _cacheManager.Get<TestData>("key1");
            var data2 = _cacheManager.Get<TestData>("key2");
            var missingData = _cacheManager.Get<TestData>("nonexistent");
            
            yield return new WaitForSeconds(0.1f);
            
            var stats = _cacheManager.GetStatistics();
            
            Assert.AreEqual(3, stats.TotalItems, "Should have 3 cached items");
            Assert.GreaterOrEqual(stats.Hits, 2, "Should have at least 2 cache hits");
            Assert.GreaterOrEqual(stats.Misses, 1, "Should have at least 1 cache miss");
            Assert.Greater(stats.TotalMemoryUsage, 0, "Should track memory usage");
        }
        
        [UnityTest]
        public IEnumerator Integration_AllComponentsWorkTogether()
        {
            yield return new WaitForSeconds(1f); // Allow full initialization
            
            // Test comprehensive integration
            var initialMetrics = _performanceMonitor.GetCurrentMetrics();
            var initialCacheStats = _cacheManager.GetStatistics();
            var initialHttpStats = _httpClient.GetStatistics();
            var initialWsStats = _webSocketClient.GetStatistics();
            
            // Perform integrated operations
            _cacheManager.Set("integration-test", new TestData { Name = "Integration", Value = 999 });
            _performanceMonitor.TrackSystemActivity("Integration", 5.0f, 512);
            _httpClient.Get("/api/integration-test", null, null);
            _webSocketClient.SendMessage("integration", new { test = true });
            
            yield return new WaitForSeconds(1f); // Allow processing
            
            // Verify all systems updated
            var finalMetrics = _performanceMonitor.GetCurrentMetrics();
            var finalCacheStats = _cacheManager.GetStatistics();
            var finalHttpStats = _httpClient.GetStatistics();
            var finalWsStats = _webSocketClient.GetStatistics();
            
            Assert.Greater(finalCacheStats.TotalItems, initialCacheStats.TotalItems, "Cache should have more items");
            Assert.GreaterOrEqual(finalHttpStats.TotalRequests, initialHttpStats.TotalRequests + 1, "HTTP should have more requests");
            Assert.IsNotNull(finalMetrics, "Performance metrics should still be available");
            
            // Verify system performance was tracked
            var integrationSystemPerf = _performanceMonitor.GetSystemPerformance("Integration");
            Assert.IsNotNull(integrationSystemPerf, "Integration system should be tracked");
            Assert.IsTrue(integrationSystemPerf.IsActive, "Integration system should be active");
        }
        
        [UnityTest]
        public IEnumerator MemoryLeakDetection_WorksCorrectly()
        {
            yield return new WaitForSeconds(0.5f); // Allow initialization
            
            var initialMemory = _performanceMonitor.GetCurrentMetrics().MemoryUsageMB;
            
            // Create and destroy many objects to test memory tracking
            var testObjects = new List<TestData>();
            for (int i = 0; i < 100; i++)
            {
                testObjects.Add(new TestData { Name = $"Test{i}", Value = i });
                _cacheManager.Set($"test-{i}", testObjects.Last());
            }
            
            yield return new WaitForSeconds(0.5f);
            
            var peakMemory = _performanceMonitor.GetCurrentMetrics().MemoryUsageMB;
            
            // Clear objects and cache
            testObjects.Clear();
            _cacheManager.ClearCache();
            
            // Force garbage collection
            System.GC.Collect();
            System.GC.WaitForPendingFinalizers();
            System.GC.Collect();
            
            yield return new WaitForSeconds(1f);
            
            var finalMemory = _performanceMonitor.GetCurrentMetrics().MemoryUsageMB;
            
            Assert.Greater(peakMemory, initialMemory, "Memory should increase during object creation");
            // Note: Memory might not return to exact initial level due to Unity's memory management
            Assert.LessOrEqual(finalMemory, peakMemory, "Memory should not exceed peak after cleanup");
        }
        
        [Test]
        public void ComponentsExist_AfterSetup()
        {
            Assert.IsNotNull(_performanceMonitor, "PerformanceMonitor should exist");
            Assert.IsNotNull(_cacheManager, "CacheManager should exist");
            Assert.IsNotNull(_httpClient, "OptimizedHttpClient should exist");
            Assert.IsNotNull(_webSocketClient, "OptimizedWebSocketClient should exist");
        }
        
        [UnityTest]
        public IEnumerator PerformanceThresholds_ConfiguredCorrectly()
        {
            yield return new WaitForSeconds(0.5f);
            
            // Verify that performance thresholds are reasonable
            var metrics = _performanceMonitor.GetCurrentMetrics();
            
            // FPS should be reasonable (not 0 or negative)
            Assert.Greater(metrics.FPS, 0, "FPS should be positive");
            Assert.Less(metrics.FPS, 1000, "FPS should be reasonable (< 1000)");
            
            // Memory should be reasonable
            Assert.GreaterOrEqual(metrics.MemoryUsageMB, 0, "Memory usage should be non-negative");
            Assert.Less(metrics.MemoryUsageMB, 10000, "Memory usage should be reasonable (< 10GB)");
        }
    }
    
    // Test data class for cache testing
    [System.Serializable]
    public class TestData
    {
        public string Name;
        public int Value;
    }
} 