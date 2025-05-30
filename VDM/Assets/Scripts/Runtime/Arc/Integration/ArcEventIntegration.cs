using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core;
using VDM.Runtime.Arc.Models;
using VDM.Runtime.Arc.Services;
using VDM.Runtime.Events;


namespace VDM.Runtime.Arc.Integration
{
    /// <summary>
    /// Handles integration between Arc system and other game systems through events
    /// </summary>
    public class ArcEventIntegration : MonoBehaviour
    {
        [Header("Settings")]
        [SerializeField] private bool enableAutoArcProgression = true;
        [SerializeField] private bool enableStorytellingMode = true;
        [SerializeField] private float arcAnalysisInterval = 60f;
        [SerializeField] private int maxActiveArcs = 5;
        
        private ArcService arcService;
        private Dictionary<string, DateTime> lastArcAnalysis = new Dictionary<string, DateTime>();
        private List<ArcDTO> monitoredArcs = new List<ArcDTO>();
        
        // Events
        public static event Action<ArcDTO> OnArcStarted;
        public static event Action<ArcDTO> OnArcProgressed;
        public static event Action<ArcDTO> OnArcCompleted;
        public static event Action<ArcDTO> OnArcStalled;
        public static event Action<ArcDTO, ArcStepDTO> OnArcStepCompleted;
        public static event Action<string> OnNarrativeEventTriggered;
        
        private void Awake()
        {
            arcService = new ArcService();
            RegisterEventHandlers();
        }
        
        private void Start()
        {
            InitializeArcMonitoring();
        }
        
        private void OnDestroy()
        {
            UnregisterEventHandlers();
        }
        
        /// <summary>
        /// Register event handlers for arc integration
        /// </summary>
        private void RegisterEventHandlers()
        {
            // Quest Events (arcs respond to quest completion)
            EventManager.Subscribe<QuestCompletedEvent>(HandleQuestCompleted);
            EventManager.Subscribe<QuestStartedEvent>(HandleQuestStarted);
            
            // Character Events
            EventManager.Subscribe<CharacterRelationshipChangedEvent>(HandleRelationshipChanged);
            EventManager.Subscribe<CharacterChoiceMadeEvent>(HandleCharacterChoice);
            
            // Faction Events
            EventManager.Subscribe<FactionWarStartedEvent>(HandleFactionWar);
            EventManager.Subscribe<FactionAllianceFormedEvent>(HandleFactionAlliance);
            
            // World Events
            EventManager.Subscribe<WorldStateChangedEvent>(HandleWorldStateChanged);
            EventManager.Subscribe<RegionConqueredEvent>(HandleRegionConquered);
            
            // Time Events
            EventManager.Subscribe<SeasonChangedEvent>(HandleSeasonChanged);
            EventManager.Subscribe<YearPassedEvent>(HandleYearPassed);
            
            // Arc-specific events
            EventManager.Subscribe<NarrativeChoiceEvent>(HandleNarrativeChoice);
            EventManager.Subscribe<StoryBranchEvent>(HandleStoryBranch);
            
            Debug.Log("Arc event handlers registered");
        }
        
        /// <summary>
        /// Unregister event handlers
        /// </summary>
        private void UnregisterEventHandlers()
        {
            EventManager.Unsubscribe<QuestCompletedEvent>(HandleQuestCompleted);
            EventManager.Unsubscribe<QuestStartedEvent>(HandleQuestStarted);
            EventManager.Unsubscribe<CharacterRelationshipChangedEvent>(HandleRelationshipChanged);
            EventManager.Unsubscribe<CharacterChoiceMadeEvent>(HandleCharacterChoice);
            EventManager.Unsubscribe<FactionWarStartedEvent>(HandleFactionWar);
            EventManager.Unsubscribe<FactionAllianceFormedEvent>(HandleFactionAlliance);
            EventManager.Unsubscribe<WorldStateChangedEvent>(HandleWorldStateChanged);
            EventManager.Unsubscribe<RegionConqueredEvent>(HandleRegionConquered);
            EventManager.Unsubscribe<SeasonChangedEvent>(HandleSeasonChanged);
            EventManager.Unsubscribe<YearPassedEvent>(HandleYearPassed);
            EventManager.Unsubscribe<NarrativeChoiceEvent>(HandleNarrativeChoice);
            EventManager.Unsubscribe<StoryBranchEvent>(HandleStoryBranch);
        }
        
        #region Initialization
        
        /// <summary>
        /// Initialize arc monitoring and analysis
        /// </summary>
        private async void InitializeArcMonitoring()
        {
            try
            {
                // Get all active arcs for monitoring
                var activeArcs = await arcService.GetArcsAsync(status: "active");
                monitoredArcs = activeArcs;
                
                // Start periodic arc analysis
                InvokeRepeating(nameof(AnalyzeArcs), arcAnalysisInterval, arcAnalysisInterval);
                
                Debug.Log($"Arc monitoring initialized with {monitoredArcs.Count} active arcs");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize arc monitoring: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Periodic analysis of arc states and progression
        /// </summary>
        private async void AnalyzeArcs()
        {
            try
            {
                // Check for stalled arcs
                var stalledArcs = await arcService.GetStalledArcsAsync();
                foreach (var arc in stalledArcs)
                {
                    OnArcStalled?.Invoke(arc);
                    await HandleStalledArc(arc);
                }
                
                // Update monitored arcs
                var activeArcs = await arcService.GetArcsAsync(status: "active");
                monitoredArcs = activeArcs;
                
                // Analyze arc relationships and dependencies
                await AnalyzeArcRelationships();
                
                Debug.Log($"Arc analysis completed. Monitoring {monitoredArcs.Count} arcs, {stalledArcs.Count} stalled");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Arc analysis failed: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Event Handlers
        
        /// <summary>
        /// Handle quest completion for arc progression
        /// </summary>
        private async void HandleQuestCompleted(QuestCompletedEvent eventData)
        {
            try
            {
                // Find arcs that include this quest
                var relevantArcs = monitoredArcs.Where(a => 
                    a.QuestIds.Contains(eventData.QuestId)).ToList();
                
                foreach (var arc in relevantArcs)
                {
                    await ProcessArcQuestCompletion(arc, eventData.QuestId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest completed for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle quest started events
        /// </summary>
        private async void HandleQuestStarted(QuestStartedEvent eventData)
        {
            try
            {
                // Check if this quest should trigger arc events
                await CheckArcTriggers("quest_started", new Dictionary<string, object>
                {
                    ["quest_id"] = eventData.QuestId,
                    ["character_id"] = eventData.CharacterId
                });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest started for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle character relationship changes
        /// </summary>
        private async void HandleRelationshipChanged(CharacterRelationshipChangedEvent eventData)
        {
            try
            {
                await CheckArcTriggers("relationship_changed", new Dictionary<string, object>
                {
                    ["character1_id"] = eventData.Character1Id,
                    ["character2_id"] = eventData.Character2Id,
                    ["relationship_type"] = eventData.RelationshipType,
                    ["old_value"] = eventData.OldValue,
                    ["new_value"] = eventData.NewValue
                });
                
                // Generate character arcs based on relationship changes
                if (enableAutoArcProgression && Math.Abs(eventData.NewValue - eventData.OldValue) > 10)
                {
                    await GenerateRelationshipArc(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling relationship changed for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle character choice events
        /// </summary>
        private async void HandleCharacterChoice(CharacterChoiceMadeEvent eventData)
        {
            try
            {
                await CheckArcTriggers("character_choice", new Dictionary<string, object>
                {
                    ["character_id"] = eventData.CharacterId,
                    ["choice_id"] = eventData.ChoiceId,
                    ["choice_data"] = eventData.ChoiceData
                });
                
                // Progress character arcs based on choices
                await ProgressCharacterArcs(eventData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling character choice for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle faction war events
        /// </summary>
        private async void HandleFactionWar(FactionWarStartedEvent eventData)
        {
            try
            {
                // Generate war arcs
                if (enableAutoArcProgression)
                {
                    await GenerateWarArc(eventData);
                }
                
                await CheckArcTriggers("faction_war", new Dictionary<string, object>
                {
                    ["faction1_id"] = eventData.Faction1Id,
                    ["faction2_id"] = eventData.Faction2Id,
                    ["war_type"] = eventData.WarType
                });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling faction war for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle faction alliance events
        /// </summary>
        private async void HandleFactionAlliance(FactionAllianceFormedEvent eventData)
        {
            try
            {
                // Generate alliance arcs
                if (enableAutoArcProgression)
                {
                    await GenerateAllianceArc(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling faction alliance for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle world state changes
        /// </summary>
        private async void HandleWorldStateChanged(WorldStateChangedEvent eventData)
        {
            try
            {
                await CheckArcTriggers("world_state_changed", new Dictionary<string, object>
                {
                    ["state_key"] = eventData.StateKey,
                    ["old_value"] = eventData.OldValue,
                    ["new_value"] = eventData.NewValue
                });
                
                // Update global arcs based on world state
                await UpdateGlobalArcs(eventData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling world state change for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle region conquest events
        /// </summary>
        private async void HandleRegionConquered(RegionConqueredEvent eventData)
        {
            try
            {
                // Generate conquest arcs
                if (enableAutoArcProgression)
                {
                    await GenerateConquestArc(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling region conquered for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle season change events
        /// </summary>
        private async void HandleSeasonChanged(SeasonChangedEvent eventData)
        {
            try
            {
                await CheckArcTriggers("season_changed", new Dictionary<string, object>
                {
                    ["old_season"] = eventData.OldSeason,
                    ["new_season"] = eventData.NewSeason,
                    ["year"] = eventData.Year
                });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling season change for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle year passed events
        /// </summary>
        private async void HandleYearPassed(YearPassedEvent eventData)
        {
            try
            {
                // Generate yearly arcs and update long-term storylines
                if (enableAutoArcProgression)
                {
                    await GenerateYearlyArcs(eventData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling year passed for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle narrative choice events
        /// </summary>
        private async void HandleNarrativeChoice(NarrativeChoiceEvent eventData)
        {
            try
            {
                await ProgressArcFromChoice(eventData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling narrative choice for arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Handle story branch events
        /// </summary>
        private async void HandleStoryBranch(StoryBranchEvent eventData)
        {
            try
            {
                await CreateBranchArcs(eventData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling story branch for arcs: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Arc Processing Methods
        
        /// <summary>
        /// Process quest completion within an arc
        /// </summary>
        private async Task ProcessArcQuestCompletion(ArcDTO arc, string questId)
        {
            try
            {
                // Update arc progress based on quest completion
                var currentStep = arc.Steps?.FirstOrDefault(s => s.Order == arc.CurrentStep);
                if (currentStep?.RelatedQuestIds?.Contains(questId) == true)
                {
                    // Mark step as progressed
                    await arcService.UpdateArcStepAsync(arc.Id, currentStep.Id, new Dictionary<string, object>
                    {
                        ["progress_percentage"] = 100f,
                        ["completed"] = true
                    });
                    
                    // Progress arc if step is complete
                    if (ShouldProgressArc(arc, currentStep))
                    {
                        var progressResponse = await arcService.ProgressArcAsync(arc.Id);
                        if (progressResponse != null)
                        {
                            OnArcProgressed?.Invoke(arc);
                            TriggerNarrativeEvents(progressResponse);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error processing arc quest completion: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Check arc triggers based on game events
        /// </summary>
        private async Task CheckArcTriggers(string triggerType, Dictionary<string, object> parameters)
        {
            try
            {
                foreach (var arc in monitoredArcs)
                {
                    if (arc.Status == "pending" && ShouldTriggerArc(arc, triggerType, parameters))
                    {
                        await arcService.StartArcAsync(arc.Id);
                        OnArcStarted?.Invoke(arc);
                        
                        Debug.Log($"Arc triggered: {arc.Title} by {triggerType}");
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error checking arc triggers: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Determine if an arc should be triggered
        /// </summary>
        private bool ShouldTriggerArc(ArcDTO arc, string triggerType, Dictionary<string, object> parameters)
        {
            // Check trigger conditions
            if (arc.TriggerConditions == null) return false;
            
            foreach (var condition in arc.TriggerConditions)
            {
                if (condition.ContainsKey("trigger_type") && 
                    condition["trigger_type"].ToString() == triggerType)
                {
                    // Evaluate condition parameters
                    if (EvaluateTriggerCondition(condition, parameters))
                    {
                        return true;
                    }
                }
            }
            
            return false;
        }
        
        /// <summary>
        /// Evaluate trigger condition against parameters
        /// </summary>
        private bool EvaluateTriggerCondition(Dictionary<string, object> condition, Dictionary<string, object> parameters)
        {
            // Simplified condition evaluation - actual implementation would be more sophisticated
            foreach (var kvp in condition)
            {
                if (kvp.Key != "trigger_type" && parameters.ContainsKey(kvp.Key))
                {
                    if (!parameters[kvp.Key].Equals(kvp.Value))
                    {
                        return false;
                    }
                }
            }
            return true;
        }
        
        /// <summary>
        /// Determine if arc should progress to next step
        /// </summary>
        private bool ShouldProgressArc(ArcDTO arc, ArcStepDTO currentStep)
        {
            // Check if current step is complete and all requirements are met
            return currentStep.Completed && 
                   currentStep.ProgressPercentage >= 100f &&
                   arc.CurrentStep < (arc.Steps?.Count - 1 ?? 0);
        }
        
        /// <summary>
        /// Handle stalled arcs
        /// </summary>
        private async Task HandleStalledArc(ArcDTO arc)
        {
            try
            {
                Debug.LogWarning($"Arc stalled: {arc.Title}");
                
                // Generate intervention events or quests to unstall the arc
                if (enableAutoArcProgression)
                {
                    await GenerateInterventionQuests(arc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling stalled arc: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Trigger narrative events from arc progression
        /// </summary>
        private void TriggerNarrativeEvents(ArcProgressionResponseDTO progressResponse)
        {
            if (progressResponse.NarrativeUpdates != null)
            {
                foreach (var update in progressResponse.NarrativeUpdates)
                {
                    OnNarrativeEventTriggered?.Invoke(update);
                }
            }
        }
        
        #endregion
        
        #region Arc Generation Methods
        
        /// <summary>
        /// Generate relationship-based character arc
        /// </summary>
        private async Task GenerateRelationshipArc(CharacterRelationshipChangedEvent eventData)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    ["arc_type"] = "character",
                    ["character_ids"] = new List<string> { eventData.Character1Id, eventData.Character2Id },
                    ["relationship_context"] = eventData.RelationshipType,
                    ["prompt"] = $"Generate character arc for {eventData.RelationshipType} relationship change"
                };
                
                var arcs = await arcService.GenerateArcsAsync(parameters);
                foreach (var arc in arcs)
                {
                    Debug.Log($"Generated relationship arc: {arc.Title}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating relationship arc: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Generate war-related arc
        /// </summary>
        private async Task GenerateWarArc(FactionWarStartedEvent eventData)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    ["arc_type"] = "global",
                    ["faction_ids"] = new List<string> { eventData.Faction1Id, eventData.Faction2Id },
                    ["war_context"] = eventData.WarType,
                    ["prompt"] = $"Generate war arc for {eventData.WarType} between factions"
                };
                
                var arcs = await arcService.GenerateArcsAsync(parameters);
                foreach (var arc in arcs)
                {
                    Debug.Log($"Generated war arc: {arc.Title}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating war arc: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Generate alliance arc
        /// </summary>
        private async Task GenerateAllianceArc(FactionAllianceFormedEvent eventData)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    ["arc_type"] = "regional",
                    ["faction_ids"] = eventData.FactionIds,
                    ["alliance_type"] = eventData.AllianceType,
                    ["prompt"] = "Generate alliance arc for faction cooperation"
                };
                
                var arcs = await arcService.GenerateArcsAsync(parameters);
                foreach (var arc in arcs)
                {
                    Debug.Log($"Generated alliance arc: {arc.Title}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating alliance arc: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Generate intervention quests for stalled arcs
        /// </summary>
        private async Task GenerateInterventionQuests(ArcDTO arc)
        {
            try
            {
                Debug.Log($"Generating intervention for stalled arc: {arc.Title}");
                // This would generate quests to help unstall the arc
                // Implementation depends on quest generation system
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating intervention quests: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Analysis Methods
        
        /// <summary>
        /// Analyze relationships between arcs
        /// </summary>
        private async Task AnalyzeArcRelationships()
        {
            try
            {
                foreach (var arc in monitoredArcs)
                {
                    var relationships = await arcService.GetArcRelationshipsAsync(arc.Id);
                    // Process relationship data for narrative consistency
                    
                    lastArcAnalysis[arc.Id] = DateTime.UtcNow;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error analyzing arc relationships: {ex.Message}");
            }
        }
        
        #endregion
        
        // Additional methods for other event handlers would be implemented here...
        private async Task ProgressCharacterArcs(CharacterChoiceMadeEvent eventData) { /* Implementation */ }
        private async Task UpdateGlobalArcs(WorldStateChangedEvent eventData) { /* Implementation */ }
        private async Task GenerateConquestArc(RegionConqueredEvent eventData) { /* Implementation */ }
        private async Task GenerateYearlyArcs(YearPassedEvent eventData) { /* Implementation */ }
        private async Task ProgressArcFromChoice(NarrativeChoiceEvent eventData) { /* Implementation */ }
        private async Task CreateBranchArcs(StoryBranchEvent eventData) { /* Implementation */ }
    }
    
    #region Event Data Classes
    
    public class QuestCompletedEvent
    {
        public string QuestId { get; set; }
        public string CharacterId { get; set; }
    }
    
    public class QuestStartedEvent
    {
        public string QuestId { get; set; }
        public string CharacterId { get; set; }
    }
    
    public class CharacterRelationshipChangedEvent
    {
        public string Character1Id { get; set; }
        public string Character2Id { get; set; }
        public string RelationshipType { get; set; }
        public int OldValue { get; set; }
        public int NewValue { get; set; }
    }
    
    public class CharacterChoiceMadeEvent
    {
        public string CharacterId { get; set; }
        public string ChoiceId { get; set; }
        public Dictionary<string, object> ChoiceData { get; set; }
    }
    
    public class FactionWarStartedEvent
    {
        public string Faction1Id { get; set; }
        public string Faction2Id { get; set; }
        public string WarType { get; set; }
    }
    
    public class FactionAllianceFormedEvent
    {
        public List<string> FactionIds { get; set; }
        public string AllianceType { get; set; }
    }
    
    public class WorldStateChangedEvent
    {
        public string StateKey { get; set; }
        public object OldValue { get; set; }
        public object NewValue { get; set; }
    }
    
    public class RegionConqueredEvent
    {
        public string RegionId { get; set; }
        public string ConquerorId { get; set; }
        public string PreviousOwnerId { get; set; }
    }
    
    public class SeasonChangedEvent
    {
        public string OldSeason { get; set; }
        public string NewSeason { get; set; }
        public int Year { get; set; }
    }
    
    public class YearPassedEvent
    {
        public int Year { get; set; }
        public Dictionary<string, object> YearSummary { get; set; }
    }
    
    public class NarrativeChoiceEvent
    {
        public string ChoiceId { get; set; }
        public string ArcId { get; set; }
        public Dictionary<string, object> ChoiceData { get; set; }
    }
    
    public class StoryBranchEvent
    {
        public string ArcId { get; set; }
        public string BranchType { get; set; }
        public List<string> BranchOptions { get; set; }
    }
    
    #endregion
} 