using System;
using System.Collections.Generic;

namespace VDM.Systems.Memory.Models
{
    /// <summary>
    /// Data transfer object for character memory
    /// </summary>
    [Serializable]
    public class MemoryDTO
    {
        public string memoryId;
        public string characterId;
        public string memoryType;
        public string content;
        public DateTime timestamp;
        public float emotionalWeight;
        public bool isImportant;
        public List<string> associatedCharacters;
        public Dictionary<string, object> metadata;

        public MemoryDTO()
        {
            memoryId = Guid.NewGuid().ToString();
            timestamp = DateTime.UtcNow;
            associatedCharacters = new List<string>();
            metadata = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Memory relationship data
    /// </summary>
    [Serializable]
    public class MemoryRelationshipDTO
    {
        public string relationshipId;
        public string characterId;
        public string targetCharacterId;
        public float relationshipStrength;
        public string relationshipType;
        public List<string> sharedMemories;
        public DateTime lastInteraction;

        public MemoryRelationshipDTO()
        {
            relationshipId = Guid.NewGuid().ToString();
            sharedMemories = new List<string>();
            lastInteraction = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Memory search criteria
    /// </summary>
    [Serializable]
    public class MemorySearchDTO
    {
        public string characterId;
        public string memoryType;
        public DateTime? startDate;
        public DateTime? endDate;
        public List<string> keywords;
        public bool onlyImportant;
        public int maxResults;

        public MemorySearchDTO()
        {
            keywords = new List<string>();
            maxResults = 50;
        }
    }
} 