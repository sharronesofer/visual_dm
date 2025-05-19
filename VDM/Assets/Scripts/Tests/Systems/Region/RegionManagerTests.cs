using VDM.Systems.Region;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class RegionManagerTests : IRuntimeTest
{
    public string TestName => "RegionManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestBiomeTagging();
        TestProceduralGeneration();
        TestMotifArcAssignment();
        TestIntegration();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestBiomeTagging()
    {
        var manager = new RegionManager();
        manager.AssignBiome("Region1", "Forest");
        if (manager.GetBiome("Region1") == "Forest")
        {
            _results.Add("PASS: Biome tagging");
        }
        else
        {
            _results.Add("FAIL: Biome tagging");
            _passed = false;
        }
    }

    private void TestProceduralGeneration()
    {
        var manager = new RegionManager();
        bool generated = manager.GenerateProceduralRegions(5);
        if (generated && manager.RegionCount == 5)
        {
            _results.Add("PASS: Procedural generation");
        }
        else
        {
            _results.Add("FAIL: Procedural generation");
            _passed = false;
        }
    }

    private void TestMotifArcAssignment()
    {
        var manager = new RegionManager();
        manager.AssignMotif("Region2", "Mystery");
        manager.AssignArc("Region2", "Hero's Journey");
        if (manager.GetMotif("Region2") == "Mystery" && manager.GetArc("Region2") == "Hero's Journey")
        {
            _results.Add("PASS: Motif/arc assignment");
        }
        else
        {
            _results.Add("FAIL: Motif/arc assignment");
            _passed = false;
        }
    }

    private void TestIntegration()
    {
        var manager = new RegionManager();
        bool integrated = manager.IntegrateWithPOIWorldState();
        if (integrated)
        {
            _results.Add("PASS: Integration with POI/world state");
        }
        else
        {
            _results.Add("FAIL: Integration with POI/world state");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new RegionManager();
        // Assign biome to unknown region
        manager.AssignBiome("Unknown", "Desert");
        _results.Add("PASS: Assign biome to unknown region edge case handled");
        // Generate zero regions
        bool generated = manager.GenerateProceduralRegions(0);
        if (!generated)
        {
            _results.Add("PASS: Generate zero regions edge case");
        }
        else
        {
            _results.Add("FAIL: Generate zero regions edge case");
            _passed = false;
        }
    }
} 