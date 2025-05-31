using NativeWebSocket;
using System;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using VDM.DTOs.Common;
using VDM.Infrastructure.Services.Websocket;
using VDM.Infrastructure.Core;
using VDM.Systems.Quest.Models;


namespace VDM.Systems.Quest.Services
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
        protected override void HandleMessage(string message)
        {
            try
            {
                var messageData = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
                
                if (!messageData.TryGetValue("type", out var messageType))
                {
                    Debug.LogWarning("Quest WebSocket message missing type field");
                    return;
                }

                var type = messageType.ToString();
                
                switch (type)
                {
                    case "quest_created":
                        if (messageData.TryGetValue("data", out var questData))
                        {
                            var questJson = JsonConvert.SerializeObject(questData);
                            var quest = JsonConvert.DeserializeObject<QuestDTO>(questJson);
                            if (quest != null)
                            {
                                OnQuestCreated?.Invoke(quest);
                            }
                        }
                        break;

                    case "quest_updated":
                        if (messageData.TryGetValue("data", out var updatedQuestData))
                        {
                            var questJson = JsonConvert.SerializeObject(updatedQuestData);
                            var quest = JsonConvert.DeserializeObject<QuestDTO>(questJson);
                            if (quest != null)
                            {
                                OnQuestUpdated?.Invoke(quest);
                            }
                        }
                        break;

                    case "quest_deleted":
                        if (messageData.TryGetValue("quest_id", out var deletedQuestIdObj))
                        {
                            var questId = deletedQuestIdObj.ToString();
                            OnQuestDeleted?.Invoke(questId);
                        }
                        break;

                    case "quest_started":
                        if (messageData.TryGetValue("data", out var startedQuestData))
                        {
                            var questJson = JsonConvert.SerializeObject(startedQuestData);
                            var quest = JsonConvert.DeserializeObject<QuestDTO>(questJson);
                            if (quest != null)
                            {
                                OnQuestStarted?.Invoke(quest);
                            }
                        }
                        break;

                    case "quest_completed":
                        if (messageData.TryGetValue("quest_id", out var completedQuestIdObj))
                        {
                            var questId = completedQuestIdObj.ToString();
                            OnQuestCompleted?.Invoke(questId);
                        }
                        break;

                    case "quest_failed":
                        if (messageData.TryGetValue("quest_id", out var failedQuestIdObj))
                        {
                            var questId = failedQuestIdObj.ToString();
                            OnQuestFailed?.Invoke(questId);
                        }
                        break;

                    case "quest_abandoned":
                        if (messageData.TryGetValue("data", out var abandonedQuestData))
                        {
                            var questJson = JsonConvert.SerializeObject(abandonedQuestData);
                            var quest = JsonConvert.DeserializeObject<QuestDTO>(questJson);
                            if (quest != null)
                            {
                                OnQuestAbandoned?.Invoke(quest);
                            }
                        }
                        break;

                    case "quest_turned_in":
                        if (messageData.TryGetValue("data", out var turnedInQuestData))
                        {
                            var questJson = JsonConvert.SerializeObject(turnedInQuestData);
                            var quest = JsonConvert.DeserializeObject<QuestDTO>(questJson);
                            if (quest != null)
                            {
                                OnQuestTurnedIn?.Invoke(quest);
                            }
                        }
                        break;

                    case "step_updated":
                        if (messageData.TryGetValue("data", out var stepUpdatedData))
                        {
                            var stepJson = JsonConvert.SerializeObject(stepUpdatedData);
                            var step = JsonConvert.DeserializeObject<QuestStepDTO>(stepJson);
                            if (step != null)
                            {
                                if (messageData.TryGetValue("quest_id", out var questIdObj))
                                {
                                    var questId = questIdObj.ToString();
                                    OnStepUpdated?.Invoke(questId, step);
                                }
                            }
                        }
                        break;

                    case "step_completed":
                        if (messageData.TryGetValue("data", out var stepCompletedData))
                        {
                            var stepJson = JsonConvert.SerializeObject(stepCompletedData);
                            var step = JsonConvert.DeserializeObject<QuestStepDTO>(stepJson);
                            if (step != null)
                            {
                                if (messageData.TryGetValue("quest_id", out var questIdObj))
                                {
                                    var questId = questIdObj.ToString();
                                    OnStepCompleted?.Invoke(questId, step);
                                }
                            }
                        }
                        break;

                    case "step_failed":
                        if (messageData.TryGetValue("data", out var stepFailedData))
                        {
                            var stepJson = JsonConvert.SerializeObject(stepFailedData);
                            var step = JsonConvert.DeserializeObject<QuestStepDTO>(stepJson);
                            if (step != null)
                            {
                                if (messageData.TryGetValue("quest_id", out var questIdObj))
                                {
                                    var questId = questIdObj.ToString();
                                    OnStepFailed?.Invoke(questId, step);
                                }
                            }
                        }
                        break;

                    case "step_started":
                        if (messageData.TryGetValue("data", out var stepStartedData))
                        {
                            var stepJson = JsonConvert.SerializeObject(stepStartedData);
                            var step = JsonConvert.DeserializeObject<QuestStepDTO>(stepJson);
                            if (step != null)
                            {
                                if (messageData.TryGetValue("quest_id", out var questIdObj))
                                {
                                    var questId = questIdObj.ToString();
                                    OnStepStarted?.Invoke(questId, step);
                                }
                            }
                        }
                        break;

                    case "progress_updated":
                        if (messageData.TryGetValue("data", out var progressData))
                        {
                            var progressJson = JsonConvert.SerializeObject(progressData);
                            var progress = JsonConvert.DeserializeObject<Dictionary<string, object>>(progressJson);
                            if (progress != null)
                            {
                                if (messageData.TryGetValue("quest_id", out var questIdObj))
                                {
                                    var questId = questIdObj.ToString();
                                    OnProgressUpdated?.Invoke(questId, progress);
                                }
                            }
                        }
                        break;

                    case "objective_progress":
                        if (messageData.TryGetValue("data", out var objectiveProgressData))
                        {
                            var objectiveProgressJson = JsonConvert.SerializeObject(objectiveProgressData);
                            var objectiveProgress = JsonConvert.DeserializeObject<Dictionary<string, object>>(objectiveProgressJson);
                            if (objectiveProgress != null)
                            {
                                if (objectiveProgress.TryGetValue("quest_id", out var questIdObj))
                                {
                                    var questId = questIdObj.ToString();
                                    if (objectiveProgress.TryGetValue("current_count", out var currentCountObj) && objectiveProgress.TryGetValue("required_count", out var requiredCountObj))
                                    {
                                        var currentCount = Convert.ToInt32(currentCountObj);
                                        var requiredCount = Convert.ToInt32(requiredCountObj);
                                        OnObjectiveProgress?.Invoke(questId, currentCount, requiredCount);
                                    }
                                }
                            }
                        }
                        break;

                    case "quest_hint_received":
                        if (messageData.TryGetValue("data", out var hintData))
                        {
                            var hintJson = JsonConvert.SerializeObject(hintData);
                            var hint = JsonConvert.DeserializeObject<string>(hintJson);
                            if (hint != null)
                            {
                                if (messageData.TryGetValue("quest_id", out var questIdObj))
                                {
                                    var questId = questIdObj.ToString();
                                    OnQuestHintReceived?.Invoke(questId, hint);
                                }
                            }
                        }
                        break;

                    case "quest_assigned_to_character":
                        if (messageData.TryGetValue("data", out var assignedData))
                        {
                            var assignedJson = JsonConvert.SerializeObject(assignedData);
                            var assigned = JsonConvert.DeserializeObject<Dictionary<string, object>>(assignedJson);
                            if (assigned != null && assigned.ContainsKey("quest_id") && assigned.ContainsKey("character_id"))
                            {
                                var questId = assigned["quest_id"].ToString();
                                var characterId = assigned["character_id"].ToString();
                                OnQuestAssignedToCharacter?.Invoke(questId, characterId);
                            }
                        }
                        break;

                    case "quest_removed_from_character":
                        if (messageData.TryGetValue("data", out var removedData))
                        {
                            var removedJson = JsonConvert.SerializeObject(removedData);
                            var removed = JsonConvert.DeserializeObject<Dictionary<string, object>>(removedJson);
                            if (removed != null && removed.ContainsKey("quest_id") && removed.ContainsKey("character_id"))
                            {
                                var questId = removed["quest_id"].ToString();
                                var characterId = removed["character_id"].ToString();
                                OnQuestRemovedFromCharacter?.Invoke(questId, characterId);
                            }
                        }
                        break;

                    case "quest_linked_to_arc":
                        if (messageData.TryGetValue("data", out var linkedData))
                        {
                            var linkedJson = JsonConvert.SerializeObject(linkedData);
                            var linked = JsonConvert.DeserializeObject<Dictionary<string, object>>(linkedJson);
                            if (linked != null && linked.ContainsKey("quest_id") && linked.ContainsKey("arc_id"))
                            {
                                var questId = linked["quest_id"].ToString();
                                var arcId = linked["arc_id"].ToString();
                                OnQuestLinkedToArc?.Invoke(questId, arcId);
                            }
                        }
                        break;

                    case "quest_unlinked_from_arc":
                        if (messageData.TryGetValue("data", out var unlinkedData))
                        {
                            var unlinkedJson = JsonConvert.SerializeObject(unlinkedData);
                            var unlinked = JsonConvert.DeserializeObject<Dictionary<string, object>>(unlinkedJson);
                            if (unlinked != null && unlinked.ContainsKey("quest_id") && unlinked.ContainsKey("arc_id"))
                            {
                                var questId = unlinked["quest_id"].ToString();
                                var arcId = unlinked["arc_id"].ToString();
                                OnQuestUnlinkedFromArc?.Invoke(questId, arcId);
                            }
                        }
                        break;

                    default:
                        Debug.LogWarning($"Unknown quest WebSocket message type: {type}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest WebSocket message: {ex.Message}");
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
        public void ClearSubscriptions()
        {
            _questSubscriptions.Clear();
            _characterSubscriptions.Clear();
            _typeSubscriptions.Clear();
        }
        
        #endregion
    }
} 