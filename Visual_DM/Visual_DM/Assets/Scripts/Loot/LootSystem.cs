using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Main entry point for loot generation, including legendary drops and quest item drops with pity mechanics.
/// </summary>
public static class LootSystem
{
    /// <summary>
    /// Represents the result of a loot generation event.
    /// </summary>
    public class LootResult
    {
        public bool LegendaryDropped;
        public List<string> ItemIds = new List<string>();
        public int Gold = 0;
        // Extend with more loot types as needed
    }

    /// <summary>
    /// Generates loot for a given encounter and player, including legendary drop logic.
    /// </summary>
    /// <param name="player">Player progression data.</param>
    /// <param name="encounter">Encounter data.</param>
    /// <param name="config">Legendary drop configuration.</param>
    /// <param name="logger">Logger for analytics.</param>
    /// <returns>LootResult containing loot details.</returns>
    public static LootResult GenerateLootForEncounter(PlayerProgressionData player, EncounterData encounter, LegendaryDropConfig config, LegendaryDropLogger logger)
    {
        var result = new LootResult();
        player.TotalLootEvents++;
        bool legendary = LegendaryDropCalculator.RollForLegendaryDrop(player, encounter, config, logger);
        result.LegendaryDropped = legendary;
        if (legendary)
        {
            result.ItemIds.Add("legendary_item"); // Replace with actual item ID logic as needed
        }
        // TODO: Add logic for other loot types (rare, common, gold, etc.)
        return result;
    }

    /// <summary>
    /// Generates quest item loot using the new drop rate and pity system.
    /// </summary>
    /// <param name="enemyType">Type of enemy (for context).</param>
    /// <param name="playerTracker">Player's drop attempt tracker.</param>
    /// <param name="questId">Quest identifier.</param>
    /// <param name="rarity">Item rarity context.</param>
    /// <param name="questItemIds">List of quest item IDs to attempt to drop.</param>
    /// <returns>List of dropped quest item IDs.</returns>
    public static List<string> GenerateQuestItemLoot(
        EnemyType enemyType,
        PlayerDropAttemptTracker playerTracker,
        string questId,
        ItemRarity rarity,
        List<string> questItemIds)
    {
        return EnemyLootGenerator.GenerateQuestLoot(enemyType, playerTracker, questId, rarity, questItemIds);
    }

    /// <summary>
    /// Generates quest item loot from a container using the new drop rate and pity system.
    /// </summary>
    /// <param name="playerTracker">Player's drop attempt tracker.</param>
    /// <param name="questId">Quest identifier.</param>
    /// <param name="rarity">Item rarity context.</param>
    /// <param name="questItemIds">List of quest item IDs to attempt to drop.</param>
    /// <returns>List of dropped quest item IDs.</returns>
    public static List<string> GenerateQuestItemLootFromContainer(
        PlayerDropAttemptTracker playerTracker,
        string questId,
        ItemRarity rarity,
        List<string> questItemIds)
    {
        return ContainerLootGenerator.GenerateQuestLoot(playerTracker, questId, rarity, questItemIds);
    }
} 