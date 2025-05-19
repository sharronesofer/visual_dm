#if UNITY_EDITOR
using NUnit.Framework;
using VDM.NPC;
using System;

namespace VDM.Tests.NPC
{
    public class BeliefCalculatorTests
    {
        [Test]
        public void CalculateBelievability_Returns_Expected_Stubbed_Value()
        {
            var rumor = new RumorData { Content = "Test rumor", SourceNpcId = 1 };
            float believability = BeliefCalculator.CalculateBelievability(2, rumor, 0f);
            Assert.That(believability, Is.GreaterThanOrEqualTo(0f).And.LessThanOrEqualTo(1f));
        }

        [Test]
        public void ApplyDecay_Decreases_Score_Over_Time()
        {
            float initial = 1.0f;
            float decayed = BeliefCalculator.ApplyDecay(initial, 10f);
            Assert.That(decayed, Is.LessThan(initial));
        }
    }
}
#endif 