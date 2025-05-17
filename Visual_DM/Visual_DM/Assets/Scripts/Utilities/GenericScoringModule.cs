using Visual_DM.Timeline.Models;
using System;
using System.Collections.Generic;

namespace Visual_DM.Utilities
{
    /// <summary>
    /// Generic scoring module for feats, configurable for different scoring types (e.g., Synergy, Utility, Cooldown, ResourceCost, EffectMagnitude).
    /// </summary>
    public class GenericScoringModule : IFeatScoringModule
    {
        private FeatPowerConfig _config;
        private readonly string _metadataKey;
        private readonly string _name;
        private readonly Func<Feat, FeatPowerConfig, float> _customScoreFunc;

        public string Name => _name;

        /// <summary>
        /// Create a generic scoring module for a specific metadata key and scoring logic.
        /// </summary>
        /// <param name="name">Name of the module (for diagnostics)</param>
        /// <param name="metadataKey">Key in feat.Metadata to use for scoring</param>
        /// <param name="customScoreFunc">Optional custom scoring function (overrides default logic)</param>
        public GenericScoringModule(string name, string metadataKey, Func<Feat, FeatPowerConfig, float> customScoreFunc = null)
        {
            _name = name;
            _metadataKey = metadataKey;
            _customScoreFunc = customScoreFunc;
        }

        public void Configure(FeatPowerConfig config) { _config = config; }

        public float Score(Feat feat, IEnumerable<Feat> allFeats = null)
        {
            if (_customScoreFunc != null)
                return _customScoreFunc(feat, _config);

            if (feat.Metadata.TryGetValue(_metadataKey, out var valueObj) && valueObj is float value)
            {
                switch (_metadataKey)
                {
                    case "Synergy":
                        return value * (_config?.SynergyWeight ?? 1f);
                    case "Utility":
                        return value * (_config?.UtilityWeight ?? 1f);
                    case "Cooldown":
                        return (float)Math.Log(1 + value) * (_config?.CooldownWeight ?? 1f);
                    case "ResourceCost":
                        return Math.Max(value * (_config?.ResourceCostWeight ?? 1f), 0.01f);
                    case "EffectValue":
                        return value * (_config?.EffectWeight ?? 1f);
                    default:
                        return value;
                }
            }
            // Fallback for EffectMagnitude
            if (_metadataKey == "EffectValue")
                return _config?.BaseEffectValue ?? 1f;
            return 1f;
        }
    }
}