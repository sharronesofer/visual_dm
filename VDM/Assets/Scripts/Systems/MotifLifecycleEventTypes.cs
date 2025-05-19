using System;
using System.Collections.Generic;

namespace VisualDM.Systems.MotifSystem
{
    /// <summary>
    /// Event data for motif state changes.
    /// </summary>
    public record MotifStateChangedEvent(
        Motif Motif,
        MotifLifecycleState OldState,
        MotifLifecycleState NewState,
        string Actor,
        string Context,
        DateTime Timestamp
    );

    /// <summary>
    /// Event data for motif trigger execution.
    /// </summary>
    public record MotifTriggeredEvent(
        Motif Motif,
        string TriggerType,
        string Actor,
        string Context,
        DateTime Timestamp
    );

    public static class MotifLifecycleEventTypes
    {
        private static readonly List<string> AllTypes = new();

        public static void RegisterEventType(string eventType)
        {
            try
            {
                if (string.IsNullOrEmpty(eventType)) return;
                if (!AllTypes.Contains(eventType))
                    AllTypes.Add(eventType);
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifLifecycleEventTypes.RegisterEventType failed", "MotifLifecycleEventTypes.RegisterEventType");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
            }
        }
    }
}