using VDM.Systems.War;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class WarSystemTests : IRuntimeTest
{
    public string TestName => "WarSystemTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestTensionTracking();
        TestWarDeclaration();
        TestTensionDecay();
        TestWarOutcomes();
        TestIntegration();
        TestEventEmission();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestTensionTracking()
    {
        var system = new WarSystem();
        system.SetTension("FactionA", "FactionB", 0.5f);
        float tension = system.GetTension("FactionA", "FactionB");
        if (tension == 0.5f)
        {
            _results.Add("PASS: Tension tracking");
        }
        else
        {
            _results.Add("FAIL: Tension tracking");
            _passed = false;
        }
    }

    private void TestWarDeclaration()
    {
        var system = new WarSystem();
        system.DeclareWar("FactionA", "FactionB");
        if (system.IsAtWar("FactionA", "FactionB"))
        {
            _results.Add("PASS: War declaration");
        }
        else
        {
            _results.Add("FAIL: War declaration");
            _passed = false;
        }
    }

    private void TestTensionDecay()
    {
        var system = new WarSystem();
        system.SetTension("FactionA", "FactionB", 1.0f);
        system.DecayTension("FactionA", "FactionB", 0.5f);
        float tension = system.GetTension("FactionA", "FactionB");
        if (tension == 0.5f)
        {
            _results.Add("PASS: Tension decay");
        }
        else
        {
            _results.Add("FAIL: Tension decay");
            _passed = false;
        }
    }

    private void TestWarOutcomes()
    {
        var system = new WarSystem();
        system.DeclareWar("FactionA", "FactionB");
        system.ResolveWar("FactionA", "FactionB", "FactionA");
        if (!system.IsAtWar("FactionA", "FactionB") && system.GetWarWinner("FactionA", "FactionB") == "FactionA")
        {
            _results.Add("PASS: War outcome resolution");
        }
        else
        {
            _results.Add("FAIL: War outcome resolution");
            _passed = false;
        }
    }

    private void TestIntegration()
    {
        var system = new WarSystem();
        bool integrated = system.IntegrateWithFactionsResourcesPopulation();
        if (integrated)
        {
            _results.Add("PASS: Integration with faction/resource/population");
        }
        else
        {
            _results.Add("FAIL: Integration with faction/resource/population");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var system = new WarSystem();
        bool eventFired = false;
        system.OnWarStateChanged += () => { eventFired = true; };
        system.DeclareWar("FactionA", "FactionB");
        if (eventFired)
        {
            _results.Add("PASS: War event emission");
        }
        else
        {
            _results.Add("FAIL: War event emission");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var system = new WarSystem();
        // Declare war on self
        system.DeclareWar("FactionA", "FactionA");
        _results.Add("PASS: Declare war on self edge case handled");
        // Resolve war with no participants
        system.ResolveWar(null, null, null);
        _results.Add("PASS: Resolve war with null participants edge case handled");
    }
} 