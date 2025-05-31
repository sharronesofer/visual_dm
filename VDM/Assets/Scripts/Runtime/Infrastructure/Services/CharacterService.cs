using NativeWebSocket;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine.Networking;
using UnityEngine;
using VDM.Systems.Character.Models;
using VDM.Infrastructure.Services;
using VDM.Infrastructure.Core;
using VDM.DTOs.Core;
using VDM.DTOs.Character;
using VDM.Systems.Character;


namespace VDM.Infrastructure.Services
{
    /// <summary>
    /// Service for managing character data communication with the backend
    /// Handles character CRUD operations, progression tracking, and real-time synchronization
    /// </summary>
    public class CharacterService : BaseHTTPClient
    {
        [Header("Character Service Configuration")]
        [SerializeField] private bool autoSyncCharacters = true;
        [SerializeField] private float syncInterval = 30f;
        
        // Character events
        public event Action<CharacterResponseDTO> OnCharacterCreated;
        public event Action<CharacterResponseDTO> OnCharacterUpdated;
        public event Action<string> OnCharacterDeleted;
        public event Action<List<CharacterResponseDTO>> OnCharactersLoaded;
        public event Action<CharacterResponseDTO> OnCharacterLevelUp;
        public event Action<CharacterResponseDTO, string> OnCharacterSkillIncreased;
        public event Action<CharacterResponseDTO, string> OnCharacterAbilityGained;

        // Local character cache
        private Dictionary<string, CharacterResponseDTO> _characterCache = new Dictionary<string, CharacterResponseDTO>();
        private Dictionary<string, CharacterModel> _characterModels = new Dictionary<string, CharacterModel>();
        
        // WebSocket integration
        private WebSocketManager _webSocketManager;
        
        // Coroutines
        private Coroutine _autoSyncCoroutine;

        protected override string GetClientName() => "CharacterService";

        protected override void InitializeClient()
        {
            base.InitializeClient();
            
            // Find WebSocket manager
            _webSocketManager = FindObjectOfType<WebSocketManager>();
            if (_webSocketManager != null)
            {
                // Subscribe to character-related WebSocket events
                _webSocketManager.RegisterMessageHandler("character_update", HandleCharacterWebSocketUpdate);
                _webSocketManager.RegisterMessageHandler("character_level_up", HandleCharacterLevelUpEvent);
                _webSocketManager.RegisterMessageHandler("character_progression", HandleCharacterProgressionEvent);
            }
            
            // Start auto sync if enabled
            if (autoSyncCharacters)
            {
                StartAutoSync();
            }
        }

        protected virtual void OnDestroy()
        {
            // Cleanup
            if (_webSocketManager != null)
            {
                _webSocketManager.UnregisterMessageHandler("character_update");
                _webSocketManager.UnregisterMessageHandler("character_level_up");
                _webSocketManager.UnregisterMessageHandler("character_progression");
            }
            
            if (_autoSyncCoroutine != null)
            {
                StopCoroutine(_autoSyncCoroutine);
            }
            
            base.OnDestroy();
        }

        #region Character CRUD Operations

        /// <summary>
        /// Create a new character
        /// </summary>
        public void CreateCharacter(CharacterCreateDTO characterData, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(CreateCharacterCoroutine(characterData, callback));
        }

        private IEnumerator CreateCharacterCoroutine(CharacterCreateDTO characterData, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            yield return PostRequestCoroutine("/characters", characterData, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    character = SafeDeserialize<CharacterResponseDTO>(response);
                    if (character != null)
                    {
                        _characterCache[character.Id] = character;
                        OnCharacterCreated?.Invoke(character);
                        
                        if (debugLogging)
                            Debug.Log($"[CharacterService] Created character: {character.CharacterName} (ID: {character.Id})");
                    }
                }
            });

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Get a character by UUID
        /// </summary>
        public void GetCharacter(string characterId, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            // Check cache first
            if (_characterCache.TryGetValue(characterId, out CharacterResponseDTO cachedCharacter))
            {
                callback?.Invoke(true, cachedCharacter);
                return;
            }

            StartCoroutine(GetCharacterCoroutine(characterId, callback));
        }

        private IEnumerator GetCharacterCoroutine(string characterId, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            yield return GetRequestCoroutine($"/characters/{characterId}", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    character = SafeDeserialize<CharacterResponseDTO>(response);
                    if (character != null)
                    {
                        _characterCache[character.Id] = character;
                    }
                }
            });

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Get a character by their game character ID
        /// </summary>
        public void GetCharacterByGameId(string characterId, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(GetCharacterByGameIdCoroutine(characterId, callback));
        }

        private IEnumerator GetCharacterByGameIdCoroutine(string characterId, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            yield return GetRequestCoroutine($"/characters/by-game-id/{characterId}", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    character = SafeDeserialize<CharacterResponseDTO>(response);
                    if (character != null)
                    {
                        _characterCache[character.Id] = character;
                    }
                }
            });

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Update an existing character
        /// </summary>
        public void UpdateCharacter(string characterId, CharacterUpdateDTO updates, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(UpdateCharacterCoroutine(characterId, updates, callback));
        }

        private IEnumerator UpdateCharacterCoroutine(string characterId, CharacterUpdateDTO updates, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            yield return PutRequestCoroutine($"/characters/{characterId}", updates, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    character = SafeDeserialize<CharacterResponseDTO>(response);
                    if (character != null)
                    {
                        _characterCache[character.Id] = character;
                        OnCharacterUpdated?.Invoke(character);
                        
                        if (debugLogging)
                            Debug.Log($"[CharacterService] Updated character: {character.CharacterName} (ID: {character.Id})");
                    }
                }
            });

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Delete (soft delete) a character
        /// </summary>
        public void DeleteCharacter(string characterId, Action<bool> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(DeleteCharacterCoroutine(characterId, callback));
        }

        private IEnumerator DeleteCharacterCoroutine(string characterId, Action<bool> callback)
        {
            bool success = false;

            yield return DeleteRequestCoroutine($"/characters/{characterId}", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    _characterCache.Remove(characterId);
                    _characterModels.Remove(characterId);
                    OnCharacterDeleted?.Invoke(characterId);
                    
                    if (debugLogging)
                        Debug.Log($"[CharacterService] Deleted character: {characterId}");
                }
            });

            callback?.Invoke(success);
        }

        #endregion

        #region Character Search and Listing

        /// <summary>
        /// Search and list characters with optional filters
        /// </summary>
        public void SearchCharacters(
            string name = null, 
            string race = null, 
            int? levelMin = null, 
            int? levelMax = null, 
            string alignment = null, 
            bool activeOnly = true, 
            int page = 1, 
            int perPage = 10, 
            Action<bool, CharacterListResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            // Build query parameters
            var queryParams = new List<string>();
            if (!string.IsNullOrEmpty(name)) queryParams.Add($"name={UnityWebRequest.EscapeURL(name)}");
            if (!string.IsNullOrEmpty(race)) queryParams.Add($"race={UnityWebRequest.EscapeURL(race)}");
            if (levelMin.HasValue) queryParams.Add($"level_min={levelMin.Value}");
            if (levelMax.HasValue) queryParams.Add($"level_max={levelMax.Value}");
            if (!string.IsNullOrEmpty(alignment)) queryParams.Add($"alignment={UnityWebRequest.EscapeURL(alignment)}");
            queryParams.Add($"active_only={activeOnly.ToString().ToLower()}");
            queryParams.Add($"page={page}");
            queryParams.Add($"per_page={perPage}");

            string queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
            string endpoint = $"/characters{queryString}";

            StartCoroutine(SearchCharactersCoroutine(endpoint, callback));
        }

        private IEnumerator SearchCharactersCoroutine(string endpoint, Action<bool, CharacterListResponseDTO> callback)
        {
            bool success = false;
            CharacterListResponseDTO result = null;

            yield return GetRequestCoroutine(endpoint, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    result = SafeDeserialize<CharacterListResponseDTO>(response);
                    if (result != null && result.Characters != null)
                    {
                        // Update cache with returned characters
                        foreach (var character in result.Characters)
                        {
                            _characterCache[character.Id] = character;
                        }
                        
                        OnCharactersLoaded?.Invoke(result.Characters);
                        
                        if (debugLogging)
                            Debug.Log($"[CharacterService] Loaded {result.Characters.Count} characters");
                    }
                }
            });

            callback?.Invoke(success, result);
        }

        #endregion

        #region Character Progression

        /// <summary>
        /// Grant experience points to a character
        /// </summary>
        public void GrantExperience(string characterId, ExperienceGrantDTO xpGrant, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(GrantExperienceCoroutine(characterId, xpGrant, callback));
        }

        private IEnumerator GrantExperienceCoroutine(string characterId, ExperienceGrantDTO xpGrant, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            yield return PostRequestCoroutine($"/characters/{characterId}/experience", xpGrant, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    character = SafeDeserialize<CharacterResponseDTO>(response);
                    if (character != null)
                    {
                        var oldCharacter = _characterCache.ContainsKey(character.Id) ? _characterCache[character.Id] : null;
                        _characterCache[character.Id] = character;
                        
                        // Check for level up
                        if (oldCharacter != null && character.Level > oldCharacter.Level)
                        {
                            OnCharacterLevelUp?.Invoke(character);
                        }
                        
                        OnCharacterUpdated?.Invoke(character);
                        
                        if (debugLogging)
                            Debug.Log($"[CharacterService] Granted {xpGrant.Amount} XP to {character.CharacterName}. New level: {character.Level}");
                    }
                }
            });

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Increase a character's skill rank
        /// </summary>
        public void IncreaseSkill(string characterId, SkillIncreaseDTO skillData, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(IncreaseSkillCoroutine(characterId, skillData, callback));
        }

        private IEnumerator IncreaseSkillCoroutine(string characterId, SkillIncreaseDTO skillData, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            yield return PostRequestCoroutine($"/characters/{characterId}/skills", skillData, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    character = SafeDeserialize<CharacterResponseDTO>(response);
                    if (character != null)
                    {
                        _characterCache[character.Id] = character;
                        OnCharacterSkillIncreased?.Invoke(character, skillData.SkillName);
                        OnCharacterUpdated?.Invoke(character);
                        
                        if (debugLogging)
                            Debug.Log($"[CharacterService] Increased {skillData.SkillName} for {character.CharacterName} by {skillData.IncreaseAmount}");
                    }
                }
            });

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Add an ability/feat to a character
        /// </summary>
        public void AddAbility(string characterId, AbilitySelectionDTO abilityData, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(AddAbilityCoroutine(characterId, abilityData, callback));
        }

        private IEnumerator AddAbilityCoroutine(string characterId, AbilitySelectionDTO abilityData, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            yield return PostRequestCoroutine($"/characters/{characterId}/abilities", abilityData, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    character = SafeDeserialize<CharacterResponseDTO>(response);
                    if (character != null)
                    {
                        _characterCache[character.Id] = character;
                        OnCharacterAbilityGained?.Invoke(character, abilityData.AbilityName);
                        OnCharacterUpdated?.Invoke(character);
                        
                        if (debugLogging)
                            Debug.Log($"[CharacterService] Added ability {abilityData.AbilityName} to {character.CharacterName}");
                    }
                }
            });

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Get character progression history
        /// </summary>
        public void GetCharacterProgression(string characterId, Action<bool, List<CharacterProgressionResponseDTO>> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(GetCharacterProgressionCoroutine(characterId, callback));
        }

        private IEnumerator GetCharacterProgressionCoroutine(string characterId, Action<bool, List<CharacterProgressionResponseDTO>> callback)
        {
            bool success = false;
            List<CharacterProgressionResponseDTO> progression = null;

            yield return GetRequestCoroutine($"/characters/{characterId}/progression", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    progression = SafeDeserializeList<CharacterProgressionResponseDTO>(response);
                    
                    if (debugLogging && progression != null)
                        Debug.Log($"[CharacterService] Retrieved {progression.Count} progression records for character {characterId}");
                }
            });

            callback?.Invoke(success, progression);
        }

        #endregion

        #region Character Model Integration

        /// <summary>
        /// Convert CharacterResponseDTO to CharacterModel for use with existing Unity systems
        /// </summary>
        public CharacterModel ConvertToCharacterModel(CharacterResponseDTO dto)
        {
            if (dto == null) return null;

            var model = new CharacterModel(dto.CharacterName, dto.Race);
            
            // Core properties
            model.Level = dto.Level;
            model.Experience = dto.Experience;
            model.Background = dto.Background;
            model.Alignment = dto.Alignment;
            
            // Stats (map from Development Bible format to Unity format)
            model.Stats = new Dictionary<string, int>
            {
                ["strength"] = dto.Attributes.Strength,
                ["dexterity"] = dto.Attributes.Dexterity,
                ["constitution"] = dto.Attributes.Constitution,
                ["intelligence"] = dto.Attributes.Intelligence,
                ["wisdom"] = dto.Attributes.Wisdom,
                ["charisma"] = dto.Attributes.Charisma
            };
            
            // Derived stats
            model.MaxHitPoints = dto.DerivedStats.MaxHitPoints;
            model.CurrentHitPoints = dto.DerivedStats.HitPoints;
            model.ArmorClass = dto.DerivedStats.ArmorClass;
            model.Initiative = dto.DerivedStats.Initiative;
            
            // Personality
            model.PersonalityTraits = dto.Personality?.Traits ?? new List<string>();
            model.Ideals = dto.Personality?.Ideals ?? new List<string>();
            model.Bonds = dto.Personality?.Bonds ?? new List<string>();
            model.Flaws = dto.Personality?.Flaws ?? new List<string>();
            
            // Abilities and skills
            // Note: Unity CharacterModel doesn't have direct abilities field, using CustomProperties
            model.CustomProperties["abilities"] = dto.Abilities;
            model.CustomProperties["skills"] = dto.Skills;
            model.CustomProperties["languages"] = dto.Languages;
            
            // Game state
            if (dto.GameState != null)
            {
                model.CustomProperties["gold"] = dto.GameState.Gold;
                model.CustomProperties["reputation"] = dto.GameState.Reputation;
                model.CustomProperties["faction_affiliations"] = dto.GameState.FactionAffiliations;
                model.CustomProperties["status_effects"] = dto.GameState.StatusEffects;
            }
            
            // Narrative
            if (dto.Narrative != null)
            {
                model.CustomProperties["narrative"] = dto.Narrative;
            }
            
            // Metadata
            if (dto.Metadata != null)
            {
                if (DateTime.TryParse(dto.Metadata.CreatedAt, out DateTime createdAt))
                    model.CreatedAt = createdAt;
                if (DateTime.TryParse(dto.Metadata.UpdatedAt, out DateTime updatedAt))
                    model.UpdatedAt = updatedAt;
            }
            
            // Cache the model
            _characterModels[dto.Id] = model;
            
            return model;
        }

        /// <summary>
        /// Get a cached CharacterModel
        /// </summary>
        public CharacterModel GetCharacterModel(string characterId)
        {
            if (_characterModels.TryGetValue(characterId, out CharacterModel model))
            {
                return model;
            }
            
            // Try to convert from cached DTO
            if (_characterCache.TryGetValue(characterId, out CharacterResponseDTO dto))
            {
                return ConvertToCharacterModel(dto);
            }
            
            return null;
        }

        #endregion

        #region WebSocket Integration

        private void HandleCharacterWebSocketUpdate(string message)
        {
            try
            {
                var updateData = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
                if (updateData.TryGetValue("character_id", out object characterIdObj))
                {
                    string characterId = characterIdObj.ToString();
                    
                    // Refresh character data
                    GetCharacter(characterId, (success, character) =>
                    {
                        if (success && character != null)
                        {
                            if (debugLogging)
                                Debug.Log($"[CharacterService] Character {character.CharacterName} updated via WebSocket");
                        }
                    });
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[CharacterService] Error handling character WebSocket update: {e.Message}");
            }
        }

        private void HandleCharacterLevelUpEvent(string message)
        {
            try
            {
                var levelUpData = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
                if (levelUpData.TryGetValue("character", out object characterObj))
                {
                    var character = JsonConvert.DeserializeObject<CharacterResponseDTO>(characterObj.ToString());
                    if (character != null)
                    {
                        _characterCache[character.Id] = character;
                        OnCharacterLevelUp?.Invoke(character);
                        
                        if (debugLogging)
                            Debug.Log($"[CharacterService] Character {character.CharacterName} leveled up to {character.Level}!");
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[CharacterService] Error handling character level up event: {e.Message}");
            }
        }

        private void HandleCharacterProgressionEvent(string message)
        {
            try
            {
                var progressionData = JsonConvert.DeserializeObject<CharacterProgressionResponseDTO>(message);
                if (progressionData != null)
                {
                    // Refresh character to get updated data
                    GetCharacter(progressionData.CharacterId, (success, character) =>
                    {
                        if (success && character != null)
                        {
                            if (debugLogging)
                                Debug.Log($"[CharacterService] Character progression event: {progressionData.EventType} for {character.CharacterName}");
                        }
                    });
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[CharacterService] Error handling character progression event: {e.Message}");
            }
        }

        #endregion

        #region Auto Sync

        private void StartAutoSync()
        {
            if (_autoSyncCoroutine != null)
            {
                StopCoroutine(_autoSyncCoroutine);
            }
            _autoSyncCoroutine = StartCoroutine(AutoSyncCoroutine());
        }

        private IEnumerator AutoSyncCoroutine()
        {
            while (autoSyncCharacters)
            {
                yield return new WaitForSeconds(syncInterval);
                
                if (_characterCache.Count > 0)
                {
                    // Sync active characters
                    var characterIds = new List<string>(_characterCache.Keys);
                    foreach (string characterId in characterIds)
                    {
                        GetCharacter(characterId, (success, character) =>
                        {
                            // Character automatically updated in cache
                        });
                        
                        // Don't spam the server
                        yield return new WaitForSeconds(1f);
                    }
                }
            }
        }

        #endregion

        #region Public Utility Methods

        /// <summary>
        /// Get all cached characters
        /// </summary>
        public List<CharacterResponseDTO> GetCachedCharacters()
        {
            return new List<CharacterResponseDTO>(_characterCache.Values);
        }

        /// <summary>
        /// Clear character cache
        /// </summary>
        public void ClearCache()
        {
            _characterCache.Clear();
            _characterModels.Clear();
        }

        /// <summary>
        /// Check if character is cached
        /// </summary>
        public bool IsCharacterCached(string characterId)
        {
            return _characterCache.ContainsKey(characterId);
        }

        #endregion

        #region Save/Load Support

        /// <summary>
        /// Get player position for save system
        /// </summary>
        public Vector3 GetPlayerPosition()
        {
            // Get player GameObject and return position
            var player = GameObject.FindGameObjectWithTag("Player");
            return player != null ? player.transform.position : Vector3.zero;
        }

        /// <summary>
        /// Get player rotation for save system
        /// </summary>
        public Vector3 GetPlayerRotation()
        {
            // Get player GameObject and return rotation
            var player = GameObject.FindGameObjectWithTag("Player");
            return player != null ? player.transform.eulerAngles : Vector3.zero;
        }

        /// <summary>
        /// Get player health for save system
        /// </summary>
        public float GetPlayerHealth()
        {
            // TODO: Implement health system integration
            return 100f; // Placeholder
        }

        /// <summary>
        /// Get player level for save system
        /// </summary>
        public int GetPlayerLevel()
        {
            // TODO: Get from current player character
            return 1; // Placeholder
        }

        /// <summary>
        /// Get player experience for save system
        /// </summary>
        public int GetPlayerExperience()
        {
            // TODO: Get from current player character
            return 0; // Placeholder
        }

        /// <summary>
        /// Get player stats for save system
        /// </summary>
        public Dictionary<string, object> GetPlayerStats()
        {
            // TODO: Get from current player character
            return new Dictionary<string, object>(); // Placeholder
        }

        /// <summary>
        /// Set player position from save system
        /// </summary>
        public void SetPlayerPosition(Vector3 position)
        {
            var player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
            {
                player.transform.position = position;
            }
        }

        /// <summary>
        /// Set player rotation from save system
        /// </summary>
        public void SetPlayerRotation(Vector3 rotation)
        {
            var player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
            {
                player.transform.eulerAngles = rotation;
            }
        }

        /// <summary>
        /// Set player health from save system
        /// </summary>
        public void SetPlayerHealth(float health)
        {
            // TODO: Implement health system integration
        }

        /// <summary>
        /// Set player level from save system
        /// </summary>
        public void SetPlayerLevel(int level)
        {
            // TODO: Set current player character level
        }

        /// <summary>
        /// Set player experience from save system
        /// </summary>
        public void SetPlayerExperience(int experience)
        {
            // TODO: Set current player character experience
        }

        /// <summary>
        /// Set player stats from save system
        /// </summary>
        public void SetPlayerStats(Dictionary<string, object> stats)
        {
            // TODO: Set current player character stats
        }

        /// <summary>
        /// Get character save data for save system
        /// </summary>
        public async System.Threading.Tasks.Task<Dictionary<string, object>> GetCharacterSaveDataAsync()
        {
            var saveData = new Dictionary<string, object>();
            
            // Convert cached characters to save format
            var characterList = new List<object>();
            foreach (var character in _characterCache.Values)
            {
                characterList.Add(new
                {
                    id = character.Id,
                    characterName = character.CharacterName,
                    race = character.Race,
                    characterClass = character.CharacterClass,
                    level = character.Level,
                    experience = character.Experience,
                    hitPoints = character.HitPoints,
                    armorClass = character.ArmorClass,
                    abilities = character.Abilities,
                    skills = character.Skills,
                    isActive = character.IsActive,
                    createdAt = character.CreatedAt?.ToString("O"),
                    updatedAt = character.UpdatedAt?.ToString("O")
                });
            }
            
            saveData["characters"] = characterList;
            saveData["cacheTimestamp"] = DateTime.UtcNow.ToString("O");
            
            return saveData;
        }

        /// <summary>
        /// Apply character save data from save system
        /// </summary>
        public async System.Threading.Tasks.Task ApplyCharacterSaveDataAsync(Dictionary<string, object> saveData)
        {
            try
            {
                if (saveData.ContainsKey("characters"))
                {
                    _characterCache.Clear();
                    _characterModels.Clear();
                    
                    var charactersData = saveData["characters"] as List<object>;
                    if (charactersData != null)
                    {
                        foreach (var charData in charactersData)
                        {
                            // Convert back to CharacterResponseDTO
                            var jsonString = JsonConvert.SerializeObject(charData);
                            var character = JsonConvert.DeserializeObject<CharacterResponseDTO>(jsonString);
                            
                            if (character != null)
                            {
                                _characterCache[character.Id] = character;
                            }
                        }
                    }
                    
                    // Notify listeners of character reload
                    var characterList = new List<CharacterResponseDTO>(_characterCache.Values);
                    OnCharactersLoaded?.Invoke(characterList);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[CharacterService] Error applying character save data: {ex.Message}");
            }
        }

        #endregion
    }
} 