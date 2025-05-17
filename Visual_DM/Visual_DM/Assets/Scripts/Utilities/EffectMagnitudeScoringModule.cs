using Visual_DM.Timeline.Models;
using System.Collections.Generic;

namespace Visual_DM.Utilities
{
    public class EffectMagnitudeScoringModule : IFeatScoringModule
    {
        private FeatPowerConfig _config;
        public string Name => "EffectMagnitude";
        public void Configure(FeatPowerConfig config) { _config = config; }
        public float Score(Feat feat, IEnumerable<Feat> allFeats = null)
        {
            if (feat.Metadata.TryGetValue("EffectValue", out var valueObj) && valueObj is float value)
                return value * (_config?.EffectWeight ?? 1f);
            return _config?.BaseEffectValue ?? 1f;
        }
    }
} 