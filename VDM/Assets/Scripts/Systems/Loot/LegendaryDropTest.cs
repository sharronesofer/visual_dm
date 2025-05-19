using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Test harness for the LegendaryDropCalculator. Includes unit tests and simulation.
/// </summary>
public class LegendaryDropTest
{
    private LegendaryDropConfig config = new LegendaryDropConfig();
    private LegendaryDropLogger logger = new LegendaryDropLogger();

    /// <summary>
    /// Run all unit tests and simulation.
    /// </summary>
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    public static void RunAllTests()
    {
        var test = new LegendaryDropTest();
        test.RunUnitTests();
        test.RunSimulation(1000);
    }

    /// <summary>
    /// Unit tests for all formula branches and edge cases.
    /// </summary>
    public void RunUnitTests()
    {
        Debug.Log("[LegendaryDropTest] Running unit tests...");
        // Test base probability
        var player = new PlayerProgressionData { Level = 1, ClassXPModifier = 1.0f, ArcCompletion = 0f, GlobalEventParticipation = 0f };
        var encounter = new EncounterData { DifficultyModifier = 1.0f };
        bool drop = LegendaryDropCalculator.RollForLegendaryDrop(player, encounter, config, logger);
        Debug.Log($"Base probability test: Drop={drop}");

        // Test level scaling
        player.Level = 20;
        drop = LegendaryDropCalculator.RollForLegendaryDrop(player, encounter, config, logger);
        Debug.Log($"Level scaling test: Drop={drop}");

        // Test Arc Completion bonus
        player.ArcCompletion = 1.0f;
        drop = LegendaryDropCalculator.RollForLegendaryDrop(player, encounter, config, logger);
        Debug.Log($"Arc Completion bonus test: Drop={drop}");

        // Test Global Event bonus
        player.GlobalEventParticipation = 1.0f;
        drop = LegendaryDropCalculator.RollForLegendaryDrop(player, encounter, config, logger);
        Debug.Log($"Global Event bonus test: Drop={drop}");

        // Test Difficulty modifier
        encounter.DifficultyModifier = 2.0f;
        drop = LegendaryDropCalculator.RollForLegendaryDrop(player, encounter, config, logger);
        Debug.Log($"Difficulty modifier test: Drop={drop}");

        // Test Class XP rate modifier
        player.ClassXPModifier = 0.5f;
        drop = LegendaryDropCalculator.RollForLegendaryDrop(player, encounter, config, logger);
        Debug.Log($"Class XP modifier test: Drop={drop}");

        // Test pity/bad luck protection (simulate many events)
        int drops = 0;
        for (int i = 0; i < 100; i++)
        {
            if (LegendaryDropCalculator.RollForLegendaryDrop(player, encounter, config, logger))
                drops++;
        }
        Debug.Log($"Pity/bad luck protection test: Drops in 100 events={drops}");
    }

    /// <summary>
    /// Simulate 1000+ player progressions from level 1 to 20 and output summary statistics.
    /// </summary>
    public void RunSimulation(int numPlayers)
    {
        Debug.Log($"[LegendaryDropTest] Running simulation for {numPlayers} players...");
        var rng = new System.Random();
        List<int> legendaryCounts = new List<int>();
        for (int i = 0; i < numPlayers; i++)
        {
            var player = new PlayerProgressionData
            {
                Level = 1,
                ClassXPModifier = 1.0f,
                ArcCompletion = 0f,
                GlobalEventParticipation = 0f
            };
            var encounter = new EncounterData { DifficultyModifier = 1.0f };
            int legendaries = 0;
            int events = 0;
            while (player.Level <= 20)
            {
                events++;
                if (LegendaryDropCalculator.RollForLegendaryDrop(player, encounter, config, logger))
                    legendaries++;
                // Simulate progression
                player.Level += rng.NextDouble() < 0.2 ? 1 : 0; // 20% chance to level up per event
                player.ArcCompletion = rng.NextDouble() < 0.05 ? 1.0f : player.ArcCompletion; // 5% chance to complete arc
                player.GlobalEventParticipation = rng.NextDouble() < 0.1 ? 1.0f : 0f; // 10% chance global event
            }
            legendaryCounts.Add(legendaries);
        }
        // Output statistics
        legendaryCounts.Sort();
        float median = legendaryCounts[legendaryCounts.Count / 2];
        float mean = 0f;
        foreach (var count in legendaryCounts) mean += count;
        mean /= legendaryCounts.Count;
        int min = legendaryCounts[0];
        int max = legendaryCounts[legendaryCounts.Count - 1];
        Debug.Log($"[LegendaryDropTest] Simulation results: Median={median}, Mean={mean:F2}, Min={min}, Max={max}");
    }
} 