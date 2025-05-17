using System.Threading.Tasks;

namespace Visual_DM.AI
{
    /// <summary>
    /// Interface for GPT-powered rumor transformation service.
    /// </summary>
    public interface IGPTRumorService
    {
        /// <summary>
        /// Transforms a game event into a rumor using GPT, applying distortion and context parameters.
        /// </summary>
        /// <param name="eventData">The original event data (JSON or string).</param>
        /// <param name="parameters">Rumor transformation parameters (distortion, NPC traits, etc.).</param>
        /// <returns>The transformed rumor as a string.</returns>
        Task<string> TransformRumorAsync(string eventData, RumorParameters parameters);
    }

    /// <summary>
    /// Parameters for rumor transformation.
    /// </summary>
    public class RumorParameters
    {
        public float DistortionLevel { get; set; } // 0.0 (truthful) to 1.0 (max distortion)
        public string NpcPersonality { get; set; } // e.g., "gossip", "truth-teller"
        public string Theme { get; set; } // e.g., "crime", "heroism"
        public int RetellingCount { get; set; } // Number of times rumor has been retold
        public float TimeSinceEvent { get; set; } // In-game time since event occurred
        // Add more parameters as needed
    }
}