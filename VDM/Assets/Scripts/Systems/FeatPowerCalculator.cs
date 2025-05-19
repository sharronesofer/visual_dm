using System;
using System.Collections.Generic;
using VisualDM.Timeline.Models;
using System.Linq;

namespace VisualDM.Systems.Utilities
{
    /// <summary>
    /// Calculates the power level of feats based on effect magnitude, resource costs, cooldowns, utility, and synergy.
    /// Modular, extensible, and configurable for future balance changes.
    /// </summary>
    public class FeatPowerCalculator
    {
        // Configuration for weighting and normalization
        public FeatPowerConfig Config { get; set; } = new FeatPowerConfig();
        private readonly List<IFeatScoringModule> _modules = new List<IFeatScoringModule>();

        public FeatPowerCalculator() { }
        public FeatPowerCalculator(FeatPowerConfig config) { Config = config; }

        /// <summary>
        /// Register a new scoring module (order matters for calculation pipeline).
        /// </summary>
        public void RegisterModule(IFeatScoringModule module)
        {
            module.Configure(Config);
            _modules.Add(module);
        }

        /// <summary>
        /// Clear all registered modules.
        /// </summary>
        public void ClearModules() => _modules.Clear();

        /// <summary>
        /// Calculates the power score for a given feat using all registered modules.
        /// </summary>
        public float CalculatePowerScore(Feat feat, IEnumerable<Feat> allFeats = null)
        {
            if (_modules.Count == 0)
                throw new InvalidOperationException("No scoring modules registered.");
            float score = 1f;
            foreach (var module in _modules)
            {
                try { score *= module.Score(feat, allFeats); }
                catch (Exception ex)
                {
                    // Log error and continue with next module
                    UnityEngine.Debug.LogError($"[FeatPowerCalculator] Module '{module.Name}' failed: {ex.Message}");
                }
            }
            return score;
        }

        /// <summary>
        /// Batch scores all feats in a dataset, returns dictionary of feat ID to score.
        /// </summary>
        public Dictionary<string, float> CalculateAllScores(IEnumerable<Feat> feats)
        {
            var featList = feats.ToList();
            var result = new Dictionary<string, float>();
            foreach (var feat in featList)
            {
                try { result[feat.Id] = CalculatePowerScore(feat, featList); }
                catch (Exception ex)
                {
                    UnityEngine.Debug.LogError($"[FeatPowerCalculator] Failed to score feat '{feat.Name}': {ex.Message}");
                    result[feat.Id] = 0f;
                }
            }
            return result;
        }

        /// <summary>
        /// Scores the effect magnitude (damage, healing, buffs, etc.)
        /// </summary>
        protected virtual float ScoreEffectMagnitude(Feat feat)
        {
            // Example: expects "EffectValue" in Metadata (float, normalized per turn/encounter)
            if (feat.Metadata.TryGetValue("EffectValue", out var valueObj) && valueObj is float value)
                return value * Config.EffectWeight;
            return Config.BaseEffectValue;
        }

        /// <summary>
        /// Scores the resource cost (mana, energy, action points, etc.)
        /// </summary>
        protected virtual float ScoreResourceCost(Feat feat)
        {
            // Example: expects "ResourceCost" in Metadata (float, higher = more costly)
            if (feat.Metadata.TryGetValue("ResourceCost", out var costObj) && costObj is float cost)
                return Math.Max(cost * Config.ResourceCostWeight, 0.01f);
            return 1f;
        }

        /// <summary>
        /// Scores the cooldown/usage limitation (longer cooldown = higher penalty)
        /// </summary>
        protected virtual float ScoreCooldown(Feat feat)
        {
            // Example: expects "Cooldown" in Metadata (float, in turns)
            if (feat.Metadata.TryGetValue("Cooldown", out var cdObj) && cdObj is float cooldown)
            {
                // Logarithmic penalty for long cooldowns
                return (float)Math.Log(1 + cooldown) * Config.CooldownWeight;
            }
            return 1f;
        }

        /// <summary>
        /// Scores the utility/versatility of the feat (situational value, flexibility)
        /// </summary>
        protected virtual float ScoreUtility(Feat feat)
        {
            // Example: expects "Utility" in Metadata (float, 1 = average, >1 = high utility)
            if (feat.Metadata.TryGetValue("Utility", out var utilObj) && utilObj is float utility)
                return utility * Config.UtilityWeight;
            return 1f;
        }

        /// <summary>
        /// Scores synergy with other feats (optional, can be extended)
        /// </summary>
        protected virtual float ScoreSynergy(Feat feat, IEnumerable<Feat> allFeats)
        {
            // Example: expects "Synergy" in Metadata (float, 1 = no synergy, >1 = strong synergy)
            if (feat.Metadata.TryGetValue("Synergy", out var synObj) && synObj is float synergy)
                return synergy * Config.SynergyWeight;
            return 1f;
        }
    }

    /// <summary>
    /// Configuration for FeatPowerCalculator weights and normalization.
    /// </summary>
    public class FeatPowerConfig
    {
        public float EffectWeight { get; set; } = 1.0f;
        public float ResourceCostWeight { get; set; } = 1.0f;
        public float CooldownWeight { get; set; } = 1.0f;
        public float UtilityWeight { get; set; } = 1.0f;
        public float SynergyWeight { get; set; } = 1.0f;
        public float BaseEffectValue { get; set; } = 1.0f; // Fallback if no effect value present
    }
} 