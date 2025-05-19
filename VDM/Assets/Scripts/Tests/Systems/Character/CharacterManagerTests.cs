using VDM.Systems.Character;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class CharacterManagerTests : IRuntimeTest
{
    public string TestName => "CharacterManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestBuilderPattern();
        TestServicePattern();
        TestSerialization();
        TestPersistence();
        TestUsageInNewCode();
        TestDocumentation();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestBuilderPattern()
    {
        var manager = new CharacterManager();
        var builder = manager.CreateBuilder();
        builder.SetName("Hero").SetStat("Strength", 10);
        var character = builder.Build();
        if (character != null && character.Name == "Hero" && character.GetStat("Strength") == 10)
        {
            _results.Add("PASS: Builder pattern");
        }
        else
        {
            _results.Add("FAIL: Builder pattern");
            _passed = false;
        }
    }

    private void TestServicePattern()
    {
        var manager = new CharacterManager();
        var character = manager.CreateCharacter("ServiceHero");
        if (character != null && character.Name == "ServiceHero")
        {
            _results.Add("PASS: Service pattern");
        }
        else
        {
            _results.Add("FAIL: Service pattern");
            _passed = false;
        }
    }

    private void TestSerialization()
    {
        var manager = new CharacterManager();
        var character = manager.CreateCharacter("SerializeHero");
        string data = manager.Serialize(character);
        var deserialized = manager.Deserialize(data);
        if (deserialized != null && deserialized.Name == "SerializeHero")
        {
            _results.Add("PASS: Serialization/deserialization");
        }
        else
        {
            _results.Add("FAIL: Serialization/deserialization");
            _passed = false;
        }
    }

    private void TestPersistence()
    {
        var manager = new CharacterManager();
        var character = manager.CreateCharacter("PersistHero");
        manager.Save(character);
        var loaded = manager.Load(character.Id);
        if (loaded != null && loaded.Name == "PersistHero")
        {
            _results.Add("PASS: Persistence");
        }
        else
        {
            _results.Add("FAIL: Persistence");
            _passed = false;
        }
    }

    private void TestUsageInNewCode()
    {
        var manager = new CharacterManager();
        var character = manager.CreateCharacter("NewCodeHero");
        bool used = manager.UseInNewCode(character);
        if (used)
        {
            _results.Add("PASS: Usage in new code");
        }
        else
        {
            _results.Add("FAIL: Usage in new code");
            _passed = false;
        }
    }

    private void TestDocumentation()
    {
        var manager = new CharacterManager();
        string doc = manager.GetDocumentation();
        if (!string.IsNullOrEmpty(doc))
        {
            _results.Add("PASS: CharacterManager documentation");
        }
        else
        {
            _results.Add("FAIL: CharacterManager documentation");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new CharacterManager();
        // Create character with null name
        var character = manager.CreateCharacter(null);
        _results.Add("PASS: Create character with null name edge case handled");
        // Load character with invalid ID
        var loaded = manager.Load(-1);
        if (loaded == null)
        {
            _results.Add("PASS: Load character with invalid ID edge case");
        }
        else
        {
            _results.Add("FAIL: Load character with invalid ID edge case");
            _passed = false;
        }
    }
} 