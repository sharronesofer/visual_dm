using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using UnityEngine;

namespace ArcSystem
{
    /// <summary>
    /// Manages persistence of arc states, supporting save/load with compression and versioning.
    /// </summary>
    public static class ArcPersistenceManager
    {
        private static readonly string SaveDirectory = Path.Combine(Application.persistentDataPath, "ArcSaves");

        /// <summary>
        /// Event triggered after an arc state is saved.
        /// </summary>
        public static event Action<ArcStateData> OnArcStateSaved;

        /// <summary>
        /// Event triggered after an arc state is loaded.
        /// </summary>
        public static event Action<ArcStateData> OnArcStateLoaded;

        /// <summary>
        /// Event triggered for analytics when a recovery event occurs.
        /// </summary>
        public static event Action<string, ArcStateData> OnRecoveryEvent;

        /// <summary>
        /// Event triggered for analytics when a failure occurs.
        /// </summary>
        public static event Action<string, Exception> OnPersistenceFailure;

        private const float PerformanceWarningThresholdMs = 50f; // Log if save/load takes longer than this

        /// <summary>
        /// Save an ArcStateData instance to disk (compressed JSON).
        /// </summary>
        public static void SaveArcState(ArcStateData arcState, bool isManual = false)
        {
            var stopwatch = System.Diagnostics.Stopwatch.StartNew();
            try
            {
                if (!Directory.Exists(SaveDirectory))
                    Directory.CreateDirectory(SaveDirectory);

                string fileName = GetFileName(arcState.ArcId, isManual);
                string json = arcState.ToJson();
                byte[] jsonBytes = System.Text.Encoding.UTF8.GetBytes(json);

                using (var fileStream = new FileStream(fileName, FileMode.Create, FileAccess.Write))
                using (var gzip = new GZipStream(fileStream, CompressionLevel.Optimal))
                {
                    gzip.Write(jsonBytes, 0, jsonBytes.Length);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ArcPersistenceManager] Failed to save arc state: {ex}");
                OnPersistenceFailure?.Invoke("save", ex);
            }
            finally
            {
                stopwatch.Stop();
                if (stopwatch.ElapsedMilliseconds > PerformanceWarningThresholdMs)
                {
                    Debug.LogWarning($"[ArcPersistenceManager] SaveArcState took {stopwatch.ElapsedMilliseconds} ms.");
                }
            }
        }

        /// <summary>
        /// Load an ArcStateData instance from disk (decompress and deserialize JSON).
        /// </summary>
        public static ArcStateData LoadArcState(string arcId, bool isManual = false)
        {
            var stopwatch = System.Diagnostics.Stopwatch.StartNew();
            try
            {
                string fileName = GetFileName(arcId, isManual);
                if (!File.Exists(fileName))
                    return null;

                using (var fileStream = new FileStream(fileName, FileMode.Open, FileAccess.Read))
                using (var gzip = new GZipStream(fileStream, CompressionMode.Decompress))
                using (var ms = new MemoryStream())
                {
                    gzip.CopyTo(ms);
                    string json = System.Text.Encoding.UTF8.GetString(ms.ToArray());
                    return ArcStateData.FromJson(json);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ArcPersistenceManager] Failed to load arc state: {ex}");
                OnPersistenceFailure?.Invoke("load", ex);
                return null;
            }
            finally
            {
                stopwatch.Stop();
                if (stopwatch.ElapsedMilliseconds > PerformanceWarningThresholdMs)
                {
                    Debug.LogWarning($"[ArcPersistenceManager] LoadArcState took {stopwatch.ElapsedMilliseconds} ms.");
                }
            }
        }

        /// <summary>
        /// Get the file name for a given arc ID and save type.
        /// </summary>
        private static string GetFileName(string arcId, bool isManual)
        {
            string type = isManual ? "manual" : "auto";
            return Path.Combine(SaveDirectory, $"arc_{arcId}_{type}.gz");
        }

        /// <summary>
        /// Save and synchronize arc state with the world state system.
        /// </summary>
        public static void SaveAndSyncArcState(ArcStateData arcState, Action syncWithWorldState = null, bool isManual = false)
        {
            SaveArcState(arcState, isManual);
            syncWithWorldState?.Invoke();
            OnArcStateSaved?.Invoke(arcState);
        }

        /// <summary>
        /// Load arc state and synchronize with the world state system.
        /// </summary>
        public static ArcStateData LoadAndSyncArcState(string arcId, Action<ArcStateData> syncWithWorldState = null, bool isManual = false)
        {
            var arcState = LoadArcState(arcId, isManual);
            syncWithWorldState?.Invoke(arcState);
            OnArcStateLoaded?.Invoke(arcState);
            return arcState;
        }

        /// <summary>
        /// Register a callback for designer tool integration (e.g., for custom editors or runtime tools).
        /// </summary>
        public static void RegisterDesignerToolCallback(Action<ArcStateData> callback)
        {
            OnArcStateSaved += callback;
            OnArcStateLoaded += callback;
        }

        /// <summary>
        /// Call this when a recovery event occurs (for analytics).
        /// </summary>
        public static void LogRecoveryEvent(string eventType, ArcStateData arcState)
        {
            Debug.Log($"[ArcPersistenceManager] Recovery event: {eventType} for arc {arcState?.ArcId}");
            OnRecoveryEvent?.Invoke(eventType, arcState);
        }

        /// <summary>
        /// List all arc save files in the save directory.
        /// </summary>
        public static List<string> ListAllArcSaveFiles()
        {
            if (!Directory.Exists(SaveDirectory))
                return new List<string>();
            return new List<string>(Directory.GetFiles(SaveDirectory, "arc_*.gz"));
        }

        /// <summary>
        /// Load raw JSON from a save file (for admin/debug).
        /// </summary>
        public static string LoadRawJson(string filePath)
        {
            if (!File.Exists(filePath)) return null;
            using (var fileStream = new FileStream(filePath, FileMode.Open, FileAccess.Read))
            using (var gzip = new GZipStream(fileStream, CompressionMode.Decompress))
            using (var ms = new MemoryStream())
            {
                gzip.CopyTo(ms);
                return System.Text.Encoding.UTF8.GetString(ms.ToArray());
            }
        }

        /// <summary>
        /// Repair and resave a corrupted arc state file (admin/debug).
        /// </summary>
        public static bool RepairAndResave(string filePath)
        {
            try
            {
                string json = LoadRawJson(filePath);
                var arcState = ArcStateData.FromJson(json);
                string error;
                if (!ArcStateValidator.IsValid(arcState, out error))
                {
                    if (ArcStateValidator.TryRepair(ref arcState))
                    {
                        SaveArcState(arcState, filePath.Contains("manual"));
                        Debug.Log($"[ArcPersistenceManager] Admin repaired and resaved arc state: {filePath}");
                        return true;
                    }
                    else
                    {
                        Debug.LogError($"[ArcPersistenceManager] Admin failed to repair arc state: {filePath}");
                        return false;
                    }
                }
                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ArcPersistenceManager] Admin repair failed: {ex}");
                return false;
            }
        }

        /// <summary>
        /// Override and resave an arc state (admin/debug).
        /// </summary>
        public static void OverrideArcState(ArcStateData arcState, bool isManual = false)
        {
            SaveArcState(arcState, isManual);
            Debug.Log($"[ArcPersistenceManager] Admin override: arc {arcState.ArcId} resaved.");
        }
    }
}