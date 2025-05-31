using NativeWebSocket;
using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using VDM.Systems.Events.Integration;
using VDM.Systems.Arc.Models;
using VDM.Systems.Arc.Services;
using VDM.Systems.Quest.Models;
using VDM.Systems.Quest.Services;
using VDM.Infrastructure.Core.Core.Systems;
using VDM.Infrastructure.Services;

namespace VDM.Infrastructure.Integration.Integration
{
    /// <summary>
    /// Manages integration between Quest and Arc narrative systems
    /// Provides unified coordination, data synchronization, and event propagation
    /// </summary>
    public class QuestArcIntegrationManager : MonoBehaviour, ISystemManager
    {
        [Header("System Services")]
        [SerializeField] private bool autoInitialize = true;
        [SerializeField] private bool enableDebugLogging = false;
        
        [Header("Integration Configuration")]
        [SerializeField] private bool enableRealTimeSync = true;
        [SerializeField] private float syncInterval = 30f;
        [SerializeField] private int maxRetryAttempts = 3;
        
        [Header("Debug Settings")]
        [SerializeField] private bool debugMode = false;
        [SerializeField] private bool logIntegrationEvents = true;
        
        [Header("System References")]
        [SerializeField] private Transform questContainer;
        [SerializeField] private Transform arcContainer;
        
        // Services
        private QuestService questService;
        private ArcService arcService;
        private QuestWebSocketHandler questWebSocketHandler;
        private ArcWebSocketHandler arcWebSocketHandler;
        
        // Data synchronization
        private Dictionary<string, List<string>> questToArcsMapping = new Dictionary<string, List<string>>();
        private Dictionary<string, List<string>> arcToQuestsMapping = new Dictionary<string, List<string>>();
        private Dictionary<string, string> characterArcMapping = new Dictionary<string, string>();
        
        // Integration state
        private bool isInitialized = false;
        private bool isProcessingIntegrationEvent = false;
        
        // Events
        public event Action<VDM.DTOs.Content.Quest.QuestDTO, ArcDTO> OnQuestArcLinked;
        public event Action<VDM.DTOs.Content.Quest.QuestDTO, ArcDTO> OnQuestArcUnlinked;
        public event Action<string, List<VDM.DTOs.Content.Quest.QuestDTO>, List<ArcDTO>> OnCharacterNarrativeUpdated;
        public event Action<IntegrationSyncResult> OnIntegrationSynced;
        public event Action<string> OnIntegrationError;
        
        // System properties
        public string SystemName => "QuestArcIntegrationManager";
        public bool IsInitialized { get; private set; } = false;
        public SystemHealthStatus HealthStatus { get; private set; } = SystemHealthStatus.Unknown;
        
        #region Unity Lifecycle
        
        private void Start()
        {
            if (autoInitialize)
            {
                InitializeIntegration();
            }
        }
        
        private void OnDestroy()
        {
            if (isInitialized)
            {
                UnsubscribeFromEvents();
            }
        }
        
        #endregion
        
        #region Initialization
        
        public async void InitializeIntegration()
        {
            try
            {
                Log("Initializing Quest-Arc Integration Manager...");
                
                // Initialize services
                await InitializeServices();
                
                // Subscribe to events
                SubscribeToEvents();
                
                // Perform initial data synchronization
                await SynchronizeData();
                
                isInitialized = true;
                Log("Quest-Arc Integration Manager initialized successfully");
            }
            catch (Exception ex)
            {
                LogError($"Failed to initialize Quest-Arc Integration: {ex.Message}");
                OnIntegrationError?.Invoke($"Initialization failed: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task InitializeServices()
        {
            // Initialize Quest services
            questService = new QuestService();
            questWebSocketHandler = new QuestWebSocketHandler();
            
            // Initialize Arc services
            arcService = new ArcService();
            arcWebSocketHandler = new ArcWebSocketHandler();
            
            // Allow services to connect
            await System.Threading.Tasks.Task.Delay(100);
            
            Log("Services initialized");
        }
        
        private void SubscribeToEvents()
        {
            // Quest events
            if (questWebSocketHandler != null)
            {
                questWebSocketHandler.OnQuestCreated += HandleQuestCreated;
                questWebSocketHandler.OnQuestUpdated += HandleQuestUpdated;
                questWebSocketHandler.OnQuestCompleted += HandleQuestCompleted;
                questWebSocketHandler.OnQuestFailed += HandleQuestFailed;
                questWebSocketHandler.OnQuestStepCompleted += HandleQuestStepCompleted;
            }
            
            // Arc events
            if (arcWebSocketHandler != null)
            {
                arcWebSocketHandler.OnArcCreated += HandleArcCreated;
                arcWebSocketHandler.OnArcUpdated += HandleArcUpdated;
                arcWebSocketHandler.OnArcCompleted += HandleArcCompleted;
                arcWebSocketHandler.OnArcStarted += HandleArcStarted;
                arcWebSocketHandler.OnStepUpdated += HandleArcStepUpdated;
                arcWebSocketHandler.OnProgressionUpdated += HandleArcProgressionUpdated;
            }
            
            Log("Event subscriptions established");
        }
        
        private void UnsubscribeFromEvents()
        {
            // Quest events
            if (questWebSocketHandler != null)
            {
                questWebSocketHandler.OnQuestCreated -= HandleQuestCreated;
                questWebSocketHandler.OnQuestUpdated -= HandleQuestUpdated;
                questWebSocketHandler.OnQuestCompleted -= HandleQuestCompleted;
                questWebSocketHandler.OnQuestFailed -= HandleQuestFailed;
                questWebSocketHandler.OnQuestStepCompleted -= HandleQuestStepCompleted;
            }
            
            // Arc events
            if (arcWebSocketHandler != null)
            {
                arcWebSocketHandler.OnArcCreated -= HandleArcCreated;
                arcWebSocketHandler.OnArcUpdated -= HandleArcUpdated;
                arcWebSocketHandler.OnArcCompleted -= HandleArcCompleted;
                arcWebSocketHandler.OnArcStarted -= HandleArcStarted;
                arcWebSocketHandler.OnStepUpdated -= HandleArcStepUpdated;
                arcWebSocketHandler.OnProgressionUpdated -= HandleArcProgressionUpdated;
            }
        }
        
        #endregion
        
        #region Data Synchronization
        
        private async System.Threading.Tasks.Task SynchronizeData()
        {
            try
            {
                Log("Starting data synchronization...");
                
                // Load all quests and arcs
                var quests = await questService.GetQuestsAsync();
                var arcs = await arcService.GetArcsAsync();
                
                // Build mapping relationships
                BuildMappingRelationships(quests, arcs);
                
                // Validate and repair inconsistencies
                await ValidateAndRepairMappings(quests, arcs);
                
                // Create synchronization result
                var syncResult = new IntegrationSyncResult
                {
                    QuestCount = quests.Count,
                    ArcCount = arcs.Count,
                    QuestArcLinks = GetTotalQuestArcLinks(),
                    CharacterMappings = characterArcMapping.Count,
                    SyncTimestamp = DateTime.UtcNow,
                    IsSuccessful = true
                };
                
                OnIntegrationSynced?.Invoke(syncResult);
                Log($"Data synchronization completed - Quests: {quests.Count}, Arcs: {arcs.Count}, Links: {syncResult.QuestArcLinks}");
            }
            catch (Exception ex)
            {
                LogError($"Data synchronization failed: {ex.Message}");
                OnIntegrationError?.Invoke($"Synchronization failed: {ex.Message}");
            }
        }
        
        private void BuildMappingRelationships(List<VDM.DTOs.Content.Quest.QuestDTO> quests, List<ArcModel> arcs)
        {
            questToArcsMapping.Clear();
            arcToQuestsMapping.Clear();
            characterArcMapping.Clear();
            
            foreach (var quest in quests)
            {
                if (string.IsNullOrEmpty(quest.ArcId)) continue;

                var arc = arcs.FirstOrDefault(a => a.Id == quest.ArcId);
                if (arc != null)
                {
                    // Add quest to arc's quest collection
                    if (!questToArcsMapping.ContainsKey(quest.Id))
                        questToArcsMapping[quest.Id] = new List<string>();
                    
                    if (!questToArcsMapping[quest.Id].Contains(arc.Id))
                        questToArcsMapping[quest.Id].Add(arc.Id);

                    // Add arc to quest's arc mapping
                    if (!arcToQuestsMapping.ContainsKey(arc.Id))
                        arcToQuestsMapping[arc.Id] = new List<string>();
                    
                    if (!arcToQuestsMapping[arc.Id].Contains(quest.Id))
                        arcToQuestsMapping[arc.Id].Add(quest.Id);
                }
            }
            
            Log($"Built mappings - Quest->Arc: {questToArcsMapping.Count}, Arc->Quest: {arcToQuestsMapping.Count}, Character->Arc: {characterArcMapping.Count}");
        }
        
        private async System.Threading.Tasks.Task ValidateAndRepairMappings(List<VDM.DTOs.Content.Quest.QuestDTO> quests, List<ArcModel> arcs)
        {
            var repairActions = new List<string>();
            
            // Validate quest references to arcs
            foreach (var quest in quests)
            {
                if (!string.IsNullOrEmpty(quest.ArcId))
                {
                    var arc = arcs.FirstOrDefault(a => a.Id == quest.ArcId);
                    if (arc == null)
                    {
                        repairActions.Add($"Quest {quest.Id} references non-existent arc {quest.ArcId}");
                        // Remove invalid reference
                        questToArcsMapping[quest.Id].Remove(quest.ArcId);
                    }
                }
            }
            
            // Validate arc references to quests
            foreach (var arc in arcs)
            {
                if (arc.QuestIds != null)
                {
                    var validQuestIds = new List<string>();
                    foreach (var questId in arc.QuestIds)
                    {
                        var quest = quests.FirstOrDefault(q => q.Id == questId);
                        if (quest != null)
                        {
                            validQuestIds.Add(questId);
                        }
                        else
                        {
                            repairActions.Add($"Arc {arc.Id} references non-existent quest {questId}");
                        }
                    }
                    arcToQuestsMapping[arc.Id] = validQuestIds;
                }
            }
            
            if (repairActions.Count > 0)
            {
                Log($"Repaired {repairActions.Count} mapping inconsistencies");
                foreach (var action in repairActions)
                {
                    Log($"Repair: {action}");
                }
            }
        }
        
        private int GetTotalQuestArcLinks()
        {
            return questToArcsMapping.Values.Sum(arcs => arcs.Count);
        }
        
        #endregion
        
        #region Quest Event Handlers
        
        private void HandleQuestCreated(VDM.DTOs.Content.Quest.QuestDTO quest)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling quest created: {quest.Title}");
                
                // Add to mapping
                questToArcsMapping[quest.Id] = new List<string>();
                
                // Link to arc if specified
                if (!string.IsNullOrEmpty(quest.ArcId))
                {
                    LinkQuestToArc(quest.Id, quest.ArcId);
                }
                
                // Update character narrative if applicable
                _ = UpdateCharacterNarrative(quest.CharacterId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling quest created: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        private void HandleQuestUpdated(VDM.DTOs.Content.Quest.QuestDTO quest)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling quest updated: {quest.Title}");
                
                // Check for arc relationship changes
                var previousArcs = questToArcsMapping.ContainsKey(quest.Id) ? 
                    new List<string>(questToArcsMapping[quest.Id]) : new List<string>();
                
                var currentArcId = quest.ArcId;
                
                // Handle arc relationship changes
                if (!string.IsNullOrEmpty(currentArcId) && !previousArcs.Contains(currentArcId))
                {
                    // New arc relationship
                    LinkQuestToArc(quest.Id, currentArcId);
                }
                else if (string.IsNullOrEmpty(currentArcId) && previousArcs.Count > 0)
                {
                    // Arc relationship removed
                    foreach (var arcId in previousArcs)
                    {
                        UnlinkQuestFromArc(quest.Id, arcId);
                    }
                }
                
                // Update character narrative
                _ = UpdateCharacterNarrative(quest.CharacterId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling quest updated: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        private void HandleQuestCompleted(VDM.DTOs.Content.Quest.QuestDTO quest)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling quest completed: {quest.Title}");
                
                // Check if related arcs should progress
                _ = CheckArcProgression(quest);
                
                // Update character narrative
                _ = UpdateCharacterNarrative(quest.CharacterId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling quest completed: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        private void HandleQuestFailed(VDM.DTOs.Content.Quest.QuestDTO quest)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling quest failed: {quest.Title}");
                
                // Check impact on related arcs
                _ = CheckArcImpact(quest, "quest_failed");
                
                // Update character narrative
                _ = UpdateCharacterNarrative(quest.CharacterId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling quest failed: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        private void HandleQuestStepCompleted(VDM.DTOs.Content.Quest.QuestDTO quest, QuestStepDTO step)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling quest step completed: {quest.Title} - {step.Title}");
                
                // Check for arc step correlations
                _ = CheckArcStepCorrelations(quest, step);
            }
            catch (Exception ex)
            {
                LogError($"Error handling quest step completed: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        #endregion
        
        #region Arc Event Handlers
        
        private void HandleArcCreated(ArcModel arc)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling arc created: {arc.Title}");
                
                // Add to mapping
                arcToQuestsMapping[arc.Id] = new List<string>();
                
                // Update character mapping
                if (!string.IsNullOrEmpty(arc.CharacterId))
                {
                    characterArcMapping[arc.CharacterId] = arc.Id;
                }
                
                // Link existing quests if specified
                if (arc.QuestIds != null)
                {
                    foreach (var questId in arc.QuestIds)
                    {
                        LinkQuestToArc(questId, arc.Id);
                    }
                }
                
                // Update character narrative
                _ = UpdateCharacterNarrative(arc.CharacterId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling arc created: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        private void HandleArcUpdated(ArcModel arc)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling arc updated: {arc.Title}");
                
                // Update character mapping
                if (!string.IsNullOrEmpty(arc.CharacterId))
                {
                    characterArcMapping[arc.CharacterId] = arc.Id;
                }
                
                // Check quest relationship changes
                var previousQuests = arcToQuestsMapping.ContainsKey(arc.Id) ? 
                    new List<string>(arcToQuestsMapping[arc.Id]) : new List<string>();
                
                var currentQuests = arc.QuestIds ?? new List<string>();
                
                // Handle new quest relationships
                foreach (var questId in currentQuests.Except(previousQuests))
                {
                    LinkQuestToArc(questId, arc.Id);
                }
                
                // Handle removed quest relationships
                foreach (var questId in previousQuests.Except(currentQuests))
                {
                    UnlinkQuestFromArc(questId, arc.Id);
                }
                
                // Update character narrative
                _ = UpdateCharacterNarrative(arc.CharacterId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling arc updated: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        private void HandleArcCompleted(ArcModel arc)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling arc completed: {arc.Title}");
                
                // Update related quests status if appropriate
                _ = UpdateRelatedQuestsOnArcCompletion(arc);
                
                // Update character narrative
                _ = UpdateCharacterNarrative(arc.CharacterId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling arc completed: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        private void HandleArcStarted(ArcModel arc)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling arc started: {arc.Title}");
                
                // Activate related quests if appropriate
                _ = ActivateRelatedQuestsOnArcStart(arc);
                
                // Update character narrative
                _ = UpdateCharacterNarrative(arc.CharacterId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling arc started: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        private void HandleArcStepUpdated(string arcId, ArcStepDTO step)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling arc step updated: {arcId} - {step.Title}");
                
                // Check for quest correlations
                _ = CheckQuestCorrelationsForArcStep(arcId, step);
            }
            catch (Exception ex)
            {
                LogError($"Error handling arc step updated: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        private void HandleArcProgressionUpdated(ArcProgressionDTO progression)
        {
            if (isProcessingIntegrationEvent) return;
            
            try
            {
                isProcessingIntegrationEvent = true;
                Log($"Handling arc progression updated: {progression.ArcId}");
                
                // Update related quest progression if appropriate
                _ = UpdateQuestProgressionFromArc(progression);
            }
            catch (Exception ex)
            {
                LogError($"Error handling arc progression updated: {ex.Message}");
            }
            finally
            {
                isProcessingIntegrationEvent = false;
            }
        }
        
        #endregion
        
        #region Integration Logic
        
        private void LinkQuestToArc(string questId, string arcId)
        {
            try
            {
                // Update quest -> arc mapping
                if (!questToArcsMapping.ContainsKey(questId))
                    questToArcsMapping[questId] = new List<string>();
                
                if (!questToArcsMapping[questId].Contains(arcId))
                    questToArcsMapping[questId].Add(arcId);
                
                // Update arc -> quest mapping
                if (!arcToQuestsMapping.ContainsKey(arcId))
                    arcToQuestsMapping[arcId] = new List<string>();
                
                if (!arcToQuestsMapping[arcId].Contains(questId))
                    arcToQuestsMapping[arcId].Add(questId);
                
                Log($"Linked quest {questId} to arc {arcId}");
                
                // Fire event if we have the actual models
                _ = FireQuestArcLinkedEvent(questId, arcId);
            }
            catch (Exception ex)
            {
                LogError($"Error linking quest to arc: {ex.Message}");
            }
        }
        
        private void UnlinkQuestFromArc(string questId, string arcId)
        {
            try
            {
                // Update quest -> arc mapping
                if (questToArcsMapping.ContainsKey(questId))
                    questToArcsMapping[questId].Remove(arcId);
                
                // Update arc -> quest mapping
                if (arcToQuestsMapping.ContainsKey(arcId))
                    arcToQuestsMapping[arcId].Remove(questId);
                
                Log($"Unlinked quest {questId} from arc {arcId}");
                
                // Fire event if we have the actual models
                _ = FireQuestArcUnlinkedEvent(questId, arcId);
            }
            catch (Exception ex)
            {
                LogError($"Error unlinking quest from arc: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task UpdateCharacterNarrative(string characterId)
        {
            if (string.IsNullOrEmpty(characterId))
                return;
            
            try
            {
                // Get character's arc
                var arcId = characterArcMapping.ContainsKey(characterId) ? characterArcMapping[characterId] : null;
                
                // Get character's quests and arcs
                var quests = await GetQuestsForCharacter(characterId);
                var arcs = await GetArcsForCharacter(characterId);
                
                OnCharacterNarrativeUpdated?.Invoke(characterId, quests, arcs);
                Log($"Updated character narrative for {characterId}: {quests.Count} quests, {arcs.Count} arcs");
            }
            catch (Exception ex)
            {
                LogError($"Error updating character narrative: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task CheckArcProgression(VDM.DTOs.Content.Quest.QuestDTO quest)
        {
            try
            {
                if (string.IsNullOrEmpty(quest.ArcId))
                    return;
                
                // Get arc and check if quest completion should advance arc
                var arc = await arcService.GetArcAsync(quest.ArcId);
                if (arc != null)
                {
                    // Logic to determine if arc should progress
                    var relatedQuests = await GetQuestsForArc(quest.ArcId);
                    var completedQuests = relatedQuests.Count(q => q.Status == QuestStatus.Completed);
                    var totalQuests = relatedQuests.Count;
                    
                    if (completedQuests > 0)
                    {
                        var progressPercentage = (float)completedQuests / totalQuests * 100f;
                        
                        // Update arc progression
                        var progressionRequest = new ArcProgressionUpdateRequest
                        {
                            ArcId = quest.ArcId,
                            CompletionPercentage = progressPercentage,
                            TriggeredBy = $"quest_completion:{quest.Id}",
                            Notes = $"Quest '{quest.Title}' completed"
                        };
                        
                        await arcService.UpdateProgressionAsync(quest.ArcId, progressionRequest);
                        Log($"Updated arc progression for {quest.ArcId}: {progressPercentage:F1}%");
                    }
                }
            }
            catch (Exception ex)
            {
                LogError($"Error checking arc progression: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task CheckArcImpact(VDM.DTOs.Content.Quest.QuestDTO quest, string impactType)
        {
            try
            {
                if (string.IsNullOrEmpty(quest.ArcId))
                    return;
                
                // Get arc and assess impact
                var arc = await arcService.GetArcAsync(quest.ArcId);
                if (arc != null)
                {
                    // Logic to determine impact on arc
                    Log($"Assessing {impactType} impact on arc {quest.ArcId}");
                    
                    // This could trigger arc step changes, status updates, etc.
                    // Implementation depends on specific business rules
                }
            }
            catch (Exception ex)
            {
                LogError($"Error checking arc impact: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task CheckArcStepCorrelations(VDM.DTOs.Content.Quest.QuestDTO quest, QuestStepDTO questStep)
        {
            try
            {
                if (string.IsNullOrEmpty(quest.ArcId))
                    return;
                
                // Get arc and check for step correlations
                var arc = await arcService.GetArcAsync(quest.ArcId);
                if (arc?.Steps != null)
                {
                    // Find correlated arc steps
                    var correlatedSteps = arc.Steps.Where(s => 
                        s.Title.Contains(questStep.Title, StringComparison.OrdinalIgnoreCase) ||
                        s.Description.Contains(questStep.Description, StringComparison.OrdinalIgnoreCase)
                    ).ToList();
                    
                    foreach (var arcStep in correlatedSteps)
                    {
                        if (arcStep.Status == ArcStepStatus.Available)
                        {
                            // Mark arc step as active or completed
                            var updateRequest = new ArcStepUpdateRequest
                            {
                                StepId = arcStep.Id,
                                Status = ArcStepStatus.Active,
                                Notes = $"Activated by quest step completion: {questStep.Title}"
                            };
                            
                            await arcService.UpdateStepAsync(quest.ArcId, arcStep.Id, updateRequest);
                            Log($"Activated arc step {arcStep.Title} due to quest step completion");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                LogError($"Error checking arc step correlations: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task CheckQuestCorrelationsForArcStep(string arcId, ArcStepDTO arcStep)
        {
            try
            {
                // Get related quests for the arc
                var relatedQuests = await GetQuestsForArc(arcId);
                
                foreach (var quest in relatedQuests)
                {
                    if (quest.Steps != null)
                    {
                        // Find correlated quest steps
                        var correlatedSteps = quest.Steps.Where(s =>
                            s.Title.Contains(arcStep.Title, StringComparison.OrdinalIgnoreCase) ||
                            s.Description.Contains(arcStep.Description, StringComparison.OrdinalIgnoreCase)
                        ).ToList();
                        
                        foreach (var questStep in correlatedSteps)
                        {
                            if (questStep.Status == QuestStepStatus.Available && arcStep.Status == ArcStepStatus.Completed)
                            {
                                // Mark quest step as active
                                var updateRequest = new QuestStepUpdateRequest
                                {
                                    StepId = questStep.Id,
                                    Status = QuestStepStatus.InProgress,
                                    Notes = $"Activated by arc step completion: {arcStep.Title}"
                                };
                                
                                await questService.UpdateStepAsync(quest.Id, questStep.Id, updateRequest);
                                Log($"Activated quest step {questStep.Title} due to arc step completion");
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                LogError($"Error checking quest correlations for arc step: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task UpdateRelatedQuestsOnArcCompletion(ArcModel arc)
        {
            try
            {
                var relatedQuests = await GetQuestsForArc(arc.Id);
                
                foreach (var quest in relatedQuests)
                {
                    if (quest.Status == QuestStatus.InProgress)
                    {
                        // Mark quest as completed if all steps are done
                        if (quest.Steps?.All(s => s.Status == QuestStepStatus.Completed) == true)
                        {
                            var updateRequest = new QuestUpdateRequest
                            {
                                Status = QuestStatus.Completed,
                                CompletionNotes = $"Completed with arc: {arc.Title}"
                            };
                            
                            await questService.UpdateQuestAsync(quest.Id, updateRequest);
                            Log($"Completed quest {quest.Title} with arc completion");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                LogError($"Error updating related quests on arc completion: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task ActivateRelatedQuestsOnArcStart(ArcModel arc)
        {
            try
            {
                var relatedQuests = await GetQuestsForArc(arc.Id);
                
                foreach (var quest in relatedQuests)
                {
                    if (quest.Status == QuestStatus.Available)
                    {
                        var updateRequest = new QuestUpdateRequest
                        {
                            Status = QuestStatus.InProgress,
                            StartNotes = $"Started with arc: {arc.Title}"
                        };
                        
                        await questService.UpdateQuestAsync(quest.Id, updateRequest);
                        Log($"Activated quest {quest.Title} with arc start");
                    }
                }
            }
            catch (Exception ex)
            {
                LogError($"Error activating related quests on arc start: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task UpdateQuestProgressionFromArc(ArcProgressionDTO progression)
        {
            try
            {
                var relatedQuests = await GetQuestsForArc(progression.ArcId);
                
                foreach (var quest in relatedQuests)
                {
                    // Update quest progression based on arc progression
                    if (quest.Steps != null && quest.Steps.Count > 0)
                    {
                        var targetStepIndex = Math.Min(
                            (int)(progression.CompletionPercentage / 100f * quest.Steps.Count),
                            quest.Steps.Count - 1
                        );
                        
                        // Activate steps up to the target index
                        for (int i = 0; i <= targetStepIndex; i++)
                        {
                            var step = quest.Steps[i];
                            if (step.Status == QuestStepStatus.Available)
                            {
                                var updateRequest = new QuestStepUpdateRequest
                                {
                                    StepId = step.Id,
                                    Status = QuestStepStatus.InProgress,
                                    Notes = $"Activated by arc progression: {progression.CompletionPercentage:F1}%"
                                };
                                
                                await questService.UpdateStepAsync(quest.Id, step.Id, updateRequest);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                LogError($"Error updating quest progression from arc: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Event Helpers
        
        private async System.Threading.Tasks.Task FireQuestArcLinkedEvent(string questId, string arcId)
        {
            try
            {
                var quest = await questService.GetQuestAsync(questId);
                var arc = await arcService.GetArcAsync(arcId);
                
                if (quest != null && arc != null)
                {
                    OnQuestArcLinked?.Invoke(quest, arc);
                }
            }
            catch (Exception ex)
            {
                LogError($"Error firing quest-arc linked event: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task FireQuestArcUnlinkedEvent(string questId, string arcId)
        {
            try
            {
                var quest = await questService.GetQuestAsync(questId);
                var arc = await arcService.GetArcAsync(arcId);
                
                if (quest != null && arc != null)
                {
                    OnQuestArcUnlinked?.Invoke(quest, arc);
                }
            }
            catch (Exception ex)
            {
                LogError($"Error firing quest-arc unlinked event: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Data Queries
        
        private async System.Threading.Tasks.Task<List<VDM.DTOs.Content.Quest.QuestDTO>> GetQuestsForCharacter(string characterId)
        {
            try
            {
                var allQuests = await questService.GetQuestsAsync();
                return allQuests.Where(q => q.CharacterId == characterId).ToList();
            }
            catch (Exception ex)
            {
                LogError($"Error getting quests for character: {ex.Message}");
                return new List<VDM.DTOs.Content.Quest.QuestDTO>();
            }
        }
        
        private async System.Threading.Tasks.Task<List<ArcModel>> GetArcsForCharacter(string characterId)
        {
            try
            {
                var allArcs = await arcService.GetArcsAsync();
                return allArcs.Where(a => a.CharacterId == characterId).ToList();
            }
            catch (Exception ex)
            {
                LogError($"Error getting arcs for character: {ex.Message}");
                return new List<ArcModel>();
            }
        }
        
        private async System.Threading.Tasks.Task<List<VDM.DTOs.Content.Quest.QuestDTO>> GetQuestsForArc(string arcId)
        {
            try
            {
                if (!arcToQuestsMapping.ContainsKey(arcId))
                    return new List<VDM.DTOs.Content.Quest.QuestDTO>();
                
                var questIds = arcToQuestsMapping[arcId];
                var quests = new List<VDM.DTOs.Content.Quest.QuestDTO>();
                
                foreach (var questId in questIds)
                {
                    var quest = await questService.GetQuestAsync(questId);
                    if (quest != null)
                        quests.Add(quest);
                }
                
                return quests;
            }
            catch (Exception ex)
            {
                LogError($"Error getting quests for arc: {ex.Message}");
                return new List<VDM.DTOs.Content.Quest.QuestDTO>();
            }
        }
        
        #endregion
        
        #region Public Interface
        
        /// <summary>
        /// Manually link a quest to an arc
        /// </summary>
        public async System.Threading.Tasks.Task<bool> LinkQuestToArcAsync(string questId, string arcId)
        {
            try
            {
                // Update quest with arc reference
                var updateRequest = new QuestUpdateRequest
                {
                    ArcId = arcId
                };
                
                var success = await questService.UpdateQuestAsync(questId, updateRequest);
                if (success)
                {
                    LinkQuestToArc(questId, arcId);
                    Log($"Manually linked quest {questId} to arc {arcId}");
                }
                
                return success;
            }
            catch (Exception ex)
            {
                LogError($"Error manually linking quest to arc: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Manually unlink a quest from an arc
        /// </summary>
        public async System.Threading.Tasks.Task<bool> UnlinkQuestFromArcAsync(string questId, string arcId)
        {
            try
            {
                // Update quest to remove arc reference
                var updateRequest = new QuestUpdateRequest
                {
                    ArcId = null
                };
                
                var success = await questService.UpdateQuestAsync(questId, updateRequest);
                if (success)
                {
                    UnlinkQuestFromArc(questId, arcId);
                    Log($"Manually unlinked quest {questId} from arc {arcId}");
                }
                
                return success;
            }
            catch (Exception ex)
            {
                LogError($"Error manually unlinking quest from arc: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Get all quests linked to a specific arc
        /// </summary>
        public async System.Threading.Tasks.Task<List<VDM.DTOs.Content.Quest.QuestDTO>> GetLinkedQuestsAsync(string arcId)
        {
            return await GetQuestsForArc(arcId);
        }
        
        /// <summary>
        /// Get all arcs linked to a specific quest
        /// </summary>
        public async System.Threading.Tasks.Task<List<ArcModel>> GetLinkedArcsAsync(string questId)
        {
            try
            {
                if (!questToArcsMapping.ContainsKey(questId))
                    return new List<ArcModel>();
                
                var arcIds = questToArcsMapping[questId];
                var arcs = new List<ArcModel>();
                
                foreach (var arcId in arcIds)
                {
                    var arc = await arcService.GetArcAsync(arcId);
                    if (arc != null)
                        arcs.Add(arc);
                }
                
                return arcs;
            }
            catch (Exception ex)
            {
                LogError($"Error getting linked arcs: {ex.Message}");
                return new List<ArcModel>();
            }
        }
        
        /// <summary>
        /// Get character narrative summary
        /// </summary>
        public async System.Threading.Tasks.Task<CharacterNarrativeSummary> GetCharacterNarrativeAsync(string characterId)
        {
            try
            {
                var quests = await GetQuestsForCharacter(characterId);
                var arcs = await GetArcsForCharacter(characterId);
                
                return new CharacterNarrativeSummary
                {
                    CharacterId = characterId,
                    Quests = quests,
                    Arcs = arcs,
                    ActiveQuestCount = quests.Count(q => q.Status == QuestStatus.InProgress),
                    CompletedQuestCount = quests.Count(q => q.Status == QuestStatus.Completed),
                    ActiveArcCount = arcs.Count(a => a.Status == ArcStatus.Active),
                    CompletedArcCount = arcs.Count(a => a.Status == ArcStatus.Completed),
                    LastUpdated = DateTime.UtcNow
                };
            }
            catch (Exception ex)
            {
                LogError($"Error getting character narrative: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Force data synchronization
        /// </summary>
        public async System.Threading.Tasks.Task ForceResyncAsync()
        {
            await SynchronizeData();
        }
        
        /// <summary>
        /// Get integration statistics
        /// </summary>
        public IntegrationStats GetIntegrationStats()
        {
            return new IntegrationStats
            {
                TotalQuests = questToArcsMapping.Count,
                TotalArcs = arcToQuestsMapping.Count,
                TotalQuestArcLinks = GetTotalQuestArcLinks(),
                TotalCharacterMappings = characterArcMapping.Count,
                IsInitialized = isInitialized,
                LastSyncTime = DateTime.UtcNow
            };
        }
        
        #endregion
        
        #region Logging
        
        private void Log(string message)
        {
            if (enableDebugLogging)
            {
                Debug.Log($"[QuestArcIntegration] {message}");
            }
        }
        
        private void LogError(string message)
        {
            Debug.LogError($"[QuestArcIntegration] {message}");
        }
        
        #endregion

        #region ISystemManager Implementation

        public void InitializeSystem()
        {
            if (IsInitialized)
                return;
                
            Initialize();
            IsInitialized = true;
            HealthStatus = SystemHealthStatus.Healthy;
        }

        public void ShutdownSystem()
        {
            if (!IsInitialized)
                return;
                
            // Cleanup resources
            questToArcsMapping.Clear();
            arcToQuestsMapping.Clear();
            characterArcMapping.Clear();
            
            IsInitialized = false;
            HealthStatus = SystemHealthStatus.Unknown;
        }

        public void UpdateSystem()
        {
            // Periodic system updates
            if (!IsInitialized)
                return;
                
            // Could implement periodic integrity checks here
        }

        public SystemHealthStatus GetHealthStatus()
        {
            return HealthStatus;
        }

        #endregion
    }
    
    #region Supporting Data Models
    
    [Serializable]
    public class IntegrationSyncResult
    {
        public int QuestCount { get; set; }
        public int ArcCount { get; set; }
        public int QuestArcLinks { get; set; }
        public int CharacterMappings { get; set; }
        public DateTime SyncTimestamp { get; set; }
        public bool IsSuccessful { get; set; }
        public string ErrorMessage { get; set; }
    }
    
    [Serializable]
    public class CharacterNarrativeSummary
    {
        public string CharacterId { get; set; }
        public List<VDM.DTOs.Content.Quest.QuestDTO> Quests { get; set; }
        public List<ArcModel> Arcs { get; set; }
        public int ActiveQuestCount { get; set; }
        public int CompletedQuestCount { get; set; }
        public int ActiveArcCount { get; set; }
        public int CompletedArcCount { get; set; }
        public DateTime LastUpdated { get; set; }
    }
    
    [Serializable]
    public class IntegrationStats
    {
        public int TotalQuests { get; set; }
        public int TotalArcs { get; set; }
        public int TotalQuestArcLinks { get; set; }
        public int TotalCharacterMappings { get; set; }
        public bool IsInitialized { get; set; }
        public DateTime LastSyncTime { get; set; }
    }
    
    #endregion
} 