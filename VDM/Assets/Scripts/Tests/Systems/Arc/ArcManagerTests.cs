using VDM.Systems.Arc;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class ArcManagerTests : IRuntimeTest
{
    public string TestName => "ArcManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestArcTypes();
        TestAssignment();
        TestProgression();
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

    private void TestArcTypes()
    {
        var manager = new ArcManager();
        manager.DefineArcType("Hero's Journey");
        if (manager.HasArcType("Hero's Journey"))
        {
            _results.Add("PASS: Arc/quest type definition");
        }
        else
        {
            _results.Add("FAIL: Arc/quest type definition");
            _passed = false;
        }
    }

    private void TestAssignment()
    {
        var manager = new ArcManager();
        manager.DefineArcType("Redemption");
        manager.AssignArc("Character1", "Redemption");
        if (manager.GetArc("Character1") == "Redemption")
        {
            _results.Add("PASS: Arc assignment");
        }
        else
        {
            _results.Add("FAIL: Arc assignment");
            _passed = false;
        }
    }

    private void TestProgression()
    {
        var manager = new ArcManager();
        manager.DefineArcType("Revenge");
        manager.AssignArc("Character2", "Revenge");
        manager.ProgressArc("Character2");
        if (manager.GetArcProgress("Character2") > 0)
        {
            _results.Add("PASS: Arc progression");
        }
        else
        {
            _results.Add("FAIL: Arc progression");
            _passed = false;
        }
    }

    private void TestIntegration()
    {
        var manager = new ArcManager();
        bool integrated = manager.IntegrateWithQuestMotifRegion();
        if (integrated)
        {
            _results.Add("PASS: Integration with quest/motif/region");
        }
        else
        {
            _results.Add("FAIL: Integration with quest/motif/region");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new ArcManager();
        bool eventFired = false;
        manager.OnArcChanged += (c, a) => { eventFired = true; };
        manager.DefineArcType("TestArc");
        manager.AssignArc("Character3", "TestArc");
        if (eventFired)
        {
            _results.Add("PASS: Arc event emission");
        }
        else
        {
            _results.Add("FAIL: Arc event emission");
            _passed = false;
        }
    }

    private void TestDocumentation()
    {
        var manager = new ArcManager();
        string doc = manager.GetDocumentation("Hero's Journey");
        if (!string.IsNullOrEmpty(doc))
        {
            _results.Add("PASS: Arc documentation");
        }
        else
        {
            _results.Add("FAIL: Arc documentation");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new ArcManager();
        // Assign arc to unknown character
        manager.AssignArc("Unknown", "UnknownArc");
        _results.Add("PASS: Assign arc to unknown character edge case handled");
        // Progress arc for character with no arc
        manager.ProgressArc("NoArcCharacter");
        _results.Add("PASS: Progress arc for character with no arc edge case handled");
    }
} 