using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine.Networking;
using UnityEngine;
using VDM.Runtime.Core.Services;
using VDM.Runtime.Character.Models;
using VDM.Runtime.Integration;


namespace VDM.Runtime.Character.Services
{
    /// <summary>
    /// Service for managing character data communication with the backend
    /// Handles character CRUD operations, progression tracking, and real-time synchronization
    /// Migrated from legacy CharacterService to new Character/Services structure
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
        /// Get a character by ID
        /// </summary>
        public void GetCharacter(string characterId, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            // Check cache first
            if (_characterCache.ContainsKey(characterId))
            {
                callback?.Invoke(true, _characterCache[characterId]);
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
                        
                        if (debugLogging)
                            Debug.Log($"[CharacterService] Retrieved character: {character.CharacterName}");
                    }
                }
            });

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Update a character
        /// </summary>
        public void UpdateCharacter(string characterId, CharacterUpdateDTO updateData, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(UpdateCharacterCoroutine(characterId, updateData, callback));
        }

        private IEnumerator UpdateCharacterCoroutine(string characterId, CharacterUpdateDTO updateData, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            yield return PutRequestCoroutine($"/characters/{characterId}", updateData, (requestSuccess, response) =>
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
                            Debug.Log($"[CharacterService] Updated character: {character.CharacterName}");
                    }
                }
            });

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Delete a character
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
                    OnCharacterDeleted?.Invoke(characterId);
                    
                    if (debugLogging)
                        Debug.Log($"[CharacterService] Deleted character: {characterId}");
                }
            });

            callback?.Invoke(success);
        }

        /// <summary>
        /// Get a list of characters with pagination
        /// </summary>
        public void GetCharacters(int page = 1, int pageSize = 10, string status = null, Action<bool, CharacterListResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(GetCharactersCoroutine(page, pageSize, status, callback));
        }

        private IEnumerator GetCharactersCoroutine(int page, int pageSize, string status, Action<bool, CharacterListResponseDTO> callback)
        {
            string endpoint = $"/characters?page={page}&page_size={pageSize}";
            if (!string.IsNullOrEmpty(status))
            {
                endpoint += $"&status={status}";
            }

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

        #region WebSocket Event Handlers

        private void HandleCharacterWebSocketUpdate(string message)
        {
            try
            {
                var character = JsonConvert.DeserializeObject<CharacterResponseDTO>(message);
                if (character != null)
                {
                    _characterCache[character.Id] = character;
                    OnCharacterUpdated?.Invoke(character);
                    
                    if (debugLogging)
                        Debug.Log($"[CharacterService] Character {character.CharacterName} updated via WebSocket");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[CharacterService] Error handling character update event: {e.Message}");
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
                                Debug.Log($"[CharacterService] Character progression event: {progressionData.ProgressionType} for {character.CharacterName}");
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
                    if (debugLogging)
                        Debug.Log($"[CharacterService] Auto-syncing {_characterCache.Count} cached characters");
                    
                    // Sync cached characters
                    var characterIds = new List<string>(_characterCache.Keys);
                    foreach (var characterId in characterIds)
                    {
                        GetCharacter(characterId, null);
                        yield return new WaitForSeconds(0.1f); // Small delay between requests
                    }
                }
            }
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Get cached character without making a network request
        /// </summary>
        public CharacterResponseDTO GetCachedCharacter(string characterId)
        {
            return _characterCache.ContainsKey(characterId) ? _characterCache[characterId] : null;
        }

        /// <summary>
        /// Clear the character cache
        /// </summary>
        public void ClearCache()
        {
            _characterCache.Clear();
            if (debugLogging)
                Debug.Log("[CharacterService] Character cache cleared");
        }

        /// <summary>
        /// Get all cached characters
        /// </summary>
        public Dictionary<string, CharacterResponseDTO> GetAllCachedCharacters()
        {
            return new Dictionary<string, CharacterResponseDTO>(_characterCache);
        }

        #endregion
    }
} 