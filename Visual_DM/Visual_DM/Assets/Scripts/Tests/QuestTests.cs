using NUnit.Framework;
using VisualDM.Quest;
using System.Collections.Generic;

namespace VisualDM.Tests
{
    [TestFixture]
    public class QuestTests
    {
        [Test]
        public void Quest_CanSetAndGetProperties()
        {
            var quest = new Quest();
            quest.Id = "q1";
            quest.Title = "Test Quest";
            quest.Description = "Desc";
            Assert.AreEqual("q1", quest.Id);
            Assert.AreEqual("Test Quest", quest.Title);
            Assert.AreEqual("Desc", quest.Description);
        }

        [Test]
        public void QuestStage_CanSetAndGetObjectives()
        {
            var stage = new QuestStage();
            stage.Objectives = new List<string> { "obj1", "obj2" };
            Assert.Contains("obj1", stage.Objectives);
            Assert.Contains("obj2", stage.Objectives);
        }

        [Test]
        public void RewardGenerator_GeneratesExpectedRewards()
        {
            var reward = RewardGenerator.GenerateReward(3, "combat", 5);
            Assert.IsNotNull(reward);
            Assert.IsTrue(reward.ItemIds.Count > 0);
            Assert.IsTrue(reward.Experience > 0);
        }
    }
} 