#if UNITY_EDITOR
using NUnit.Framework;
using System;
using System.Collections.Generic;
using VDM.NPC;

namespace VDM.Tests.NPC
{
    public class RumorDataTests
    {
        [Test]
        public void RumorData_Serialization_Deserialization_Works()
        {
            var rumor = new RumorData
            {
                Content = "The king is ill.",
                SourceNpcId = 1,
                Timestamp = DateTime.UtcNow,
                TruthValue = 0.8f,
                PropagationRadius = 10f,
                Category = RumorCategory.News,
                BelievabilityScores = new Dictionary<int, float> { { 1, 0.9f }, { 2, 0.5f } }
            };
            var json = rumor.ToJson();
            var loaded = RumorData.FromJson(json);
            Assert.AreEqual(rumor.Content, loaded.Content);
            Assert.AreEqual(rumor.SourceNpcId, loaded.SourceNpcId);
            Assert.AreEqual(rumor.TruthValue, loaded.TruthValue);
            Assert.AreEqual(rumor.PropagationRadius, loaded.PropagationRadius);
            Assert.AreEqual(rumor.Category, loaded.Category);
            Assert.AreEqual(rumor.BelievabilityScores.Count, loaded.BelievabilityScores.Count);
        }

        [Test]
        public void RumorManager_Add_Find_Remove_Works()
        {
            var manager = new RumorManager();
            var rumor = new RumorData { Content = "Bandits on the road!", SourceNpcId = 2, Category = RumorCategory.Danger };
            manager.AddRumor(rumor);
            var found = manager.FindRumorsBySource(2);
            Assert.IsTrue(found.Contains(rumor));
            manager.RemoveRumor(rumor);
            Assert.IsFalse(manager.ActiveRumors.Contains(rumor));
        }
    }
}
#endif 