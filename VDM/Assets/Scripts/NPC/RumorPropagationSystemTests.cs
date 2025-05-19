#if UNITY_EDITOR
using NUnit.Framework;
using VDM.NPC;
using UnityEngine;

namespace VDM.Tests.NPC
{
    public class RumorPropagationSystemTests
    {
        [Test]
        public void MergeRumors_Returns_Merged_When_Similar()
        {
            var sys = new GameObject().AddComponent<RumorPropagationSystem>();
            var a = new RumorData { Content = "Bandits on the road", SourceNpcId = 1, TruthValue = 0.7f, Category = RumorCategory.Danger };
            var b = new RumorData { Content = "Bandits on the road!", SourceNpcId = 2, TruthValue = 0.9f, Category = RumorCategory.Danger };
            var merged = sys.MergeRumors(a, b);
            Assert.IsNotNull(merged);
            Assert.AreEqual(a.Category, merged.Category);
        }

        [Test]
        public void MergeRumors_Returns_Null_When_Different()
        {
            var sys = new GameObject().AddComponent<RumorPropagationSystem>();
            var a = new RumorData { Content = "Bandits on the road", SourceNpcId = 1 };
            var b = new RumorData { Content = "The king is ill", SourceNpcId = 2 };
            var merged = sys.MergeRumors(a, b);
            Assert.IsNull(merged);
        }

        [Test]
        public void TryShareRumor_Does_Not_Share_If_Too_Far()
        {
            var sys = new GameObject().AddComponent<RumorPropagationSystem>();
            bool called = false;
            sys.OnRumorPropagated += (r, from, to) => called = true;
            var rumor = new RumorData { Content = "Test", SourceNpcId = 1 };
            sys.TryShareRumor(rumor, 1, 2, Vector2.zero, new Vector2(100, 0));
            Assert.IsFalse(called);
        }
    }
}
#endif 