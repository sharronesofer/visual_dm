using System;

namespace VisualDM.Systems.EventSystem
{
    /// <summary>
    /// Event data for when a player acquires a new feat or progresses in a feat.
    /// </summary>
    public record FeatProgressionEvent(
        string CharacterId,
        string FeatId,
        int NewLevel,
        DateTime Timestamp
    );

    /// <summary>
    /// Event data for UI notifications (e.g., system messages, alerts).
    /// </summary>
    public record UINotificationEvent(
        string Message,
        string Level, // e.g., "info", "warning", "error"
        DateTime Timestamp
    );

    /// <summary>
    /// Event data for game state changes (e.g., state transitions, key variable changes).
    /// </summary>
    public record GameStateChangedEvent(
        string StateKey,
        object NewValue,
        object OldValue,
        DateTime Timestamp
    );
} 