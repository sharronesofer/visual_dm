using UnityEngine;

namespace VisualDM.UI
{
    /// <summary>
    /// Provides haptic feedback for gestures on supported devices.
    /// </summary>
    public static class HapticSystemsService
    {
        public static void TriggerSystems()
        {
#if UNITY_ANDROID || UNITY_IOS
            Handheld.Vibrate();
#endif
        }
    }
} 