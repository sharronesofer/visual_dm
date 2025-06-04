using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.DTOs.Character;
using VDM.Core.Services;
using VDM.Systems.Character.Models;

namespace VDM.Systems.Character.UI
{
    /// <summary>
    /// Manages skill check UI interactions and coordinates with backend noncombat skills system.
    /// Provides a Unity interface for the comprehensive skill check mechanics.
    /// </summary>
    public class SkillCheckManager : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private Canvas skillCheckCanvas;
        [SerializeField] private GameObject skillCheckPrefab;
        
        [Header("Configuration")]
        [SerializeField] private float animationDuration = 2.5f;
        [SerializeField] private bool enableDebugLogs = true;
        
        // Events for skill check lifecycle
        public static event Action<SkillCheckRequestDTO> OnSkillCheckRequested;
        public static event Action<SkillCheckResultDTO> OnSkillCheckCompleted;
        public static event Action<string> OnSkillCheckCancelled;
        
        // Current skill check state
        private SkillCheckRequestDTO currentRequest;
        private GameObject currentSkillCheckUI;
        private bool isSkillCheckActive = false;
        
        // Services
        private ICharacterService characterService;
        private ISkillCheckService skillCheckService;
        private IWebSocketService webSocketService;
        
        private void Awake()
        {
            // Initialize services
            characterService = ServiceContainer.Instance.GetService<ICharacterService>();
            skillCheckService = ServiceContainer.Instance.GetService<ISkillCheckService>();
            webSocketService = ServiceContainer.Instance.GetService<IWebSocketService>();
            
            // Ensure canvas is set up
            if (skillCheckCanvas == null)
            {
                skillCheckCanvas = GetComponentInChildren<Canvas>();
            }
        }
        
        private void OnEnable()
        {
            // Subscribe to skill check events
            OnSkillCheckRequested += HandleSkillCheckRequest;
        }
        
        private void OnDisable()
        {
            // Unsubscribe from events
            OnSkillCheckRequested -= HandleSkillCheckRequest;
        }
        
        /// <summary>
        /// Initiate a skill check with multiple skill options.
        /// This is the main entry point for skill checks from dialogue, exploration, etc.
        /// </summary>
        /// <param name="request">Skill check request with options and context</param>
        public static void RequestSkillCheck(SkillCheckRequestDTO request)
        {
            OnSkillCheckRequested?.Invoke(request);
        }
        
        /// <summary>
        /// Quick skill check for a specific skill (used for passive checks, etc.)
        /// </summary>
        /// <param name="characterId">Character making the check</param>
        /// <param name="skillName">Skill to check</param>
        /// <param name="dc">Difficulty class</param>
        /// <param name="environmentalConditions">Environmental modifiers</param>
        /// <param name="description">Description of the check</param>
        public static void RequestQuickSkillCheck(
            string characterId, 
            string skillName, 
            int dc, 
            List<string> environmentalConditions = null,
            string description = "")
        {
            var request = new SkillCheckRequestDTO
            {
                CharacterId = characterId,
                Context = description,
                EnvironmentalConditions = environmentalConditions ?? new List<string>(),
                SkillOptions = new List<SkillCheckOptionDTO>
                {
                    new SkillCheckOptionDTO
                    {
                        SkillName = skillName,
                        OptionText = $"Use {skillName.Replace("_", " ")}",
                        DC = dc,
                        Description = description,
                        EnvironmentalConditions = environmentalConditions ?? new List<string>()
                    }
                }
            };
            
            RequestSkillCheck(request);
        }
        
        private async void HandleSkillCheckRequest(SkillCheckRequestDTO request)
        {
            if (isSkillCheckActive)
            {
                LogDebug("Skill check already active, ignoring new request");
                return;
            }
            
            currentRequest = request;
            isSkillCheckActive = true;
            
            try
            {
                // Get character data
                var character = await characterService.GetCharacterAsync(request.CharacterId);
                if (character == null)
                {
                    LogError($"Character not found: {request.CharacterId}");
                    return;
                }
                
                // Show skill check UI
                await ShowSkillCheckUI(character, request);
            }
            catch (Exception ex)
            {
                LogError($"Error handling skill check request: {ex.Message}");
                CompleteSkillCheck(null);
            }
        }
        
        private async Task ShowSkillCheckUI(CharacterDTO character, SkillCheckRequestDTO request)
        {
            try
            {
                // Create skill check UI instance
                if (skillCheckPrefab != null)
                {
                    currentSkillCheckUI = Instantiate(skillCheckPrefab, skillCheckCanvas.transform);
                    var uiComponent = currentSkillCheckUI.GetComponent<SkillCheckUIComponent>();
                    
                    if (uiComponent != null)
                    {
                        // Configure the UI component
                        await uiComponent.InitializeAsync(character, request, this);
                    }
                    else
                    {
                        LogError("SkillCheckUIComponent not found on prefab");
                        // Fall back to web integration
                        await ShowWebSkillCheckUI(character, request);
                    }
                }
                else
                {
                    // Fall back to web integration if no prefab
                    await ShowWebSkillCheckUI(character, request);
                }
            }
            catch (Exception ex)
            {
                LogError($"Error showing skill check UI: {ex.Message}");
                CompleteSkillCheck(null);
            }
        }
        
        private async Task ShowWebSkillCheckUI(CharacterDTO character, SkillCheckRequestDTO request)
        {
            // Send request to web UI via WebSocket
            var webRequest = new
            {
                type = "skill_check_request",
                data = new
                {
                    character = character,
                    skillOptions = request.SkillOptions,
                    environmentalConditions = request.EnvironmentalConditions,
                    context = request.Context
                }
            };
            
            if (webSocketService != null)
            {
                await webSocketService.SendAsync(webRequest);
                LogDebug("Sent skill check request to web UI");
            }
            else
            {
                LogError("WebSocket service not available");
                CompleteSkillCheck(null);
            }
        }
        
        /// <summary>
        /// Execute a skill check against the backend service.
        /// Called by UI components when player selects a skill option.
        /// </summary>
        /// <param name="characterId">Character making the check</param>
        /// <param name="skillOption">Selected skill option</param>
        /// <returns>Skill check result</returns>
        public async Task<SkillCheckResultDTO> ExecuteSkillCheck(string characterId, SkillCheckOptionDTO skillOption)
        {
            try
            {
                LogDebug($"Executing skill check: {skillOption.SkillName} for character {characterId}");
                
                // Prepare skill check data for backend
                var skillCheckData = new
                {
                    character_id = characterId,
                    skill_name = skillOption.SkillName,
                    dc = skillOption.DC,
                    environmental_conditions = skillOption.EnvironmentalConditions,
                    description = skillOption.Description
                };
                
                // Call backend skill check service
                var result = await skillCheckService.MakeSkillCheckAsync(skillCheckData);
                
                LogDebug($"Skill check result: {result.TotalRoll} vs DC {result.DC} = {(result.Success ? "Success" : "Failure")}");
                
                return result;
            }
            catch (Exception ex)
            {
                LogError($"Error executing skill check: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Complete the current skill check and clean up UI.
        /// </summary>
        /// <param name="result">Final skill check result (null if cancelled)</param>
        public void CompleteSkillCheck(SkillCheckResultDTO result)
        {
            try
            {
                // Clean up UI
                if (currentSkillCheckUI != null)
                {
                    Destroy(currentSkillCheckUI);
                    currentSkillCheckUI = null;
                }
                
                // Fire completion events
                if (result != null)
                {
                    OnSkillCheckCompleted?.Invoke(result);
                    LogDebug($"Skill check completed: {result.SkillName} - {(result.Success ? "Success" : "Failure")}");
                }
                else
                {
                    OnSkillCheckCancelled?.Invoke(currentRequest?.CharacterId ?? "unknown");
                    LogDebug("Skill check cancelled");
                }
                
                // Reset state
                currentRequest = null;
                isSkillCheckActive = false;
            }
            catch (Exception ex)
            {
                LogError($"Error completing skill check: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Get passive skill score for a character.
        /// Used for automatic checks, detection, etc.
        /// </summary>
        /// <param name="characterId">Character ID</param>
        /// <param name="skillName">Skill name</param>
        /// <param name="environmentalConditions">Environmental conditions</param>
        /// <returns>Passive skill score</returns>
        public async Task<int> GetPassiveSkillScore(
            string characterId, 
            string skillName, 
            List<string> environmentalConditions = null)
        {
            try
            {
                var passiveData = new
                {
                    character_id = characterId,
                    skill_name = skillName,
                    environmental_conditions = environmentalConditions ?? new List<string>()
                };
                
                var result = await skillCheckService.GetPassiveSkillScoreAsync(passiveData);
                LogDebug($"Passive {skillName} for {characterId}: {result}");
                
                return result;
            }
            catch (Exception ex)
            {
                LogError($"Error getting passive skill score: {ex.Message}");
                return 10; // Default fallback
            }
        }
        
        /// <summary>
        /// Make an opposed skill check between two characters.
        /// </summary>
        /// <param name="character1Id">First character</param>
        /// <param name="character2Id">Second character</param>
        /// <param name="skill1">Skill for first character</param>
        /// <param name="skill2">Skill for second character</param>
        /// <param name="description">Description of the contest</param>
        /// <returns>Opposed check result</returns>
        public async Task<OpposedSkillCheckResultDTO> MakeOpposedSkillCheck(
            string character1Id,
            string character2Id,
            string skill1,
            string skill2 = null,
            string description = "")
        {
            try
            {
                var opposedData = new
                {
                    character1_id = character1Id,
                    character2_id = character2Id,
                    skill1 = skill1,
                    skill2 = skill2 ?? skill1,
                    description = description
                };
                
                var result = await skillCheckService.MakeOpposedSkillCheckAsync(opposedData);
                
                LogDebug($"Opposed skill check: {character1Id} vs {character2Id} - " +
                        $"{(result.Character1Wins ? "Character 1" : "Character 2")} wins");
                
                return result;
            }
            catch (Exception ex)
            {
                LogError($"Error making opposed skill check: {ex.Message}");
                throw;
            }
        }
        
        // Helper methods
        private void LogDebug(string message)
        {
            if (enableDebugLogs)
            {
                Debug.Log($"[SkillCheckManager] {message}");
            }
        }
        
        private void LogError(string message)
        {
            Debug.LogError($"[SkillCheckManager] {message}");
        }
        
        // Public API for other systems
        public bool IsSkillCheckActive => isSkillCheckActive;
        public SkillCheckRequestDTO CurrentRequest => currentRequest;
    }
} 