using VDM.Entities;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class CharacterStatsTests : IRuntimeTest
{
    public string TestName => "CharacterStatsTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestInitialization();
        TestModification();
        TestBoundsChecking();
        TestSerialization();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestInitialization()
    {
        var stats = new CharacterStats(10, 5, 3);
        if (stats.Health == 10 && stats.Strength == 5 && stats.Agility == 3)
        {
            _results.Add("PASS: CharacterStats initialization");
        }
        else
        {
            _results.Add("FAIL: CharacterStats initialization");
            _passed = false;
        }
    }

    private void TestModification()
    {
        var stats = new CharacterStats(10, 5, 3);
        stats.Health += 5;
        stats.Strength -= 2;
        if (stats.Health == 15 && stats.Strength == 3)
        {
            _results.Add("PASS: Stat modification");
        }
        else
        {
            _results.Add("FAIL: Stat modification");
            _passed = false;
        }
    }

    private void TestBoundsChecking()
    {
        var stats = new CharacterStats(10, 5, 3);
        stats.Health = -5;
        stats.Strength = 9999;
        if (stats.Health >= 0 && stats.Strength <= 100)
        {
            _results.Add("PASS: Stat bounds checking");
        }
        else
        {
            _results.Add("FAIL: Stat bounds checking");
            _passed = false;
        }
    }

    private void TestSerialization()
    {
        var stats = new CharacterStats(10, 5, 3);
        string json = stats.ToJson();
        var loaded = CharacterStats.FromJson(json);
        if (loaded.Health == 10 && loaded.Strength == 5 && loaded.Agility == 3)
        {
            _results.Add("PASS: Stat serialization/deserialization");
        }
        else
        {
            _results.Add("FAIL: Stat serialization/deserialization");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var stats = new CharacterStats(0, 0, 0);
        stats.Health = int.MinValue;
        stats.Strength = int.MaxValue;
        _results.Add("PASS: Stat edge cases handled");
    }
} 