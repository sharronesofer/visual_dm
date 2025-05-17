using System;
using UnityEngine;

/// <summary>
/// Calculates whether a legendary item should drop, based on player progression, encounter, and configuration.
/// </summary>
public static class LegendaryDropCalculator
{
    /// <summary>
    /// Roll for a legendary drop using the progression formula and log the event.
    /// </summary>
    /// <param name="player">Player progression data.</param>
    /// <param name="encounter">Encounter data.</param>
    /// <param name="config">Legendary drop configuration.</param>
    /// <param name="logger">Logger for analytics.</param>
    /// <returns>True if legendary drops, false otherwise.</returns>
    public static bool RollForLegendaryDrop(PlayerProgressionData player, EncounterData encounter, LegendaryDropConfig config, LegendaryDropLogger logger)
    {
        // Calculate base probability
        float pLevel = (player.Level / 20f) * config.PLevel;
        float arcBonus = 1f + player.ArcCompletion * config.PArc;
        float globalBonus = 1f + player.GlobalEventParticipation * config.PGlobal;
        float classModifier = player.ClassXPModifier;
        float difficultyModifier = encounter.DifficultyModifier;
        float pity = player.LegendaryPity;

        float probability = (config.PBase + pLevel) * classModifier * arcBonus * globalBonus * difficultyModifier + pity;
        probability = Mathf.Min(probability, config.MaxProbability);

        // Hard cap: enforce minimum events between legendaries
        if (player.EventsSinceLastLegendary < config.MinEventsBetweenLegendaries)
        {
            logger.LogLootEvent(player.PlayerId, player.Level, player.ClassName, encounter.EncounterId, player.TotalLootEvents, probability, false);
            player.LegendaryPity += config.PityIncrement;
            player.EventsSinceLastLegendary++;
            return false;
        }

        // Pity: guarantee after max events
        if (player.EventsSinceLastLegendary >= config.MaxEventsWithoutLegendary)
        {
            logger.LogLegendaryDrop(player.PlayerId, player.Level, player.ClassName, encounter.EncounterId, player.TotalLootEvents);
            player.LegendaryPity = 0f;
            player.EventsSinceLastLegendary = 0;
            player.TotalLegendaries++; 
            return true;
        }

        // Roll
        bool legendaryDropped = UnityEngine.Random.value < probability;
        logger.LogLootEvent(player.PlayerId, player.Level, player.ClassName, encounter.EncounterId, player.TotalLootEvents, probability, legendaryDropped);
        if (legendaryDropped)
        {
            logger.LogLegendaryDrop(player.PlayerId, player.Level, player.ClassName, encounter.EncounterId, player.TotalLootEvents);
            player.LegendaryPity = 0f;
            player.EventsSinceLastLegendary = 0;
            player.TotalLegendaries++;
        }
        else
        {
            player.LegendaryPity += config.PityIncrement;
            player.EventsSinceLastLegendary++;
        }
        return legendaryDropped;
    }
}

// --- Supporting Data Structures ---

/// <summary>
/// Player progression data for legendary drop calculation.
/// </summary>
public class PlayerProgressionData
{
    public int PlayerId;
    public int Level;
    public string ClassName;
    public float ClassXPModifier = 1.0f; // 1.0 = baseline
    public float ArcCompletion = 0f; // 0-1
    public float GlobalEventParticipation = 0f; // 0-1
    public int EventsSinceLastLegendary = 9999;
    public float LegendaryPity = 0f;
    public int TotalLootEvents = 0;
    public int TotalLegendaries = 0;
}

/// <summary>
/// Encounter data for legendary drop calculation.
/// </summary>
public class EncounterData
{
    public int EncounterId;
    public float DifficultyModifier = 1.0f; // 1.0 = normal, >1.0 = harder
} 