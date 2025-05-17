using UnityEngine;

namespace VisualDM.UI.Navigation
{
    /// <summary>
    /// Provides haptic feedback for gestures on supported devices.
    /// </summary>
    public static class HapticFeedbackService
    {
        public static void TriggerFeedback()
        {
#if UNITY_ANDROID || UNITY_IOS
            Handheld.Vibrate();
#endif
        }
    }
} 