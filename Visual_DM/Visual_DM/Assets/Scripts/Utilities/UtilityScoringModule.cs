using Visual_DM.Timeline.Models;
using System.Collections.Generic;

namespace Visual_DM.Utilities
{
    public class UtilityScoringModule : IFeatScoringModule
    {
        private FeatPowerConfig _config;
        public string Name => "Utility";
        public void Configure(FeatPowerConfig config) { _config = config; }
        public float Score(Feat feat, IEnumerable<Feat> allFeats = null)
        {
            if (feat.Metadata.TryGetValue("Utility", out var utilObj) && utilObj is float utility)
                return utility * (_config?.UtilityWeight ?? 1f);
            return 1f;
        }
    }
} 