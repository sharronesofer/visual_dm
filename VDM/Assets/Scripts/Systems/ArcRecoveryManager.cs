using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.ArcSystem
{
    /// <summary>
    /// Handles recovery, rollback, and conflict resolution for arc state changes.
    /// </summary>
    public static class ArcRecoveryManager
    {
        private static readonly Dictionary<string, ArcStateData> _checkpoints = new Dictionary<string, ArcStateData>();

        /// <summary>
        /// Event for user-facing recovery/failure messages.
        /// </summary>
        public static event Action<string, string> OnUserRecoveryMessage;

        /// <summary>
        /// Begin a transaction for an arc state change (creates a checkpoint).
        /// </summary>
        public static void BeginTransaction(string arcId, ArcStateData currentState)
        {
            // Deep copy for checkpoint
            _checkpoints[arcId] = DeepCopy(currentState);
        }

        /// <summary>
        /// Commit a transaction (removes checkpoint).
        /// </summary>
        public static void CommitTransaction(string arcId)
        {
            if (_checkpoints.ContainsKey(arcId))
                _checkpoints.Remove(arcId);
        }

        /// <summary>
        /// Rollback to the last checkpoint for the given arc.
        /// </summary>
        public static ArcStateData Rollback(string arcId)
        {
            if (_checkpoints.TryGetValue(arcId, out var checkpoint))
            {
                // Restore checkpoint and remove it
                _checkpoints.Remove(arcId);
                return DeepCopy(checkpoint);
            }
            Debug.LogWarning($"[ArcRecoveryManager] No checkpoint found for arc {arcId}.");
            return null;
        }

        /// <summary>
        /// Resolve conflicts between two arc states (prefers latest timestamp).
        /// </summary>
        public static ArcStateData ResolveConflict(ArcStateData a, ArcStateData b)
        {
            if (a == null) return b;
            if (b == null) return a;
            return a.LastUpdated >= b.LastUpdated ? a : b;
        }

        /// <summary>
        /// Handle unrecoverable state by providing a fallback arc state.
        /// </summary>
        public static ArcStateData Fallback(string arcId)
        {
            Debug.LogError($"[ArcRecoveryManager] Unrecoverable state for arc {arcId}. Using fallback.");
            // Return a minimal valid state or a default arc state
            return new ArcStateData { ArcId = arcId, Progress = 0, LastUpdated = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(), Version = 1 };
        }

        /// <summary>
        /// Deep copy utility for ArcStateData (via JSON roundtrip).
        /// </summary>
        private static ArcStateData DeepCopy(ArcStateData state)
        {
            if (state == null) return null;
            string json = state.ToJson();
            return ArcStateData.FromJson(json);
        }

        /// <summary>
        /// Trigger a user-facing message for recovery or fallback events.
        /// </summary>
        public static void ShowUserRecoveryMessage(string title, string message)
        {
            Debug.Log($"[ArcRecoveryManager] USER MESSAGE: {title} - {message}");
            OnUserRecoveryMessage?.Invoke(title, message);
        }
    }
}