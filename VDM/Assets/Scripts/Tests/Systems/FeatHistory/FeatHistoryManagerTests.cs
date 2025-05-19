using VDM.Systems.FeatHistory;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class FeatHistoryManagerTests : IRuntimeTest
{
    public string TestName => "FeatHistoryManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestFeatRecording();
        TestFeatRetrieval();
        TestEventEmission();
        TestAnalyticsIntegration();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestFeatRecording()
    {
        var manager = new FeatHistoryManager();
        manager.RecordFeat("Hero", "Defeated Dragon");
        if (manager.HasFeat("Hero", "Defeated Dragon"))
        {
            _results.Add("PASS: Feat recording");
        }
        else
        {
            _results.Add("FAIL: Feat recording");
            _passed = false;
        }
    }

    private void TestFeatRetrieval()
    {
        var manager = new FeatHistoryManager();
        manager.RecordFeat("Hero", "Saved Village");
        var feats = manager.GetFeats("Hero");
        if (feats != null && feats.Contains("Saved Village"))
        {
            _results.Add("PASS: Feat retrieval");
        }
        else
        {
            _results.Add("FAIL: Feat retrieval");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new FeatHistoryManager();
        bool eventFired = false;
        manager.OnFeatRecorded += (c, f) => { eventFired = true; };
        manager.RecordFeat("Hero", "Discovered Secret");
        if (eventFired)
        {
            _results.Add("PASS: Feat event emission");
        }
        else
        {
            _results.Add("FAIL: Feat event emission");
            _passed = false;
        }
    }

    private void TestAnalyticsIntegration()
    {
        var manager = new FeatHistoryManager();
        manager.EnableAnalytics(true);
        manager.RecordFeat("Hero", "Analytics Feat");
        bool analyticsLogged = manager.AnalyticsLogged("Hero", "Analytics Feat");
        if (analyticsLogged)
        {
            _results.Add("PASS: Analytics integration");
        }
        else
        {
            _results.Add("FAIL: Analytics integration");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new FeatHistoryManager();
        // Record null feat
        manager.RecordFeat("Hero", null);
        _results.Add("PASS: Record null feat edge case handled");
        // Retrieve feats for unknown character
        var feats = manager.GetFeats("Unknown");
        if (feats != null && feats.Count == 0)
        {
            _results.Add("PASS: Retrieve feats for unknown character edge case");
        }
        else
        {
            _results.Add("FAIL: Retrieve feats for unknown character edge case");
            _passed = false;
        }
    }
} 