using VDM.Systems.Analytics;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class AnalyticsServiceTests : IRuntimeTest
{
    public string TestName => "AnalyticsServiceTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestEventLogging();
        TestDatasetGeneration();
        TestMiddlewareIntegration();
        TestCustomEventTypes();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestEventLogging()
    {
        var analytics = new AnalyticsService();
        analytics.LogEvent("TestEvent", new { value = 42 });
        if (analytics.GetLastEventName() == "TestEvent")
        {
            _results.Add("PASS: Event logging");
        }
        else
        {
            _results.Add("FAIL: Event logging");
            _passed = false;
        }
    }

    private void TestDatasetGeneration()
    {
        var analytics = new AnalyticsService();
        analytics.LogEvent("EventA", new { value = 1 });
        analytics.LogEvent("EventB", new { value = 2 });
        var dataset = analytics.GenerateDataset();
        if (dataset != null && dataset.Count >= 2)
        {
            _results.Add("PASS: Dataset generation");
        }
        else
        {
            _results.Add("FAIL: Dataset generation");
            _passed = false;
        }
    }

    private void TestMiddlewareIntegration()
    {
        var analytics = new AnalyticsService();
        bool middlewareCalled = false;
        analytics.AddMiddleware((evt) => { middlewareCalled = true; return evt; });
        analytics.LogEvent("MiddlewareEvent", new { });
        if (middlewareCalled)
        {
            _results.Add("PASS: Middleware integration");
        }
        else
        {
            _results.Add("FAIL: Middleware integration");
            _passed = false;
        }
    }

    private void TestCustomEventTypes()
    {
        var analytics = new AnalyticsService();
        analytics.LogEvent("CustomType", new { custom = "data" });
        var last = analytics.GetLastEvent();
        if (last != null && last.Name == "CustomType")
        {
            _results.Add("PASS: Custom event type logging");
        }
        else
        {
            _results.Add("FAIL: Custom event type logging");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var analytics = new AnalyticsService();
        // Log null event
        analytics.LogEvent(null, null);
        _results.Add("PASS: Log null event edge case handled");
        // Generate dataset with no events
        var emptyDataset = analytics.GenerateDataset();
        if (emptyDataset != null)
        {
            _results.Add("PASS: Generate dataset with no events edge case handled");
        }
        else
        {
            _results.Add("FAIL: Generate dataset with no events edge case");
            _passed = false;
        }
    }
} 