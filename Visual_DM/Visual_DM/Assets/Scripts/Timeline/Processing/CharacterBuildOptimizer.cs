using System;
using System.Collections.Generic;
using System.Linq;
using Visual_DM.Timeline.Models;
using VisualDM.Simulation;

namespace Visual_DM.Timeline.Processing
{
    public class CharacterBuildOptimizer
    {
        private readonly FeatDataSet _featDataSet;

        public CharacterBuildOptimizer(FeatDataSet featDataSet)
        {
            _featDataSet = featDataSet;
        }

        public List<Feat> RecommendFeats(CharacterBuild build, int maxFeats = 10)
        {
            // 1. Filter feats by level and prerequisites
            var availableFeats = _featDataSet.GetFeatsByLevel(build.Level)
                .Where(f => ArePrerequisitesMet(f, build.SelectedFeats))
                .ToList();

            // 2. Score feats based on build stats, role, playstyle, and synergies
            var scoredFeats = availableFeats
                .Select(f => new { Feat = f, Score = ScoreFeat(f, build) })
                .OrderByDescending(x => x.Score)
                .Take(maxFeats)
                .Select(x => x.Feat)
                .ToList();

            return scoredFeats;
        }

        private bool ArePrerequisitesMet(Feat feat, List<Feat> selectedFeats)
        {
            if (feat.Prerequisites == null || feat.Prerequisites.Count == 0) return true;
            var selectedIds = new HashSet<string>(selectedFeats.Select(f => f.Id));
            return feat.Prerequisites.All(selectedIds.Contains);
        }

        private float ScoreFeat(Feat feat, CharacterBuild build)
        {
            float score = 0f;
            // Example: Score by category and role synergy
            if (feat.Category == FeatCategory.Combat && build.Role == "Tank") score += 2f;
            if (feat.Category == FeatCategory.Magic && build.Role == "DPS") score += 2f;
            if (feat.Category == FeatCategory.Utility && build.Playstyle == "Utility") score += 2f;
            // Example: Score by stat requirements (if present in Metadata)
            if (feat.Metadata.TryGetValue("Stat", out var statObj) && statObj is string statName)
            {
                int statValue = build.Stats.GetStat(statName);
                score += statValue * 0.1f;
            }
            // Example: Synergy with already selected feats
            score += CalculateSynergy(feat, build.SelectedFeats);
            // Example: Penalize for high level requirement
            score -= feat.LevelRequirement * 0.1f;
            return score;
        }

        private float CalculateSynergy(Feat feat, List<Feat> selectedFeats)
        {
            float synergy = 0f;
            // Example: If feat shares category with selected feats, boost score
            if (selectedFeats.Any(f => f.Category == feat.Category)) synergy += 1f;
            // Extension point: Add more advanced synergy logic here as needed.
            return synergy;
        }
    }
} 