using UnityEngine;

namespace VDM.Combat
{
    /// <summary>
    /// Logging utility for combat events and errors.
    /// </summary>
    public static class CombatLogger
    {
        public static void Log(string message)
        {
            Debug.Log($"[Combat] {message}");
        }

        public static void LogWarning(string message)
        {
            Debug.LogWarning($"[Combat] {message}");
        }

        public static void LogError(string message)
        {
            Debug.LogError($"[Combat] {message}");
        }
    }
} 