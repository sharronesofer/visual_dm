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

    /// <summary>
    /// Event data for relationship state changes (rival/nemesis system).
    /// Fired when an NPC's relationship with another changes state (e.g., neutral → rival, rival → nemesis).
    /// </summary>
    public record RelationshipStateChangedEvent(
        string NPCId,
        string TargetId,
        VisualDM.NPC.RelationshipState OldState,
        VisualDM.NPC.RelationshipState NewState,
        float Intensity,
        DateTime Timestamp
    );

    /// <summary>
    /// Event data for relationship-impacting game events (combat, quest, dialogue, etc.).
    /// Used to trigger relationship state machine updates.
    /// </summary>
    public record RelationshipEventTrigger(
        string NPCId,
        string TargetId,
        string EventType,
        float EventScore,
        string Context,
        DateTime Timestamp
    );

    /// <summary>
    /// Event data for grudge level changes (grudge point system).
    /// Fired when a grudge threshold is crossed for a player-NPC pair.
    /// </summary>
    public record GrudgeLevelChangedEvent(
        string SourceNpcId,
        string TargetNpcId,
        string OldLevel,
        string NewLevel,
        int TotalPoints,
        DateTime Timestamp
    );
}