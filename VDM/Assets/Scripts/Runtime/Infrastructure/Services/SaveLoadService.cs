using Newtonsoft.Json;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.DTOs.Core.Shared;
using VDM.DTOs.Game.SaveLoad;
using VDM.DTOs.Game.Time;
using VDM.Infrastructure.Services;
using VDM.Systems;
using VDM.Systems.Quest.Services;
using VDM.Systems.WorldState.Services;


namespace VDM.Infrastructure.Services
{
    /// <summary>
    /// Service for managing save and load operations, integrating with backend storage system
    /// </summary>
    public class SaveLoadService : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private bool enableAutoSave = true;
        [SerializeField] private float autoSaveIntervalMinutes = 5f;
        [SerializeField] private int maxSaveSlots = 10;
        [SerializeField] private bool enableCloudSync = true;
        [SerializeField] private bool enableEncryption = true;

        [Header("Dependencies")]
        [SerializeField] private CharacterService characterService;
        [SerializeField] private QuestService questService;
        [SerializeField] private TimeService timeService;
        [SerializeField] private WorldStatePersistence worldStatePersistence;
        [SerializeField] private StateManager stateManager;

        // Events
        public event System.Action<bool> OnSaveCompleted;
        public event System.Action<bool> OnLoadCompleted;
        public event System.Action<SaveGameMetadataDTO[]> OnSaveListLoaded;
        public event System.Action<string> OnSaveError;
        public event System.Action<float> OnSaveProgress;

        private float autoSaveTimer = 0f;
        private bool isOperationInProgress = false;
        private string currentSaveSlot = "default";
        private Dictionary<string, SaveGameMetadataDTO> cachedSaveMetadata = new Dictionary<string, SaveGameMetadataDTO>();

        private void Start()
        {
            InitializeService();
        }

        private void Update()
        {
            if (enableAutoSave && !isOperationInProgress)
            {
                autoSaveTimer += Time.deltaTime;
                if (autoSaveTimer >= autoSaveIntervalMinutes * 60f)
                {
                    autoSaveTimer = 0f;
                    _ = AutoSaveAsync();
                }
            }
        }

        private void InitializeService()
        {
            // Find dependencies if not assigned
            if (characterService == null)
                characterService = FindObjectOfType<CharacterService>();
            if (questService == null)
                questService = FindObjectOfType<QuestService>();
            if (timeService == null)
                timeService = FindObjectOfType<TimeService>();
            if (worldStatePersistence == null)
                worldStatePersistence = FindObjectOfType<WorldStatePersistence>();
            if (stateManager == null)
                stateManager = FindObjectOfType<StateManager>();

            AnalyticsManager.TrackEvent("SaveLoadService_Initialized", new Dictionary<string, object>
            {
                {"auto_save_enabled", enableAutoSave},
                {"auto_save_interval", autoSaveIntervalMinutes},
                {"max_save_slots", maxSaveSlots}
            });
        }

        /// <summary>
        /// Save the current game state to the specified slot
        /// </summary>
        public async Task<bool> SaveGameAsync(string slotName = null, string description = "")
        {
            if (isOperationInProgress)
            {
                Debug.LogWarning("Save operation already in progress");
                return false;
            }

            isOperationInProgress = true;
            OnSaveProgress?.Invoke(0f);

            try
            {
                string saveSlot = slotName ?? currentSaveSlot;
                Debug.Log($"Starting save operation for slot: {saveSlot}");

                // Collect save data from all systems
                OnSaveProgress?.Invoke(0.2f);
                var saveData = await CollectSaveDataAsync();

                // Create save request
                OnSaveProgress?.Invoke(0.4f);
                var saveRequest = new SaveGameRequestDTO
                {
                    SlotName = saveSlot,
                    SaveData = saveData,
                    Description = description,
                    EnableEncryption = enableEncryption,
                    EnableCloudSync = enableCloudSync
                };

                // Send save request to backend
                OnSaveProgress?.Invoke(0.6f);
                var response = await HttpClientUtility.PostAsync<SaveGameResponseDTO>(
                    "/api/world-state/save", 
                    saveRequest
                );

                OnSaveProgress?.Invoke(0.8f);

                if (response != null && response.Success)
                {
                    // Update cached metadata
                    cachedSaveMetadata[saveSlot] = response.Metadata;
                    currentSaveSlot = saveSlot;

                    // Save local backup if enabled
                    await SaveLocalBackupAsync(saveData, saveSlot);

                    OnSaveProgress?.Invoke(1f);
                    OnSaveCompleted?.Invoke(true);

                    AnalyticsManager.TrackEvent("Game_Saved", new Dictionary<string, object>
                    {
                        {"slot_name", saveSlot},
                        {"file_size", response.Metadata.FileSizeBytes},
                        {"save_duration", response.Metadata.SaveDuration},
                        {"cloud_sync", enableCloudSync}
                    });

                    Debug.Log($"Game saved successfully to slot: {saveSlot}");
                    return true;
                }
                else
                {
                    string error = response?.ErrorMessage ?? "Unknown save error";
                    OnSaveError?.Invoke(error);
                    OnSaveCompleted?.Invoke(false);
                    Debug.LogError($"Save failed: {error}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                string error = $"Save operation failed: {ex.Message}";
                OnSaveError?.Invoke(error);
                OnSaveCompleted?.Invoke(false);
                Debug.LogError(error);
                return false;
            }
            finally
            {
                isOperationInProgress = false;
            }
        }

        /// <summary>
        /// Load game state from the specified slot
        /// </summary>
        public async Task<bool> LoadGameAsync(string slotName = null)
        {
            if (isOperationInProgress)
            {
                Debug.LogWarning("Load operation already in progress");
                return false;
            }

            isOperationInProgress = true;
            OnSaveProgress?.Invoke(0f);

            try
            {
                string saveSlot = slotName ?? currentSaveSlot;
                Debug.Log($"Starting load operation for slot: {saveSlot}");

                OnSaveProgress?.Invoke(0.2f);
                
                // Create load request
                var loadRequest = new LoadGameRequestDTO
                {
                    SlotName = saveSlot,
                    ValidateChecksum = true,
                    EnableCloudSync = enableCloudSync
                };

                // Send load request to backend
                OnSaveProgress?.Invoke(0.4f);
                var response = await HttpClientUtility.PostAsync<LoadGameResponseDTO>(
                    "/api/world-state/load", 
                    loadRequest
                );

                if (response != null && response.Success && response.SaveData != null)
                {
                    OnSaveProgress?.Invoke(0.6f);
                    
                    // Apply loaded data to all systems
                    await ApplySaveDataAsync(response.SaveData);
                    
                    OnSaveProgress?.Invoke(0.8f);
                    
                    // Update current slot
                    currentSaveSlot = saveSlot;
                    
                    OnSaveProgress?.Invoke(1f);
                    OnLoadCompleted?.Invoke(true);

                    AnalyticsManager.TrackEvent("Game_Loaded", new Dictionary<string, object>
                    {
                        {"slot_name", saveSlot},
                        {"load_duration", response.LoadDuration},
                        {"cloud_sync", enableCloudSync}
                    });

                    Debug.Log($"Game loaded successfully from slot: {saveSlot}");
                    return true;
                }
                else
                {
                    // Try local backup if backend load fails
                    var localData = await LoadLocalBackupAsync(saveSlot);
                    if (localData != null)
                    {
                        await ApplySaveDataAsync(localData);
                        OnLoadCompleted?.Invoke(true);
                        Debug.Log($"Game loaded from local backup: {saveSlot}");
                        return true;
                    }

                    string error = response?.ErrorMessage ?? "Save file not found or corrupted";
                    OnSaveError?.Invoke(error);
                    OnLoadCompleted?.Invoke(false);
                    Debug.LogError($"Load failed: {error}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                string error = $"Load operation failed: {ex.Message}";
                OnSaveError?.Invoke(error);
                OnLoadCompleted?.Invoke(false);
                Debug.LogError(error);
                return false;
            }
            finally
            {
                isOperationInProgress = false;
            }
        }

        /// <summary>
        /// Get list of available save files
        /// </summary>
        public async Task<SaveGameMetadataDTO[]> GetSaveListAsync()
        {
            try
            {
                var response = await HttpClientUtility.GetAsync<SaveGameMetadataDTO[]>("/api/world-state/saves");
                
                if (response != null)
                {
                    // Update cached metadata
                    cachedSaveMetadata.Clear();
                    foreach (var metadata in response)
                    {
                        cachedSaveMetadata[metadata.SlotName] = metadata;
                    }
                    
                    OnSaveListLoaded?.Invoke(response);
                    return response;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get save list: {ex.Message}");
            }

            return new SaveGameMetadataDTO[0];
        }

        /// <summary>
        /// Delete a save file
        /// </summary>
        public async Task<bool> DeleteSaveAsync(string slotName)
        {
            try
            {
                var deleteRequest = new DeleteSaveRequestDTO { SlotName = slotName };
                var response = await HttpClientUtility.PostAsync<DeleteSaveResponseDTO>(
                    "/api/world-state/delete-save", 
                    deleteRequest
                );

                if (response != null && response.Success)
                {
                    cachedSaveMetadata.Remove(slotName);
                    await DeleteLocalBackupAsync(slotName);
                    
                    AnalyticsManager.TrackEvent("Save_Deleted", new Dictionary<string, object>
                    {
                        {"slot_name", slotName}
                    });
                    
                    return true;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete save: {ex.Message}");
            }

            return false;
        }

        /// <summary>
        /// Perform auto-save operation
        /// </summary>
        private async Task AutoSaveAsync()
        {
            await SaveGameAsync("autosave", "Auto-save");
        }

        /// <summary>
        /// Quick save to default slot
        /// </summary>
        public async Task<bool> QuickSaveAsync()
        {
            return await SaveGameAsync("quicksave", "Quick save");
        }

        /// <summary>
        /// Quick load from default slot
        /// </summary>
        public async Task<bool> QuickLoadAsync()
        {
            return await LoadGameAsync("quicksave");
        }

        /// <summary>
        /// Collect save data from all game systems
        /// </summary>
        private async Task<GameSaveDataDTO> CollectSaveDataAsync()
        {
            var saveData = new GameSaveDataDTO();

            try
            {
                // Player data
                if (characterService != null)
                {
                    saveData.PlayerData = new PlayerSaveDataDTO
                    {
                        Position = characterService.GetPlayerPosition(),
                        Rotation = characterService.GetPlayerRotation(),
                        Health = characterService.GetPlayerHealth(),
                        Level = characterService.GetPlayerLevel(),
                        Experience = characterService.GetPlayerExperience(),
                        Stats = characterService.GetPlayerStats()
                    };
                }

                // World state data
                if (worldStatePersistence != null)
                {
                    saveData.WorldData = worldStatePersistence.GetWorldSaveData();
                }

                // Character data
                if (characterService != null)
                {
                    saveData.CharacterData = await characterService.GetCharacterSaveDataAsync();
                }

                // Quest data
                if (questService != null)
                {
                    saveData.QuestData = await questService.GetQuestSaveDataAsync();
                }

                // Inventory data (placeholder - will be implemented with Task 15)
                saveData.InventoryData = new InventorySaveDataDTO
                {
                    Items = new List<object>(),
                    Currency = 0
                };

                // Time data
                if (timeService != null)
                {
                    saveData.TimeData = timeService.GetTimeSaveData();
                }

                // Game settings
                saveData.SettingsData = new SettingsSaveDataDTO
                {
                    GraphicsSettings = new Dictionary<string, object>(),
                    AudioSettings = new Dictionary<string, object>(),
                    GameplaySettings = new Dictionary<string, object>()
                };

                Debug.Log("Save data collected successfully");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error collecting save data: {ex.Message}");
                throw;
            }

            return saveData;
        }

        /// <summary>
        /// Apply loaded save data to all game systems
        /// </summary>
        private async Task ApplySaveDataAsync(GameSaveDataDTO saveData)
        {
            try
            {
                // Apply player data
                if (saveData.PlayerData != null && characterService != null)
                {
                    characterService.SetPlayerPosition(saveData.PlayerData.Position);
                    characterService.SetPlayerRotation(saveData.PlayerData.Rotation);
                    characterService.SetPlayerHealth(saveData.PlayerData.Health);
                    characterService.SetPlayerLevel(saveData.PlayerData.Level);
                    characterService.SetPlayerExperience(saveData.PlayerData.Experience);
                    characterService.SetPlayerStats(saveData.PlayerData.Stats);
                }

                // Apply world state data
                if (saveData.WorldData != null && worldStatePersistence != null)
                {
                    worldStatePersistence.ApplyWorldSaveData(saveData.WorldData);
                }

                // Apply character data
                if (saveData.CharacterData != null && characterService != null)
                {
                    await characterService.ApplyCharacterSaveDataAsync(saveData.CharacterData);
                }

                // Apply quest data
                if (saveData.QuestData != null && questService != null)
                {
                    await questService.ApplyQuestSaveDataAsync(saveData.QuestData);
                }

                // Apply time data
                if (saveData.TimeData != null && timeService != null)
                {
                    timeService.ApplyTimeSaveData(saveData.TimeData);
                }

                Debug.Log("Save data applied successfully");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error applying save data: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Save local backup for offline access
        /// </summary>
        private async Task SaveLocalBackupAsync(GameSaveDataDTO saveData, string slotName)
        {
            try
            {
                string backupPath = Path.Combine(Application.persistentDataPath, "saves", $"{slotName}.json");
                Directory.CreateDirectory(Path.GetDirectoryName(backupPath));
                
                string jsonData = JsonConvert.SerializeObject(saveData, Formatting.Indented);
                await File.WriteAllTextAsync(backupPath, jsonData);
                
                Debug.Log($"Local backup saved: {backupPath}");
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to save local backup: {ex.Message}");
            }
        }

        /// <summary>
        /// Load local backup
        /// </summary>
        private async Task<GameSaveDataDTO> LoadLocalBackupAsync(string slotName)
        {
            try
            {
                string backupPath = Path.Combine(Application.persistentDataPath, "saves", $"{slotName}.json");
                
                if (File.Exists(backupPath))
                {
                    string jsonData = await File.ReadAllTextAsync(backupPath);
                    return JsonConvert.DeserializeObject<GameSaveDataDTO>(jsonData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to load local backup: {ex.Message}");
            }

            return null;
        }

        /// <summary>
        /// Delete local backup
        /// </summary>
        private async Task DeleteLocalBackupAsync(string slotName)
        {
            try
            {
                string backupPath = Path.Combine(Application.persistentDataPath, "saves", $"{slotName}.json");
                
                if (File.Exists(backupPath))
                {
                    File.Delete(backupPath);
                    Debug.Log($"Local backup deleted: {backupPath}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to delete local backup: {ex.Message}");
            }
        }

        /// <summary>
        /// Get metadata for a specific save slot
        /// </summary>
        public SaveGameMetadataDTO GetSaveMetadata(string slotName)
        {
            cachedSaveMetadata.TryGetValue(slotName, out var metadata);
            return metadata;
        }

        /// <summary>
        /// Check if a save operation is currently in progress
        /// </summary>
        public bool IsOperationInProgress => isOperationInProgress;

        /// <summary>
        /// Set auto-save configuration
        /// </summary>
        public void SetAutoSaveConfig(bool enabled, float intervalMinutes)
        {
            enableAutoSave = enabled;
            autoSaveIntervalMinutes = intervalMinutes;
            autoSaveTimer = 0f; // Reset timer
        }

        /// <summary>
        /// Get current save slot
        /// </summary>
        public string GetCurrentSaveSlot()
        {
            return currentSaveSlot;
        }

        /// <summary>
        /// Set current save slot
        /// </summary>
        public void SetCurrentSaveSlot(string slotName)
        {
            currentSaveSlot = slotName;
        }
    }
} 