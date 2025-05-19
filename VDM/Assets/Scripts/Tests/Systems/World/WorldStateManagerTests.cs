using VDM.Systems.World;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class WorldStateManagerTests : IRuntimeTest
{
    public string TestName => "WorldStateManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestHierarchy();
        TestVersioning();
        TestHistory();
        TestCategorization();
        TestRegionTagging();
        TestEventEmission();
        TestQueries();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestHierarchy()
    {
        var manager = new WorldStateManager();
        manager.SetState("World/Region/City", "Active");
        if (manager.GetState("World/Region/City") == "Active")
        {
            _results.Add("PASS: Hierarchy");
        }
        else
        {
            _results.Add("FAIL: Hierarchy");
            _passed = false;
        }
    }

    private void TestVersioning()
    {
        var manager = new WorldStateManager();
        manager.SetState("World/Versioned", "V1");
        manager.UpdateVersion("World/Versioned", "V2");
        if (manager.GetVersion("World/Versioned") == "V2")
        {
            _results.Add("PASS: Versioning");
        }
        else
        {
            _results.Add("FAIL: Versioning");
            _passed = false;
        }
    }

    private void TestHistory()
    {
        var manager = new WorldStateManager();
        manager.SetState("World/History", "Old");
        manager.SetState("World/History", "New");
        var history = manager.GetHistory("World/History");
        if (history != null && history.Count >= 2)
        {
            _results.Add("PASS: History");
        }
        else
        {
            _results.Add("FAIL: History");
            _passed = false;
        }
    }

    private void TestCategorization()
    {
        var manager = new WorldStateManager();
        manager.SetCategory("World/Region", "Urban");
        if (manager.GetCategory("World/Region") == "Urban")
        {
            _results.Add("PASS: Categorization");
        }
        else
        {
            _results.Add("FAIL: Categorization");
            _passed = false;
        }
    }

    private void TestRegionTagging()
    {
        var manager = new WorldStateManager();
        manager.TagRegion("Region1", "Mountain");
        if (manager.GetRegionTag("Region1") == "Mountain")
        {
            _results.Add("PASS: Region tagging");
        }
        else
        {
            _results.Add("FAIL: Region tagging");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new WorldStateManager();
        bool eventFired = false;
        manager.OnStateChanged += (k, v) => { eventFired = true; };
        manager.SetState("World/Event", "Changed");
        if (eventFired)
        {
            _results.Add("PASS: Event emission");
        }
        else
        {
            _results.Add("FAIL: Event emission");
            _passed = false;
        }
    }

    private void TestQueries()
    {
        var manager = new WorldStateManager();
        manager.SetState("World/Query", "Q1");
        var keys = manager.QueryKeys("World");
        if (keys != null && keys.Contains("World/Query"))
        {
            _results.Add("PASS: Queries");
        }
        else
        {
            _results.Add("FAIL: Queries");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new WorldStateManager();
        // Set state with null key
        manager.SetState(null, "Null");
        _results.Add("PASS: Set state with null key edge case handled");
        // Get state for unknown key
        var state = manager.GetState("Unknown/Key");
        if (state == null)
        {
            _results.Add("PASS: Get state for unknown key edge case");
        }
        else
        {
            _results.Add("FAIL: Get state for unknown key edge case");
            _passed = false;
        }
    }
} 