using VDM.Motifs;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class MotifCacheManagerTests : IRuntimeTest
{
    public string TestName => "MotifCacheManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestAddition();
        TestRetrieval();
        TestEviction();
        TestCacheLimits();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestAddition()
    {
        var cache = new MotifCacheManager(3);
        cache.AddMotif("A", new Motif("A"));
        if (cache.Contains("A"))
        {
            _results.Add("PASS: Motif addition");
        }
        else
        {
            _results.Add("FAIL: Motif addition");
            _passed = false;
        }
    }

    private void TestRetrieval()
    {
        var cache = new MotifCacheManager(3);
        cache.AddMotif("B", new Motif("B"));
        var motif = cache.GetMotif("B");
        if (motif != null && motif.Name == "B")
        {
            _results.Add("PASS: Motif retrieval");
        }
        else
        {
            _results.Add("FAIL: Motif retrieval");
            _passed = false;
        }
    }

    private void TestEviction()
    {
        var cache = new MotifCacheManager(2);
        cache.AddMotif("C", new Motif("C"));
        cache.AddMotif("D", new Motif("D"));
        cache.AddMotif("E", new Motif("E")); // Should evict "C"
        if (!cache.Contains("C") && cache.Contains("D") && cache.Contains("E"))
        {
            _results.Add("PASS: Motif eviction");
        }
        else
        {
            _results.Add("FAIL: Motif eviction");
            _passed = false;
        }
    }

    private void TestCacheLimits()
    {
        var cache = new MotifCacheManager(1);
        cache.AddMotif("F", new Motif("F"));
        cache.AddMotif("G", new Motif("G"));
        if (cache.Contains("G") && !cache.Contains("F"))
        {
            _results.Add("PASS: Cache limit enforcement");
        }
        else
        {
            _results.Add("FAIL: Cache limit enforcement");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var cache = new MotifCacheManager(2);
        // Retrieve non-existent motif
        var motif = cache.GetMotif("Z");
        if (motif == null)
        {
            _results.Add("PASS: Retrieve non-existent motif edge case");
        }
        else
        {
            _results.Add("FAIL: Retrieve non-existent motif edge case");
            _passed = false;
        }
        // Add null motif
        cache.AddMotif("Null", null);
        _results.Add("PASS: Add null motif edge case handled");
    }
} 