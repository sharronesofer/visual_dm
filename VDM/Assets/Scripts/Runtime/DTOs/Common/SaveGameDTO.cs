using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;
using VDM.DTOs.Game.Time;
using VDM.DTOs.Game.Character;

namespace VDM.DTOs.Game.SaveLoad
{
    /// <summary>
    /// Save game metadata information
    /// </summary>
    [Serializable]
    public class SaveGameMetadataDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public string PlayerId { get; set; } = string.Empty;
        public DateTime SaveDate { get; set; } = DateTime.UtcNow;
        public string GameTime { get; set; }
        public int Level { get; set; } = 1;
        public double PlaytimeHours { get; set; } = 0.0;
        public string Location { get; set; }
        public int CharacterCount { get; set; } = 0;
        public long FileSizeBytes { get; set; } = 0;
        public string Version { get; set; } = "1.0.0";
        public bool IsAutosave { get; set; } = false;
        public bool IsQuicksave { get; set; } = false;
        public string ScreenshotPath { get; set; }
        public List<string> Tags { get; set; } = new List<string>();
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Complete game save data
    /// </summary>
    [Serializable]
    public class GameSaveDataDTO : MetadataDTO
    {
        public SaveGameMetadataDTO Metadata { get; set; } = new SaveGameMetadataDTO();
        public Dictionary<string, object> WorldState { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> Characters { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> PlayerData { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> GameTime { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> Settings { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> QuestData { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> InventoryData { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> FactionData { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> RegionData { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> CustomData { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Create save game request
    /// </summary>
    [Serializable]
    public class CreateSaveGameRequestDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public bool IsAutosave { get; set; } = false;
        public bool IsQuicksave { get; set; } = false;
        public bool IncludeScreenshot { get; set; } = true;
        public List<string> Tags { get; set; } = new List<string>();
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Load game request
    /// </summary>
    [Serializable]
    public class LoadGameRequestDTO
    {
        public string SaveId { get; set; } = string.Empty;
        public bool ValidateIntegrity { get; set; } = true;
        public bool BackupCurrent { get; set; } = true;
    }

    /// <summary>
    /// Save game list response
    /// </summary>
    [Serializable]
    public class SaveGameListResponseDTO : SuccessResponseDTO
    {
        public List<SaveGameMetadataDTO> Saves { get; set; } = new List<SaveGameMetadataDTO>();
        public int TotalCount { get; set; } = 0;
        public long TotalSizeBytes { get; set; } = 0;
    }

    /// <summary>
    /// Save game response
    /// </summary>
    [Serializable]
    public class SaveGameResponseDTO : SuccessResponseDTO
    {
        public SaveGameMetadataDTO SaveMetadata { get; set; } = new SaveGameMetadataDTO();
        public string Operation { get; set; } = "save";
        public string FilePath { get; set; }
    }

    /// <summary>
    /// Load game response
    /// </summary>
    [Serializable]
    public class LoadGameResponseDTO : SuccessResponseDTO
    {
        public GameSaveDataDTO SaveData { get; set; } = new GameSaveDataDTO();
        public DateTime LoadedAt { get; set; } = DateTime.UtcNow;
        public bool IntegrityCheck { get; set; } = true;
    }
} 