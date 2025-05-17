using System;
using System.Collections.Generic;
using System.Linq;

namespace Visual_DM.FeatHistory
{
    public enum RecommendationStrategy { Collaborative, ContentBased, Hybrid }

    public class FeatRecommendationEngine
    {
        private List<Feat> allFeats;
        private List<FeatAchievementEvent> allEvents;
        private FeatHistoryAnalyzer analyzer;
        private Random rng = new Random();

        public FeatRecommendationEngine(List<Feat> feats, List<FeatAchievementEvent> events)
        {
            allFeats = feats;
            allEvents = events;
            analyzer = new FeatHistoryAnalyzer(events);
        }

        // Main entry: get recommendations for a player
        public List<Feat> GetRecommendations(string characterId, int topN = 3, RecommendationStrategy? forcedStrategy = null)
        {
            var strategy = forcedStrategy ?? AssignStrategyForPlayer(characterId);
            switch (strategy)
            {
                case RecommendationStrategy.Collaborative:
                    return CollaborativeFiltering(characterId, topN);
                case RecommendationStrategy.ContentBased:
                    return ContentBasedFiltering(characterId, topN);
                case RecommendationStrategy.Hybrid:
                default:
                    return HybridScoring(characterId, topN);
            }
        }

        // Collaborative filtering: recommend feats acquired by similar player types
        private List<Feat> CollaborativeFiltering(string characterId, int topN)
        {
            var playerTypes = analyzer.ClassifyPlayerTypes();
            if (!playerTypes.ContainsKey(characterId)) return new List<Feat>();
            var myType = playerTypes[characterId];
            var similarPlayers = playerTypes.Where(kv => kv.Value == myType && kv.Key != characterId).Select(kv => kv.Key);
            var featsBySimilar = allEvents.Where(e => similarPlayers.Contains(e.CharacterId)).Select(e => e.FeatId).Distinct();
            var myFeats = allEvents.Where(e => e.CharacterId == characterId).Select(e => e.FeatId).ToHashSet();
            var recFeats = featsBySimilar.Except(myFeats).Take(topN).ToList();
            return allFeats.Where(f => recFeats.Contains(f.Id)).ToList();
        }

        // Content-based filtering: recommend feats similar to those already acquired
        private List<Feat> ContentBasedFiltering(string characterId, int topN)
        {
            var myFeats = allEvents.Where(e => e.CharacterId == characterId).Select(e => e.FeatId).ToHashSet();
            var myFeatObjs = allFeats.Where(f => myFeats.Contains(f.Id)).ToList();
            // Simple similarity: recommend feats sharing metadata keys/values
            var candidateFeats = allFeats.Where(f => !myFeats.Contains(f.Id)).ToList();
            var scored = new List<(Feat feat, int score)>();
            foreach (var candidate in candidateFeats)
            {
                int score = 0;
                foreach (var myFeat in myFeatObjs)
                {
                    if (candidate.Metadata != null && myFeat.Metadata != null)
                    {
                        score += candidate.Metadata.Keys.Intersect(myFeat.Metadata.Keys).Count();
                        score += candidate.Metadata.Values.Intersect(myFeat.Metadata.Values).Count();
                    }
                }
                scored.Add((candidate, score));
            }
            return scored.OrderByDescending(s => s.score).Take(topN).Select(s => s.feat).ToList();
        }

        // Hybrid: combine both with scoring
        private List<Feat> HybridScoring(string characterId, int topN)
        {
            var collab = CollaborativeFiltering(characterId, allFeats.Count);
            var content = ContentBasedFiltering(characterId, allFeats.Count);
            var myFeats = allEvents.Where(e => e.CharacterId == characterId).Select(e => e.FeatId).ToHashSet();
            var candidateFeats = allFeats.Where(f => !myFeats.Contains(f.Id)).ToList();
            var scores = new Dictionary<string, double>();
            foreach (var feat in candidateFeats)
            {
                double score = 0;
                if (collab.Any(f => f.Id == feat.Id)) score += 1.0;
                if (content.Any(f => f.Id == feat.Id)) score += 1.0;
                // Weight by rarity (rarer feats get higher score)
                int count = allEvents.Count(e => e.FeatId == feat.Id);
                score += 1.0 / (1 + count);
                scores[feat.Id] = score;
            }
            return candidateFeats.OrderByDescending(f => scores[f.Id]).Take(topN).ToList();
        }

        // A/B testing: randomly assign strategy per player
        private Dictionary<string, RecommendationStrategy> abAssignments = new Dictionary<string, RecommendationStrategy>();
        private RecommendationStrategy AssignStrategyForPlayer(string characterId)
        {
            if (!abAssignments.ContainsKey(characterId))
            {
                var values = Enum.GetValues(typeof(RecommendationStrategy));
                abAssignments[characterId] = (RecommendationStrategy)values.GetValue(rng.Next(values.Length));
            }
            return abAssignments[characterId];
        }

        // Feedback capture (stub)
        public void RecordFeedback(string characterId, string featId, bool accepted)
        {
            // In production, store feedback for future tuning
            // For now, just log
            Console.WriteLine($"[RecommendationEngine] Feedback: {characterId} {(accepted ? "accepted" : "ignored")} {featId}");
        }
    }
} 