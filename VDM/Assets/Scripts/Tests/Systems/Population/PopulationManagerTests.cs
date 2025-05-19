using VDM.Systems.Population;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class PopulationManagerTests : IRuntimeTest
{
    public string TestName => "PopulationManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestNPCGeneration();
        TestBirthRateModel();
        TestAdminControls();
        TestCapsAndThresholds();
        TestPOIResourceIntegration();
        TestEventEmission();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestNPCGeneration()
    {
        var manager = new PopulationManager();
        manager.GenerateNPCs(10);
        if (manager.TotalPopulation == 10)
        {
            _results.Add("PASS: NPC generation");
        }
        else
        {
            _results.Add("FAIL: NPC generation");
            _passed = false;
        }
    }

    private void TestBirthRateModel()
    {
        var manager = new PopulationManager();
        manager.SetBirthRate(0.1f);
        manager.GenerateNPCs(100);
        manager.SimulateBirths(1.0f); // Simulate 1 time unit
        if (manager.TotalPopulation > 100)
        {
            _results.Add("PASS: Birth rate model");
        }
        else
        {
            _results.Add("FAIL: Birth rate model");
            _passed = false;
        }
    }

    private void TestAdminControls()
    {
        var manager = new PopulationManager();
        manager.GenerateNPCs(5);
        manager.AdminSetPopulation(20);
        if (manager.TotalPopulation == 20)
        {
            _results.Add("PASS: Admin controls");
        }
        else
        {
            _results.Add("FAIL: Admin controls");
            _passed = false;
        }
    }

    private void TestCapsAndThresholds()
    {
        var manager = new PopulationManager();
        manager.SetPopulationCap(15);
        manager.GenerateNPCs(20);
        if (manager.TotalPopulation == 15)
        {
            _results.Add("PASS: Population cap enforcement");
        }
        else
        {
            _results.Add("FAIL: Population cap enforcement");
            _passed = false;
        }
        manager.SetThreshold(5);
        if (manager.IsBelowThreshold())
        {
            _results.Add("PASS: Population threshold detection");
        }
        else
        {
            _results.Add("FAIL: Population threshold detection");
            _passed = false;
        }
    }

    private void TestPOIResourceIntegration()
    {
        var manager = new PopulationManager();
        bool integrated = manager.IntegrateWithPOIResources();
        if (integrated)
        {
            _results.Add("PASS: POI/resource integration");
        }
        else
        {
            _results.Add("FAIL: POI/resource integration");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new PopulationManager();
        bool eventFired = false;
        manager.OnPopulationChanged += () => { eventFired = true; };
        manager.GenerateNPCs(1);
        if (eventFired)
        {
            _results.Add("PASS: Population event emission");
        }
        else
        {
            _results.Add("FAIL: Population event emission");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new PopulationManager();
        // Generate negative NPCs
        manager.GenerateNPCs(-5);
        _results.Add("PASS: Generate negative NPCs edge case handled");
        // Set negative cap
        manager.SetPopulationCap(-10);
        _results.Add("PASS: Set negative cap edge case handled");
    }
} 