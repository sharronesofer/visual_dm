using NUnit.Framework;
using VisualDM.Simulation;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace VisualDM.Tests
{
    [TestFixture]
    public class SimulationTests
    {
        [Test]
        public void CharacterStats_ApplyAndRemoveModifiers()
        {
            var stats = new CharacterStats(10, 10, 10, 10, 10, 10);
            stats.ApplyAdditiveMod("Strength", 5);
            Assert.GreaterOrEqual(stats.Strength, 10);
            stats.RemoveAdditiveMod("Strength", 5);
            Assert.AreEqual(10, stats.Strength);
        }

        [Test]
        public void TestCaseGenerator_GeneratesBuildsAndEdgeCases()
        {
            var fighter = TestCaseGenerator.GenerateBuild(CharacterArchetype.Fighter, 3);
            Assert.AreEqual("Fighter", fighter.Name);
            var minStats = TestCaseGenerator.GenerateEdgeCase("min-stats");
            Assert.AreEqual(1, minStats.Stats.Strength);
            var batch = TestCaseGenerator.GenerateBatch(new[] { CharacterArchetype.Fighter }, new[] { 1, 2 }, new[] { "combat" });
            Assert.IsNotEmpty(batch);
        }

        [Test]
        public async Task SimulationManager_SimulateBatchParallel_Works()
        {
            var jobs = new List<(SimulatedCharacter, SimulatedCharacter, int, int)>
            {
                (TestCaseGenerator.GenerateBuild(CharacterArchetype.Fighter), TestCaseGenerator.GenerateBuild(CharacterArchetype.Mage), 5, 10)
            };
            var results = await SimulationManager.SimulateBatchParallel(jobs);
            Assert.IsNotEmpty(results);
        }

        [Test]
        public void StatisticalAnalysis_ComputeMetrics()
        {
            var tc = new TestCase
            {
                Name = "Test",
                Character = TestCaseGenerator.GenerateBuild(CharacterArchetype.Fighter),
                Scenario = "combat",
                Version = 1,
                Metadata = ""
            };
            var dps = StatisticalAnalysis.ComputeDPS(tc);
            var surv = StatisticalAnalysis.ComputeSurvivability(tc);
            var util = StatisticalAnalysis.ComputeUtility(tc);
            Assert.GreaterOrEqual(dps, 0f);
            Assert.GreaterOrEqual(surv, 0f);
            Assert.GreaterOrEqual(util, 0f);
        }
    }
} 