using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.ArcSystem
{
    /// <summary>
    /// Provides validation and repair utilities for ArcStateData.
    /// </summary>
    public static class ArcStateValidator
    {
        /// <summary>
        /// Validate the integrity of an ArcStateData instance.
        /// </summary>
        public static bool IsValid(ArcStateData state, out string error)
        {
            error = null;
            if (state == null)
            {
                error = "ArcStateData is null.";
                return false;
            }
            if (string.IsNullOrEmpty(state.ArcId))
            {
                error = "ArcId is missing.";
                return false;
            }
            if (state.Progress < 0)
            {
                error = "Progress cannot be negative.";
                return false;
            }
            if (state.Version < 1)
            {
                error = "Invalid version number.";
                return false;
            }
            // Add more validation rules as needed
            return true;
        }

        /// <summary>
        /// Attempt to repair a corrupted or invalid ArcStateData instance.
        /// </summary>
        public static bool TryRepair(ref ArcStateData state)
        {
            bool repaired = false;
            if (state == null)
            {
                state = new ArcStateData { ArcId = "unknown", Progress = 0, LastUpdated = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(), Version = 1 };
                repaired = true;
            }
            if (string.IsNullOrEmpty(state.ArcId))
            {
                state.ArcId = "unknown";
                repaired = true;
            }
            if (state.Progress < 0)
            {
                state.Progress = 0;
                repaired = true;
            }
            if (state.Version < 1)
            {
                state.Version = 1;
                repaired = true;
            }
            // Add more repair logic as needed
            return repaired;
        }

        /// <summary>
        /// Provide a fallback ArcStateData for unrecoverable cases.
        /// </summary>
        public static ArcStateData Fallback(string arcId)
        {
            Debug.LogError($"[ArcStateValidator] Unrecoverable state for arc {arcId}. Using fallback.");
            return new ArcStateData { ArcId = arcId, Progress = 0, LastUpdated = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(), Version = 1 };
        }
    }
}