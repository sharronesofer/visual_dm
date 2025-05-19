using System;
using System.Collections.Generic;
using UnityEngine;

public static class DropCalculator
{
    private static readonly System.Random rng = new System.Random((int)DateTime.UtcNow.Ticks & 0x0000FFFF);
    private static readonly Dictionary<string, float> dropRateCache = new Dictionary<string, float>();

    // Telemetry data
    public static int TotalDropChecks = 0;
    public static int TotalDrops = 0;
    public static List<float> DropRatesUsed = new List<float>();
    public static List<int> AttemptsPerDrop = new List<int>();

    public static float CalculateFinalDropRate(QuestItemDropData data, ItemRarity rarity, EnemyType enemyType)
    {
        if (data == null) return 0f;
        string cacheKey = $"{data.ItemId}_{rarity}_{enemyType}";
        if (dropRateCache.TryGetValue(cacheKey, out float cachedRate))
            return cachedRate;
        float rate = data.BaseDropRate;
        if (data.RarityModifiers != null && data.RarityModifiers.TryGetValue(rarity, out float rarityMod))
            rate *= rarityMod;
        if (data.EnemyTypeModifiers != null && data.EnemyTypeModifiers.TryGetValue(enemyType, out float enemyMod))
            rate *= enemyMod;
        rate = Mathf.Clamp(rate, data.MinDropRate, data.MaxDropRate);
        dropRateCache[cacheKey] = rate;
        return rate;
    }

    public static bool ShouldDrop(float probability)
    {
        if (probability <= 0f) return false;
        if (probability >= 1f) return true;
        TotalDropChecks++;
        DropRatesUsed.Add(probability);
        bool result = rng.NextDouble() < probability;
        if (result) TotalDrops++;
        return result;
    }

    // Batch drop calculation for multiple items
    public static List<bool> BatchShouldDrop(List<float> probabilities)
    {
        var results = new List<bool>(probabilities.Count);
        foreach (var p in probabilities)
            results.Add(ShouldDrop(p));
        return results;
    }

    // Performance profiling utility
    public static float Profile(Action action, out long elapsedTicks)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        action();
        sw.Stop();
        elapsedTicks = sw.ElapsedTicks;
        return sw.ElapsedMilliseconds;
    }

    // Telemetry reporting
    public static void ReportTelemetry()
    {
        Debug.Log($"[DropCalculator] TotalDropChecks: {TotalDropChecks}, TotalDrops: {TotalDrops}, AvgRate: {(DropRatesUsed.Count > 0 ? (DropRatesUsed.Sum() / DropRatesUsed.Count) : 0f):F4}");
    }

    public static void ResetTelemetry()
    {
        TotalDropChecks = 0;
        TotalDrops = 0;
        DropRatesUsed.Clear();
        AttemptsPerDrop.Clear();
    }
} 