using System;
using System.Collections.Generic;

namespace VisualDM.MotifSystem
{
    /// <summary>
    /// Provides schema and business rule validation for Motif and MotifPool.
    /// </summary>
    public static class MotifValidator
    {
        /// <summary>
        /// Validates a motif and returns true if valid, false otherwise. Never throws.
        /// </summary>
        /// <param name="motif">The motif to validate.</param>
        /// <returns>True if valid, false otherwise.</returns>
        public static bool ValidateMotif(Motif motif)
        {
            try
            {
                if (motif == null) return false;
                if (string.IsNullOrEmpty(motif.Theme)) return false;
                if (motif.Lifespan <= 0) return false;
                // Add more validation rules as needed
                return true;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifValidator.ValidateMotif failed", "MotifValidator.ValidateMotif");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return false;
            }
        }

        /// <summary>
        /// Validates a motif and throws an exception if invalid. For internal assertions only.
        /// </summary>
        /// <param name="motif">The motif to validate.</param>
        /// <exception cref="ArgumentException">Thrown if motif is invalid.</exception>
        public static void ValidateMotifOrThrow(Motif motif)
        {
            if (motif == null) throw new ArgumentException("Motif is null.");
            if (string.IsNullOrEmpty(motif.Theme)) throw new ArgumentException("Motif theme is null or empty.");
            if (motif.Lifespan <= 0) throw new ArgumentException("Motif lifespan must be positive.");
            // Add more validation rules as needed
        }

        /// <summary>
        /// Validates a set of motifs and returns a list of error messages for invalid motifs.
        /// </summary>
        /// <param name="motifs">The motifs to validate.</param>
        /// <returns>List of error messages for invalid motifs.</returns>
        public static List<string> ValidateMotifSet(IEnumerable<Motif> motifs)
        {
            var errors = new List<string>();
            try
            {
                foreach (var motif in motifs)
                {
                    if (!ValidateMotif(motif))
                        errors.Add($"Invalid motif: {motif?.Theme ?? "<null>"}");
                }
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifValidator.ValidateMotifSet failed", "MotifValidator.ValidateMotifSet");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                errors.Add("Exception occurred during motif set validation.");
            }
            return errors;
        }

        public static ValidationResult ValidateMotifPool(MotifPool pool)
        {
            return pool.Validate();
        }

        public static bool IsValidTheme(string theme)
        {
            return MotifFactory.CanonicalMotifs.Contains(theme);
        }
    }
}