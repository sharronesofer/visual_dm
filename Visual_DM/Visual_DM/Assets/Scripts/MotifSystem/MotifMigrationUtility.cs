using System;
using System.Collections.Generic;

namespace VisualDM.MotifSystem
{
    /// <summary>
    /// Utility for migrating existing motifs to the new lifecycle management system.
    /// </summary>
    public static class MotifMigrationUtility
    {
        public static void MigrateMotif(Motif motif)
        {
            // Add or update required metadata for lifecycle management
            if (!motif.Metadata.ContainsKey("LifecycleState"))
                motif.Metadata["LifecycleState"] = MotifLifecycleState.Created.ToString();
            // Add other migration logic as needed
        }

        public static void MigrateMotifPool(MotifPool pool)
        {
            foreach (var motif in pool.ActiveMotifs)
                MigrateMotif(motif);
        }

        /// <summary>
        /// Migrates a motif to a target version. Returns true if successful, false otherwise.
        /// </summary>
        /// <param name="motif">The motif to migrate.</param>
        /// <param name="targetVersion">The target version.</param>
        /// <returns>True if migration succeeded, false otherwise.</returns>
        public static bool MigrateMotif(Motif motif, string targetVersion)
        {
            try
            {
                if (motif == null || string.IsNullOrEmpty(targetVersion)) return false;
                // Migration logic here
                motif.Version = targetVersion;
                return true;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifMigrationUtility.MigrateMotif failed", "MotifMigrationUtility.MigrateMotif");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return false;
            }
        }

        /// <summary>
        /// Bulk migrates a set of motifs to a target version. Returns the list of successfully migrated motifs.
        /// </summary>
        /// <param name="motifs">The motifs to migrate.</param>
        /// <param name="targetVersion">The target version.</param>
        /// <returns>List of migrated motifs.</returns>
        public static List<Motif> BulkMigrate(IEnumerable<Motif> motifs, string targetVersion)
        {
            var migrated = new List<Motif>();
            try
            {
                foreach (var motif in motifs)
                {
                    if (MigrateMotif(motif, targetVersion))
                        migrated.Add(motif);
                }
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifMigrationUtility.BulkMigrate failed", "MotifMigrationUtility.BulkMigrate");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
            return migrated;
        }
    }
}