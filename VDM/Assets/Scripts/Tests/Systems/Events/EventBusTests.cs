using VDM.Systems.Events;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class EventBusTests : IRuntimeTest
{
    public string TestName => "EventBusTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestEventTypeDefinitions();
        TestRegistrationSubscription();
        TestMiddleware();
        TestLoggingFilteringAnalytics();
        TestExtensibility();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestEventTypeDefinitions()
    {
        var bus = new EventBus();
        if (bus.HasEventType("TestEvent"))
        {
            _results.Add("PASS: Event type definitions");
        }
        else
        {
            _results.Add("FAIL: Event type definitions");
            _passed = false;
        }
    }

    private void TestRegistrationSubscription()
    {
        var bus = new EventBus();
        bool called = false;
        bus.Subscribe("TestEvent", (e) => { called = true; });
        bus.Emit("TestEvent", null);
        if (called)
        {
            _results.Add("PASS: Registration/subscription");
        }
        else
        {
            _results.Add("FAIL: Registration/subscription");
            _passed = false;
        }
    }

    private void TestMiddleware()
    {
        var bus = new EventBus();
        bool middlewareCalled = false;
        bus.AddMiddleware((e) => { middlewareCalled = true; return e; });
        bus.Emit("TestEvent", null);
        if (middlewareCalled)
        {
            _results.Add("PASS: Middleware");
        }
        else
        {
            _results.Add("FAIL: Middleware");
            _passed = false;
        }
    }

    private void TestLoggingFilteringAnalytics()
    {
        var bus = new EventBus();
        bus.EnableLogging(true);
        bus.Emit("TestEvent", null);
        if (bus.LastLogContains("TestEvent"))
        {
            _results.Add("PASS: Logging/filtering/analytics hooks");
        }
        else
        {
            _results.Add("FAIL: Logging/filtering/analytics hooks");
            _passed = false;
        }
    }

    private void TestExtensibility()
    {
        var bus = new EventBus();
        bool extended = bus.ExtendWithCustomEvent("CustomEvent");
        if (extended && bus.HasEventType("CustomEvent"))
        {
            _results.Add("PASS: Extensibility");
        }
        else
        {
            _results.Add("FAIL: Extensibility");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var bus = new EventBus();
        // Subscribe to unknown event
        bus.Subscribe("UnknownEvent", (e) => { });
        _results.Add("PASS: Subscribe to unknown event edge case handled");
        // Emit null event
        bus.Emit(null, null);
        _results.Add("PASS: Emit null event edge case handled");
    }
} 