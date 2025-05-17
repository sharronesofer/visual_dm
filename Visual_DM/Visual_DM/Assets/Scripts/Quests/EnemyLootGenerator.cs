using System.Collections.Generic;
using UnityEngine;

public class EnemyLootGenerator
{
    public static List<string> GenerateQuestLoot(
        EnemyType enemyType,
        PlayerDropAttemptTracker playerTracker,
        string questId,
        ItemRarity rarity,
        List<string> questItemIds)
    {
        var droppedItems = new List<string>();
        foreach (var itemId in questItemIds)
        {
            var dropData = QuestDropManager.Instance.GetDropData(itemId);
            if (dropData == null) continue;
            float baseRate = DropCalculator.CalculateFinalDropRate(dropData, rarity, enemyType);
            int attempts = playerTracker.GetAttemptCount(itemId);
            float pityRate = PityCalculator.CalculateModifiedDropRate(
                baseRate,
                attempts,
                dropData.MinDropRate,
                dropData.MaxDropRate,
                3, // Example: pity activates after 3 fails
                0.05f // Example: 5% increase per fail after threshold
            );
            if (DropCalculator.ShouldDrop(pityRate))
            {
                droppedItems.Add(itemId);
                playerTracker.ResetCounter(itemId);
            }
            else
            {
                playerTracker.IncrementCounter(itemId);
            }
        }
        return droppedItems;
    }
} 