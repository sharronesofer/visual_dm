using System;
using System.Collections.Generic;
using NUnit.Framework;
using VisualDM.Quest;

namespace VisualDM.Tests
{
    public class QuestMemorySystemTests
    {
        [SetUp]
        public void Setup()
        {
            // Clear memory before each test (simulate new instance)
            var system = QuestMemorySystem.Instance;
            system.DeserializeAll("{\"PlayerChoices\":[],\"WorldStateHistory\":[]}");
        }

        [Test]
        public void Test_Record_And_Query_PlayerChoice()
        {
            var system = QuestMemorySystem.Instance;
            system.RecordPlayerChoice("quest1", "choiceA", 1.0f, 0.9f);
            var results = system.QueryPlayerChoices("quest1");
            Assert.AreEqual(1, results.Count);
            Assert.AreEqual("choiceA", results[0].ChoiceId);
        }

        [Test]
        public void Test_Record_And_Query_WorldStateSnapshot()
        {
            var system = QuestMemorySystem.Instance;
            var diff = new Dictionary<string, object> { { "dragonDefeated", true } };
            var affected = new List<string> { "dragon" };
            system.RecordWorldStateSnapshot(diff, affected);
            var results = system.QueryWorldStateHistory();
            Assert.AreEqual(1, results.Count);
            Assert.IsTrue(results[0].StateDiff.ContainsKey("dragonDefeated"));
        }

        [Test]
        public void Test_Decay_Choices_Removes_Low_Importance()
        {
            var system = QuestMemorySystem.Instance;
            system.RecordPlayerChoice("quest1", "choiceA", 1.0f, 0.05f);
            system.DecayChoices(decayRate: 0.9f, minImportance: 0.1f);
            var results = system.QueryPlayerChoices();
            Assert.IsEmpty(results);
        }

        [Test]
        public void Test_Serialization_And_Deserialization()
        {
            var system = QuestMemorySystem.Instance;
            system.RecordPlayerChoice("quest1", "choiceA", 1.0f, 0.9f);
            var json = system.SerializeAll();
            var newSystem = QuestMemorySystem.Instance;
            newSystem.DeserializeAll(json);
            var results = newSystem.QueryPlayerChoices("quest1");
            Assert.AreEqual(1, results.Count);
            Assert.AreEqual("choiceA", results[0].ChoiceId);
        }

        [Test]
        public void Test_State_Diffing()
        {
            var oldState = new Dictionary<string, object> { { "dragonDefeated", false }, { "gold", 100 } };
            var newState = new Dictionary<string, object> { { "dragonDefeated", true }, { "gold", 150 } };
            var diff = QuestMemorySystem.DiffStates(oldState, newState);
            Assert.AreEqual(2, diff.Count);
            Assert.AreEqual(false, diff["dragonDefeated"].oldValue);
            Assert.AreEqual(true, diff["dragonDefeated"].newValue);
            Assert.AreEqual(100, diff["gold"].oldValue);
            Assert.AreEqual(150, diff["gold"].newValue);
        }
    }
} 