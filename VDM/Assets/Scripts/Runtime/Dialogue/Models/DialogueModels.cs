using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.Dialogue.Models
{
    /// <summary>
    /// Represents a conversation entry in a dialogue history
    /// </summary>
    [Serializable]
    public class ConversationEntryModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("conversation_id")]
        public string ConversationId { get; set; }
        
        [JsonProperty("speaker")]
        public string Speaker { get; set; }
        
        [JsonProperty("message")]
        public string Message { get; set; }
        
        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; }
        
        [JsonProperty("type")]
        public string Type { get; set; } = "dialogue";
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("is_player")]
        public bool IsPlayer { get; set; }
        
        [JsonProperty("emotion")]
        public string Emotion { get; set; }
        
        [JsonProperty("tone")]
        public string Tone { get; set; }
    }
    
    /// <summary>
    /// Represents a complete conversation session
    /// </summary>
    [Serializable]
    public class ConversationModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("participants")]
        public Dictionary<string, string> Participants { get; set; } = new Dictionary<string, string>();
        
        [JsonProperty("location_id")]
        public string LocationId { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("active")]
        public bool Active { get; set; }
        
        [JsonProperty("message_count")]
        public int MessageCount { get; set; }
        
        [JsonProperty("started_at")]
        public DateTime StartedAt { get; set; }
        
        [JsonProperty("ended_at")]
        public DateTime? EndedAt { get; set; }
        
        [JsonProperty("messages")]
        public List<ConversationEntryModel> Messages { get; set; } = new List<ConversationEntryModel>();
        
        [JsonProperty("current_speaker")]
        public string CurrentSpeaker { get; set; }
        
        [JsonProperty("context")]
        public ConversationContextModel Context { get; set; } = new ConversationContextModel();
    }
    
    /// <summary>
    /// Represents conversation context and state
    /// </summary>
    [Serializable]
    public class ConversationContextModel
    {
        [JsonProperty("topic")]
        public string Topic { get; set; }
        
        [JsonProperty("mood")]
        public string Mood { get; set; }
        
        [JsonProperty("relationship_level")]
        public float RelationshipLevel { get; set; }
        
        [JsonProperty("history_summary")]
        public string HistorySummary { get; set; }
        
        [JsonProperty("key_points")]
        public List<string> KeyPoints { get; set; } = new List<string>();
        
        [JsonProperty("flags")]
        public Dictionary<string, bool> Flags { get; set; } = new Dictionary<string, bool>();
        
        [JsonProperty("variables")]
        public Dictionary<string, object> Variables { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Represents a dialogue choice/option available to the player
    /// </summary>
    [Serializable]
    public class DialogueOptionModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("text")]
        public string Text { get; set; }
        
        [JsonProperty("condition")]
        public string Condition { get; set; }
        
        [JsonProperty("consequence")]
        public string Consequence { get; set; }
        
        [JsonProperty("emotion")]
        public string Emotion { get; set; }
        
        [JsonProperty("skill_check")]
        public SkillCheckModel SkillCheck { get; set; }
        
        [JsonProperty("relationship_change")]
        public float RelationshipChange { get; set; }
        
        [JsonProperty("available")]
        public bool Available { get; set; } = true;
        
        [JsonProperty("used")]
        public bool Used { get; set; } = false;
        
        [JsonProperty("priority")]
        public int Priority { get; set; } = 0;
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();
    }
    
    /// <summary>
    /// Represents a skill check requirement for dialogue options
    /// </summary>
    [Serializable]
    public class SkillCheckModel
    {
        [JsonProperty("skill")]
        public string Skill { get; set; }
        
        [JsonProperty("difficulty")]
        public int Difficulty { get; set; }
        
        [JsonProperty("success_text")]
        public string SuccessText { get; set; }
        
        [JsonProperty("failure_text")]
        public string FailureText { get; set; }
        
        [JsonProperty("alternative_options")]
        public List<DialogueOptionModel> AlternativeOptions { get; set; } = new List<DialogueOptionModel>();
    }
    
    /// <summary>
    /// Represents a dialogue tree node
    /// </summary>
    [Serializable]
    public class DialogueNodeModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("speaker_id")]
        public string SpeakerId { get; set; }
        
        [JsonProperty("text")]
        public string Text { get; set; }
        
        [JsonProperty("emotion")]
        public string Emotion { get; set; }
        
        [JsonProperty("animation")]
        public string Animation { get; set; }
        
        [JsonProperty("audio_clip")]
        public string AudioClip { get; set; }
        
        [JsonProperty("options")]
        public List<DialogueOptionModel> Options { get; set; } = new List<DialogueOptionModel>();
        
        [JsonProperty("conditions")]
        public List<string> Conditions { get; set; } = new List<string>();
        
        [JsonProperty("effects")]
        public List<DialogueEffectModel> Effects { get; set; } = new List<DialogueEffectModel>();
        
        [JsonProperty("next_node_id")]
        public string NextNodeId { get; set; }
        
        [JsonProperty("is_end_node")]
        public bool IsEndNode { get; set; } = false;
    }
    
    /// <summary>
    /// Represents an effect that occurs during dialogue
    /// </summary>
    [Serializable]
    public class DialogueEffectModel
    {
        [JsonProperty("type")]
        public string Type { get; set; }
        
        [JsonProperty("target")]
        public string Target { get; set; }
        
        [JsonProperty("value")]
        public object Value { get; set; }
        
        [JsonProperty("duration")]
        public float Duration { get; set; }
        
        [JsonProperty("parameters")]
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Represents a complete dialogue tree
    /// </summary>
    [Serializable]
    public class DialogueTreeModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("title")]
        public string Title { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("nodes")]
        public List<DialogueNodeModel> Nodes { get; set; } = new List<DialogueNodeModel>();
        
        [JsonProperty("start_node_id")]
        public string StartNodeId { get; set; }
        
        [JsonProperty("characters")]
        public List<string> Characters { get; set; } = new List<string>();
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();
        
        [JsonProperty("version")]
        public int Version { get; set; } = 1;
        
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; }
        
        [JsonProperty("updated_at")]
        public DateTime UpdatedAt { get; set; }
    }
    
    #region Request/Response DTOs
    
    /// <summary>
    /// Request model for starting a conversation
    /// </summary>
    [Serializable]
    public class StartConversationRequest
    {
        [JsonProperty("participants")]
        public Dictionary<string, string> Participants { get; set; } = new Dictionary<string, string>();
        
        [JsonProperty("location_id")]
        public string LocationId { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("dialogue_tree_id")]
        public string DialogueTreeId { get; set; }
        
        [JsonProperty("context")]
        public ConversationContextModel Context { get; set; }
    }
    
    /// <summary>
    /// Request model for sending a message
    /// </summary>
    [Serializable]
    public class SendMessageRequest
    {
        [JsonProperty("sender_id")]
        public string SenderId { get; set; }
        
        [JsonProperty("content")]
        public string Content { get; set; }
        
        [JsonProperty("type")]
        public string Type { get; set; } = "dialogue";
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("emotion")]
        public string Emotion { get; set; }
        
        [JsonProperty("option_id")]
        public string OptionId { get; set; }
    }
    
    /// <summary>
    /// Request model for generating NPC response
    /// </summary>
    [Serializable]
    public class GenerateResponseRequest
    {
        [JsonProperty("responder_id")]
        public string ResponderId { get; set; }
        
        [JsonProperty("message_type")]
        public string MessageType { get; set; } = "dialogue";
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("context")]
        public ConversationContextModel Context { get; set; }
        
        [JsonProperty("use_ai")]
        public bool UseAI { get; set; } = true;
    }
    
    /// <summary>
    /// Response model for dialogue actions
    /// </summary>
    [Serializable]
    public class DialogueActionResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }
        
        [JsonProperty("message")]
        public string Message { get; set; }
        
        [JsonProperty("data")]
        public object Data { get; set; }
        
        [JsonProperty("next_options")]
        public List<DialogueOptionModel> NextOptions { get; set; } = new List<DialogueOptionModel>();
        
        [JsonProperty("effects")]
        public List<DialogueEffectModel> Effects { get; set; } = new List<DialogueEffectModel>();
    }
    
    /// <summary>
    /// Response model for conversation history
    /// </summary>
    [Serializable]
    public class ConversationHistoryResponse
    {
        [JsonProperty("conversation_id")]
        public string ConversationId { get; set; }
        
        [JsonProperty("messages")]
        public List<ConversationEntryModel> Messages { get; set; } = new List<ConversationEntryModel>();
        
        [JsonProperty("total_count")]
        public int TotalCount { get; set; }
        
        [JsonProperty("page")]
        public int Page { get; set; }
        
        [JsonProperty("page_size")]
        public int PageSize { get; set; }
    }
    
    #endregion
    
    #region Analytics and Metrics
    
    /// <summary>
    /// Analytics data for dialogue interactions
    /// </summary>
    [Serializable]
    public class DialogueAnalyticsModel
    {
        [JsonProperty("conversation_id")]
        public string ConversationId { get; set; }
        
        [JsonProperty("total_messages")]
        public int TotalMessages { get; set; }
        
        [JsonProperty("duration_seconds")]
        public float DurationSeconds { get; set; }
        
        [JsonProperty("participant_counts")]
        public Dictionary<string, int> ParticipantCounts { get; set; } = new Dictionary<string, int>();
        
        [JsonProperty("emotion_distribution")]
        public Dictionary<string, int> EmotionDistribution { get; set; } = new Dictionary<string, int>();
        
        [JsonProperty("relationship_changes")]
        public Dictionary<string, float> RelationshipChanges { get; set; } = new Dictionary<string, float>();
        
        [JsonProperty("dialogue_options_used")]
        public List<string> DialogueOptionsUsed { get; set; } = new List<string>();
        
        [JsonProperty("skill_checks_attempted")]
        public List<SkillCheckAttemptModel> SkillChecksAttempted { get; set; } = new List<SkillCheckAttemptModel>();
    }
    
    /// <summary>
    /// Model for tracking skill check attempts
    /// </summary>
    [Serializable]
    public class SkillCheckAttemptModel
    {
        [JsonProperty("skill")]
        public string Skill { get; set; }
        
        [JsonProperty("difficulty")]
        public int Difficulty { get; set; }
        
        [JsonProperty("roll")]
        public int Roll { get; set; }
        
        [JsonProperty("success")]
        public bool Success { get; set; }
        
        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; }
    }
    
    #endregion
} 