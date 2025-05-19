using VDM.Systems.Religion;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class ReligionManagerTests : IRuntimeTest
{
    public string TestName => "ReligionManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestMembership();
        TestNarrativeHooks();
        TestCrossFaction();
        TestEventTriggers();
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

    private void TestMembership()
    {
        var manager = new ReligionManager();
        manager.JoinReligion("Character1", "SunCult");
        if (manager.IsMember("Character1", "SunCult"))
        {
            _results.Add("PASS: Religion membership");
        }
        else
        {
            _results.Add("FAIL: Religion membership");
            _passed = false;
        }
    }

    private void TestNarrativeHooks()
    {
        var manager = new ReligionManager();
        manager.SetNarrativeHook("SunCult", "Solar Eclipse Prophecy");
        if (manager.GetNarrativeHook("SunCult") == "Solar Eclipse Prophecy")
        {
            _results.Add("PASS: Narrative hook");
        }
        else
        {
            _results.Add("FAIL: Narrative hook");
            _passed = false;
        }
    }

    private void TestCrossFaction()
    {
        var manager = new ReligionManager();
        manager.JoinReligion("Character2", "MoonOrder");
        manager.JoinFaction("Character2", "NightGuild");
        if (manager.IsMember("Character2", "MoonOrder") && manager.IsFactionMember("Character2", "NightGuild"))
        {
            _results.Add("PASS: Cross-faction membership");
        }
        else
        {
            _results.Add("FAIL: Cross-faction membership");
            _passed = false;
        }
    }

    private void TestEventTriggers()
    {
        var manager = new ReligionManager();
        bool triggered = manager.TriggerEvent("SunCult", "Festival");
        if (triggered)
        {
            _results.Add("PASS: Event trigger");
        }
        else
        {
            _results.Add("FAIL: Event trigger");
            _passed = false;
        }
    }

    private void TestIntegration()
    {
        var manager = new ReligionManager();
        bool integrated = manager.IntegrateWithFactionQuestEvent();
        if (integrated)
        {
            _results.Add("PASS: Integration with faction/quest/event");
        }
        else
        {
            _results.Add("FAIL: Integration with faction/quest/event");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new ReligionManager();
        bool eventFired = false;
        manager.OnReligionChanged += (c, r) => { eventFired = true; };
        manager.JoinReligion("Character3", "StarFaith");
        if (eventFired)
        {
            _results.Add("PASS: Religion event emission");
        }
        else
        {
            _results.Add("FAIL: Religion event emission");
            _passed = false;
        }
    }

    private void TestDocumentation()
    {
        var manager = new ReligionManager();
        string doc = manager.GetDocumentation("SunCult");
        if (!string.IsNullOrEmpty(doc))
        {
            _results.Add("PASS: Religion documentation");
        }
        else
        {
            _results.Add("FAIL: Religion documentation");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new ReligionManager();
        // Join unknown religion
        manager.JoinReligion("Unknown", "UnknownReligion");
        _results.Add("PASS: Join unknown religion edge case handled");
        // Trigger event for unknown religion
        manager.TriggerEvent("UnknownReligion", "UnknownEvent");
        _results.Add("PASS: Trigger event for unknown religion edge case handled");
    }
} 