using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Interface for all reward types.
    /// </summary>
    public interface IReward
    {
        void ApplyReward(); // Implement application logic per reward type
    }

    public class ExperienceReward : IReward
    {
        public float Amount { get; set; }
        public void ApplyReward() { /* Add XP to player profile */ }
    }

    public class ItemReward : IReward
    {
        public List<string> ItemIds { get; set; }
        public void ApplyReward() { /* Add items to inventory */ }
    }

    public class CurrencyReward : IReward
    {
        public int Amount { get; set; }
        public string CurrencyType { get; set; }
        public void ApplyReward() { /* Add currency to player */ }
    }

    public class ReputationReward : IReward
    {
        public Dictionary<string, float> ReputationChanges { get; set; }
        public void ApplyReward() { /* Modify faction reputation */ }
    }

    /// <summary>
    /// Configurable weighting for reward calculation factors.
    /// </summary>
    [Serializable]
    public class RewardCalculationConfig
    {
        public Dictionary<string, float> FactorWeights = new Dictionary<string, float>
        {
            {"playerLevel", 1.0f},
            {"questDifficulty", 1.5f},
            {"completionQuality", 1.2f},
            {"timeTaken", 0.8f},
            {"customModifier", 1.0f}
        };
    }

    /// <summary>
    /// Context for reward calculation (expand as needed).
    /// </summary>
    public class RewardCalculationContext
    {
        public int PlayerLevel;
        public int QuestDifficulty;
        public float CompletionQuality; // 0-1
        public float TimeTaken; // seconds
        public Dictionary<string, float> CustomModifiers = new();
    }

    /// <summary>
    /// Bundle of calculated rewards.
    /// </summary>
    public class RewardBundle
    {
        public List<IReward> Rewards = new();
    }

    /// <summary>
    /// Main reward calculation engine.
    /// </summary>
    public static class RewardCalculationEngine
    {
        private static RewardCalculationConfig _config = new RewardCalculationConfig();

        public static void SetConfig(RewardCalculationConfig config)
        {
            _config = config;
        }

        /// <summary>
        /// Calculates rewards for a quest based on context and config.
        /// </summary>
        public static RewardBundle CalculateRewards(RewardCalculationContext context)
        {
            // Defensive copy for thread safety
            var weights = new Dictionary<string, float>(_config.FactorWeights);
            float xp = CalculateExperience(context, weights);
            var items = CalculateItems(context, weights);
            int currency = CalculateCurrency(context, weights);
            var reputation = CalculateReputation(context, weights);

            var bundle = new RewardBundle();
            if (xp > 0)
                bundle.Rewards.Add(new ExperienceReward { Amount = xp });
            if (items.Count > 0)
                bundle.Rewards.Add(new ItemReward { ItemIds = items });
            if (currency > 0)
                bundle.Rewards.Add(new CurrencyReward { Amount = currency, CurrencyType = "gold" });
            if (reputation.Count > 0)
                bundle.Rewards.Add(new ReputationReward { ReputationChanges = reputation });
            return bundle;
        }

        // Example reward factor calculations
        private static float CalculateExperience(RewardCalculationContext ctx, Dictionary<string, float> weights)
        {
            float baseXP = 100f;
            float xp = baseXP * (1f + ctx.QuestDifficulty * weights["questDifficulty"]) * (1f + ctx.PlayerLevel * weights["playerLevel"]);
            xp *= Mathf.Clamp01(ctx.CompletionQuality * weights["completionQuality"]);
            if (ctx.CustomModifiers.TryGetValue("xp", out var mod))
                xp *= mod;
            return Mathf.Max(0, xp);
        }

        private static List<string> CalculateItems(RewardCalculationContext ctx, Dictionary<string, float> weights)
        {
            var items = new List<string>();
            if (ctx.QuestDifficulty >= 4) items.Add("legendary_item");
            else if (ctx.QuestDifficulty == 3) items.Add("rare_item");
            else if (ctx.QuestDifficulty == 2) items.Add("uncommon_item");
            else items.Add("common_item");
            return items;
        }

        private static int CalculateCurrency(RewardCalculationContext ctx, Dictionary<string, float> weights)
        {
            float baseGold = 50f;
            float gold = baseGold * (1f + ctx.QuestDifficulty * weights["questDifficulty"]);
            gold *= Mathf.Clamp01(ctx.CompletionQuality * weights["completionQuality"]);
            if (ctx.CustomModifiers.TryGetValue("gold", out var mod))
                gold *= mod;
            return Mathf.Max(0, Mathf.RoundToInt(gold));
        }

        private static Dictionary<string, float> CalculateReputation(RewardCalculationContext ctx, Dictionary<string, float> weights)
        {
            var rep = new Dictionary<string, float>();
            if (ctx.CustomModifiers.TryGetValue("factionA", out var mod))
                rep["FactionA"] = 10f * ctx.QuestDifficulty * mod;
            return rep;
        }

        /// <summary>
        /// Batch calculation for multiple quests (performance optimization).
        /// </summary>
        public static List<RewardBundle> CalculateRewardsBatch(List<RewardCalculationContext> contexts)
        {
            var results = new List<RewardBundle>(contexts.Count);
            foreach (var ctx in contexts)
                results.Add(CalculateRewards(ctx));
            return results;
        }

        /// <summary>
        /// Async calculation for thread safety in heavy scenarios.
        /// </summary>
        public static Task<RewardBundle> CalculateRewardsAsync(RewardCalculationContext context)
        {
            return Task.Run(() => CalculateRewards(context));
        }
    }
} 