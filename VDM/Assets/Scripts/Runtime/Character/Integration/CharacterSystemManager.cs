using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Runtime.Core.Integration;
using VDM.Runtime.Character.Models;
using VDM.Runtime.Character.Services;
using VDM.Runtime.Character.UI;


namespace VDM.Runtime.Character.Integration
{
    /// <summary>
    /// Character System Manager
    /// Manages the character system lifecycle, integration with Unity, and coordination with other systems
    /// </summary>
    public class CharacterSystemManager : SystemManager
    {
        [Header("Character System Configuration")]
        [SerializeField] private bool autoLoadCharacters = true;
        [SerializeField] private bool enableCharacterSync = true;
        [SerializeField] private float autoSaveInterval = 300f; // 5 minutes

        [Header("UI References")]
        [SerializeField] private CharacterPanel characterPanel;
        [SerializeField] private GameObject characterListPrefab;
        [SerializeField] private Transform characterUIContainer;

        // Services
        private CharacterService _characterService;
        
        // Current state
        private CharacterResponseDTO _activeCharacter;
        private List<CharacterResponseDTO> _loadedCharacters = new List<CharacterResponseDTO>();
        
        // Auto save
        private float _lastAutoSave;

        // Events
        public event Action<CharacterResponseDTO> OnActiveCharacterChanged;
        public event Action<List<CharacterResponseDTO>> OnCharactersLoaded;
        public event Action<CharacterResponseDTO> OnCharacterCreated;
        public event Action<CharacterResponseDTO> OnCharacterUpdated;
        public event Action<string> OnCharacterDeleted;

        protected override void InitializeSystem()
        {
            base.InitializeSystem();

            // Initialize character service
            _characterService = GetOrCreateService<CharacterService>();
            
            if (_characterService != null)
            {
                // Subscribe to service events
                _characterService.OnCharacterCreated += HandleCharacterCreated;
                _characterService.OnCharacterUpdated += HandleCharacterUpdated;
                _characterService.OnCharacterDeleted += HandleCharacterDeleted;
                _characterService.OnCharactersLoaded += HandleCharactersLoaded;
                _characterService.OnCharacterLevelUp += HandleCharacterLevelUp;
                _characterService.OnCharacterSkillIncreased += HandleCharacterSkillIncreased;
                _characterService.OnCharacterAbilityGained += HandleCharacterAbilityGained;
            }

            // Setup UI if available
            SetupUI();

            // Auto load characters if enabled
            if (autoLoadCharacters)
            {
                LoadCharacters();
            }

            _lastAutoSave = Time.time;
        }

        protected override void OnDestroy()
        {
            // Cleanup service events
            if (_characterService != null)
            {
                _characterService.OnCharacterCreated -= HandleCharacterCreated;
                _characterService.OnCharacterUpdated -= HandleCharacterUpdated;
                _characterService.OnCharacterDeleted -= HandleCharacterDeleted;
                _characterService.OnCharactersLoaded -= HandleCharactersLoaded;
                _characterService.OnCharacterLevelUp -= HandleCharacterLevelUp;
                _characterService.OnCharacterSkillIncreased -= HandleCharacterSkillIncreased;
                _characterService.OnCharacterAbilityGained -= HandleCharacterAbilityGained;
            }

            base.OnDestroy();
        }

        private void Update()
        {
            // Auto save functionality
            if (enableCharacterSync && _activeCharacter != null && 
                Time.time - _lastAutoSave > autoSaveInterval)
            {
                AutoSaveActiveCharacter();
                _lastAutoSave = Time.time;
            }
        }

        private void SetupUI()
        {
            if (characterPanel != null)
            {
                characterPanel.OnCharacterSelected += HandleCharacterSelected;
                characterPanel.OnEditRequested += HandleEditCharacterRequested;
                characterPanel.OnProgressionRequested += HandleProgressionRequested;
                characterPanel.OnInventoryRequested += HandleInventoryRequested;
                characterPanel.OnRelationshipsRequested += HandleRelationshipsRequested;
            }
        }

        #region Public API

        /// <summary>
        /// Set the active character
        /// </summary>
        public void SetActiveCharacter(CharacterResponseDTO character)
        {
            if (character == null) return;

            _activeCharacter = character;
            
            // Update UI
            if (characterPanel != null)
            {
                characterPanel.DisplayCharacter(character);
            }

            OnActiveCharacterChanged?.Invoke(character);
            
            if (debugLogging)
                Debug.Log($"[CharacterSystemManager] Active character set to: {character.CharacterName}");
        }

        /// <summary>
        /// Set active character by ID
        /// </summary>
        public void SetActiveCharacterById(string characterId)
        {
            if (_characterService == null) return;

            _characterService.GetCharacter(characterId, (success, character) =>
            {
                if (success && character != null)
                {
                    SetActiveCharacter(character);
                }
                else
                {
                    Debug.LogError($"[CharacterSystemManager] Failed to load character {characterId}");
                }
            });
        }

        /// <summary>
        /// Get the currently active character
        /// </summary>
        public CharacterResponseDTO GetActiveCharacter()
        {
            return _activeCharacter;
        }

        /// <summary>
        /// Load all characters
        /// </summary>
        public void LoadCharacters(int page = 1, int pageSize = 50)
        {
            if (_characterService == null)
            {
                Debug.LogError("[CharacterSystemManager] CharacterService not available!");
                return;
            }

            _characterService.GetCharacters(page, pageSize, null, (success, result) =>
            {
                if (success && result != null)
                {
                    _loadedCharacters = result.Characters ?? new List<CharacterResponseDTO>();
                    OnCharactersLoaded?.Invoke(_loadedCharacters);
                    
                    if (debugLogging)
                        Debug.Log($"[CharacterSystemManager] Loaded {_loadedCharacters.Count} characters");
                }
                else
                {
                    Debug.LogError("[CharacterSystemManager] Failed to load characters");
                }
            });
        }

        /// <summary>
        /// Create a new character
        /// </summary>
        public void CreateCharacter(CharacterCreateDTO characterData)
        {
            if (_characterService == null)
            {
                Debug.LogError("[CharacterSystemManager] CharacterService not available!");
                return;
            }

            _characterService.CreateCharacter(characterData, (success, character) =>
            {
                if (success && character != null)
                {
                    // Add to loaded characters
                    _loadedCharacters.Add(character);
                    OnCharacterCreated?.Invoke(character);
                    
                    // Set as active if no current active character
                    if (_activeCharacter == null)
                    {
                        SetActiveCharacter(character);
                    }
                    
                    if (debugLogging)
                        Debug.Log($"[CharacterSystemManager] Created character: {character.CharacterName}");
                }
                else
                {
                    Debug.LogError("[CharacterSystemManager] Failed to create character");
                }
            });
        }

        /// <summary>
        /// Update a character
        /// </summary>
        public void UpdateCharacter(string characterId, CharacterUpdateDTO updateData)
        {
            if (_characterService == null)
            {
                Debug.LogError("[CharacterSystemManager] CharacterService not available!");
                return;
            }

            _characterService.UpdateCharacter(characterId, updateData, (success, character) =>
            {
                if (success && character != null)
                {
                    // Update in loaded characters list
                    int index = _loadedCharacters.FindIndex(c => c.Id == character.Id);
                    if (index >= 0)
                    {
                        _loadedCharacters[index] = character;
                    }
                    
                    // Update active character if it's the same one
                    if (_activeCharacter != null && _activeCharacter.Id == character.Id)
                    {
                        _activeCharacter = character;
                        OnActiveCharacterChanged?.Invoke(character);
                    }
                    
                    OnCharacterUpdated?.Invoke(character);
                    
                    if (debugLogging)
                        Debug.Log($"[CharacterSystemManager] Updated character: {character.CharacterName}");
                }
                else
                {
                    Debug.LogError($"[CharacterSystemManager] Failed to update character {characterId}");
                }
            });
        }

        /// <summary>
        /// Delete a character
        /// </summary>
        public void DeleteCharacter(string characterId)
        {
            if (_characterService == null)
            {
                Debug.LogError("[CharacterSystemManager] CharacterService not available!");
                return;
            }

            _characterService.DeleteCharacter(characterId, (success) =>
            {
                if (success)
                {
                    // Remove from loaded characters
                    _loadedCharacters.RemoveAll(c => c.Id == characterId);
                    
                    // Clear active character if it was deleted
                    if (_activeCharacter != null && _activeCharacter.Id == characterId)
                    {
                        _activeCharacter = null;
                        OnActiveCharacterChanged?.Invoke(null);
                        
                        if (characterPanel != null)
                        {
                            characterPanel.DisplayCharacter(null);
                        }
                    }
                    
                    OnCharacterDeleted?.Invoke(characterId);
                    
                    if (debugLogging)
                        Debug.Log($"[CharacterSystemManager] Deleted character: {characterId}");
                }
                else
                {
                    Debug.LogError($"[CharacterSystemManager] Failed to delete character {characterId}");
                }
            });
        }

        /// <summary>
        /// Grant experience to active character
        /// </summary>
        public void GrantExperienceToActive(int amount, string source = "")
        {
            if (_activeCharacter == null)
            {
                Debug.LogWarning("[CharacterSystemManager] No active character to grant experience to");
                return;
            }

            var xpGrant = new ExperienceGrantDTO
            {
                Amount = amount,
                Source = source
            };

            _characterService.GrantExperience(_activeCharacter.Id, xpGrant);
        }

        /// <summary>
        /// Increase skill for active character
        /// </summary>
        public void IncreaseSkillForActive(string skillName, int amount = 1)
        {
            if (_activeCharacter == null)
            {
                Debug.LogWarning("[CharacterSystemManager] No active character to increase skill for");
                return;
            }

            var skillData = new SkillIncreaseDTO
            {
                SkillName = skillName,
                IncreaseAmount = amount
            };

            _characterService.IncreaseSkill(_activeCharacter.Id, skillData);
        }

        /// <summary>
        /// Add ability to active character
        /// </summary>
        public void AddAbilityToActive(string abilityName)
        {
            if (_activeCharacter == null)
            {
                Debug.LogWarning("[CharacterSystemManager] No active character to add ability to");
                return;
            }

            var abilityData = new AbilitySelectionDTO
            {
                AbilityName = abilityName
            };

            _characterService.AddAbility(_activeCharacter.Id, abilityData);
        }

        /// <summary>
        /// Get all loaded characters
        /// </summary>
        public List<CharacterResponseDTO> GetLoadedCharacters()
        {
            return new List<CharacterResponseDTO>(_loadedCharacters);
        }

        #endregion

        #region Event Handlers

        private void HandleCharacterCreated(CharacterResponseDTO character)
        {
            OnCharacterCreated?.Invoke(character);
        }

        private void HandleCharacterUpdated(CharacterResponseDTO character)
        {
            OnCharacterUpdated?.Invoke(character);
        }

        private void HandleCharacterDeleted(string characterId)
        {
            OnCharacterDeleted?.Invoke(characterId);
        }

        private void HandleCharactersLoaded(List<CharacterResponseDTO> characters)
        {
            OnCharactersLoaded?.Invoke(characters);
        }

        private void HandleCharacterLevelUp(CharacterResponseDTO character)
        {
            // Special handling for level up events
            ShowNotification($"{character.CharacterName} reached level {character.Level}!", NotificationType.Success);
            
            // Update active character if it's the same one
            if (_activeCharacter != null && _activeCharacter.Id == character.Id)
            {
                _activeCharacter = character;
                OnActiveCharacterChanged?.Invoke(character);
            }
        }

        private void HandleCharacterSkillIncreased(CharacterResponseDTO character, string skillName)
        {
            ShowNotification($"{character.CharacterName} improved {skillName}!", NotificationType.Info);
        }

        private void HandleCharacterAbilityGained(CharacterResponseDTO character, string abilityName)
        {
            ShowNotification($"{character.CharacterName} gained {abilityName}!", NotificationType.Success);
        }

        private void HandleCharacterSelected(CharacterResponseDTO character)
        {
            SetActiveCharacter(character);
        }

        private void HandleEditCharacterRequested(CharacterResponseDTO character)
        {
            // TODO: Open character editing interface
            Debug.Log($"[CharacterSystemManager] Edit requested for character: {character?.CharacterName}");
        }

        private void HandleProgressionRequested(CharacterResponseDTO character)
        {
            // TODO: Open character progression interface
            Debug.Log($"[CharacterSystemManager] Progression requested for character: {character?.CharacterName}");
        }

        private void HandleInventoryRequested(CharacterResponseDTO character)
        {
            // TODO: Open character inventory interface
            Debug.Log($"[CharacterSystemManager] Inventory requested for character: {character?.CharacterName}");
        }

        private void HandleRelationshipsRequested(CharacterResponseDTO character)
        {
            // TODO: Open character relationships interface
            Debug.Log($"[CharacterSystemManager] Relationships requested for character: {character?.CharacterName}");
        }

        #endregion

        #region Auto Save

        private void AutoSaveActiveCharacter()
        {
            if (_activeCharacter == null || _characterService == null) return;

            // Create update DTO with current state
            var updateData = new CharacterUpdateDTO
            {
                CharacterName = _activeCharacter.CharacterName,
                // Add other fields that might have changed
            };

            // Only save if there are actual changes
            // TODO: Implement change tracking
            
            if (debugLogging)
                Debug.Log($"[CharacterSystemManager] Auto-saving character: {_activeCharacter.CharacterName}");
        }

        #endregion

        #region Utility Methods

        private void ShowNotification(string message, NotificationType type)
        {
            // TODO: Integrate with notification system
            Debug.Log($"[CharacterSystemManager] {type}: {message}");
        }

        #endregion
    }

    public enum NotificationType
    {
        Info,
        Success,
        Warning,
        Error
    }
} 