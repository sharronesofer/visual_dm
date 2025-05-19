using System;
using UnityEngine;

namespace VisualDM.AI
{
    /// <summary>
    /// Provides methods to evaluate the truth value between an original event and a rumor.
    /// </summary>
    public static class RumorTruthEvaluator
    {
        /// <summary>
        /// Calculates a percentage-based truth value between the original event and the rumor.
        /// Uses normalized Levenshtein distance as a simple similarity metric.
        /// </summary>
        public static float CalculateTruthValue(string original, string rumor)
        {
            if (string.IsNullOrEmpty(original) || string.IsNullOrEmpty(rumor))
                return 0f;
            int distance = LevenshteinDistance(original, rumor);
            int maxLen = Mathf.Max(original.Length, rumor.Length);
            if (maxLen == 0) return 1f;
            float similarity = 1f - (float)distance / maxLen;
            return Mathf.Clamp01(similarity);
        }

        // Levenshtein distance implementation
        private static int LevenshteinDistance(string s, string t)
        {
            int n = s.Length;
            int m = t.Length;
            int[,] d = new int[n + 1, m + 1];
            for (int i = 0; i <= n; i++) d[i, 0] = i;
            for (int j = 0; j <= m; j++) d[0, j] = j;
            for (int i = 1; i <= n; i++)
            {
                for (int j = 1; j <= m; j++)
                {
                    int cost = (s[i - 1] == t[j - 1]) ? 0 : 1;
                    d[i, j] = Mathf.Min(
                        Mathf.Min(d[i - 1, j] + 1, d[i, j - 1] + 1),
                        d[i - 1, j - 1] + cost
                    );
                }
            }
            return d[n, m];
        }

        // Runtime test for truth value calculation
        [ContextMenu("Test Truth Value Calculation")]
        public static void TestTruthValueCalculation()
        {
            string original = "NPC_A saw NPC_B steal a coin.";
            string rumor = "NPC_B was caught stealing money at the tavern.";
            float truth = CalculateTruthValue(original, rumor);
            Debug.Log($"[TruthValueTest] Truth value between:\nOriginal: {original}\nRumor: {rumor}\nResult: {truth:P0}");
        }
    }
}