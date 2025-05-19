using VDM.POI;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class POIStateManagerTests : IRuntimeTest
{
    public string TestName => "POIStateManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestStateTransitions();
        TestPopulationThresholds();
        TestExemptionOverrides();
        TestEventEmission();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestStateTransitions()
    {
        var manager = new POIStateManager();
        manager.SetPopulation("TestPOI", 100);
        manager.UpdateState("TestPOI");
        if (manager.GetState("TestPOI") == POIStateType.Normal)
        {
            _results.Add("PASS: State transition to Normal");
        }
        else
        {
            _results.Add("FAIL: State transition to Normal");
            _passed = false;
        }
    }

    private void TestPopulationThresholds()
    {
        var manager = new POIStateManager();
        manager.SetPopulation("TestPOI", 10); // Below threshold
        manager.UpdateState("TestPOI");
        if (manager.GetState("TestPOI") == POIStateType.Ruins)
        {
            _results.Add("PASS: State transition to Ruins at low population");
        }
        else
        {
            _results.Add("FAIL: State transition to Ruins at low population");
            _passed = false;
        }
    }

    private void TestExemptionOverrides()
    {
        var manager = new POIStateManager();
        manager.SetPopulation("ExemptPOI", 10);
        manager.AddExemption("ExemptPOI");
        manager.UpdateState("ExemptPOI");
        if (manager.GetState("ExemptPOI") == POIStateType.Normal)
        {
            _results.Add("PASS: Exemption prevents state transition");
        }
        else
        {
            _results.Add("FAIL: Exemption did not prevent state transition");
            _passed = false;
        }
        manager.OverrideState("ExemptPOI", POIStateType.Dungeon);
        if (manager.GetState("ExemptPOI") == POIStateType.Dungeon)
        {
            _results.Add("PASS: Manual override sets state");
        }
        else
        {
            _results.Add("FAIL: Manual override did not set state");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new POIStateManager();
        bool eventFired = false;
        manager.OnStateChanged += (poi, state) => { eventFired = true; };
        manager.SetPopulation("EventPOI", 10);
        manager.UpdateState("EventPOI");
        if (eventFired)
        {
            _results.Add("PASS: State change event emission");
        }
        else
        {
            _results.Add("FAIL: State change event not emitted");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new POIStateManager();
        // Update state for non-existent POI
        try
        {
            manager.UpdateState("NoPOI");
            _results.Add("PASS: Update state for non-existent POI handled");
        }
        catch
        {
            _results.Add("FAIL: Exception thrown for non-existent POI");
            _passed = false;
        }
        // Remove exemption for non-existent POI
        manager.RemoveExemption("NoPOI");
        _results.Add("PASS: Remove exemption for non-existent POI handled");
    }
} 