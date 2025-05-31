using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.DTOs.Social.Faction
{
    /// <summary>
    /// Base DTO for faction system with common fields
    /// </summary>
    [Serializable]
    public abstract class FactionBaseDTO
    {
        public bool isActive = true;
        public DateTime createdAt;
        public DateTime updatedAt;
        public string createdBy;
        public string updatedBy;
    }

    /// <summary>
    /// Primary DTO for faction system
    /// </summary>
    [Serializable]
    public class FactionDTO : FactionBaseDTO
    {
        public string name = string.Empty;
        public string description;
        public string status = "active";
        public Dictionary<string, object> properties = new();
        public string factionType = "neutral";
        public int powerLevel = 50;
        public List<string> territory = new();
        public List<string> allies = new();
        public List<string> enemies = new();
        public string leaderId;
        public int memberCount = 0;
    }

    /// <summary>
    /// Request DTO for creating faction
    /// </summary>
    [Serializable]
    public class CreateFactionDTO
    {
        public string name = string.Empty;
        public string description;
        public Dictionary<string, object> properties = new();
        public string factionType = "neutral";
        public int powerLevel = 50;
        public string leaderId;
    }

    /// <summary>
    /// Request DTO for updating faction
    /// </summary>
    [Serializable]
    public class UpdateFactionDTO
    {
        public string name;
        public string description;
        public string status;
        public Dictionary<string, object> properties;
        public string factionType;
        public int? powerLevel;
        public string leaderId;
    }

    /// <summary>
    /// Response DTO for faction
    /// </summary>
    [Serializable]
    public class FactionResponseDTO
    {
        public bool success = true;
        public string message;
        public FactionDTO data;
        public List<string> errors = new();
        public DateTime timestamp;

        public FactionResponseDTO() 
        { 
            timestamp = DateTime.UtcNow;
        }
        
        public FactionResponseDTO(FactionDTO data) : this()
        {
            this.data = data;
        }
    }

    /// <summary>
    /// Response DTO for faction lists
    /// </summary>
    [Serializable]
    public class FactionListResponseDTO
    {
        public bool success = true;
        public string message;
        public List<FactionDTO> data = new();
        public List<string> errors = new();
        public DateTime timestamp;
        public int total;
        public int page;
        public int size;
        public bool hasNext;
        public bool hasPrev;

        public FactionListResponseDTO() 
        { 
            timestamp = DateTime.UtcNow;
        }
        
        public FactionListResponseDTO(List<FactionDTO> data, int total, int page, int size, bool hasNext, bool hasPrev) : this()
        {
            this.data = data;
            this.total = total;
            this.page = page;
            this.size = size;
            this.hasNext = hasNext;
            this.hasPrev = hasPrev;
        }
    }

    /// <summary>
    /// Relationship DTO for faction relationships
    /// </summary>
    [Serializable]
    public class RelationshipDTO : FactionBaseDTO
    {
        public string factionAId;
        public string factionBId;
        public string factionAName = string.Empty;
        public string factionBName = string.Empty;
        public string relationshipType = "neutral";
        public int relationshipValue = 0;
        public List<RelationshipEventDTO> relationshipHistory = new();
        public List<TradeAgreementDTO> tradeAgreements = new();
    }

    /// <summary>
    /// Relationship event DTO for tracking faction relationship changes
    /// </summary>
    [Serializable]
    public class RelationshipEventDTO
    {
        public string eventType = string.Empty;
        public string description;
        public int relationshipChange = 0;
        public DateTime eventDate;
        public List<string> participants = new();
        public DateTime createdAt;
        public DateTime updatedAt;
        public string createdBy;
        public string updatedBy;
    }

    /// <summary>
    /// Trade agreement DTO for faction trade relationships
    /// </summary>
    [Serializable]
    public class TradeAgreementDTO
    {
        public string agreementId;
        public string factionAId;
        public string factionBId;
        public string agreementType = "trade";
        public Dictionary<string, object> terms = new();
        public DateTime startDate;
        public DateTime? endDate;
        public string status = "active";
        public float tradeVolume = 0f;
        public DateTime createdAt;
        public DateTime updatedAt;
        public string createdBy;
        public string updatedBy;
    }

    /// <summary>
    /// Diplomacy DTO for faction diplomatic actions
    /// </summary>
    [Serializable]
    public class DiplomacyDTO : FactionBaseDTO
    {
        public string fromFactionId;
        public string toFactionId;
        public string diplomacyId;
        public string actionType = "proposal";
        public Dictionary<string, object> proposal = new();
        public string status = "pending";
        public Dictionary<string, object> response;
        public DateTime? deadline;
        public Dictionary<string, object> consequences;
    }
} 