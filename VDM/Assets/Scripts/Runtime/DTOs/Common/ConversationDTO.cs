using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Social.Dialogue
{
    /// <summary>
    /// Conversation message data transfer object
    /// </summary>
    [Serializable]
    public class ConversationMessageDTO
    {
        public string Id { get; set; } = string.Empty;
        public string ConversationId { get; set; } = string.Empty;
        public string SenderId { get; set; } = string.Empty;
        public string Content { get; set; } = string.Empty;
        public string Type { get; set; } = "dialogue";
        public string Timestamp { get; set; } = string.Empty;
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Conversation data transfer object
    /// </summary>
    [Serializable]
    public class ConversationDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public List<string> Participants { get; set; } = new List<string>();
        public List<ConversationMessageDTO> Messages { get; set; } = new List<ConversationMessageDTO>();
        public string Status { get; set; } = "active";
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Dialogue option for conversation choices
    /// </summary>
    [Serializable]
    public class DialogueOptionDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Text { get; set; } = string.Empty;
        public string? Condition { get; set; }
        public string? Consequence { get; set; }
        public Dictionary<string, object>? SkillCheck { get; set; }
    }

    /// <summary>
    /// Dialogue node data transfer object for conversation structure
    /// </summary>
    [Serializable]
    public class DialogueNodeDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Text { get; set; } = string.Empty;
        public string SpeakerId { get; set; } = string.Empty;
        public List<DialogueOptionDTO> Options { get; set; } = new List<DialogueOptionDTO>();
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        public bool IsEndNode { get; set; } = false;
    }

    /// <summary>
    /// Start conversation request
    /// </summary>
    [Serializable]
    public class StartConversationRequestDTO
    {
        public string Title { get; set; } = string.Empty;
        public List<string> ParticipantIds { get; set; } = new List<string>();
        public string LocationId { get; set; }
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Send message request
    /// </summary>
    [Serializable]
    public class SendMessageRequestDTO
    {
        public string ConversationId { get; set; } = string.Empty;
        public string Content { get; set; } = string.Empty;
        public string Type { get; set; } = "dialogue";
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Conversation response
    /// </summary>
    [Serializable]
    public class ConversationResponseDTO : SuccessResponseDTO
    {
        public ConversationDTO Conversation { get; set; } = new ConversationDTO();
    }

    /// <summary>
    /// Message response
    /// </summary>
    [Serializable]
    public class MessageResponseDTO : SuccessResponseDTO
    {
        public ConversationMessageDTO Message { get; set; } = new ConversationMessageDTO();
    }

    /// <summary>
    /// Mock conversation data for Unity testing
    /// </summary>
    [Serializable]
    public class MockConversationDataDTO
    {
        public string ConversationId { get; set; } = string.Empty;
        public Dictionary<string, string> Participants { get; set; } = new Dictionary<string, string>();
        public List<ConversationMessageDTO> Messages { get; set; } = new List<ConversationMessageDTO>();
        public List<DialogueOptionDTO> DialogueOptions { get; set; } = new List<DialogueOptionDTO>();
    }
} 