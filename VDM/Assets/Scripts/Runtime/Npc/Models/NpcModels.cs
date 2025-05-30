using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.Npc.Models
{
    #region Core Enums
    
    /// <summary>
    /// NPC personality traits
    /// </summary>
    [Serializable]
    public enum PersonalityTrait
    {
        Friendly,
        Aggressive,
        Shy,
        Confident,
        Curious,
        Suspicious,
        Loyal,
        Treacherous,
        Wise,
        Naive,
        Humorous,
        Serious,
        Creative,
        Logical
    }
    
    /// <summary>
    /// NPC behavior types
    /// </summary>
    [Serializable]
    public enum BehaviorType
    {
        Passive,
        Aggressive,
        Defensive,
        Neutral,
        Helpful,
        Hostile,
        Merchant,
        Guard,
        Wanderer,
        Worker
    }
    
    /// <summary>
    /// NPC interaction styles
    /// </summary>
    [Serializable]
    public enum InteractionStyle
    {
        Formal,
        Casual,
        Friendly,
        Hostile,
        Professional,
        Mysterious,
        Enthusiastic,
        Reserved
    }
    
    /// <summary>
    /// Memory importance levels
    /// </summary>
    [Serializable]
    public enum MemoryImportance
    {
        Low = 1,
        Medium = 2,
        High = 3,
        Critical = 4
    }
    
    /// <summary>
    /// Memory types
    /// </summary>
    [Serializable]
    public enum MemoryType
    {
        Conversation,
        Event,
        Relationship,
        Quest,
        Item,
        Location,
        Personal,
        Rumor
    }
    
    /// <summary>
    /// NPC generation methods
    /// </summary>
    [Serializable]
    public enum GenerationMethod
    {
        Random,
        Template,
        Manual,
        AI,
        Procedural
    }
    
    #endregion
    
    #region Core Models
    
    /// <summary>
    /// Main NPC model representing a non-player character
    /// </summary>
    [Serializable]
    public class NpcModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("name")]
        public string Name { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("background")]
        public string Background { get; set; }
        
        [JsonProperty("appearance")]
        public NpcAppearanceModel Appearance { get; set; }
        
        [JsonProperty("personality")]
        public NpcPersonalityModel Personality { get; set; }
        
        [JsonProperty("stats")]
        public NpcStatsModel Stats { get; set; }
        
        [JsonProperty("behavior")]
        public NpcBehaviorModel Behavior { get; set; }
        
        [JsonProperty("dialogue")]
        public NpcDialogueModel Dialogue { get; set; }
        
        [JsonProperty("location")]
        public NpcLocationModel Location { get; set; }
        
        [JsonProperty("relationships")]
        public Dictionary<string, float> Relationships { get; set; }
        
        [JsonProperty("memories")]
        public List<NpcMemoryModel> Memories { get; set; }
        
        [JsonProperty("skills")]
        public Dictionary<string, int> Skills { get; set; }
        
        [JsonProperty("inventory")]
        public List<string> Inventory { get; set; }
        
        [JsonProperty("quests")]
        public List<string> QuestIds { get; set; }
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
        
        [JsonProperty("is_active")]
        public bool IsActive { get; set; }
        
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; }
        
        [JsonProperty("updated_at")]
        public DateTime UpdatedAt { get; set; }
        
        [JsonProperty("version")]
        public int Version { get; set; }
        
        public NpcModel()
        {
            Appearance = new NpcAppearanceModel();
            Personality = new NpcPersonalityModel();
            Stats = new NpcStatsModel();
            Behavior = new NpcBehaviorModel();
            Dialogue = new NpcDialogueModel();
            Location = new NpcLocationModel();
            Relationships = new Dictionary<string, float>();
            Memories = new List<NpcMemoryModel>();
            Skills = new Dictionary<string, int>();
            Inventory = new List<string>();
            QuestIds = new List<string>();
            Tags = new List<string>();
            Metadata = new Dictionary<string, object>();
            IsActive = true;
            CreatedAt = DateTime.UtcNow;
            UpdatedAt = DateTime.UtcNow;
            Version = 1;
        }
    }
    
    /// <summary>
    /// NPC appearance configuration
    /// </summary>
    [Serializable]
    public class NpcAppearanceModel
    {
        [JsonProperty("gender")]
        public string Gender { get; set; }
        
        [JsonProperty("age")]
        public int Age { get; set; }
        
        [JsonProperty("height")]
        public string Height { get; set; }
        
        [JsonProperty("build")]
        public string Build { get; set; }
        
        [JsonProperty("hair_color")]
        public string HairColor { get; set; }
        
        [JsonProperty("hair_style")]
        public string HairStyle { get; set; }
        
        [JsonProperty("eye_color")]
        public string EyeColor { get; set; }
        
        [JsonProperty("skin_tone")]
        public string SkinTone { get; set; }
        
        [JsonProperty("clothing")]
        public string Clothing { get; set; }
        
        [JsonProperty("accessories")]
        public List<string> Accessories { get; set; }
        
        [JsonProperty("distinctive_features")]
        public List<string> DistinctiveFeatures { get; set; }
        
        [JsonProperty("avatar_url")]
        public string AvatarUrl { get; set; }
        
        [JsonProperty("model_path")]
        public string ModelPath { get; set; }
        
        public NpcAppearanceModel()
        {
            Accessories = new List<string>();
            DistinctiveFeatures = new List<string>();
        }
    }
    
    /// <summary>
    /// NPC personality traits and characteristics
    /// </summary>
    [Serializable]
    public class NpcPersonalityModel
    {
        [JsonProperty("traits")]
        public List<PersonalityTrait> Traits { get; set; }
        
        [JsonProperty("values")]
        public List<string> Values { get; set; }
        
        [JsonProperty("fears")]
        public List<string> Fears { get; set; }
        
        [JsonProperty("goals")]
        public List<string> Goals { get; set; }
        
        [JsonProperty("likes")]
        public List<string> Likes { get; set; }
        
        [JsonProperty("dislikes")]
        public List<string> Dislikes { get; set; }
        
        [JsonProperty("mannerisms")]
        public List<string> Mannerisms { get; set; }
        
        [JsonProperty("speech_patterns")]
        public List<string> SpeechPatterns { get; set; }
        
        [JsonProperty("emotional_state")]
        public string EmotionalState { get; set; }
        
        [JsonProperty("mood")]
        public float Mood { get; set; } // -1.0 to 1.0
        
        [JsonProperty("openness")]
        public float Openness { get; set; } // 0.0 to 1.0
        
        [JsonProperty("conscientiousness")]
        public float Conscientiousness { get; set; } // 0.0 to 1.0
        
        [JsonProperty("extraversion")]
        public float Extraversion { get; set; } // 0.0 to 1.0
        
        [JsonProperty("agreeableness")]
        public float Agreeableness { get; set; } // 0.0 to 1.0
        
        [JsonProperty("neuroticism")]
        public float Neuroticism { get; set; } // 0.0 to 1.0
        
        public NpcPersonalityModel()
        {
            Traits = new List<PersonalityTrait>();
            Values = new List<string>();
            Fears = new List<string>();
            Goals = new List<string>();
            Likes = new List<string>();
            Dislikes = new List<string>();
            Mannerisms = new List<string>();
            SpeechPatterns = new List<string>();
            EmotionalState = "neutral";
            Mood = 0.0f;
            Openness = 0.5f;
            Conscientiousness = 0.5f;
            Extraversion = 0.5f;
            Agreeableness = 0.5f;
            Neuroticism = 0.5f;
        }
    }
    
    /// <summary>
    /// NPC statistical attributes
    /// </summary>
    [Serializable]
    public class NpcStatsModel
    {
        [JsonProperty("level")]
        public int Level { get; set; }
        
        [JsonProperty("health")]
        public int Health { get; set; }
        
        [JsonProperty("max_health")]
        public int MaxHealth { get; set; }
        
        [JsonProperty("strength")]
        public int Strength { get; set; }
        
        [JsonProperty("dexterity")]
        public int Dexterity { get; set; }
        
        [JsonProperty("intelligence")]
        public int Intelligence { get; set; }
        
        [JsonProperty("wisdom")]
        public int Wisdom { get; set; }
        
        [JsonProperty("charisma")]
        public int Charisma { get; set; }
        
        [JsonProperty("constitution")]
        public int Constitution { get; set; }
        
        [JsonProperty("luck")]
        public int Luck { get; set; }
        
        [JsonProperty("combat_level")]
        public int CombatLevel { get; set; }
        
        [JsonProperty("social_level")]
        public int SocialLevel { get; set; }
        
        [JsonProperty("custom_stats")]
        public Dictionary<string, int> CustomStats { get; set; }
        
        public NpcStatsModel()
        {
            Level = 1;
            Health = 100;
            MaxHealth = 100;
            Strength = 10;
            Dexterity = 10;
            Intelligence = 10;
            Wisdom = 10;
            Charisma = 10;
            Constitution = 10;
            Luck = 10;
            CombatLevel = 1;
            SocialLevel = 1;
            CustomStats = new Dictionary<string, int>();
        }
    }
    
    /// <summary>
    /// NPC behavior configuration
    /// </summary>
    [Serializable]
    public class NpcBehaviorModel
    {
        [JsonProperty("behavior_type")]
        public BehaviorType BehaviorType { get; set; }
        
        [JsonProperty("interaction_style")]
        public InteractionStyle InteractionStyle { get; set; }
        
        [JsonProperty("aggression")]
        public float Aggression { get; set; } // 0.0 to 1.0
        
        [JsonProperty("friendliness")]
        public float Friendliness { get; set; } // 0.0 to 1.0
        
        [JsonProperty("trust")]
        public float Trust { get; set; } // 0.0 to 1.0
        
        [JsonProperty("honesty")]
        public float Honesty { get; set; } // 0.0 to 1.0
        
        [JsonProperty("courage")]
        public float Courage { get; set; } // 0.0 to 1.0
        
        [JsonProperty("loyalty")]
        public float Loyalty { get; set; } // 0.0 to 1.0
        
        [JsonProperty("movement_pattern")]
        public string MovementPattern { get; set; }
        
        [JsonProperty("patrol_route")]
        public List<Vector3> PatrolRoute { get; set; }
        
        [JsonProperty("idle_animations")]
        public List<string> IdleAnimations { get; set; }
        
        [JsonProperty("combat_behavior")]
        public string CombatBehavior { get; set; }
        
        [JsonProperty("flee_threshold")]
        public float FleeThreshold { get; set; } // 0.0 to 1.0
        
        [JsonProperty("response_time")]
        public float ResponseTime { get; set; }
        
        [JsonProperty("decision_factors")]
        public Dictionary<string, float> DecisionFactors { get; set; }
        
        public NpcBehaviorModel()
        {
            BehaviorType = BehaviorType.Neutral;
            InteractionStyle = InteractionStyle.Casual;
            Aggression = 0.3f;
            Friendliness = 0.5f;
            Trust = 0.5f;
            Honesty = 0.7f;
            Courage = 0.5f;
            Loyalty = 0.5f;
            MovementPattern = "stationary";
            PatrolRoute = new List<Vector3>();
            IdleAnimations = new List<string>();
            CombatBehavior = "defensive";
            FleeThreshold = 0.2f;
            ResponseTime = 1.0f;
            DecisionFactors = new Dictionary<string, float>();
        }
    }
    
    /// <summary>
    /// NPC dialogue configuration
    /// </summary>
    [Serializable]
    public class NpcDialogueModel
    {
        [JsonProperty("default_greeting")]
        public string DefaultGreeting { get; set; }
        
        [JsonProperty("default_farewell")]
        public string DefaultFarewell { get; set; }
        
        [JsonProperty("conversation_starters")]
        public List<string> ConversationStarters { get; set; }
        
        [JsonProperty("topics")]
        public Dictionary<string, List<string>> Topics { get; set; }
        
        [JsonProperty("dialogue_trees")]
        public List<string> DialogueTreeIds { get; set; }
        
        [JsonProperty("voice_settings")]
        public Dictionary<string, object> VoiceSettings { get; set; }
        
        [JsonProperty("language")]
        public string Language { get; set; }
        
        [JsonProperty("accent")]
        public string Accent { get; set; }
        
        [JsonProperty("speech_speed")]
        public float SpeechSpeed { get; set; } // 0.5 to 2.0
        
        [JsonProperty("speech_pitch")]
        public float SpeechPitch { get; set; } // 0.5 to 2.0
        
        [JsonProperty("vocabulary_complexity")]
        public float VocabularyComplexity { get; set; } // 0.0 to 1.0
        
        [JsonProperty("formality_level")]
        public float FormalityLevel { get; set; } // 0.0 to 1.0
        
        [JsonProperty("emotional_expressiveness")]
        public float EmotionalExpressiveness { get; set; } // 0.0 to 1.0
        
        public NpcDialogueModel()
        {
            DefaultGreeting = "Hello there!";
            DefaultFarewell = "Goodbye!";
            ConversationStarters = new List<string>();
            Topics = new Dictionary<string, List<string>>();
            DialogueTreeIds = new List<string>();
            VoiceSettings = new Dictionary<string, object>();
            Language = "en";
            Accent = "neutral";
            SpeechSpeed = 1.0f;
            SpeechPitch = 1.0f;
            VocabularyComplexity = 0.5f;
            FormalityLevel = 0.5f;
            EmotionalExpressiveness = 0.5f;
        }
    }
    
    /// <summary>
    /// NPC location and positioning data
    /// </summary>
    [Serializable]
    public class NpcLocationModel
    {
        [JsonProperty("current_position")]
        public Vector3 CurrentPosition { get; set; }
        
        [JsonProperty("home_position")]
        public Vector3 HomePosition { get; set; }
        
        [JsonProperty("work_position")]
        public Vector3 WorkPosition { get; set; }
        
        [JsonProperty("region_id")]
        public string RegionId { get; set; }
        
        [JsonProperty("area_id")]
        public string AreaId { get; set; }
        
        [JsonProperty("building_id")]
        public string BuildingId { get; set; }
        
        [JsonProperty("room_id")]
        public string RoomId { get; set; }
        
        [JsonProperty("spawn_points")]
        public List<Vector3> SpawnPoints { get; set; }
        
        [JsonProperty("restricted_areas")]
        public List<string> RestrictedAreas { get; set; }
        
        [JsonProperty("movement_speed")]
        public float MovementSpeed { get; set; }
        
        [JsonProperty("rotation")]
        public Vector3 Rotation { get; set; }
        
        [JsonProperty("last_known_position")]
        public Vector3 LastKnownPosition { get; set; }
        
        [JsonProperty("position_history")]
        public List<Vector3> PositionHistory { get; set; }
        
        public NpcLocationModel()
        {
            CurrentPosition = Vector3.zero;
            HomePosition = Vector3.zero;
            WorkPosition = Vector3.zero;
            SpawnPoints = new List<Vector3>();
            RestrictedAreas = new List<string>();
            MovementSpeed = 1.0f;
            Rotation = Vector3.zero;
            LastKnownPosition = Vector3.zero;
            PositionHistory = new List<Vector3>();
        }
    }
    
    /// <summary>
    /// NPC memory entry
    /// </summary>
    [Serializable]
    public class NpcMemoryModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("npc_id")]
        public string NpcId { get; set; }
        
        [JsonProperty("content")]
        public string Content { get; set; }
        
        [JsonProperty("memory_type")]
        public MemoryType MemoryType { get; set; }
        
        [JsonProperty("importance")]
        public MemoryImportance Importance { get; set; }
        
        [JsonProperty("emotional_impact")]
        public float EmotionalImpact { get; set; } // -1.0 to 1.0
        
        [JsonProperty("related_character_id")]
        public string RelatedCharacterId { get; set; }
        
        [JsonProperty("related_location")]
        public string RelatedLocation { get; set; }
        
        [JsonProperty("related_quest_id")]
        public string RelatedQuestId { get; set; }
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
        
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; }
        
        [JsonProperty("last_accessed")]
        public DateTime LastAccessed { get; set; }
        
        [JsonProperty("access_count")]
        public int AccessCount { get; set; }
        
        [JsonProperty("decay_rate")]
        public float DecayRate { get; set; } // 0.0 to 1.0
        
        [JsonProperty("is_active")]
        public bool IsActive { get; set; }
        
        public NpcMemoryModel()
        {
            Id = Guid.NewGuid().ToString();
            Tags = new List<string>();
            Metadata = new Dictionary<string, object>();
            CreatedAt = DateTime.UtcNow;
            LastAccessed = DateTime.UtcNow;
            AccessCount = 0;
            DecayRate = 0.01f;
            IsActive = true;
        }
    }
    
    #endregion
    
    #region Request/Response DTOs
    
    /// <summary>
    /// Request to create a new NPC
    /// </summary>
    [Serializable]
    public class CreateNpcRequest
    {
        [JsonProperty("name")]
        public string Name { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("template_id")]
        public string TemplateId { get; set; }
        
        [JsonProperty("generation_method")]
        public GenerationMethod GenerationMethod { get; set; }
        
        [JsonProperty("parameters")]
        public Dictionary<string, object> Parameters { get; set; }
        
        [JsonProperty("location")]
        public NpcLocationModel Location { get; set; }
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; }
        
        public CreateNpcRequest()
        {
            GenerationMethod = GenerationMethod.Random;
            Parameters = new Dictionary<string, object>();
            Tags = new List<string>();
        }
    }
    
    /// <summary>
    /// Request to update an existing NPC
    /// </summary>
    [Serializable]
    public class UpdateNpcRequest
    {
        [JsonProperty("name")]
        public string Name { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("background")]
        public string Background { get; set; }
        
        [JsonProperty("appearance")]
        public NpcAppearanceModel Appearance { get; set; }
        
        [JsonProperty("personality")]
        public NpcPersonalityModel Personality { get; set; }
        
        [JsonProperty("behavior")]
        public NpcBehaviorModel Behavior { get; set; }
        
        [JsonProperty("dialogue")]
        public NpcDialogueModel Dialogue { get; set; }
        
        [JsonProperty("location")]
        public NpcLocationModel Location { get; set; }
        
        [JsonProperty("skills")]
        public Dictionary<string, int> Skills { get; set; }
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
        
        [JsonProperty("is_active")]
        public bool? IsActive { get; set; }
    }
    
    /// <summary>
    /// Request to add memory to an NPC
    /// </summary>
    [Serializable]
    public class AddNpcMemoryRequest
    {
        [JsonProperty("content")]
        public string Content { get; set; }
        
        [JsonProperty("memory_type")]
        public MemoryType MemoryType { get; set; }
        
        [JsonProperty("importance")]
        public MemoryImportance Importance { get; set; }
        
        [JsonProperty("emotional_impact")]
        public float EmotionalImpact { get; set; }
        
        [JsonProperty("related_character_id")]
        public string RelatedCharacterId { get; set; }
        
        [JsonProperty("related_location")]
        public string RelatedLocation { get; set; }
        
        [JsonProperty("related_quest_id")]
        public string RelatedQuestId { get; set; }
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
        
        public AddNpcMemoryRequest()
        {
            MemoryType = MemoryType.Personal;
            Importance = MemoryImportance.Medium;
            EmotionalImpact = 0.0f;
            Tags = new List<string>();
            Metadata = new Dictionary<string, object>();
        }
    }
    
    /// <summary>
    /// Request to add rumor to an NPC's knowledge
    /// </summary>
    [Serializable]
    public class AddNpcRumorRequest
    {
        [JsonProperty("content")]
        public string Content { get; set; }
        
        [JsonProperty("source")]
        public string Source { get; set; }
        
        [JsonProperty("reliability")]
        public float Reliability { get; set; } // 0.0 to 1.0
        
        [JsonProperty("spread_chance")]
        public float SpreadChance { get; set; } // 0.0 to 1.0
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
        
        public AddNpcRumorRequest()
        {
            Reliability = 0.5f;
            SpreadChance = 0.3f;
            Tags = new List<string>();
            Metadata = new Dictionary<string, object>();
        }
    }
    
    /// <summary>
    /// Response containing NPC list with pagination
    /// </summary>
    [Serializable]
    public class NpcListResponse
    {
        [JsonProperty("npcs")]
        public List<NpcModel> Npcs { get; set; }
        
        [JsonProperty("total_count")]
        public int TotalCount { get; set; }
        
        [JsonProperty("page")]
        public int Page { get; set; }
        
        [JsonProperty("page_size")]
        public int PageSize { get; set; }
        
        [JsonProperty("total_pages")]
        public int TotalPages { get; set; }
        
        public NpcListResponse()
        {
            Npcs = new List<NpcModel>();
        }
    }
    
    /// <summary>
    /// Response containing NPC memories with pagination
    /// </summary>
    [Serializable]
    public class NpcMemoryResponse
    {
        [JsonProperty("memories")]
        public List<NpcMemoryModel> Memories { get; set; }
        
        [JsonProperty("total_count")]
        public int TotalCount { get; set; }
        
        [JsonProperty("page")]
        public int Page { get; set; }
        
        [JsonProperty("page_size")]
        public int PageSize { get; set; }
        
        [JsonProperty("total_pages")]
        public int TotalPages { get; set; }
        
        public NpcMemoryResponse()
        {
            Memories = new List<NpcMemoryModel>();
        }
    }
    
    #endregion
    
    #region Analytics and Statistics
    
    /// <summary>
    /// NPC analytics and statistics
    /// </summary>
    [Serializable]
    public class NpcAnalyticsModel
    {
        [JsonProperty("npc_id")]
        public string NpcId { get; set; }
        
        [JsonProperty("total_interactions")]
        public int TotalInteractions { get; set; }
        
        [JsonProperty("total_conversations")]
        public int TotalConversations { get; set; }
        
        [JsonProperty("average_conversation_length")]
        public float AverageConversationLength { get; set; }
        
        [JsonProperty("relationship_changes")]
        public Dictionary<string, float> RelationshipChanges { get; set; }
        
        [JsonProperty("memory_count")]
        public int MemoryCount { get; set; }
        
        [JsonProperty("memory_by_type")]
        public Dictionary<MemoryType, int> MemoryByType { get; set; }
        
        [JsonProperty("quest_involvement")]
        public List<string> QuestInvolvement { get; set; }
        
        [JsonProperty("location_visits")]
        public Dictionary<string, int> LocationVisits { get; set; }
        
        [JsonProperty("personality_drift")]
        public Dictionary<string, float> PersonalityDrift { get; set; }
        
        [JsonProperty("interaction_patterns")]
        public Dictionary<string, object> InteractionPatterns { get; set; }
        
        [JsonProperty("generated_at")]
        public DateTime GeneratedAt { get; set; }
        
        public NpcAnalyticsModel()
        {
            RelationshipChanges = new Dictionary<string, float>();
            MemoryByType = new Dictionary<MemoryType, int>();
            QuestInvolvement = new List<string>();
            LocationVisits = new Dictionary<string, int>();
            PersonalityDrift = new Dictionary<string, float>();
            InteractionPatterns = new Dictionary<string, object>();
            GeneratedAt = DateTime.UtcNow;
        }
    }
    
    #endregion
} 