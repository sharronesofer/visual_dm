using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core;
using VDM.Runtime.Events;
using VDM.Runtime.Quest.Models;
using VDM.Runtime.Quest.Services;


namespace VDM.Runtime.Quest.Integration
{
    /// <summary>
    /// Handles integration between Quest system and other game systems through events
    /// </summary>
    public class QuestEventIntegration : MonoBehaviour
    {
        [Header("Settings")]
        [SerializeField] private bool enableAutoQuestGeneration = true;
        [SerializeField] private float questGenerationCooldown = 30f;
        [SerializeField] private int maxActiveQuests = 10;
        
        private QuestService questService;
        private Dictionary<string, DateTime> lastQuestGeneration = new Dictionary<string, DateTime>();
        
        // Events
        public static event Action<QuestDTO> OnQuestGenerated;
        public static event Action<QuestDTO> OnQuestCompleted;
        public static event Action<QuestDTO> OnQuestFailed;
        public static event Action<QuestDTO, QuestStepDTO> OnQuestStepCompleted;
        
        private void Awake()
        {
            questService = new QuestService();
            RegisterEventHandlers();
        }
        
        private void OnDestroy()
        {
            UnregisterEventHandlers();
        }
        
        /// <summary>
        /// Register event handlers for quest integration
        /// </summary>
        private void RegisterEventHandlers()
        {
            // NPC Events
            EventManager.Subscribe<NPCDialogueCompletedEvent>(HandleDialogueCompleted);
            EventManager.Subscribe<NPCInteractionEvent>(HandleNPCInteraction);
            
            // Player Events
            EventManager.Subscribe<PlayerItemAcquiredEvent>(HandleItemAcquired);
            EventManager.Subscribe<PlayerLocationChangedEvent>(HandleLocationChanged);
            EventManager.Subscribe<PlayerLevelUpEvent>(HandlePlayerLevelUp);
            
            // Combat Events
            EventManager.Subscribe<EnemyDefeatedEvent>(HandleEnemyDefeated);
            EventManager.Subscribe<CombatEndedEvent>(HandleCombatEnded);
            
            // World Events
            EventManager.Subscribe<TimeChangedEvent>(HandleTimeChanged);
            EventManager.Subscribe<RegionEventTriggeredEvent>(HandleRegionEvent);
            
            // Faction Events
            EventManager.Subscribe<FactionReputationChangedEvent>(HandleReputationChanged);
            EventManager.Subscribe<FactionConflictStartedEvent>(HandleFactionConflict);
            
            Debug.Log("Quest event handlers registered");
        }
        
        /// <summary>
        /// Unregister event handlers
        /// </summary>
        private void UnregisterEventHandlers()
        {
            EventManager.Unsubscribe<NPCDialogueCompletedEvent>(HandleDialogueCompleted);
            EventManager.Unsubscribe<NPCInteractionEvent>(HandleNPCInteraction);
            EventManager.Unsubscribe<PlayerItemAcquiredEvent>(HandleItemAcquired);
            EventManager.Unsubscribe<PlayerLocationChangedEvent>(HandleLocationChanged);
            EventManager.Unsubscribe<PlayerLevelUpEvent>(HandlePlayerLevelUp);
            EventManager.Unsubscribe<EnemyDefeatedEvent>(HandleEnemyDefeated);
            EventManager.Unsubscribe<CombatEndedEvent>(HandleCombatEnded);
            EventManager.Unsubscribe<TimeChangedEvent>(HandleTimeChanged);
            EventManager.Unsubscribe<RegionEventTriggeredEvent>(HandleRegionEvent);
            EventManager.Unsubscribe<FactionReputationChangedEvent>(HandleReputationChanged);
            EventManager.Unsubscribe<FactionConflictStartedEvent>(HandleFactionConflict);
        }
        
        #region Event Handlers
        
        /// <summary>
        /// Handle dialogue completion events for quest progression
        /// </summary>
        private async void HandleDialogueCompleted(NPCDialogueCompletedEvent eventData)
        {
            try
            {
                // Check for quest step completion
                await CheckQuestStepCompletion("dialogue", new Dictionary<string, object>
                {
                    ["npc_id"] = eventData.NPCId,
                    ["dialogue_id"] = eventData.DialogueId,
                    ["player_id"] = eventData.PlayerId
                });
                
                // Generate new quests from dialogue
                if (enableAutoQuestGeneration && ShouldGenerateQuest(eventData.NPCId))
                {
                    await GenerateQuestFromDialogue(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling dialogue completed event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle NPC interaction events
        /// </summary>
        private async void HandleNPCInteraction(NPCInteractionEvent eventData)
        {
            try
            {
                await CheckQuestStepCompletion("npc_interaction", new Dictionary<string, object>
                {
                    ["npc_id"] = eventData.NPCId,
                    ["interaction_type"] = eventData.InteractionType,
                    ["player_id"] = eventData.PlayerId
                });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling NPC interaction event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle item acquisition events
        /// </summary>
        private async void HandleItemAcquired(PlayerItemAcquiredEvent eventData)
        {
            try
            {
                await CheckQuestStepCompletion("item_acquisition", new Dictionary<string, object>
                {
                    ["item_id"] = eventData.ItemId,
                    ["quantity"] = eventData.Quantity,
                    ["player_id"] = eventData.PlayerId
                });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling item acquired event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle location change events
        /// </summary>
        private async void HandleLocationChanged(PlayerLocationChangedEvent eventData)
        {
            try
            {
                await CheckQuestStepCompletion("location", new Dictionary<string, object>
                {
                    ["location_id"] = eventData.NewLocationId,
                    ["region_id"] = eventData.RegionId,
                    ["player_id"] = eventData.PlayerId
                });
                
                // Generate location-based quests
                if (enableAutoQuestGeneration && ShouldGenerateQuest(eventData.NewLocationId))
                {
                    await GenerateLocationQuests(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling location changed event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle player level up events
        /// </summary>
        private async void HandlePlayerLevelUp(PlayerLevelUpEvent eventData)
        {
            try
            {
                // Generate level-appropriate quests
                if (enableAutoQuestGeneration)
                {
                    await GenerateLevelAppropriateQuests(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling player level up event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle enemy defeated events
        /// </summary>
        private async void HandleEnemyDefeated(EnemyDefeatedEvent eventData)
        {
            try
            {
                await CheckQuestStepCompletion("enemy_defeat", new Dictionary<string, object>
                {
                    ["enemy_id"] = eventData.EnemyId,
                    ["enemy_type"] = eventData.EnemyType,
                    ["player_id"] = eventData.PlayerId
                });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling enemy defeated event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle combat ended events
        /// </summary>
        private async void HandleCombatEnded(CombatEndedEvent eventData)
        {
            try
            {
                await CheckQuestStepCompletion("combat", new Dictionary<string, object>
                {
                    ["combat_result"] = eventData.Result,
                    ["participants"] = eventData.Participants,
                    ["player_id"] = eventData.PlayerId
                });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling combat ended event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle time change events
        /// </summary>
        private async void HandleTimeChanged(TimeChangedEvent eventData)
        {
            try
            {
                // Check for time-based quest step completion
                await CheckQuestStepCompletion("time", new Dictionary<string, object>
                {
                    ["current_time"] = eventData.CurrentTime,
                    ["time_delta"] = eventData.TimeDelta
                });
                
                // Generate time-based quests (daily, weekly, etc.)
                if (enableAutoQuestGeneration && ShouldGenerateTimeBasedQuests(eventData))
                {
                    await GenerateTimeBasedQuests(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling time changed event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle region events
        /// </summary>
        private async void HandleRegionEvent(RegionEventTriggeredEvent eventData)
        {
            try
            {
                // Generate region-specific quests
                if (enableAutoQuestGeneration)
                {
                    await GenerateRegionQuests(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling region event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle faction reputation changes
        /// </summary>
        private async void HandleReputationChanged(FactionReputationChangedEvent eventData)
        {
            try
            {
                // Generate faction quests based on reputation
                if (enableAutoQuestGeneration && eventData.NewValue > eventData.OldValue)
                {
                    await GenerateFactionQuests(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling reputation changed event: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle faction conflict events
        /// </summary>
        private async void HandleFactionConflict(FactionConflictStartedEvent eventData)
        {
            try
            {
                // Generate conflict-related quests
                if (enableAutoQuestGeneration)
                {
                    await GenerateConflictQuests(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling faction conflict event: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Quest Generation Methods
        
        /// <summary>
        /// Check if quest step completion criteria are met
        /// </summary>
        private async Task CheckQuestStepCompletion(string stepType, Dictionary<string, object> parameters)
        {
            try
            {
                // Get active quests for the player
                var activeQuests = await questService.GetActiveQuestsAsync(parameters.GetValueOrDefault("player_id")?.ToString());
                
                foreach (var quest in activeQuests)
                {
                    foreach (var step in quest.Steps)
                    {
                        if (step.Status == "pending" && step.Type == stepType)
                        {
                            if (await IsStepCompleted(step, parameters))
                            {
                                await CompleteQuestStep(quest, step);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error checking quest step completion: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Check if a quest step is completed based on parameters
        /// </summary>
        private async Task<bool> IsStepCompleted(QuestStepDTO step, Dictionary<string, object> parameters)
        {
            // Implementation depends on step requirements and parameters
            // This is a simplified version - actual implementation would be more complex
            
            switch (step.Type)
            {
                case "dialogue":
                    return step.TargetNPCId == parameters.GetValueOrDefault("npc_id")?.ToString();
                    
                case "item_acquisition":
                    return step.RequiredItems?.ContainsKey(parameters.GetValueOrDefault("item_id")?.ToString()) == true;
                    
                case "location":
                    return step.TargetLocationId == parameters.GetValueOrDefault("location_id")?.ToString();
                    
                case "enemy_defeat":
                    return step.TargetEnemyType == parameters.GetValueOrDefault("enemy_type")?.ToString();
                    
                default:
                    return false;
            }
        }
        
        /// <summary>
        /// Complete a quest step
        /// </summary>
        private async Task CompleteQuestStep(QuestDTO quest, QuestStepDTO step)
        {
            try
            {
                var updateRequest = new QuestStepUpdateDTO
                {
                    Status = "completed",
                    CompletedAt = DateTime.UtcNow
                };
                
                await questService.UpdateQuestStepAsync(quest.Id, step.Id, updateRequest);
                
                OnQuestStepCompleted?.Invoke(quest, step);
                
                // Check if quest is complete
                if (quest.Steps.All(s => s.Status == "completed"))
                {
                    await questService.CompleteQuestAsync(quest.Id);
                    OnQuestCompleted?.Invoke(quest);
                }
                
                Debug.Log($"Quest step completed: {step.Description}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error completing quest step: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Check if a quest should be generated for the given context
        /// </summary>
        private bool ShouldGenerateQuest(string contextId)
        {
            if (string.IsNullOrEmpty(contextId))
                return false;
                
            if (lastQuestGeneration.TryGetValue(contextId, out var lastTime))
            {
                return (DateTime.UtcNow - lastTime).TotalSeconds > questGenerationCooldown;
            }
            
            return true;
        }
        
        /// <summary>
        /// Generate quest from dialogue completion
        /// </summary>
        private async Task GenerateQuestFromDialogue(NPCDialogueCompletedEvent eventData)
        {
            try
            {
                var prompt = $"Generate a quest based on dialogue completion with NPC {eventData.NPCId}";
                var quest = await questService.GenerateQuestsAsync(prompt, 1);
                
                if (quest?.Count > 0)
                {
                    lastQuestGeneration[eventData.NPCId] = DateTime.UtcNow;
                    OnQuestGenerated?.Invoke(quest[0]);
                    Debug.Log($"Generated quest from dialogue: {quest[0].Title}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating quest from dialogue: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Generate location-based quests
        /// </summary>
        private async Task GenerateLocationQuests(PlayerLocationChangedEvent eventData)
        {
            try
            {
                var prompt = $"Generate location-based quests for region {eventData.RegionId} at location {eventData.NewLocationId}";
                var quests = await questService.GenerateQuestsAsync(prompt, 2);
                
                foreach (var quest in quests)
                {
                    OnQuestGenerated?.Invoke(quest);
                }
                
                lastQuestGeneration[eventData.NewLocationId] = DateTime.UtcNow;
                Debug.Log($"Generated {quests.Count} location quests");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating location quests: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Generate level-appropriate quests
        /// </summary>
        private async Task GenerateLevelAppropriateQuests(PlayerLevelUpEvent eventData)
        {
            try
            {
                var prompt = $"Generate level {eventData.NewLevel} appropriate quests for player {eventData.PlayerId}";
                var quests = await questService.GenerateQuestsAsync(prompt, 1);
                
                foreach (var quest in quests)
                {
                    OnQuestGenerated?.Invoke(quest);
                }
                
                Debug.Log($"Generated {quests.Count} level-appropriate quests");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating level-appropriate quests: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Check if time-based quests should be generated
        /// </summary>
        private bool ShouldGenerateTimeBasedQuests(TimeChangedEvent eventData)
        {
            // Generate daily quests at dawn, weekly quests on specific days, etc.
            // This is a simplified implementation
            return eventData.CurrentTime.Hour == 6 && eventData.CurrentTime.Minute == 0;
        }
        
        /// <summary>
        /// Generate time-based quests
        /// </summary>
        private async Task GenerateTimeBasedQuests(TimeChangedEvent eventData)
        {
            try
            {
                var prompt = $"Generate daily quests for time {eventData.CurrentTime}";
                var quests = await questService.GenerateQuestsAsync(prompt, 1);
                
                foreach (var quest in quests)
                {
                    OnQuestGenerated?.Invoke(quest);
                }
                
                Debug.Log($"Generated {quests.Count} time-based quests");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating time-based quests: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Generate region-specific quests
        /// </summary>
        private async Task GenerateRegionQuests(RegionEventTriggeredEvent eventData)
        {
            try
            {
                var prompt = $"Generate quests for region event {eventData.EventType} in region {eventData.RegionId}";
                var quests = await questService.GenerateQuestsAsync(prompt, 2);
                
                foreach (var quest in quests)
                {
                    OnQuestGenerated?.Invoke(quest);
                }
                
                Debug.Log($"Generated {quests.Count} region quests");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating region quests: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Generate faction-related quests
        /// </summary>
        private async Task GenerateFactionQuests(FactionReputationChangedEvent eventData)
        {
            try
            {
                var prompt = $"Generate faction quests for faction {eventData.FactionId} with reputation {eventData.NewValue}";
                var quests = await questService.GenerateQuestsAsync(prompt, 1);
                
                foreach (var quest in quests)
                {
                    OnQuestGenerated?.Invoke(quest);
                }
                
                Debug.Log($"Generated {quests.Count} faction quests");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating faction quests: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Generate conflict-related quests
        /// </summary>
        private async Task GenerateConflictQuests(FactionConflictStartedEvent eventData)
        {
            try
            {
                var prompt = $"Generate conflict quests for factions {eventData.Faction1Id} vs {eventData.Faction2Id}";
                var quests = await questService.GenerateQuestsAsync(prompt, 2);
                
                foreach (var quest in quests)
                {
                    OnQuestGenerated?.Invoke(quest);
                }
                
                Debug.Log($"Generated {quests.Count} conflict quests");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating conflict quests: {ex.Message}");
            }
        }
        
        #endregion
    }
    
    #region Event Data Classes
    
    public class NPCDialogueCompletedEvent
    {
        public string NPCId { get; set; }
        public string DialogueId { get; set; }
        public string PlayerId { get; set; }
    }
    
    public class NPCInteractionEvent
    {
        public string NPCId { get; set; }
        public string InteractionType { get; set; }
        public string PlayerId { get; set; }
    }
    
    public class PlayerItemAcquiredEvent
    {
        public string ItemId { get; set; }
        public int Quantity { get; set; }
        public string PlayerId { get; set; }
    }
    
    public class PlayerLocationChangedEvent
    {
        public string NewLocationId { get; set; }
        public string RegionId { get; set; }
        public string PlayerId { get; set; }
    }
    
    public class PlayerLevelUpEvent
    {
        public string PlayerId { get; set; }
        public int NewLevel { get; set; }
        public int OldLevel { get; set; }
    }
    
    public class EnemyDefeatedEvent
    {
        public string EnemyId { get; set; }
        public string EnemyType { get; set; }
        public string PlayerId { get; set; }
    }
    
    public class CombatEndedEvent
    {
        public string Result { get; set; }
        public List<string> Participants { get; set; }
        public string PlayerId { get; set; }
    }
    
    public class TimeChangedEvent
    {
        public DateTime CurrentTime { get; set; }
        public TimeSpan TimeDelta { get; set; }
    }
    
    public class RegionEventTriggeredEvent
    {
        public string RegionId { get; set; }
        public string EventType { get; set; }
        public Dictionary<string, object> EventData { get; set; }
    }
    
    public class FactionReputationChangedEvent
    {
        public string FactionId { get; set; }
        public string PlayerId { get; set; }
        public int OldValue { get; set; }
        public int NewValue { get; set; }
    }
    
    public class FactionConflictStartedEvent
    {
        public string Faction1Id { get; set; }
        public string Faction2Id { get; set; }
        public string ConflictType { get; set; }
    }
    
    #endregion
} 