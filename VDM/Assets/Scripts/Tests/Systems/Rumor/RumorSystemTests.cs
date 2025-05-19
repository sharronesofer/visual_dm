using VDM.Systems.Rumor;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class RumorSystemTests : IRuntimeTest
{
    public string TestName => "RumorSystemTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestRumorCreation();
        TestMutation();
        TestBelievability();
        TestDecay();
        TestEventEmission();
        TestAnalyticsIntegration();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestRumorCreation()
    {
        var system = new RumorSystem();
        var rumor = system.CreateRumor("Origin", "Test content");
        if (rumor != null && rumor.Content == "Test content")
        {
            _results.Add("PASS: Rumor creation");
        }
        else
        {
            _results.Add("FAIL: Rumor creation");
            _passed = false;
        }
    }

    private void TestMutation()
    {
        var system = new RumorSystem();
        var rumor = system.CreateRumor("Origin", "Original");
        var mutated = system.MutateRumor(rumor);
        if (mutated != null && mutated.Content != rumor.Content)
        {
            _results.Add("PASS: Rumor mutation");
        }
        else
        {
            _results.Add("FAIL: Rumor mutation");
            _passed = false;
        }
    }

    private void TestBelievability()
    {
        var system = new RumorSystem();
        var rumor = system.CreateRumor("Origin", "Believable");
        float believability = system.CalculateBelievability(rumor);
        if (believability >= 0 && believability <= 1)
        {
            _results.Add("PASS: Believability calculation");
        }
        else
        {
            _results.Add("FAIL: Believability calculation");
            _passed = false;
        }
    }

    private void TestDecay()
    {
        var system = new RumorSystem();
        var rumor = system.CreateRumor("Origin", "Decay");
        float before = rumor.Strength;
        system.DecayRumor(rumor, 0.5f);
        if (rumor.Strength < before)
        {
            _results.Add("PASS: Rumor decay");
        }
        else
        {
            _results.Add("FAIL: Rumor decay");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var system = new RumorSystem();
        bool eventFired = false;
        system.OnRumorChanged += (r) => { eventFired = true; };
        var rumor = system.CreateRumor("Origin", "Event");
        system.MutateRumor(rumor);
        if (eventFired)
        {
            _results.Add("PASS: Rumor event emission");
        }
        else
        {
            _results.Add("FAIL: Rumor event not emitted");
            _passed = false;
        }
    }

    private void TestAnalyticsIntegration()
    {
        var system = new RumorSystem();
        system.EnableAnalytics(true);
        var rumor = system.CreateRumor("Origin", "Analytics");
        bool analyticsLogged = system.AnalyticsLogged(rumor);
        if (analyticsLogged)
        {
            _results.Add("PASS: Analytics integration");
        }
        else
        {
            _results.Add("FAIL: Analytics integration");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var system = new RumorSystem();
        // Mutate null rumor
        var mutated = system.MutateRumor(null);
        if (mutated == null)
        {
            _results.Add("PASS: Mutate null rumor edge case");
        }
        else
        {
            _results.Add("FAIL: Mutate null rumor edge case");
            _passed = false;
        }
        // Decay null rumor
        system.DecayRumor(null, 0.5f);
        _results.Add("PASS: Decay null rumor edge case handled");
    }
} 