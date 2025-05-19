using UnityEngine;

namespace VisualDM.UI
{
    public class HapticSystemsModule : MonoBehaviour, ISystemsModule
    {
        public void TriggerSystems(ActionType type, int importance, Vector2 position, SystemsContext context = null)
        {
            var config = SystemsManager.Instance?.config;
            if (config != null && (!config.HapticEnabled || !config.AllowVibration)) return;
            // Only vibrate on supported platforms (mobile)
#if UNITY_ANDROID || UNITY_IOS
            int durationMs = Mathf.Clamp(50 + importance * 25, 50, 500); // Scale duration by importance
            TriggerMobileVibration(durationMs);
#else
            // No-op for unsupported platforms
#endif
        }

#if UNITY_ANDROID || UNITY_IOS
        private void TriggerMobileVibration(int durationMs)
        {
#if UNITY_ANDROID
            using (var unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            {
                var currentActivity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity");
                var vibrator = currentActivity.Call<AndroidJavaObject>("getSystemService", "vibrator");
                if (vibrator != null)
                {
                    vibrator.Call("vibrate", (long)durationMs);
                }
            }
#elif UNITY_IOS
            Handheld.Vibrate(); // iOS only supports default vibration
#endif
        }
#endif
    }
}