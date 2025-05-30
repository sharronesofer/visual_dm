using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Runtime.Core;
using VDM.Runtime.Quest.Models;
using VDM.Runtime.Services.WebSocket;


namespace VDM.Runtime.Quest.Services
{
    /// <summary>
    /// WebSocket handler for real-time Quest system communication
    /// </summary>
    public class QuestWebSocketHandler : BaseWebSocketHandler
    {
        // Quest Events
        public event Action<QuestDTO> OnQuestCreated;
        public event Action<QuestDTO> OnQuestUpdated;
        public event Action<string> OnQuestDeleted;
        public event Action<QuestDTO> OnQuestStarted;
        public event Action<QuestDTO> OnQuestCompleted;
        public event Action<QuestDTO> OnQuestFailed;
        public event Action<QuestDTO> OnQuestAbandoned;
        public event Action<QuestDTO> OnQuestTurnedIn;
        
        // Quest Step Events
        public event Action<string, QuestStepDTO> OnStepUpdated;
        public event Action<string, QuestStepDTO> OnStepCompleted;
        public event Action<string, QuestStepDTO> OnStepFailed;
        public event Action<string, QuestStepDTO> OnStepStarted;
        
        // Quest Progress Events
        public event Action<string, Dictionary<string, object>> OnProgressUpdated;
        public event Action<string, int, int> OnObjectiveProgress;
        public event Action<string, string> OnQuestHintReceived;
        
        // Integration Events
        public event Action<string, string> OnQuestAssignedToCharacter;
        public event Action<string, string> OnQuestRemovedFromCharacter;
        public event Action<string, string> OnQuestLinkedToArc;
        public event Action<string, string> OnQuestUnlinkedFromArc;
        
        private readonly Dictionary<string, bool> _questSubscriptions = new Dictionary<string, bool>();
        private readonly Dictionary<string, bool> _characterSubscriptions = new Dictionary<string, bool>();
        private readonly Dictionary<string, bool> _typeSubscriptions = new Dictionary<string, bool>();
        
        public QuestWebSocketHandler() : base("quest")
        {
        }
        
        #region Message Handling
        
        /// <summary>
        /// Handle incoming WebSocket message
        /// </summary>
        /// <param name="message">WebSocket message</param>
        protected override void HandleMessage(WebSocketMessage message)
        {
            try
            {
                switch (message.Type)
                {
                    // Quest lifecycle events
                    case "quest_created":
                        HandleQuestCreated(message);
                        break;
                    case "quest_updated":
                        HandleQuestUpdated(message);
                        break;
                    case "quest_deleted":
                        HandleQuestDeleted(message);
                        break;
                    case "quest_started":
                        HandleQuestStarted(message);
                        break;
                    case "quest_completed":
                        HandleQuestCompleted(message);
                        break;
                    case "quest_failed":
                        HandleQuestFailed(message);
                        break;
                    case "quest_abandoned":
                        HandleQuestAbandoned(message);
                        break;
                    case "quest_turned_in":
                        HandleQuestTurnedIn(message);
                        break;
                    
                    // Quest step events
                    case "step_updated":
                        HandleStepUpdated(message);
                        break;
                    case "step_completed":
                        HandleStepCompleted(message);
                        break;
                    case "step_failed":
                        HandleStepFailed(message);
                        break;
                    case "step_started":
                        HandleStepStarted(message);
                        break;
                    
                    // Progress events
                    case "progress_updated":
                        HandleProgressUpdated(message);
                        break;
                    case "objective_progress":
                        HandleObjectiveProgress(message);
                        break;
                    case "quest_hint_received":
                        HandleQuestHintReceived(message);
                        break;
                    
                    // Integration events
                    case "quest_assigned_to_character":
                        HandleQuestAssignedToCharacter(message);
                        break;
                    case "quest_removed_from_character":
                        HandleQuestRemovedFromCharacter(message);
                        break;
                    case "quest_linked_to_arc":
                        HandleQuestLinkedToArc(message);
                        break;
                    case "quest_unlinked_from_arc":
                        HandleQuestUnlinkedFromArc(message);
                        break;
                    
                    default:
                        Debug.LogWarning($"Unknown quest message type: {message.Type}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest WebSocket message: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Quest Lifecycle Handlers
        
        private void HandleQuestCreated(WebSocketMessage message)
        {
            try
            {
                var quest = JsonConvert.DeserializeObject<QuestDTO>(message.Data.ToString());
                if (quest != null)
                {
                    Debug.Log($"Quest created: {quest.Title} (ID: {quest.Id})");
                    OnQuestCreated?.Invoke(quest);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest created: {ex.Message}");
            }
        }
        
        private void HandleQuestUpdated(WebSocketMessage message)
        {
            try
            {
                var quest = JsonConvert.DeserializeObject<QuestDTO>(message.Data.ToString());
                if (quest != null)
                {
                    Debug.Log($"Quest updated: {quest.Title} (ID: {quest.Id})");
                    OnQuestUpdated?.Invoke(quest);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest updated: {ex.Message}");
            }
        }
        
        private void HandleQuestDeleted(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id"))
                {
                    var questId = data["quest_id"].ToString();
                    Debug.Log($"Quest deleted: {questId}");
                    OnQuestDeleted?.Invoke(questId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest deleted: {ex.Message}");
            }
        }
        
        private void HandleQuestStarted(WebSocketMessage message)
        {
            try
            {
                var quest = JsonConvert.DeserializeObject<QuestDTO>(message.Data.ToString());
                if (quest != null)
                {
                    Debug.Log($"Quest started: {quest.Title} (ID: {quest.Id})");
                    OnQuestStarted?.Invoke(quest);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest started: {ex.Message}");
            }
        }
        
        private void HandleQuestCompleted(WebSocketMessage message)
        {
            try
            {
                var quest = JsonConvert.DeserializeObject<QuestDTO>(message.Data.ToString());
                if (quest != null)
                {
                    Debug.Log($"Quest completed: {quest.Title} (ID: {quest.Id})");
                    OnQuestCompleted?.Invoke(quest);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest completed: {ex.Message}");
            }
        }
        
        private void HandleQuestFailed(WebSocketMessage message)
        {
            try
            {
                var quest = JsonConvert.DeserializeObject<QuestDTO>(message.Data.ToString());
                if (quest != null)
                {
                    Debug.Log($"Quest failed: {quest.Title} (ID: {quest.Id})");
                    OnQuestFailed?.Invoke(quest);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest failed: {ex.Message}");
            }
        }
        
        private void HandleQuestAbandoned(WebSocketMessage message)
        {
            try
            {
                var quest = JsonConvert.DeserializeObject<QuestDTO>(message.Data.ToString());
                if (quest != null)
                {
                    Debug.Log($"Quest abandoned: {quest.Title} (ID: {quest.Id})");
                    OnQuestAbandoned?.Invoke(quest);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest abandoned: {ex.Message}");
            }
        }
        
        private void HandleQuestTurnedIn(WebSocketMessage message)
        {
            try
            {
                var quest = JsonConvert.DeserializeObject<QuestDTO>(message.Data.ToString());
                if (quest != null)
                {
                    Debug.Log($"Quest turned in: {quest.Title} (ID: {quest.Id})");
                    OnQuestTurnedIn?.Invoke(quest);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest turned in: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Quest Step Handlers
        
        private void HandleStepUpdated(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("step"))
                {
                    var questId = data["quest_id"].ToString();
                    var step = JsonConvert.DeserializeObject<QuestStepDTO>(data["step"].ToString());
                    if (step != null)
                    {
                        Debug.Log($"Quest step updated: {step.Description} (Quest: {questId}, Step: {step.Id})");
                        OnStepUpdated?.Invoke(questId, step);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling step updated: {ex.Message}");
            }
        }
        
        private void HandleStepCompleted(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("step"))
                {
                    var questId = data["quest_id"].ToString();
                    var step = JsonConvert.DeserializeObject<QuestStepDTO>(data["step"].ToString());
                    if (step != null)
                    {
                        Debug.Log($"Quest step completed: {step.Description} (Quest: {questId}, Step: {step.Id})");
                        OnStepCompleted?.Invoke(questId, step);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling step completed: {ex.Message}");
            }
        }
        
        private void HandleStepFailed(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("step"))
                {
                    var questId = data["quest_id"].ToString();
                    var step = JsonConvert.DeserializeObject<QuestStepDTO>(data["step"].ToString());
                    if (step != null)
                    {
                        Debug.Log($"Quest step failed: {step.Description} (Quest: {questId}, Step: {step.Id})");
                        OnStepFailed?.Invoke(questId, step);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling step failed: {ex.Message}");
            }
        }
        
        private void HandleStepStarted(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("step"))
                {
                    var questId = data["quest_id"].ToString();
                    var step = JsonConvert.DeserializeObject<QuestStepDTO>(data["step"].ToString());
                    if (step != null)
                    {
                        Debug.Log($"Quest step started: {step.Description} (Quest: {questId}, Step: {step.Id})");
                        OnStepStarted?.Invoke(questId, step);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling step started: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Progress Handlers
        
        private void HandleProgressUpdated(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("progress_data"))
                {
                    var questId = data["quest_id"].ToString();
                    var progressData = JsonConvert.DeserializeObject<Dictionary<string, object>>(data["progress_data"].ToString());
                    Debug.Log($"Quest progress updated: {questId}");
                    OnProgressUpdated?.Invoke(questId, progressData);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling progress updated: {ex.Message}");
            }
        }
        
        private void HandleObjectiveProgress(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("current_count") && data.ContainsKey("required_count"))
                {
                    var questId = data["quest_id"].ToString();
                    var currentCount = Convert.ToInt32(data["current_count"]);
                    var requiredCount = Convert.ToInt32(data["required_count"]);
                    Debug.Log($"Quest objective progress: {questId} ({currentCount}/{requiredCount})");
                    OnObjectiveProgress?.Invoke(questId, currentCount, requiredCount);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling objective progress: {ex.Message}");
            }
        }
        
        private void HandleQuestHintReceived(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("hint"))
                {
                    var questId = data["quest_id"].ToString();
                    var hint = data["hint"].ToString();
                    Debug.Log($"Quest hint received for {questId}: {hint}");
                    OnQuestHintReceived?.Invoke(questId, hint);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest hint received: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Integration Handlers
        
        private void HandleQuestAssignedToCharacter(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("character_id"))
                {
                    var questId = data["quest_id"].ToString();
                    var characterId = data["character_id"].ToString();
                    Debug.Log($"Quest {questId} assigned to character {characterId}");
                    OnQuestAssignedToCharacter?.Invoke(questId, characterId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest assigned to character: {ex.Message}");
            }
        }
        
        private void HandleQuestRemovedFromCharacter(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("character_id"))
                {
                    var questId = data["quest_id"].ToString();
                    var characterId = data["character_id"].ToString();
                    Debug.Log($"Quest {questId} removed from character {characterId}");
                    OnQuestRemovedFromCharacter?.Invoke(questId, characterId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest removed from character: {ex.Message}");
            }
        }
        
        private void HandleQuestLinkedToArc(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("arc_id"))
                {
                    var questId = data["quest_id"].ToString();
                    var arcId = data["arc_id"].ToString();
                    Debug.Log($"Quest {questId} linked to arc {arcId}");
                    OnQuestLinkedToArc?.Invoke(questId, arcId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest linked to arc: {ex.Message}");
            }
        }
        
        private void HandleQuestUnlinkedFromArc(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("quest_id") && data.ContainsKey("arc_id"))
                {
                    var questId = data["quest_id"].ToString();
                    var arcId = data["arc_id"].ToString();
                    Debug.Log($"Quest {questId} unlinked from arc {arcId}");
                    OnQuestUnlinkedFromArc?.Invoke(questId, arcId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest unlinked from arc: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Subscription Management
        
        /// <summary>
        /// Subscribe to updates for a specific quest
        /// </summary>
        /// <param name="questId">Quest ID to subscribe to</param>
        public async void SubscribeToQuest(string questId)
        {
            try
            {
                if (string.IsNullOrEmpty(questId))
                {
                    Debug.LogError("Quest ID cannot be null or empty");
                    return;
                }
                
                if (_questSubscriptions.ContainsKey(questId))
                {
                    Debug.LogWarning($"Already subscribed to quest: {questId}");
                    return;
                }
                
                var subscribeMessage = new
                {
                    action = "subscribe",
                    target = "quest",
                    quest_id = questId
                };
                
                await SendMessage(subscribeMessage);
                _questSubscriptions[questId] = true;
                
                Debug.Log($"Subscribed to quest updates: {questId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error subscribing to quest {questId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Unsubscribe from updates for a specific quest
        /// </summary>
        /// <param name="questId">Quest ID to unsubscribe from</param>
        public async void UnsubscribeFromQuest(string questId)
        {
            try
            {
                if (string.IsNullOrEmpty(questId))
                {
                    Debug.LogError("Quest ID cannot be null or empty");
                    return;
                }
                
                if (!_questSubscriptions.ContainsKey(questId))
                {
                    Debug.LogWarning($"Not subscribed to quest: {questId}");
                    return;
                }
                
                var unsubscribeMessage = new
                {
                    action = "unsubscribe",
                    target = "quest",
                    quest_id = questId
                };
                
                await SendMessage(unsubscribeMessage);
                _questSubscriptions.Remove(questId);
                
                Debug.Log($"Unsubscribed from quest updates: {questId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error unsubscribing from quest {questId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Subscribe to updates for a specific character's quests
        /// </summary>
        /// <param name="characterId">Character ID to subscribe to</param>
        public async void SubscribeToCharacterQuests(string characterId)
        {
            try
            {
                if (string.IsNullOrEmpty(characterId))
                {
                    Debug.LogError("Character ID cannot be null or empty");
                    return;
                }
                
                if (_characterSubscriptions.ContainsKey(characterId))
                {
                    Debug.LogWarning($"Already subscribed to character quests: {characterId}");
                    return;
                }
                
                var subscribeMessage = new
                {
                    action = "subscribe",
                    target = "character_quests",
                    character_id = characterId
                };
                
                await SendMessage(subscribeMessage);
                _characterSubscriptions[characterId] = true;
                
                Debug.Log($"Subscribed to character quest updates: {characterId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error subscribing to character quests {characterId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Subscribe to updates for a specific quest type
        /// </summary>
        /// <param name="questType">Quest type to subscribe to</param>
        public async void SubscribeToQuestType(string questType)
        {
            try
            {
                if (string.IsNullOrEmpty(questType))
                {
                    Debug.LogError("Quest type cannot be null or empty");
                    return;
                }
                
                var typeKey = questType.ToLower();
                
                if (_typeSubscriptions.ContainsKey(typeKey))
                {
                    Debug.LogWarning($"Already subscribed to quest type: {questType}");
                    return;
                }
                
                var subscribeMessage = new
                {
                    action = "subscribe",
                    target = "quest_type",
                    quest_type = typeKey
                };
                
                await SendMessage(subscribeMessage);
                _typeSubscriptions[typeKey] = true;
                
                Debug.Log($"Subscribed to quest type updates: {questType}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error subscribing to quest type {questType}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Clear all subscriptions
        /// </summary>
        public override void ClearSubscriptions()
        {
            base.ClearSubscriptions();
            _questSubscriptions.Clear();
            _characterSubscriptions.Clear();
            _typeSubscriptions.Clear();
        }
        
        #endregion
    }
} 