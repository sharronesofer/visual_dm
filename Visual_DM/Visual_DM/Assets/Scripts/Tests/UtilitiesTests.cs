using NUnit.Framework;
using Visual_DM.Utilities;
using Visual_DM.Timeline.Models;
using System.Collections.Generic;

namespace VisualDM.Tests
{
    [TestFixture]
    public class UtilitiesTests
    {
        [Test]
        public void FeatPowerCalculator_CalculatesScoreWithModules()
        {
            var calculator = new FeatPowerCalculator();
            calculator.RegisterModule(new EffectMagnitudeScoringModule());
            calculator.RegisterModule(new ResourceCostScoringModule());
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
            var calculator = new FeatPowerCalculator();
            calculator.RegisterModule(new EffectMagnitudeScoringModule());
            var feats = new List<Feat>
            {
                new Feat { Id = "f1", Name = "Low", Metadata = new Dictionary<string, object> { { "EffectValue", 0.1f } } },
                new Feat { Id = "f2", Name = "High", Metadata = new Dictionary<string, object> { { "EffectValue", 100f } } },
                new Feat { Id = "f3", Name = "Mid", Metadata = new Dictionary<string, object> { { "EffectValue", 1f } } }
            };
            var engine = new FeatAnalysisEngine(calculator, stddevThreshold: 1.0f);
            var report = engine.Analyze(feats);
            Assert.IsTrue(report.FlaggedFeats.Exists(f => f.ImbalanceType == "Overpowered"));
            Assert.IsTrue(report.FlaggedFeats.Exists(f => f.ImbalanceType == "Underpowered"));
        }

        [Test]
        public void ScoringModules_ProduceExpectedScores()
        {
            var feat = new Feat { Id = "f1", Name = "Test", Metadata = new Dictionary<string, object> { { "EffectValue", 2f }, { "ResourceCost", 1.5f }, { "Cooldown", 3f }, { "Utility", 0.8f }, { "Synergy", 1.2f } } };
            var config = new FeatPowerConfig();
            var effect = new EffectMagnitudeScoringModule();
            var resource = new ResourceCostScoringModule();
            var cooldown = new CooldownScoringModule();
            var utility = new UtilityScoringModule();
            var synergy = new SynergyScoringModule();
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