namespace VDM.Runtime.Events.Models
{
    /// <summary>
    /// Centralized event type constants aligned with backend event system.
    /// Provides consistent event type identifiers across frontend and backend.
    /// </summary>
    public static class EventTypes
    {
        // System Events
        public const string SystemInitialized = "system.initialized";
        public const string SystemShutdown = "system.shutdown";
        public const string GameStarted = "game.started";
        public const string GameStopped = "game.stopped";
        public const string GameSaved = "game.saved";
        public const string GameLoaded = "game.loaded";
        
        // Character Events
        public const string CharacterCreated = "character.created";
        public const string CharacterUpdated = "character.updated";
        public const string CharacterDeleted = "character.deleted";
        public const string CharacterLeveledUp = "character.leveled_up";
        
        // Combat Events
        public const string CombatStarted = "combat.started";
        public const string CombatEnded = "combat.ended";
        public const string CombatTurnStarted = "combat.turn_started";
        public const string CombatTurnEnded = "combat.turn_ended";
        
        // Quest Events
        public const string QuestCreated = "quest.created";
        public const string QuestUpdated = "quest.updated";
        public const string QuestCompleted = "quest.completed";
        public const string QuestFailed = "quest.failed";
        
        // Faction Events
        public const string FactionCreated = "faction.created";
        public const string FactionUpdated = "faction.updated";
        public const string FactionRelationshipChanged = "faction.relationship_changed";
        
        // NPC Events
        public const string NpcCreated = "npc.created";
        public const string NpcUpdated = "npc.updated";
        public const string NpcDeleted = "npc.deleted";
        public const string NpcInteraction = "npc.interaction";
        
        // Dialogue Events
        public const string DialogueStarted = "dialogue.started";
        public const string DialogueEnded = "dialogue.ended";
        public const string DialogueMessageSent = "dialogue.message_sent";
        
        // Time Events
        public const string TimeAdvanced = "time.advanced";
        public const string TimeScaleChanged = "time.scale_changed";
        
        // World Events
        public const string WorldGenerated = "world.generated";
        public const string WorldStateChanged = "world.state_changed";
        public const string RegionUpdated = "region.updated";
        
        // Data Events
        public const string DataLoaded = "data.loaded";
        public const string DataSaved = "data.saved";
        public const string DataValidated = "data.validated";
        public const string DataError = "data.error";
        
        // UI Events
        public const string UiPanelOpened = "ui.panel_opened";
        public const string UiPanelClosed = "ui.panel_closed";
        public const string UiButtonClicked = "ui.button_clicked";
        public const string UiInputChanged = "ui.input_changed";
        
        // Memory Events
        public const string MemoryCreated = "memory.created";
        public const string MemoryUpdated = "memory.updated";
        public const string MemoryDecayed = "memory.decayed";
        
        // Custom Events
        public const string Custom = "custom";
    }
} 