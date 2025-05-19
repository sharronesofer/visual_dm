using VDM.Systems.Memory;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class MemoryManagerTests : IRuntimeTest
{
    public string TestName => "MemoryManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestMemoryCreation();
        TestDecay();
        TestRelevanceScoring();
        TestGraphOperations();
        TestEventEmission();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestMemoryCreation()
    {
        var manager = new MemoryManager();
        manager.AddMemory("test", 1.0f);
        if (manager.GetMemory("test") != null)
        {
            _results.Add("PASS: Memory creation");
        }
        else
        {
            _results.Add("FAIL: Memory creation");
            _passed = false;
        }
    }

    private void TestDecay()
    {
        var manager = new MemoryManager();
        manager.AddMemory("decay", 1.0f);
        manager.DecayAll(0.5f);
        var mem = manager.GetMemory("decay");
        if (mem != null && mem.Strength < 1.0f)
        {
            _results.Add("PASS: Memory decay");
        }
        else
        {
            _results.Add("FAIL: Memory decay");
            _passed = false;
        }
    }

    private void TestRelevanceScoring()
    {
        var manager = new MemoryManager();
        manager.AddMemory("rel", 0.8f);
        float score = manager.GetRelevance("rel");
        if (score > 0)
        {
            _results.Add("PASS: Relevance scoring");
        }
        else
        {
            _results.Add("FAIL: Relevance scoring");
            _passed = false;
        }
    }

    private void TestGraphOperations()
    {
        var manager = new MemoryManager();
        manager.AddMemory("A", 1.0f);
        manager.AddMemory("B", 0.5f);
        manager.LinkMemories("A", "B");
        if (manager.AreLinked("A", "B"))
        {
            _results.Add("PASS: Memory graph operations");
        }
        else
        {
            _results.Add("FAIL: Memory graph operations");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var manager = new MemoryManager();
        bool eventFired = false;
        manager.OnMemoryChanged += (id) => { eventFired = true; };
        manager.AddMemory("event", 1.0f);
        if (eventFired)
        {
            _results.Add("PASS: Memory event emission");
        }
        else
        {
            _results.Add("FAIL: Memory event not emitted");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new MemoryManager();
        // Decay non-existent memory
        manager.DecayAll(0.5f);
        _results.Add("PASS: Decay with no memories handled");
        // Link non-existent memories
        manager.LinkMemories("X", "Y");
        _results.Add("PASS: Link non-existent memories handled");
    }
} 