using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.DTOs.Core;
using VDM.Runtime.Character;
using VDM.Systems;


namespace VDM.Runtime.Services
{
    /// <summary>
    /// Manages character progression UI/UX and coordinates with backend via CharacterService
    /// Handles level ups, ability selection (3 per level), and skill allocation (max rank = level + 3)
    /// </summary>
    public class CharacterProgressionManager : MonoBehaviour
    {
        [Header("Progression Configuration")]
        [SerializeField] private bool showProgressionUI = true;
        [SerializeField] private float levelUpAnimationDuration = 2f;
        
        // Events for progression notifications
        public event Action<CharacterResponseDTO, int> OnLevelUp;
        public event Action<CharacterResponseDTO, List<string>> OnAbilitiesAvailable;
        public event Action<CharacterResponseDTO, string> OnSkillIncreased;
        public event Action<CharacterResponseDTO, string> OnAbilitySelected;
        public event Action<CharacterResponseDTO> OnProgressionComplete;

        // Service dependencies
        private CharacterService _characterService;
        private WebSocketManager _webSocketManager;
        
        // Progression state tracking
        private Dictionary<string, ProgressionSession> _activeProgressionSessions = new Dictionary<string, ProgressionSession>();
        
        // Available abilities for selection (should be loaded from game data)
        private List<CharacterAbilityTemplate> _availableAbilities = new List<CharacterAbilityTemplate>();

        private void Awake()
        {
            // Find required services
            _characterService = FindObjectOfType<CharacterService>();
            _webSocketManager = FindObjectOfType<WebSocketManager>();
            
            if (_characterService == null)
            {
                Debug.LogError("[CharacterProgressionManager] CharacterService not found! Character progression will not work.");
                return;
            }
            
            // Subscribe to character service events
            _characterService.OnCharacterLevelUp += HandleCharacterLevelUp;
            _characterService.OnCharacterSkillIncreased += HandleSkillIncreased;
            _characterService.OnCharacterAbilityGained += HandleAbilityGained;
            
            // Load available abilities from game data
            LoadAvailableAbilities();
        }

        private void OnDestroy()
        {
            // Unsubscribe from events
            if (_characterService != null)
            {
                _characterService.OnCharacterLevelUp -= HandleCharacterLevelUp;
                _characterService.OnCharacterSkillIncreased -= HandleSkillIncreased;
                _characterService.OnCharacterAbilityGained -= HandleAbilityGained;
            }
        }

        #region Experience and Level Management

        /// <summary>
        /// Grant experience to a character (delegates to backend)
        /// </summary>
        public void GrantExperience(string characterId, int amount, string source = "Unknown", string notes = "")
        {
            if (_characterService == null)
            {
                Debug.LogError("[CharacterProgressionManager] CharacterService not available");
                return;
            }

            var xpGrant = new ExperienceGrantDTO
            {
                Amount = amount,
                Source = source,
                Notes = notes
            };

            Debug.Log($"[CharacterProgressionManager] Granting {amount} XP to character {characterId} from {source}");

            _characterService.GrantExperience(characterId, xpGrant, (success, character) =>
            {
                if (success && character != null)
                {
                    Debug.Log($"[CharacterProgressionManager] Successfully granted XP. Character is now level {character.Level}");
                }
                else
                {
                    Debug.LogError($"[CharacterProgressionManager] Failed to grant experience to character {characterId}");
                }
            });
        }

        /// <summary>
        /// Handle level up event from character service
        /// </summary>
        private void HandleCharacterLevelUp(CharacterResponseDTO character)
        {
            Debug.Log($"[CharacterProgressionManager] Character {character.CharacterName} leveled up to {character.Level}!");
            
            // Create or update progression session
            if (!_activeProgressionSessions.ContainsKey(character.Id))
            {
                _activeProgressionSessions[character.Id] = new ProgressionSession(character);
            }
            
            var session = _activeProgressionSessions[character.Id];
            session.NewLevel = character.Level;
            
            // Development Bible: 3 abilities per level
            int abilitiesToSelect = 3;
            session.AbilitiesToSelect = abilitiesToSelect;
            session.AbilitiesSelected = 0;
            
            // Fire level up event
            OnLevelUp?.Invoke(character, character.Level);
            
            // Show ability selection UI if configured
            if (showProgressionUI)
            {
                ShowAbilitySelectionUI(character, abilitiesToSelect);
            }
        }

        #endregion

        #region Ability Selection

        /// <summary>
        /// Load available abilities from game data
        /// </summary>
        private void LoadAvailableAbilities()
        {
            // TODO: Load from actual game data files
            // For now, create some example abilities
            _availableAbilities = new List<CharacterAbilityTemplate>
            {
                new CharacterAbilityTemplate("Combat Reflexes", "Gain +2 initiative bonus", new List<string>()),
                new CharacterAbilityTemplate("Arcane Focus", "Increase mana regeneration by 25%", new List<string>()),
                new CharacterAbilityTemplate("Iron Will", "Resistance to mental effects", new List<string>()),
                new CharacterAbilityTemplate("Fleet Footed", "Increase movement speed by 5 feet", new List<string>()),
                new CharacterAbilityTemplate("Keen Senses", "Advantage on perception checks", new List<string>()),
                new CharacterAbilityTemplate("Weapon Mastery", "Proficiency with martial weapons", new List<string>()),
                new CharacterAbilityTemplate("Spell Focus", "Increase spell save DC by 1", new List<string> { "Arcane Focus" }),
                new CharacterAbilityTemplate("Improved Reflexes", "Additional +2 initiative bonus", new List<string> { "Combat Reflexes" }),
                new CharacterAbilityTemplate("Battle Hardened", "Reduce damage taken by 1 per hit", new List<string> { "Iron Will" }),
                new CharacterAbilityTemplate("Master Archer", "Increased range with ranged weapons", new List<string> { "Weapon Mastery" })
            };
            
            Debug.Log($"[CharacterProgressionManager] Loaded {_availableAbilities.Count} available abilities");
        }

        /// <summary>
        /// Get abilities available for a character based on their current abilities and level
        /// </summary>
        public List<CharacterAbilityTemplate> GetAvailableAbilities(CharacterResponseDTO character)
        {
            var available = new List<CharacterAbilityTemplate>();
            var currentAbilities = new HashSet<string>(character.Abilities);
            
            foreach (var ability in _availableAbilities)
            {
                // Skip if character already has this ability
                if (currentAbilities.Contains(ability.Name))
                    continue;
                
                // Check prerequisites
                bool prerequisitesMet = true;
                foreach (var prerequisite in ability.Prerequisites)
                {
                    if (!currentAbilities.Contains(prerequisite))
                    {
                        prerequisitesMet = false;
                        break;
                    }
                }
                
                if (prerequisitesMet)
                {
                    available.Add(ability);
                }
            }
            
            return available;
        }

        /// <summary>
        /// Select an ability for a character (delegates to backend)
        /// </summary>
        public void SelectAbility(string characterId, string abilityName)
        {
            if (_characterService == null)
            {
                Debug.LogError("[CharacterProgressionManager] CharacterService not available");
                return;
            }

            var abilitySelection = new AbilitySelectionDTO
            {
                AbilityName = abilityName,
                PrerequisitesMet = true // We validate this on the frontend before calling
            };

            Debug.Log($"[CharacterProgressionManager] Selecting ability {abilityName} for character {characterId}");

            _characterService.AddAbility(characterId, abilitySelection, (success, character) =>
            {
                if (success && character != null)
                {
                    Debug.Log($"[CharacterProgressionManager] Successfully added ability {abilityName}");
                    
                    // Update progression session
                    if (_activeProgressionSessions.ContainsKey(characterId))
                    {
                        var session = _activeProgressionSessions[characterId];
                        session.AbilitiesSelected++;
                        session.SelectedAbilities.Add(abilityName);
                        
                        // Check if progression is complete
                        if (session.AbilitiesSelected >= session.AbilitiesToSelect)
                        {
                            CompleteProgression(characterId, character);
                        }
                        else if (showProgressionUI)
                        {
                            // Show ability selection for remaining choices
                            int remaining = session.AbilitiesToSelect - session.AbilitiesSelected;
                            ShowAbilitySelectionUI(character, remaining);
                        }
                    }
                }
                else
                {
                    Debug.LogError($"[CharacterProgressionManager] Failed to add ability {abilityName} to character {characterId}");
                }
            });
        }

        /// <summary>
        /// Show ability selection UI (placeholder for actual UI implementation)
        /// </summary>
        private void ShowAbilitySelectionUI(CharacterResponseDTO character, int choicesRemaining)
        {
            var availableAbilities = GetAvailableAbilities(character);
            
            Debug.Log($"[CharacterProgressionManager] Showing ability selection UI for {character.CharacterName}");
            Debug.Log($"Choices remaining: {choicesRemaining}");
            Debug.Log($"Available abilities: {string.Join(", ", availableAbilities.ConvertAll(a => a.Name))}");
            
            // Fire event for UI to handle
            OnAbilitiesAvailable?.Invoke(character, availableAbilities.ConvertAll(a => a.Name));
            
            // TODO: Show actual UI panel for ability selection
            // This should display available abilities with descriptions and prerequisites
            // Allow player to select the required number of abilities
        }

        /// <summary>
        /// Handle ability gained event from character service
        /// </summary>
        private void HandleAbilityGained(CharacterResponseDTO character, string abilityName)
        {
            Debug.Log($"[CharacterProgressionManager] Character {character.CharacterName} gained ability: {abilityName}");
            OnAbilitySelected?.Invoke(character, abilityName);
        }

        #endregion

        #region Skill Management

        /// <summary>
        /// Increase a character's skill (delegates to backend with validation)
        /// </summary>
        public void IncreaseSkill(string characterId, string skillName, int increaseAmount = 1)
        {
            if (_characterService == null)
            {
                Debug.LogError("[CharacterProgressionManager] CharacterService not available");
                return;
            }

            // Get character first to validate skill limits
            _characterService.GetCharacter(characterId, (success, character) =>
            {
                if (success && character != null)
                {
                    // Development Bible: max skill rank = level + 3
                    int maxRank = character.Level + 3;
                    int currentRank = character.Skills.ContainsKey(skillName) ? character.Skills[skillName] : 0;
                    int newRank = currentRank + increaseAmount;
                    
                    if (newRank > maxRank)
                    {
                        Debug.LogWarning($"[CharacterProgressionManager] Cannot increase {skillName} beyond max rank {maxRank} for level {character.Level}");
                        return;
                    }
                    
                    var skillIncrease = new SkillIncreaseDTO
                    {
                        SkillName = skillName,
                        IncreaseAmount = increaseAmount
                    };

                    Debug.Log($"[CharacterProgressionManager] Increasing {skillName} by {increaseAmount} for character {characterId}");

                    _characterService.IncreaseSkill(characterId, skillIncrease, (skillSuccess, updatedCharacter) =>
                    {
                        if (skillSuccess && updatedCharacter != null)
                        {
                            Debug.Log($"[CharacterProgressionManager] Successfully increased {skillName} to {updatedCharacter.Skills[skillName]}");
                        }
                        else
                        {
                            Debug.LogError($"[CharacterProgressionManager] Failed to increase skill {skillName} for character {characterId}");
                        }
                    });
                }
                else
                {
                    Debug.LogError($"[CharacterProgressionManager] Failed to get character {characterId} for skill validation");
                }
            });
        }

        /// <summary>
        /// Get maximum allowed skill rank for a character level (Development Bible rule)
        /// </summary>
        public int GetMaxSkillRank(int characterLevel)
        {
            return characterLevel + 3;
        }

        /// <summary>
        /// Validate if a skill increase is allowed
        /// </summary>
        public bool CanIncreaseSkill(CharacterResponseDTO character, string skillName, int increaseAmount = 1)
        {
            int maxRank = GetMaxSkillRank(character.Level);
            int currentRank = character.Skills.ContainsKey(skillName) ? character.Skills[skillName] : 0;
            int newRank = currentRank + increaseAmount;
            
            return newRank <= maxRank;
        }

        /// <summary>
        /// Handle skill increased event from character service
        /// </summary>
        private void HandleSkillIncreased(CharacterResponseDTO character, string skillName)
        {
            Debug.Log($"[CharacterProgressionManager] Character {character.CharacterName} increased skill: {skillName}");
            OnSkillIncreased?.Invoke(character, skillName);
        }

        #endregion

        #region Progression Session Management

        /// <summary>
        /// Complete a character's progression session
        /// </summary>
        private void CompleteProgression(string characterId, CharacterResponseDTO character)
        {
            if (_activeProgressionSessions.ContainsKey(characterId))
            {
                var session = _activeProgressionSessions[characterId];
                Debug.Log($"[CharacterProgressionManager] Completing progression for {character.CharacterName} - Level {session.NewLevel}");
                Debug.Log($"Abilities selected: {string.Join(", ", session.SelectedAbilities)}");
                
                // Remove completed session
                _activeProgressionSessions.Remove(characterId);
                
                // Fire completion event
                OnProgressionComplete?.Invoke(character);
            }
        }

        /// <summary>
        /// Get active progression session for a character
        /// </summary>
        public ProgressionSession GetProgressionSession(string characterId)
        {
            return _activeProgressionSessions.ContainsKey(characterId) ? _activeProgressionSessions[characterId] : null;
        }

        /// <summary>
        /// Check if a character has an active progression session
        /// </summary>
        public bool HasActiveProgression(string characterId)
        {
            return _activeProgressionSessions.ContainsKey(characterId);
        }

        #endregion

        #region Public Utility Methods

        /// <summary>
        /// Get character progression history
        /// </summary>
        public void GetProgressionHistory(string characterId, Action<bool, List<CharacterProgressionResponseDTO>> callback)
        {
            if (_characterService == null)
            {
                callback?.Invoke(false, null);
                return;
            }
            
            _characterService.GetCharacterProgression(characterId, callback);
        }

        /// <summary>
        /// Calculate experience needed for next level (example formula)
        /// </summary>
        public int CalculateExperienceForLevel(int level)
        {
            // Example progression: level * 100 + (level - 1) * 50
            return level * 100 + (level - 1) * 50;
        }

        /// <summary>
        /// Calculate experience needed to reach a target level
        /// </summary>
        public int CalculateExperienceToLevel(int currentLevel, int targetLevel)
        {
            int totalExperience = 0;
            for (int level = currentLevel + 1; level <= targetLevel; level++)
            {
                totalExperience += CalculateExperienceForLevel(level);
            }
            return totalExperience;
        }

        #endregion
    }

    /// <summary>
    /// Represents an active character progression session
    /// </summary>
    [Serializable]
    public class ProgressionSession
    {
        public string CharacterId { get; set; }
        public string CharacterName { get; set; }
        public int OldLevel { get; set; }
        public int NewLevel { get; set; }
        public int AbilitiesToSelect { get; set; }
        public int AbilitiesSelected { get; set; }
        public List<string> SelectedAbilities { get; set; } = new List<string>();
        public DateTime StartedAt { get; set; }

        public ProgressionSession(CharacterResponseDTO character)
        {
            CharacterId = character.Id;
            CharacterName = character.CharacterName;
            OldLevel = character.Level - 1; // Assume just leveled up
            NewLevel = character.Level;
            StartedAt = DateTime.Now;
        }

        /// <summary>
        /// Check if progression session is complete
        /// </summary>
        public bool IsComplete => AbilitiesSelected >= AbilitiesToSelect;
    }

    /// <summary>
    /// Template for available character abilities
    /// </summary>
    [Serializable]
    public class CharacterAbilityTemplate
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public List<string> Prerequisites { get; set; } = new List<string>();

        public CharacterAbilityTemplate(string name, string description, List<string> prerequisites)
        {
            Name = name;
            Description = description;
            Prerequisites = prerequisites ?? new List<string>();
        }
    }
} 