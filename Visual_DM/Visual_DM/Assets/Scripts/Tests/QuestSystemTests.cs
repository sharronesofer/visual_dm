using NUnit.Framework;
using VisualDM.Quest;
using System.Collections.Generic;

namespace VisualDM.Tests
{
    [TestFixture]
    public class QuestSystemTests
    {
        [Test]
        public void QuestTemplate_GeneratesQuestWithParameters()
        {
            var template = new QuestTemplate { TemplateId = "t1", BaseTitle = "Base", BaseDescription = "Desc", BaseDifficulty = 2 };
            var quest = template.GenerateQuest(new Dictionary<string, object> { { "custom", 1 } });
            Assert.IsNotNull(quest);
            Assert.AreEqual("Base", quest.Title);
        }

        [Test]
        public void QuestDependencyManager_AddsAndDetectsDependencies()
        {
            var manager = new QuestDependencyManager();
            manager.AddDependency("q1", "q2");
            Assert.IsTrue(manager.HasDependency("q1", "q2"));
            manager.RemoveDependency("q1", "q2");
            Assert.IsFalse(manager.HasDependency("q1", "q2"));
        }

        [Test]
        public void LocationStateSystem_ManagesLocations()
        {
            var system = new LocationStateSystem();
            system.AddLocation("loc1");
            Assert.IsTrue(system.HasLocation("loc1"));
            system.RemoveLocation("loc1");
            Assert.IsFalse(system.HasLocation("loc1"));
        }

        [Test]
        public void FactionRelationshipSystem_ManagesFactions()
        {
            var system = new FactionRelationshipSystem();
            system.AddFaction("f1");
            system.SetRelationship("f1", "f2", 0.5f);
            Assert.AreEqual(0.5f, system.GetRelationship("f1", "f2"));
        }

        [Test]
        public void WorldStateManager_TracksState()
        {
            var manager = new WorldStateManager();
            manager.SetState("key", 42);
            Assert.AreEqual(42, manager.GetState<int>("key"));
            manager.RemoveState("key");
            Assert.IsFalse(manager.HasState("key"));
        }

        [Test]
        public void QuestStageManager_ManagesStages()
        {
            var manager = new QuestStageManager();
            var stage = new QuestStage { Id = "s1" };
            manager.AddStage(stage);
            Assert.IsNotNull(manager.GetStage("s1"));
            manager.RemoveStage("s1");
            Assert.IsNull(manager.GetStage("s1"));
        }

        [Test]
        public void QuestSerialization_SerializesAndDeserializes()
        {
            var quest = new Quest { Id = "q1", Title = "Test" };
            var json = QuestSerialization.Serialize(quest);
            var deserialized = QuestSerialization.Deserialize(json);
            Assert.AreEqual("q1", deserialized.Id);
        }

        [Test]
        public void QuestManager_AddsAndRemovesQuests()
        {
            var manager = new QuestManager();
            var quest = new Quest { Id = "q1" };
            manager.AddQuest(quest);
            Assert.IsNotNull(manager.GetQuest("q1"));
            manager.RemoveQuest("q1");
            Assert.IsNull(manager.GetQuest("q1"));
        }

        [Test]
        public void QuestReward_And_Requirement_Constructors()
        {
            var reward = new QuestReward { Type = "Gold", Amount = 100 };
            Assert.AreEqual("Gold", reward.Type);
            Assert.AreEqual(100, reward.Amount);
            var req = new QuestRequirement { Type = "Level", Value = 5 };
            Assert.AreEqual("Level", req.Type);
            Assert.AreEqual(5, req.Value);
        }

        [Test]
        public void ConditionEvaluator_EvaluatesConditions()
        {
            var evaluator = new ConditionEvaluator();
            Assert.DoesNotThrow(() => evaluator.Evaluate("true"));
        }

        [Test]
        public void HiddenObjective_ConstructsAndSetsProperties()
        {
            var obj = new HiddenObjective("id1", "desc1");
            Assert.AreEqual("id1", obj.Id);
            Assert.AreEqual("desc1", obj.Description);
        }
    }
} 