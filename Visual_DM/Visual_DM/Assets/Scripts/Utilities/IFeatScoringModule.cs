using Visual_DM.Timeline.Models;
using System.Collections.Generic;

namespace Visual_DM.Utilities
{
    /// <summary>
    /// Interface for modular scoring components in the FeatPowerCalculator engine.
    /// </summary>
    public interface IFeatScoringModule
    {
        /// <summary>
        /// Returns a multiplier or additive score for the given feat.
        /// </summary>
        float Score(Feat feat, IEnumerable<Feat> allFeats = null);
        /// <summary>
        /// Optional: Configure the module with custom parameters.
        /// </summary>
        void Configure(FeatPowerConfig config);
        /// <summary>
        /// Optional: Returns the name of the module for diagnostics.
        /// </summary>
        string Name { get; }
    }
} 