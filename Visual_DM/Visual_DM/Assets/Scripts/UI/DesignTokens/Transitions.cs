using UnityEngine;

namespace VisualDM.UI.DesignTokens
{
    public static class Transitions
    {
        // Durations (in seconds)
        public const float Short = 0.1f;
        public const float Regular = 0.2f;
        public const float Long = 0.4f;

        // Easing curves (can be assigned at runtime or use built-in AnimationCurve presets)
        public static AnimationCurve EaseIn = AnimationCurve.EaseInOut(0, 0, 1, 1);
        public static AnimationCurve EaseOut = AnimationCurve.EaseInOut(0, 0, 1, 1);
        public static AnimationCurve EaseInOut = AnimationCurve.EaseInOut(0, 0, 1, 1);

        // Usage:
        // - Use Short/Regular/Long for animation durations
        // - Use EaseIn/EaseOut/EaseInOut for UI transitions
    }
} 