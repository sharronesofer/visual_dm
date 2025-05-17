using Visual_DM.Timeline.Models;
using System.Collections.Generic;
using System;

namespace Visual_DM.Utilities
{
    public class CooldownScoringModule : IFeatScoringModule
    {
        private FeatPowerConfig _config;
        public string Name => "Cooldown";
        public void Configure(FeatPowerConfig config) { _config = config; }
        public float Score(Feat feat, IEnumerable<Feat> allFeats = null)
        {
            if (feat.Metadata.TryGetValue("Cooldown", out var cdObj) && cdObj is float cooldown)
                return (float)Math.Log(1 + cooldown) * (_config?.CooldownWeight ?? 1f);
            return 1f;
        }
    }
} 