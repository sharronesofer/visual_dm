using System.Collections.Generic;
using System.Threading.Tasks;
using NUnit.Framework;
using VisualDM.Quest;

namespace VisualDM.Tests
{
    public class RewardCalculationEngineTests
    {
        [Test]
        public void Test_Experience_Scaling_By_Level_And_Difficulty()
        {
            var context = new RewardCalculationContext
            {
                PlayerLevel = 5,
                QuestDifficulty = 3,
                CompletionQuality = 1.0f,
                TimeTaken = 120f
            };
            var bundle = RewardCalculationEngine.CalculateRewards(context);
            var xpReward = bundle.Rewards.Find(r => r is ExperienceReward) as ExperienceReward;
            Assert.IsNotNull(xpReward);
            Assert.Greater(xpReward.Amount, 0);
        }

        [Test]
        public void Test_Item_Reward_Tiers()
        {
            var context = new RewardCalculationContext { PlayerLevel = 1, QuestDifficulty = 4, CompletionQuality = 1.0f };
            var bundle = RewardCalculationEngine.CalculateRewards(context);
            var itemReward = bundle.Rewards.Find(r => r is ItemReward) as ItemReward;
            Assert.IsNotNull(itemReward);
            Assert.Contains("legendary_item", itemReward.ItemIds);
        }

        [Test]
        public void Test_Currency_Reward_Modifier()
        {
            var context = new RewardCalculationContext
            {
                PlayerLevel = 2,
                QuestDifficulty = 2,
                CompletionQuality = 1.0f,
                CustomModifiers = new Dictionary<string, float> { { "gold", 2.0f } }
            };
            var bundle = RewardCalculationEngine.CalculateRewards(context);
            var currencyReward = bundle.Rewards.Find(r => r is CurrencyReward) as CurrencyReward;
            Assert.IsNotNull(currencyReward);
            Assert.Greater(currencyReward.Amount, 50);
        }

        [Test]
        public void Test_Reputation_Reward_CustomModifier()
        {
            var context = new RewardCalculationContext
            {
                PlayerLevel = 1,
                QuestDifficulty = 3,
                CompletionQuality = 1.0f,
                CustomModifiers = new Dictionary<string, float> { { "factionA", 3.0f } }
            };
            var bundle = RewardCalculationEngine.CalculateRewards(context);
            var repReward = bundle.Rewards.Find(r => r is ReputationReward) as ReputationReward;
            Assert.IsNotNull(repReward);
            Assert.IsTrue(repReward.ReputationChanges.ContainsKey("FactionA"));
            Assert.AreEqual(90f, repReward.ReputationChanges["FactionA"]);
        }

        [Test]
        public void Test_Zero_CompletionQuality_Yields_Minimal_Reward()
        {
            var context = new RewardCalculationContext
            {
                PlayerLevel = 1,
                QuestDifficulty = 1,
                CompletionQuality = 0.0f
            };
            var bundle = RewardCalculationEngine.CalculateRewards(context);
            var xpReward = bundle.Rewards.Find(r => r is ExperienceReward) as ExperienceReward;
            Assert.IsNotNull(xpReward);
            Assert.AreEqual(0, xpReward.Amount);
        }

        [Test]
        public async Task Test_Concurrent_Reward_Calculation()
        {
            var contexts = new List<RewardCalculationContext>();
            for (int i = 0; i < 10; i++)
            {
                contexts.Add(new RewardCalculationContext
                {
                    PlayerLevel = i,
                    QuestDifficulty = i % 5,
                    CompletionQuality = 1.0f
                });
            }
            var tasks = new List<Task<RewardBundle>>();
            foreach (var ctx in contexts)
                tasks.Add(RewardCalculationEngine.CalculateRewardsAsync(ctx));
            var results = await Task.WhenAll(tasks);
            Assert.AreEqual(10, results.Length);
            foreach (var bundle in results)
                Assert.IsTrue(bundle.Rewards.Count > 0);
        }
    }
} 