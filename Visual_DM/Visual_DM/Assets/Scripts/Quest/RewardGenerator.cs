using System;
using System.Collections.Generic;

namespace VisualDM.Quest
{
    /// <summary>
    /// Generates rewards for quests based on difficulty, type, and player level.
    /// </summary>
    public static class RewardGenerator
    {
        /// <summary>
        /// Generates a QuestReward based on parameters.
        /// </summary>
        public static QuestReward GenerateReward(int difficulty, string questType, int playerLevel)
        {
            var reward = new QuestReward();
            // Example scaling logic
            reward.Experience = ScaleExperience(difficulty, playerLevel);
            reward.ItemIds = GenerateItems(difficulty, questType);
            reward.ReputationRewards = GenerateReputation(difficulty, questType);
            reward.SpecialRewards = GenerateSpecialRewards(difficulty, questType);
            return reward;
        }

        private static float ScaleExperience(int difficulty, int playerLevel)
        {
            // Example: base XP * difficulty multiplier * player level
            float baseXP = 100f;
            float multiplier = 1f + (difficulty * 0.5f);
            return baseXP * multiplier * (1f + playerLevel * 0.1f);
        }

        private static List<string> GenerateItems(int difficulty, string questType)
        {
            var items = new List<string>();
            // Example: Add item ids based on difficulty/type
            if (difficulty >= 4) items.Add("legendary_item");
            else if (difficulty == 3) items.Add("rare_item");
            else if (difficulty == 2) items.Add("uncommon_item");
            else items.Add("common_item");
            // Add questType-specific items as needed
            return items;
        }

        private static Dictionary<string, float> GenerateReputation(int difficulty, string questType)
        {
            var rep = new Dictionary<string, float>();
            // Example: Faction reputation scaling
            if (questType == "faction")
                rep["FactionA"] = 10f * difficulty;
            return rep;
        }

        private static List<string> GenerateSpecialRewards(int difficulty, string questType)
        {
            var specials = new List<string>();
            // Example: Add special rewards for epic quests
            if (difficulty >= 4) specials.Add("unique_ability");
            return specials;
        }
    }
} 