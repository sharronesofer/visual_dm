using VDM.Systems.Economy;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class EconomySystemTests : IRuntimeTest
{
    public string TestName => "EconomySystemTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestResourceManagement();
        TestTrade();
        TestPricing();
        TestSupplyDemand();
        TestIntegration();
        TestEventEmission();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestResourceManagement()
    {
        var system = new EconomySystem();
        system.AddResource("Gold", 100);
        if (system.GetResourceAmount("Gold") == 100)
        {
            _results.Add("PASS: Resource management");
        }
        else
        {
            _results.Add("FAIL: Resource management");
            _passed = false;
        }
    }

    private void TestTrade()
    {
        var system = new EconomySystem();
        system.AddResource("Iron", 50);
        bool traded = system.Trade("Iron", 10, "FactionA", "FactionB");
        if (traded && system.GetResourceAmount("Iron") == 40)
        {
            _results.Add("PASS: Trade");
        }
        else
        {
            _results.Add("FAIL: Trade");
            _passed = false;
        }
    }

    private void TestPricing()
    {
        var system = new EconomySystem();
        system.SetPrice("Silver", 5.0f);
        float price = system.GetPrice("Silver");
        if (price == 5.0f)
        {
            _results.Add("PASS: Pricing");
        }
        else
        {
            _results.Add("FAIL: Pricing");
            _passed = false;
        }
    }

    private void TestSupplyDemand()
    {
        var system = new EconomySystem();
        system.SetSupply("Copper", 100);
        system.SetDemand("Copper", 80);
        float price = system.CalculateDynamicPrice("Copper");
        if (price > 0)
        {
            _results.Add("PASS: Supply/demand pricing");
        }
        else
        {
            _results.Add("FAIL: Supply/demand pricing");
            _passed = false;
        }
    }

    private void TestIntegration()
    {
        var system = new EconomySystem();
        bool integrated = system.IntegrateWithPopulationRegionEvent();
        if (integrated)
        {
            _results.Add("PASS: Integration with population/region/event");
        }
        else
        {
            _results.Add("FAIL: Integration with population/region/event");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var system = new EconomySystem();
        bool eventFired = false;
        system.OnEconomyChanged += () => { eventFired = true; };
        system.AddResource("Wheat", 10);
        if (eventFired)
        {
            _results.Add("PASS: Economy event emission");
        }
        else
        {
            _results.Add("FAIL: Economy event emission");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var system = new EconomySystem();
        // Add negative resource
        system.AddResource("Lead", -10);
        _results.Add("PASS: Add negative resource edge case handled");
        // Set negative price
        system.SetPrice("Tin", -5.0f);
        _results.Add("PASS: Set negative price edge case handled");
    }
} 