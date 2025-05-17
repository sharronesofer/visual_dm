using System;
using System.Threading.Tasks;
using VisualDM.Systems.EventSystem;

namespace VisualDM.MotifSystem
{
    /// <summary>
    /// Central dispatcher for motif lifecycle events. Supports sync/async publish and event logging.
    /// </summary>
    public static class MotifEventDispatcher
    {
        public static event Action<MotifEventBase> OnStateChanged;
        public static event Action<MotifEventBase> OnTriggered;

        public static void PublishStateChanged(MotifStateChangedEvent evt)
        {
            try
            {
                EventBus.Instance.Publish(evt);
                LogEvent(evt);
                OnStateChanged?.Invoke(evt);
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifEventDispatcher.PublishStateChanged failed", "MotifEventDispatcher.PublishStateChanged");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
        }

        public static async Task PublishStateChangedAsync(MotifStateChangedEvent evt)
        {
            try
            {
                await EventBus.Instance.PublishAsync(evt);
                LogEvent(evt);
                OnStateChanged?.Invoke(evt);
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifEventDispatcher.PublishStateChangedAsync failed", "MotifEventDispatcher.PublishStateChangedAsync");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
        }

        public static void PublishTriggered(MotifTriggeredEvent evt)
        {
            try
            {
                EventBus.Instance.Publish(evt);
                LogEvent(evt);
                OnTriggered?.Invoke(evt);
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifEventDispatcher.PublishTriggered failed", "MotifEventDispatcher.PublishTriggered");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
        }

        public static async Task PublishTriggeredAsync(MotifTriggeredEvent evt)
        {
            try
            {
                await EventBus.Instance.PublishAsync(evt);
                LogEvent(evt);
                OnTriggered?.Invoke(evt);
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifEventDispatcher.PublishTriggeredAsync failed", "MotifEventDispatcher.PublishTriggeredAsync");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
        }

        private static void LogEvent(object evt)
        {
            // TODO: Replace with a more robust audit/logging system if needed
            UnityEngine.Debug.Log($"[MotifEvent] {evt}");
        }
    }
} 
} 