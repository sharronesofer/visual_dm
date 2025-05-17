using System.Collections.Generic;
using NUnit.Framework;
using VisualDM.Quest;

namespace VisualDM.Tests
{
    public class QuestDesignerToolsTests
    {
        [Test]
        public void Test_ValidateRewardTemplate_Valid()
        {
            var template = new RewardTemplate { Name = "Standard", BaseXP = 100, BaseGold = 50 };
            var result = QuestDesignerTools.ValidateRewardTemplate(template);
            Assert.IsTrue(result.IsValid);
            Assert.IsEmpty(result.Errors);
        }

        [Test]
        public void Test_ValidateRewardTemplate_Invalid()
        {
            var template = new RewardTemplate { Name = "", BaseXP = -10, BaseGold = -5 };
            var result = QuestDesignerTools.ValidateRewardTemplate(template);
            Assert.IsFalse(result.IsValid);
            Assert.IsNotEmpty(result.Errors);
        }

        [Test]
        public void Test_ValidateConsequenceTemplate_Valid()
        {
            var template = new ConsequenceTemplate { Name = "Anger NPC", Severity = ConsequenceSeverity.Major, Category = ConsequenceCategory.NPC, Description = "NPC is angered." };
            var result = QuestDesignerTools.ValidateConsequenceTemplate(template);
            Assert.IsTrue(result.IsValid);
            Assert.IsEmpty(result.Errors);
        }

        [Test]
        public void Test_ValidateConsequenceTemplate_Warning()
        {
            var template = new ConsequenceTemplate { Name = "NoDesc", Severity = ConsequenceSeverity.Minor, Category = ConsequenceCategory.World, Description = "" };
            var result = QuestDesignerTools.ValidateConsequenceTemplate(template);
            Assert.IsTrue(result.IsValid);
            Assert.IsNotEmpty(result.Warnings);
        }

        [Test]
        public void Test_PreviewReward()
        {
            var template = new RewardTemplate { Name = "PreviewTest", BaseXP = 10, BaseGold = 5, ItemIds = new List<string> { "item1" }, Reputation = new Dictionary<string, float> { { "FactionA", 5f } } };
            var preview = QuestDesignerTools.PreviewReward(template);
            Assert.IsTrue(preview.Contains("PreviewTest"));
            Assert.IsTrue(preview.Contains("item1"));
        }

        [Test]
        public void Test_PreviewConsequence()
        {
            var template = new ConsequenceTemplate { Name = "PreviewConseq", Severity = ConsequenceSeverity.Critical, Category = ConsequenceCategory.Faction, Description = "Major event." };
            var preview = QuestDesignerTools.PreviewConsequence(template);
            Assert.IsTrue(preview.Contains("PreviewConseq"));
            Assert.IsTrue(preview.Contains("Critical"));
        }
    }
} 