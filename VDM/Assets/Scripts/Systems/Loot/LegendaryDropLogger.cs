using System;
using UnityEngine;

/// <summary>
/// Handles analytics logging for legendary drop events.
/// </summary>
public class LegendaryDropLogger
{
    /// <summary>
    /// Log a legendary drop event.
    /// </summary>
    public void LogLegendaryDrop(int playerId, int level, string className, int encounterId, int eventNumber)
    {
        Debug.Log($"[LegendaryDrop] Player {playerId} (Class: {className}, Level: {level}) received a legendary in encounter {encounterId} at event #{eventNumber}.");
    }

    /// <summary>
    /// Log an eligible loot event (even if no legendary dropped).
    /// </summary>
    public void LogLootEvent(int playerId, int level, string className, int encounterId, int eventNumber, float probability, bool legendaryDropped)
    {
        Debug.Log($"[LootEvent] Player {playerId} (Class: {className}, Level: {level}), Encounter {encounterId}, Event #{eventNumber}, LegendaryChance: {probability:F4}, Dropped: {legendaryDropped}");
    }

    // Future: Add file or server logging here
} 