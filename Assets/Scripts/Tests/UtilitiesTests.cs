using NUnit.Framework;
using VDM.World;
using VDM.Timeline.Models;
using System.Collections.Generic;

namespace VDM.Tests
{
    [TestFixture]
    public class UtilitiesTests
    {
        [Test]
        public void FeatPowerCalculator_CalculatesScoreWithModules()
        {
            var calculator = new FeatPowerCalculator();
            calculator.RegisterModule(new GenericScoringModule("EffectMagnitude", "EffectValue"));
            calculator.RegisterModule(new GenericScoringModule("ResourceCost", "ResourceCost"));
            var feat = new Feat { Id = "f1", Name = "Test Feat", Metadata = new Dictionary<string, object> { { "EffectValue", 2f }, { "ResourceCost", 1.5f } } };
            var score = calculator.CalculatePowerScore(feat);
            Assert.Greater(score, 0f);
        }

        [Test]
        public void FeatPowerCalculator_ThrowsIfNoModulesRegistered()
        {
            var calculator = new FeatPowerCalculator();
            var feat = new Feat { Id = "f1", Name = "Test Feat" };
            Assert.Throws<System.InvalidOperationException>(() => calculator.CalculatePowerScore(feat));
        }

        [Test]
        public void FeatAnalysisEngine_FlagsOverpoweredAndUnderpowered()
        {
            var engine = new FeatAnalysisEngine();
            var calculator = new FeatPowerCalculator();
            calculator.RegisterModule(new GenericScoringModule("EffectMagnitude", "EffectValue"));
            calculator.RegisterModule(new GenericScoringModule("ResourceCost", "ResourceCost"));
            engine.SetPowerCalculator(calculator);
            var overpoweredFeat = new Feat { Id = "f1", Name = "Overpowered", Metadata = new Dictionary<string, object> { { "EffectValue", 10f }, { "ResourceCost", 1f } } };
            var underpoweredFeat = new Feat { Id = "f2", Name = "Underpowered", Metadata = new Dictionary<string, object> { { "EffectValue", 0.1f }, { "ResourceCost", 5f } } };
            var overpoweredResult = engine.AnalyzeFeat(overpoweredFeat);
            var underpoweredResult = engine.AnalyzeFeat(underpoweredFeat);
            Assert.IsTrue(overpoweredResult.IsOverpowered);
            Assert.IsTrue(underpoweredResult.IsUnderpowered);
        }

        [Test]
        public void GenericScoringModule_ScoresCorrectly()
        {
            var feat = new Feat { Id = "f1", Name = "Test", Metadata = new Dictionary<string, object> { { "EffectValue", 2f }, { "ResourceCost", 1.5f }, { "Cooldown", 3f }, { "Utility", 0.8f }, { "Synergy", 1.2f } } };
            var config = new FeatPowerConfig();
            var effect = new GenericScoringModule("EffectMagnitude", "EffectValue");
            var resource = new GenericScoringModule("ResourceCost", "ResourceCost");
            var cooldown = new GenericScoringModule("Cooldown", "Cooldown");
            var utility = new GenericScoringModule("Utility", "Utility");
            var synergy = new GenericScoringModule("Synergy", "Synergy");
            effect.Configure(config);
            resource.Configure(config);
            cooldown.Configure(config);
            utility.Configure(config);
            synergy.Configure(config);
            Assert.Greater(effect.Score(feat), 0f);
            Assert.Greater(resource.Score(feat), 0f);
            Assert.Greater(cooldown.Score(feat), 0f);
            Assert.Greater(utility.Score(feat), 0f);
            Assert.Greater(synergy.Score(feat), 0f);
        }
    }
} 