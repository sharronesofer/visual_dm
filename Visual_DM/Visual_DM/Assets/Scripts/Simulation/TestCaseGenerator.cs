using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Simulation
{
    public enum CharacterArchetype { Fighter, Mage, Rogue }

    [Serializable]
    public class TestCase
    {
        public string Name;
        public SimulatedCharacter Character;
        public string Scenario;
        public int Version;
        public string Metadata;
    }

    public static class TestCaseGenerator
    {
        private static int currentVersion = 1;
        private static System.Random rng = new System.Random();

        // Generate a character build for a given archetype
        public static SimulatedCharacter GenerateBuild(CharacterArchetype archetype, int level = 1, int seed = -1)
        {
            if (seed >= 0) rng = new System.Random(seed);
            CharacterStats stats = archetype switch
            {
                CharacterArchetype.Fighter => new CharacterStats(15, 13, 14, 8, 10, 10),
                CharacterArchetype.Mage => new CharacterStats(8, 12, 10, 16, 14, 10),
                CharacterArchetype.Rogue => new CharacterStats(10, 16, 12, 12, 10, 12),
                _ => new CharacterStats()
            };
            var character = new SimulatedCharacter(archetype.ToString(), stats);
            // Add starting feats, inventory, etc. as needed
            return character;
        }

        // Simulate progression path (level up, feat acquisition)
        public static void ProgressCharacter(SimulatedCharacter character, int targetLevel, Func<SimulatedCharacter, Feat> featSelector = null)
        {
            for (int lvl = 2; lvl <= targetLevel; lvl++)
            {
                // Example: every even level, gain a feat
                if (lvl % 2 == 0 && featSelector != null)
                {
                    var feat = featSelector(character);
                    if (feat != null) character.ApplyFeat(feat);
                }
                // Optionally increase stats, add inventory, etc.
            }
        }

        // Generate a scenario (combat, exploration, social)
        public static string GenerateScenario(string type, Dictionary<string, object> parameters = null)
        {
            // For now, just return a string; can be expanded to scenario objects
            if (type == "combat")
                return "Standard combat vs. equal-level enemy";
            if (type == "exploration")
                return "Trap disarm in dungeon";
            if (type == "social")
                return "Persuasion check with noble";
            return "Custom scenario";
        }

        // Load custom test cases from JSON (stub)
        public static List<TestCase> LoadCustomTestCases(string json)
        {
            // TODO: Implement JSON parsing
            return new List<TestCase>();
        }

        // Generate edge case builds
        public static SimulatedCharacter GenerateEdgeCase(string type)
        {
            if (type == "min-stats")
                return new SimulatedCharacter("MinStats", new CharacterStats(1, 1, 1, 1, 1, 1));
            if (type == "max-stats")
                return new SimulatedCharacter("MaxStats", new CharacterStats(20, 20, 20, 20, 20, 20));
            // Add more as needed
            return GenerateBuild(CharacterArchetype.Fighter);
        }

        // Generate a batch of test cases
        public static List<TestCase> GenerateBatch(CharacterArchetype[] archetypes, int[] levels, string[] scenarios)
        {
            var cases = new List<TestCase>();
            foreach (var archetype in archetypes)
            {
                foreach (var level in levels)
                {
                    var character = GenerateBuild(archetype, level);
                    foreach (var scenario in scenarios)
                    {
                        cases.Add(new TestCase
                        {
                            Name = $"{archetype}_L{level}_{scenario}",
                            Character = character.Clone(),
                            Scenario = scenario,
                            Version = currentVersion,
                            Metadata = $"Archetype: {archetype}, Level: {level}, Scenario: {scenario}"
                        });
                    }
                }
            }
            return cases;
        }

        // Versioning utilities
        public static void SetVersion(int version) => currentVersion = version;
        public static int GetVersion() => currentVersion;
    }
} 