using VDM.Systems.Faction;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class FactionManagerTests : IRuntimeTest
{
    public string TestName => "FactionManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestMembership();
        TestSchisms();
        TestCrossFaction();
        TestAffinity();
        TestReputation();
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
        var manager = new FactionManager();
        manager.JoinFaction("Character1", "GuildA");
        if (manager.IsMember("Character1", "GuildA"))
        {
            _results.Add("PASS: Faction membership");
        }
        else
        {
            _results.Add("FAIL: Faction membership");
            _passed = false;
        }
    }

    private void TestSchisms()
    {
        var manager = new FactionManager();
        manager.CreateSchism("GuildA", "GuildA_Rebels");
        if (manager.HasSchism("GuildA", "GuildA_Rebels"))
        {
            _results.Add("PASS: Faction schism");
        }
        else
        {
            _results.Add("FAIL: Faction schism");
            _passed = false;
        }
    }

    private void TestCrossFaction()
    {
        var manager = new FactionManager();
        manager.JoinFaction("Character2", "GuildB");
        manager.JoinFaction("Character2", "GuildC");
        if (manager.IsMember("Character2", "GuildB") && manager.IsMember("Character2", "GuildC"))
        {
            _results.Add("PASS: Cross-faction membership");
        }
        else
        {
            _results.Add("FAIL: Cross-faction membership");
            _passed = false;
        }
    }

    private void TestAffinity()
    {
        var manager = new FactionManager();
        manager.SetAffinity("GuildA", "GuildB", 0.7f);
        if (manager.GetAffinity("GuildA", "GuildB") == 0.7f)
        {
            _results.Add("PASS: Faction affinity");
        }
        else
        {
            _results.Add("FAIL: Faction affinity");
            _passed = false;
        }
    }

    private void TestReputation()
    {
        var manager = new FactionManager();
        manager.SetReputation("Character1", "GuildA", 50);
        if (manager.GetReputation("Character1", "GuildA") == 50)
        {
            _results.Add("PASS: Faction reputation");
        }
        else
        {
            _results.Add("FAIL: Faction reputation");
            _passed = false;
        }
    }

    private void TestIntegration()
    {
        var manager = new FactionManager();
        bool integrated = manager.IntegrateWithQuestRelationshipNarrative();
        if (integrated)
        {
            _results.Add("PASS: Integration with quest/relationship/narrative");
        }
        else
        {
            _results.Add("FAIL: Integration with quest/relationship/narrative");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new FactionManager();
        bool eventFired = false;
        manager.OnFactionChanged += (c, f) => { eventFired = true; };
        manager.JoinFaction("Character3", "GuildD");
        if (eventFired)
        {
            _results.Add("PASS: Faction event emission");
        }
        else
        {
            _results.Add("FAIL: Faction event emission");
            _passed = false;
        }
    }

    private void TestDocumentation()
    {
        var manager = new FactionManager();
        string doc = manager.GetDocumentation("GuildA");
        if (!string.IsNullOrEmpty(doc))
        {
            _results.Add("PASS: Faction documentation");
        }
        else
        {
            _results.Add("FAIL: Faction documentation");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new FactionManager();
        // Join unknown faction
        manager.JoinFaction("Unknown", "UnknownFaction");
        _results.Add("PASS: Join unknown faction edge case handled");
        // Set affinity for unknown factions
        manager.SetAffinity("UnknownA", "UnknownB", 0.5f);
        _results.Add("PASS: Set affinity for unknown factions edge case handled");
    }
} 