using System;
using System.Collections.Generic;
using System.Linq;

namespace Visual_DM.FeatHistory
{
    public class FeatHistoryAnalyzer
    {
        private List<FeatAchievementEvent> events;

        public FeatHistoryAnalyzer(List<FeatAchievementEvent> events)
        {
            this.events = events ?? new List<FeatAchievementEvent>();
        }

        // 1. Most frequently acquired feats (global)
        public Dictionary<string, int> GetMostFrequentFeatsGlobal(int topN = 5)
        {
            return events.GroupBy(e => e.FeatId)
                .OrderByDescending(g => g.Count())
                .Take(topN)
                .ToDictionary(g => g.Key, g => g.Count());
        }

        // 2. Most frequently acquired feats (per character)
        public Dictionary<string, Dictionary<string, int>> GetMostFrequentFeatsPerCharacter(int topN = 3)
        {
            return events.GroupBy(e => e.CharacterId)
                .ToDictionary(
                    g => g.Key,
                    g => g.GroupBy(e => e.FeatId)
                        .OrderByDescending(gg => gg.Count())
                        .Take(topN)
                        .ToDictionary(gg => gg.Key, gg => gg.Count())
                );
        }

        // 3. Temporal analysis: streaks/clusters
        public Dictionary<string, List<List<FeatAchievementEvent>>> GetAcquisitionStreaks(TimeSpan maxGap)
        {
            var result = new Dictionary<string, List<List<FeatAchievementEvent>>>();
            foreach (var charGroup in events.GroupBy(e => e.CharacterId))
            {
                var sorted = charGroup.OrderBy(e => e.Timestamp).ToList();
                var streaks = new List<List<FeatAchievementEvent>>();
                var currentStreak = new List<FeatAchievementEvent>();
                for (int i = 0; i < sorted.Count; i++)
                {
                    if (i == 0 || (sorted[i].Timestamp - sorted[i - 1].Timestamp) <= maxGap)
                    {
                        currentStreak.Add(sorted[i]);
                    }
                    else
                    {
                        if (currentStreak.Count > 0) streaks.Add(new List<FeatAchievementEvent>(currentStreak));
                        currentStreak.Clear();
                        currentStreak.Add(sorted[i]);
                    }
                }
                if (currentStreak.Count > 0) streaks.Add(currentStreak);
                result[charGroup.Key] = streaks;
            }
            return result;
        }

        // 4. Player type classification (simple example)
        public Dictionary<string, string> ClassifyPlayerTypes()
        {
            var result = new Dictionary<string, string>();
            foreach (var charGroup in events.GroupBy(e => e.CharacterId))
            {
                var featCounts = charGroup.GroupBy(e => e.FeatId).ToDictionary(g => g.Key, g => g.Count());
                // Example: classify based on feat IDs (should be replaced with real logic)
                if (featCounts.Keys.Any(id => id.Contains("power")))
                    result[charGroup.Key] = "Aggressive";
                else if (featCounts.Keys.Any(id => id.Contains("defense")))
                    result[charGroup.Key] = "Defensive";
                else
                    result[charGroup.Key] = "Balanced";
            }
            return result;
        }

        // 5. Anomaly detection: rare feats, sudden changes
        public List<FeatAchievementEvent> DetectAnomalies(int rareThreshold = 1)
        {
            var featCounts = events.GroupBy(e => e.FeatId).ToDictionary(g => g.Key, g => g.Count());
            return events.Where(e => featCounts[e.FeatId] <= rareThreshold).ToList();
        }

        // 6. Summary statistics
        public Dictionary<string, object> GetSummaryStatistics()
        {
            var stats = new Dictionary<string, object>();
            stats["TotalEvents"] = events.Count;
            stats["UniqueCharacters"] = events.Select(e => e.CharacterId).Distinct().Count();
            stats["UniqueFeats"] = events.Select(e => e.FeatId).Distinct().Count();
            if (events.Count > 0)
            {
                var times = events.Select(e => e.Timestamp).OrderBy(t => t).ToList();
                stats["FirstEvent"] = times.First();
                stats["LastEvent"] = times.Last();
                stats["AverageIntervalSeconds"] = times.Zip(times.Skip(1), (a, b) => (b - a).TotalSeconds).DefaultIfEmpty(0).Average();
            }
            return stats;
        }
    }
} 