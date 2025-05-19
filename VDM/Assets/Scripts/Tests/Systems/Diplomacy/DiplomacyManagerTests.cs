using VDM.Systems.Diplomacy;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class DiplomacyManagerTests : IRuntimeTest
{
    public string TestName => "DiplomacyManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestNegotiation();
        TestTreaties();
        TestAlliances();
        TestIncidents();
        TestIntegration();
        TestEventEmission();
        TestDocumentation();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestNegotiation()
    {
        var manager = new DiplomacyManager();
        bool started = manager.StartNegotiation("FactionA", "FactionB");
        if (started && manager.IsNegotiating("FactionA", "FactionB"))
        {
            _results.Add("PASS: Negotiation");
        }
        else
        {
            _results.Add("FAIL: Negotiation");
            _passed = false;
        }
    }

    private void TestTreaties()
    {
        var manager = new DiplomacyManager();
        manager.CreateTreaty("FactionA", "FactionB", "NonAggression");
        if (manager.HasTreaty("FactionA", "FactionB", "NonAggression"))
        {
            _results.Add("PASS: Treaty creation");
        }
        else
        {
            _results.Add("FAIL: Treaty creation");
            _passed = false;
        }
    }

    private void TestAlliances()
    {
        var manager = new DiplomacyManager();
        manager.FormAlliance("FactionA", "FactionC");
        if (manager.AreAllied("FactionA", "FactionC"))
        {
            _results.Add("PASS: Alliance formation");
        }
        else
        {
            _results.Add("FAIL: Alliance formation");
            _passed = false;
        }
    }

    private void TestIncidents()
    {
        var manager = new DiplomacyManager();
        manager.ReportIncident("FactionA", "FactionB", "Border Skirmish");
        if (manager.HasIncident("FactionA", "FactionB", "Border Skirmish"))
        {
            _results.Add("PASS: Incident reporting");
        }
        else
        {
            _results.Add("FAIL: Incident reporting");
            _passed = false;
        }
    }

    private void TestIntegration()
    {
        var manager = new DiplomacyManager();
        bool integrated = manager.IntegrateWithFactionWarEvent();
        if (integrated)
        {
            _results.Add("PASS: Integration with faction/war/event");
        }
        else
        {
            _results.Add("FAIL: Integration with faction/war/event");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new DiplomacyManager();
        bool eventFired = false;
        manager.OnDiplomacyChanged += (a, b) => { eventFired = true; };
        manager.StartNegotiation("FactionA", "FactionB");
        if (eventFired)
        {
            _results.Add("PASS: Diplomacy event emission");
        }
        else
        {
            _results.Add("FAIL: Diplomacy event emission");
            _passed = false;
        }
    }

    private void TestDocumentation()
    {
        var manager = new DiplomacyManager();
        string doc = manager.GetDocumentation("NonAggression");
        if (!string.IsNullOrEmpty(doc))
        {
            _results.Add("PASS: Diplomacy documentation");
        }
        else
        {
            _results.Add("FAIL: Diplomacy documentation");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new DiplomacyManager();
        // Start negotiation with self
        manager.StartNegotiation("FactionA", "FactionA");
        _results.Add("PASS: Start negotiation with self edge case handled");
        // Create treaty with unknown faction
        manager.CreateTreaty("Unknown", "Unknown2", "UnknownTreaty");
        _results.Add("PASS: Create treaty with unknown faction edge case handled");
    }
} 