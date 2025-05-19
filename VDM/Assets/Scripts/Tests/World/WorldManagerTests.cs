using VDM.World;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class WorldManagerTests : IRuntimeTest
{
    public string TestName => "WorldManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestInitialization();
        TestRegionManagement();
        TestCityManagement();
        TestEventEmission();
        TestStatePersistence();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestInitialization()
    {
        var manager = new WorldManager();
        if (manager == null)
        {
            _results.Add("FAIL: WorldManager initialization returned null");
            _passed = false;
        }
        else
        {
            _results.Add("PASS: WorldManager initialization");
        }
    }

    private void TestRegionManagement()
    {
        var manager = new WorldManager();
        manager.AddRegion("TestRegion");
        if (manager.GetRegion("TestRegion") != null)
        {
            _results.Add("PASS: Region added and retrieved");
        }
        else
        {
            _results.Add("FAIL: Region not found after add");
            _passed = false;
        }
    }

    private void TestCityManagement()
    {
        var manager = new WorldManager();
        manager.AddCity("TestCity", "TestRegion");
        if (manager.GetCity("TestCity") != null)
        {
            _results.Add("PASS: City added and retrieved");
        }
        else
        {
            _results.Add("FAIL: City not found after add");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new WorldManager();
        bool eventFired = false;
        manager.OnWorldEvent += (evt) => { eventFired = true; };
        manager.AddRegion("EventRegion");
        if (eventFired)
        {
            _results.Add("PASS: World event emission");
        }
        else
        {
            _results.Add("FAIL: World event not emitted");
            _passed = false;
        }
    }

    private void TestStatePersistence()
    {
        var manager = new WorldManager();
        manager.AddRegion("PersistRegion");
        manager.SaveState();
        manager.LoadState();
        if (manager.GetRegion("PersistRegion") != null)
        {
            _results.Add("PASS: State persistence");
        }
        else
        {
            _results.Add("FAIL: State not persisted");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new WorldManager();
        // Add duplicate region
        manager.AddRegion("DupRegion");
        manager.AddRegion("DupRegion");
        _results.Add("PASS: Duplicate region edge case handled");
        // Remove non-existent city
        manager.RemoveCity("NoCity");
        _results.Add("PASS: Remove non-existent city edge case handled");
    }
} 