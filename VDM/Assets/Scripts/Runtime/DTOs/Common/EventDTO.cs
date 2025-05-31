using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Core.Events
{
    /// <summary>
    /// Event priority levels for processing order
    /// </summary>
    public enum EventPriorityDTO
    {
        Background = 10,
        Low = 25,
        Normal = 50,
        High = 75,
        Critical = 100
    }

    /// <summary>
    /// System-level event types
    /// </summary>
    public enum SystemEventTypeDTO
    {
        Startup,
        Shutdown,
        Error,
        Warning,
        Info,
        ConfigChanged
    }

    /// <summary>
    /// Character-related event types
    /// </summary>
    public enum CharacterEventTypeDTO
    {
        Created,
        Updated,
        Deleted,
        Moved,
        Interacted,
        RelationshipChanged,
        LevelUp,
        SkillChanged
    }

    /// <summary>
    /// Memory-related event types
    /// </summary>
    public enum MemoryEventTypeDTO
    {
        Created,
        Reinforced,
        Deleted,
        Accessed,
        Modified,
        Recalled
    }

    /// <summary>
    /// Combat-related event types
    /// </summary>
    public enum CombatEventTypeDTO
    {
        Started,
        Ended,
        Attack,
        Defend,
        EffectApplied,
        EffectRemoved,
        Death
    }

    /// <summary>
    /// Time-related event types
    /// </summary>
    public enum TimeEventTypeDTO
    {
        Advanced,
        DayChanged,
        MonthChanged,
        YearChanged,
        SeasonChanged,
        ScheduledEvent
    }

    /// <summary>
    /// POI-related event types
    /// </summary>
    public enum POIEventTypeDTO
    {
        StateChanged,
        Created,
        Destroyed,
        Discovered,
        Modified,
        ControlChanged,
        InfluenceChanged,
        PopulationChanged
    }

    /// <summary>
    /// Population-related event types
    /// </summary>
    public enum PopulationEventTypeDTO
    {
        Changed,
        Birth,
        Death,
        Migration,
        StateChanged,
        Catastrophe,
        WarImpact,
        ResourceShortage,
        SeasonalEffect
    }

    /// <summary>
    /// Rumor-related event types
    /// </summary>
    public enum RumorEventTypeDTO
    {
        Spread,
        Created,
        Mutated,
        Verified,
        Debunked,
        Forgotten,
        Updated,
        Deleted
    }

    /// <summary>
    /// Motif-related event types
    /// </summary>
    public enum MotifEventTypeDTO
    {
        Changed,
        Activated,
        Deactivated,
        Reinforced
    }

    /// <summary>
    /// Inventory-related event types
    /// </summary>
    public enum InventoryEventTypeDTO
    {
        ItemAdded,
        ItemRemoved,
        ItemUsed,
        ItemEquipped,
        ItemUnequipped
    }

    /// <summary>
    /// Arc-related event types
    /// </summary>
    public enum ArcEventTypeDTO
    {
        Created,
        Activated,
        Deactivated,
        Completed,
        Failed,
        Stalled,
        Resumed,
        Cancelled,
        StepStarted,
        StepCompleted,
        StepFailed,
        StepSkipped,
        StepGenerated,
        ProgressionUpdated,
        NarrativeUpdated,
        StepsRegenerated,
        TagsUpdated,
        PriorityChanged,
        QuestGenerated,
        QuestCompleted,
        QuestFailed,
        QuestOpportunityCreated,
        QuestOpportunityExpired,
        NpcInteraction,
        FactionRelationshipChanged,
        RegionEvent,
        WorldStateImpact,
        MemoryRecorded,
        AnalyticsGenerated,
        PerformanceMeasured,
        BottleneckIdentified,
        SuccessPatternIdentified
    }

    /// <summary>
    /// Storage-related event types
    /// </summary>
    public enum StorageEventTypeDTO
    {
        Save,
        Load,
        Autosave,
        Checkpoint,
        Error
    }

    /// <summary>
    /// Base class for all events in the system
    /// </summary>
    [Serializable]
    public abstract class EventBaseDTO
    {
        public string EventId { get; set; } = Guid.NewGuid().ToString();

        public string EventType { get; set; } = string.Empty;

        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        public EventPriorityDTO Priority { get; set; } = EventPriorityDTO.Normal;

        public string? SourceSystem { get; set; }

        public string? CorrelationId { get; set; }

        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// System-level event
    /// </summary>
    [Serializable]
    public class SystemEventDTO : EventBaseDTO
    {
        public string SystemName { get; set; } = string.Empty;

        public SystemEventTypeDTO SystemEventType { get; set; } = SystemEventTypeDTO.Info;

        public Dictionary<string, object> EventData { get; set; } = new Dictionary<string, object>();

        public string? ErrorMessage { get; set; }

        public int? ErrorCode { get; set; }

        public string? StackTrace { get; set; }

        public string Severity { get; set; } = "info"; // "warning", "error", "critical"
    }

    /// <summary>
    /// Game-level event
    /// </summary>
    [Serializable]
    public class GameEventDTO : EventBaseDTO
    {
        public string GameId { get; set; } = string.Empty;

        public Dictionary<string, object> EventData { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Character-related event
    /// </summary>
    [Serializable]
    public class CharacterEventDTO : EventBaseDTO
    {
        public string CharacterId { get; set; } = string.Empty;

        public CharacterEventTypeDTO CharacterEventType { get; set; } = CharacterEventTypeDTO.Updated;

        public Dictionary<string, object>? OldValues { get; set; }

        public Dictionary<string, object>? NewValues { get; set; }

        public string? InteractionTargetId { get; set; }

        public string? InteractionType { get; set; }
    }

    /// <summary>
    /// Memory-related event
    /// </summary>
    [Serializable]
    public class MemoryEventDTO : EventBaseDTO
    {
        public string MemoryId { get; set; } = string.Empty;

        public string EntityId { get; set; } = string.Empty;

        public MemoryEventTypeDTO MemoryEventType { get; set; } = MemoryEventTypeDTO.Created;

        public string? MemoryContent { get; set; }

        public float? Importance { get; set; }

        public Dictionary<string, object>? Context { get; set; }
    }

    /// <summary>
    /// POI-related event
    /// </summary>
    [Serializable]
    public class POIEventDTO : EventBaseDTO
    {
        public string PoiId { get; set; } = string.Empty;

        public POIEventTypeDTO PoiEventType { get; set; } = POIEventTypeDTO.StateChanged;

        public string? OldState { get; set; }

        public string? NewState { get; set; }

        public List<string> AffectedEntities { get; set; } = new List<string>();

        public Dictionary<string, object> Changes { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Arc-related event
    /// </summary>
    [Serializable]
    public class ArcEventDTO : EventBaseDTO
    {
        public string ArcId { get; set; } = string.Empty;

        public ArcEventTypeDTO ArcEventType { get; set; } = ArcEventTypeDTO.Created;

        public string? StepId { get; set; }

        public string? QuestId { get; set; }

        public string? NpcId { get; set; }

        public string? FactionId { get; set; }

        public string? RegionId { get; set; }

        public string? NarrativeUpdate { get; set; }

        public Dictionary<string, object>? ProgressionData { get; set; }

        public Dictionary<string, object>? AnalyticsData { get; set; }
    }

    /// <summary>
    /// Event dispatcher command for publishing events
    /// </summary>
    [Serializable]
    public class PublishEventRequestDTO
    {
        public EventBaseDTO Event { get; set; } = new SystemEventDTO();

        public bool Async { get; set; } = false;

        public List<string>? MiddlewareFilters { get; set; }
    }

    /// <summary>
    /// Event subscription request
    /// </summary>
    [Serializable]
    public class EventSubscriptionRequestDTO
    {
        public List<string> EventTypes { get; set; } = new List<string>();

        public Dictionary<string, object>? Filters { get; set; }

        public string? CallbackUrl { get; set; }

        public string? WebhookSecret { get; set; }
    }

    /// <summary>
    /// Event history query request
    /// </summary>
    [Serializable]
    public class EventHistoryRequestDTO : PaginationRequestDTO
    {
        public List<string>? EventTypes { get; set; }

        public string? EntityId { get; set; }

        public DateTime? StartTime { get; set; }

        public DateTime? EndTime { get; set; }

        public EventPriorityDTO? MinPriority { get; set; }

        public string? SourceSystem { get; set; }
    }

    /// <summary>
    /// Event history response
    /// </summary>
    [Serializable]
    public class EventHistoryResponseDTO : PaginatedResponseDTO<EventBaseDTO>
    {
        public int TotalEvents { get; set; } = 0;

        public Dictionary<string, int> EventTypesSummary { get; set; } = new Dictionary<string, int>();

        public Dictionary<string, int> PrioritySummary { get; set; } = new Dictionary<string, int>();
    }
} 