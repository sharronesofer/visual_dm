using Visual_DM.Timeline.Models;
using System.Collections.Generic;
using System;

namespace Visual_DM.Utilities
{
    public class ResourceCostScoringModule : IFeatScoringModule
    {
        private FeatPowerConfig _config;
        public string Name => "ResourceCost";
        public void Configure(FeatPowerConfig config) { _config = config; }
        public float Score(Feat feat, IEnumerable<Feat> allFeats = null)
        {
            if (feat.Metadata.TryGetValue("ResourceCost", out var costObj) && costObj is float cost)
                return Math.Max(cost * (_config?.ResourceCostWeight ?? 1f), 0.01f);
            return 1f;
        }
    }
} 