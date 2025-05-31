using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;

namespace VDM.Tests.Core
{
    /// <summary>
    /// Base class for all VDM tests providing common functionality and utilities
    /// </summary>
    public abstract class VDMTestBase
    {
        protected TestContext TestContext { get; private set; }
        protected MockBackendService MockBackend { get; private set; }
        protected TestPerformanceTracker PerformanceTracker { get; private set; }

        [SetUp]
        public virtual void SetUp()
        {
            TestContext = new TestContext();
            MockBackend = new MockBackendService();
            PerformanceTracker = new TestPerformanceTracker();
            
            // Initialize test environment
            UnityEngine.Debug.Log($"[TEST] Starting test: {TestContext.Test.Name}");
        }

        [TearDown]
        public virtual void TearDown()
        {
            PerformanceTracker?.Dispose();
            MockBackend?.Dispose();
            TestContext?.Dispose();
            
            UnityEngine.Debug.Log($"[TEST] Completed test: {TestContext.Test.Name}");
        }

        /// <summary>
        /// Assert that performance metrics meet expected criteria
        /// </summary>
        protected void AssertPerformance(float maxExecutionTimeMs, int maxMemoryAllocations = -1)
        {
            var metrics = PerformanceTracker.GetMetrics();
            Assert.LessOrEqual(metrics.ExecutionTimeMs, maxExecutionTimeMs, 
                $"Test execution time {metrics.ExecutionTimeMs}ms exceeds maximum {maxExecutionTimeMs}ms");
            
            if (maxMemoryAllocations > 0)
            {
                Assert.LessOrEqual(metrics.MemoryAllocations, maxMemoryAllocations,
                    $"Memory allocations {metrics.MemoryAllocations} exceed maximum {maxMemoryAllocations}");
            }
        }

        /// <summary>
        /// Create test data for a specific system
        /// </summary>
        protected T CreateTestData<T>() where T : class, new()
        {
            return TestDataFactory.Create<T>();
        }

        /// <summary>
        /// Verify that an async operation completes within timeout
        /// </summary>
        protected async Task<T> AssertAsyncCompletion<T>(Task<T> task, int timeoutMs = 5000)
        {
            var completedTask = await Task.WhenAny(task, Task.Delay(timeoutMs));
            Assert.AreEqual(task, completedTask, $"Task did not complete within {timeoutMs}ms");
            return await task;
        }
    }

    /// <summary>
    /// Base class for unit tests focusing on individual components
    /// </summary>
    public abstract class VDMUnitTestBase : VDMTestBase
    {
        [SetUp]
        public override void SetUp()
        {
            base.SetUp();
            // Unit tests should not have external dependencies
            MockBackend.EnableOfflineMode();
        }
    }

    /// <summary>
    /// Base class for integration tests that test system interactions
    /// </summary>
    public abstract class VDMIntegrationTestBase : VDMTestBase
    {
        [SetUp]
        public override void SetUp()
        {
            base.SetUp();
            // Integration tests may use mock backend services
            MockBackend.EnableMockMode();
        }
    }

    /// <summary>
    /// Base class for UI tests with UI-specific utilities
    /// </summary>
    public abstract class VDMUITestBase : VDMTestBase
    {
        protected UITestHelper UIHelper { get; private set; }
        protected Canvas TestCanvas { get; private set; }

        [SetUp]
        public override void SetUp()
        {
            base.SetUp();
            UIHelper = new UITestHelper();
            TestCanvas = UIHelper.CreateTestCanvas();
        }

        [TearDown]
        public override void TearDown()
        {
            UIHelper?.Dispose();
            if (TestCanvas != null)
            {
                UnityEngine.Object.DestroyImmediate(TestCanvas.gameObject);
            }
            base.TearDown();
        }

        /// <summary>
        /// Wait for UI element to appear
        /// </summary>
        protected IEnumerator WaitForUIElement<T>(string name, float timeout = 2f) where T : Component
        {
            var stopwatch = Stopwatch.StartNew();
            T element = null;
            
            while (stopwatch.ElapsedMilliseconds < timeout * 1000 && element == null)
            {
                element = UnityEngine.Object.FindObjectOfType<T>();
                yield return null;
            }
            
            Assert.IsNotNull(element, $"UI element {typeof(T).Name} with name '{name}' not found within {timeout}s");
        }

        /// <summary>
        /// Simulate user input on UI element
        /// </summary>
        protected void SimulateClick(GameObject target)
        {
            UIHelper.SimulateClick(target);
        }
    }

    /// <summary>
    /// Base class for end-to-end tests simulating complete user workflows
    /// </summary>
    public abstract class VDMEndToEndTestBase : VDMTestBase
    {
        protected ScenarioRunner ScenarioRunner { get; private set; }

        [SetUp]
        public override void SetUp()
        {
            base.SetUp();
            ScenarioRunner = new ScenarioRunner(MockBackend);
        }

        [TearDown]
        public override void TearDown()
        {
            ScenarioRunner?.Dispose();
            base.TearDown();
        }

        /// <summary>
        /// Run a complete user scenario
        /// </summary>
        protected async Task<ScenarioResult> RunScenario(string scenarioName, Dictionary<string, object> parameters = null)
        {
            return await ScenarioRunner.RunScenario(scenarioName, parameters);
        }
    }

    /// <summary>
    /// Performance metrics for test execution
    /// </summary>
    public class TestPerformanceMetrics
    {
        public float ExecutionTimeMs { get; set; }
        public int MemoryAllocations { get; set; }
        public long MemoryUsageBytes { get; set; }
        public int GCCollections { get; set; }
        public float FrameRate { get; set; }
    }

    /// <summary>
    /// Tracks performance metrics during test execution
    /// </summary>
    public class TestPerformanceTracker : IDisposable
    {
        private readonly Stopwatch _stopwatch;
        private readonly long _initialMemory;
        private readonly int _initialGCCollections;
        private bool _disposed;

        public TestPerformanceTracker()
        {
            _stopwatch = Stopwatch.StartNew();
            _initialMemory = GC.GetTotalMemory(false);
            _initialGCCollections = GC.CollectionCount(0);
        }

        public TestPerformanceMetrics GetMetrics()
        {
            return new TestPerformanceMetrics
            {
                ExecutionTimeMs = _stopwatch.ElapsedMilliseconds,
                MemoryAllocations = (int)(GC.GetTotalMemory(false) - _initialMemory),
                MemoryUsageBytes = GC.GetTotalMemory(false),
                GCCollections = GC.CollectionCount(0) - _initialGCCollections,
                FrameRate = Application.targetFrameRate
            };
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _stopwatch?.Stop();
                _disposed = true;
            }
        }
    }

    /// <summary>
    /// Test context providing test metadata and utilities
    /// </summary>
    public class TestContext : IDisposable
    {
        public TestContext.TestAdapter Test { get; private set; }
        public Dictionary<string, object> Properties { get; private set; }

        public TestContext()
        {
            Test = TestContext.CurrentContext.Test;
            Properties = new Dictionary<string, object>();
        }

        public void SetProperty(string key, object value)
        {
            Properties[key] = value;
        }

        public T GetProperty<T>(string key, T defaultValue = default(T))
        {
            return Properties.TryGetValue(key, out var value) ? (T)value : defaultValue;
        }

        public void Dispose()
        {
            Properties?.Clear();
        }
    }
} 