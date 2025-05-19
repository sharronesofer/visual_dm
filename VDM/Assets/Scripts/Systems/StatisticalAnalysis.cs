using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace VisualDM.Simulation
{
    public static class StatisticalAnalysis
    {
        // Basic statistics
        public static float Mean(List<float> values) => values.Count == 0 ? 0f : values.Sum() / values.Count;
        public static float Median(List<float> values)
        {
            if (values.Count == 0) return 0f;
            var sorted = values.OrderBy(x => x).ToList();
            int mid = sorted.Count / 2;
            return sorted.Count % 2 == 0 ? (sorted[mid - 1] + sorted[mid]) / 2f : sorted[mid];
        }
        public static float StdDev(List<float> values)
        {
            if (values.Count == 0) return 0f;
            float mean = Mean(values);
            float sumSq = values.Sum(v => (v - mean) * (v - mean));
            return Mathf.Sqrt(sumSq / values.Count);
        }

        // Outlier detection (z-score)
        public static List<int> DetectOutliers(List<float> values, float zThreshold = 2.0f)
        {
            var outliers = new List<int>();
            float mean = Mean(values);
            float std = StdDev(values);
            if (std < 0.0001f) return outliers;
            for (int i = 0; i < values.Count; i++)
            {
                float z = Mathf.Abs((values[i] - mean) / std);
                if (z > zThreshold) outliers.Add(i);
            }
            return outliers;
        }

        // Feat interaction analysis
        public static Dictionary<string, float> AnalyzeFeatSynergy(List<TestCase> testCases)
        {
            // Map feat name to average performance metric (e.g., win rate)
            var featScores = new Dictionary<string, List<float>>();
            foreach (var tc in testCases)
            {
                if (tc.Character.ActiveFeats == null) continue;
                foreach (var feat in tc.Character.ActiveFeats)
                {
                    if (!featScores.ContainsKey(feat.Name)) featScores[feat.Name] = new List<float>();
                    // For demo, use a dummy metric (could be win rate, DPS, etc.)
                    featScores[feat.Name].Add(UnityEngine.Random.value); // Replace with real metric
                }
            }
            return featScores.ToDictionary(kv => kv.Key, kv => Mean(kv.Value));
        }

        // Detect overpowered/underpowered feat combos
        public static List<string> DetectBrokenCombos(List<TestCase> testCases, float threshold = 0.9f)
        {
            var synergy = AnalyzeFeatSynergy(testCases);
            return synergy.Where(kv => kv.Value > threshold || kv.Value < (1 - threshold)).Select(kv => kv.Key).ToList();
        }

        // Compare feat effectiveness across archetypes
        public static Dictionary<string, Dictionary<CharacterArchetype, float>> CompareFeatEffectiveness(List<TestCase> testCases)
        {
            var result = new Dictionary<string, Dictionary<CharacterArchetype, List<float>>>();
            foreach (var tc in testCases)
            {
                if (tc.Character.ActiveFeats == null) continue;
                foreach (var feat in tc.Character.ActiveFeats)
                {
                    if (!result.ContainsKey(feat.Name)) result[feat.Name] = new Dictionary<CharacterArchetype, List<float>>();
                    var arch = Enum.TryParse<CharacterArchetype>(tc.Character.Name, out var a) ? a : CharacterArchetype.Fighter;
                    if (!result[feat.Name].ContainsKey(arch)) result[feat.Name][arch] = new List<float>();
                    result[feat.Name][arch].Add(UnityEngine.Random.value); // Replace with real metric
                }
            }
            // Convert lists to means
            var output = new Dictionary<string, Dictionary<CharacterArchetype, float>>();
            foreach (var feat in result.Keys)
            {
                output[feat] = new Dictionary<CharacterArchetype, float>();
                foreach (var arch in result[feat].Keys)
                    output[feat][arch] = Mean(result[feat][arch]);
            }
            return output;
        }

        // DPS, survivability, utility metrics (stub)
        public static float ComputeDPS(TestCase tc) => UnityEngine.Random.Range(5f, 20f); // Replace with real logic
        public static float ComputeSurvivability(TestCase tc) => UnityEngine.Random.Range(0.5f, 1.0f); // Replace with real logic
        public static float ComputeUtility(TestCase tc) => UnityEngine.Random.Range(0f, 1.0f); // Replace with real logic

        // Visualization stubs
        public class FeatInteractionGraph { /* To be implemented for reporting system */ }
        public class FeatDependencyTree { /* To be implemented for reporting system */ }

        // Pattern recognition for problematic combos (stub)
        public static List<string> RecognizeProblematicCombos(List<TestCase> testCases)
        {
            // Example: frequent outliers, high synergy pairs
            return DetectBrokenCombos(testCases, 0.95f);
        }
    }
} 