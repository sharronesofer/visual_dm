using UnityEngine;

namespace VisualDM.AI
{
    /// <summary>
    /// ScriptableObject for configuring default rumor transformation parameters.
    /// </summary>
    [CreateAssetMenu(fileName = "RumorTransformationConfig", menuName = "AI/Rumor Transformation Config")]
    public class RumorTransformationConfig : ScriptableObject
    {
        [Range(0f, 1f)] public float DefaultDistortionLevel = 0.3f;
        public string DefaultTheme = "general";
        public string DefaultNpcPersonality = "neutral";
        public int DefaultRetellingCount = 1;
        public float DefaultTimeSinceEvent = 0f;
        [Header("Monitoring & Logging")]
        public bool EnableDebugLogs = true;
        public string DashboardEndpoint = ""; // For future dashboard integration
        // Add more fields as needed for designer tuning
    }
}