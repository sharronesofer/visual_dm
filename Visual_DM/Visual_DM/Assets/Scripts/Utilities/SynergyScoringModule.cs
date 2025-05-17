using Visual_DM.Timeline.Models;
using System.Collections.Generic;

namespace Visual_DM.Utilities
{
    public class SynergyScoringModule : IFeatScoringModule
    {
        private FeatPowerConfig _config;
        public string Name => "Synergy";
        public void Configure(FeatPowerConfig config) { _config = config; }
        public float Score(Feat feat, IEnumerable<Feat> allFeats = null)
        {
            if (feat.Metadata.TryGetValue("Synergy", out var synObj) && synObj is float synergy)
                return synergy * (_config?.SynergyWeight ?? 1f);
            return 1f;
        }
    }
} 