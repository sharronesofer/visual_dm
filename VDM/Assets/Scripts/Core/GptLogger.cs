using UnityEngine;

namespace VisualDM.Core
{
    public class GptLogger
    {
        public enum VerbosityLevel { Error, Warning, Info, Debug }
        public VerbosityLevel Level { get; set; } = VerbosityLevel.Info;

        public void LogInfo(string message)
        {
            if (Level >= VerbosityLevel.Info)
                Debug.Log($"[GPT][INFO] {message}");
        }

        public void LogWarning(string message)
        {
            if (Level >= VerbosityLevel.Warning)
                Debug.LogWarning($"[GPT][WARN] {message}");
        }

        public void LogError(string message)
        {
            if (Level >= VerbosityLevel.Error)
                Debug.LogError($"[GPT][ERROR] {message}");
        }

        public void LogDebug(string message)
        {
            if (Level >= VerbosityLevel.Debug)
                Debug.Log($"[GPT][DEBUG] {message}");
        }
    }
} 