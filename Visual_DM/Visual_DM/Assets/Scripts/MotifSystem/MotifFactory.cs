using System;
using System.Collections.Generic;
using Systems.Integration;

namespace VisualDM.MotifSystem
{
    /// <summary>
    /// Factory for creating Motif instances, handling canonical themes, randomization, and versioning.
    /// </summary>
    public static class MotifFactory
    {
        public static readonly List<string> CanonicalMotifs = new List<string>
        {
            "Ascension", "Betrayal", "Chaos", "Collapse", "Compulsion", "Control",
            "Death", "Deception", "Defiance", "Desire", "Destiny", "Echo", "Expansion",
            "Faith", "Fear", "Futility", "Grief", "Guilt", "Hope", "Hunger", "Innocence",
            "Invention", "Isolation", "Justice", "Loyalty", "Madness", "Obsession",
            "Paranoia", "Power", "Pride", "Protection", "Rebirth", "Redemption",
            "Regret", "Revelation", "Ruin", "Sacrifice", "Silence", "Shadow",
            "Stagnation", "Temptation", "Time", "Transformation", "Truth", "Unity",
            "Vengeance", "Worship"
        };

        private static readonly Random _rng = new Random();

        /// <summary>
        /// Rolls a new motif, optionally using the chaos engine to determine chaos source.
        /// </summary>
        /// <param name="exclude">Themes to exclude from selection.</param>
        /// <param name="chaosEngine">The chaos engine for determining chaos source.</param>
        /// <returns>A valid motif or a fallback motif.</returns>
        public static Motif RollNewMotif(HashSet<string> exclude = null, IChaosEngine chaosEngine = null)
        {
            bool chaosSource = false;
            if (chaosEngine == null)
            {
                try { chaosEngine = ServiceLocator.Instance.Resolve<IChaosEngine>(); } catch { }
            }
            if (chaosEngine != null)
            {
                try { chaosSource = chaosEngine.GetChaosState()?.ChaosLevel > 0.5f; } catch { chaosSource = false; }
            }
            try
            {
                exclude = exclude ?? new HashSet<string>();
                var options = CanonicalMotifs.FindAll(m => !exclude.Contains(m));
                if (options.Count == 0)
                    throw new InvalidOperationException("No motifs available to select.");
                var theme = options[_rng.Next(options.Count)];
                int lifespan = _rng.Next(5, 20);
                var motif = new Motif(theme, lifespan, "1.0.0", chaosSource);
                // Data integrity check
                if (!MotifValidator.ValidateMotif(motif))
                {
                    VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError($"MotifFactory: Invalid motif created: {motif?.Theme ?? "<null>"}", "MotifFactory.RollNewMotif");
                    VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                    return GetFallbackMotif();
                }
                // Publish motif event to ChaosEngine
                try
                {
                    if (chaosEngine != null)
                    {
                        var eventData = new MotifEventData
                        {
                            MotifTheme = motif.Theme,
                            IsChaosSource = motif.ChaosSource,
                            EventType = "MotifRolled",
                            Context = "RollNewMotif"
                        };
                        chaosEngine.OnMotifEvent(eventData);
                    }
                }
                catch (Exception ex)
                {
                    IntegrationLogger.Log($"[MotifFactory] Failed to notify ChaosEngine: {ex.Message}", LogLevel.Warn, "MotifFactory", "ChaosEngine", "MotifRolled", "Error");
                }
                return motif;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifFactory.RollNewMotif failed", "MotifFactory.RollNewMotif");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return GetFallbackMotif();
            }
        }

        /// <summary>
        /// Returns a fallback motif if motif creation fails or is invalid.
        /// </summary>
        /// <returns>A fallback motif.</returns>
        private static Motif GetFallbackMotif()
        {
            return new Motif("Fallback", 10, "1.0.0", false);
        }
    }
}