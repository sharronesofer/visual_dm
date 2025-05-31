using NativeWebSocket;
using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Infrastructure.Services.Websocket;
using VDM.Systems.Arc.Models;
using Newtonsoft.Json;


namespace VDM.Systems.Arc.Services
{
    /// <summary>
    /// WebSocket handler for real-time Arc system communication
    /// </summary>
    public class ArcWebSocketHandler : BaseWebSocketHandler
    {
        // Arc Events
        public event Action<ArcModel> OnArcCreated;
        public event Action<ArcModel> OnArcUpdated;
        public event Action<string> OnArcDeleted;
        public event Action<ArcModel> OnArcStarted;
        public event Action<ArcModel> OnArcCompleted;
        public event Action<ArcModel> OnArcFailed;
        public event Action<ArcModel> OnArcStalled;
        
        // Arc Step Events
        public event Action<string, ArcStepModel> OnStepUpdated;
        public event Action<string, ArcStepModel> OnStepCompleted;
        public event Action<string, ArcStepModel> OnStepFailed;
        public event Action<string, ArcStepModel> OnStepStarted;
        
        // Arc Progression Events
        public event Action<ArcProgressionModel> OnProgressionUpdated;
        public event Action<string, string> OnMilestoneReached;
        public event Action<ArcModel> OnArcPhaseChanged;
        
        // Integration Events
        public event Action<QuestOpportunityModel> OnQuestOpportunityCreated;
        public event Action<string, List<string>> OnArcQuestLinked;
        public event Action<string, string> OnCharacterJoinedArc;
        public event Action<string, string> OnCharacterLeftArc;
        
        private readonly Dictionary<string, bool> _arcSubscriptions = new Dictionary<string, bool>();
        private readonly Dictionary<string, bool> _characterSubscriptions = new Dictionary<string, bool>();
        private readonly Dictionary<string, bool> _typeSubscriptions = new Dictionary<string, bool>();
        
        public ArcWebSocketHandler() : base("arc")
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
                    Debug.LogWarning("Arc WebSocket message missing type field");
                    return;
                }

                var type = messageType.ToString();
                
                switch (type)
                {
                    case "arc_update":
                        if (messageData.TryGetValue("data", out var arcData))
                        {
                            var arcJson = JsonConvert.SerializeObject(arcData);
                            var arc = JsonConvert.DeserializeObject<ArcDTO>(arcJson);
                            if (arc != null)
                            {
                                OnArcUpdate?.Invoke(arc);
                            }
                        }
                        break;

                    case "arc_created":
                        if (messageData.TryGetValue("data", out var newArcData))
                        {
                            var arcJson = JsonConvert.SerializeObject(newArcData);
                            var arc = JsonConvert.DeserializeObject<ArcDTO>(arcJson);
                            if (arc != null)
                            {
                                OnArcCreated?.Invoke(arc);
                            }
                        }
                        break;

                    case "arc_deleted":
                        if (messageData.TryGetValue("arc_id", out var arcIdObj))
                        {
                            var arcId = arcIdObj.ToString();
                            OnArcDeleted?.Invoke(arcId);
                        }
                        break;

                    case "arc_quest_update":
                        if (messageData.TryGetValue("data", out var questUpdateData))
                        {
                            var updateJson = JsonConvert.SerializeObject(questUpdateData);
                            var update = JsonConvert.DeserializeObject<ArcQuestUpdateEvent>(updateJson);
                            if (update != null)
                            {
                                OnArcQuestUpdate?.Invoke(update);
                            }
                        }
                        break;

                    case "arc_status_change":
                        if (messageData.TryGetValue("data", out var statusData))
                        {
                            var statusJson = JsonConvert.SerializeObject(statusData);
                            var statusChange = JsonConvert.DeserializeObject<ArcStatusChangeEvent>(statusJson);
                            if (statusChange != null)
                            {
                                OnArcStatusChange?.Invoke(statusChange);
                            }
                        }
                        break;

                    default:
                        Debug.LogWarning($"Unknown arc WebSocket message type: {type}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc WebSocket message: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Arc Lifecycle Handlers
        
        private void HandleArcCreated(WebSocketMessage message)
        {
            try
            {
                var arc = JsonConvert.DeserializeObject<ArcModel>(message.Data.ToString());
                if (arc != null)
                {
                    Debug.Log($"Arc created: {arc.Title} (ID: {arc.Id})");
                    OnArcCreated?.Invoke(arc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc created: {ex.Message}");
            }
        }
        
        private void HandleArcUpdated(WebSocketMessage message)
        {
            try
            {
                var arc = JsonConvert.DeserializeObject<ArcModel>(message.Data.ToString());
                if (arc != null)
                {
                    Debug.Log($"Arc updated: {arc.Title} (ID: {arc.Id})");
                    OnArcUpdated?.Invoke(arc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc updated: {ex.Message}");
            }
        }
        
        private void HandleArcDeleted(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("arc_id"))
                {
                    var arcId = data["arc_id"].ToString();
                    Debug.Log($"Arc deleted: {arcId}");
                    OnArcDeleted?.Invoke(arcId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc deleted: {ex.Message}");
            }
        }
        
        private void HandleArcStarted(WebSocketMessage message)
        {
            try
            {
                var arc = JsonConvert.DeserializeObject<ArcModel>(message.Data.ToString());
                if (arc != null)
                {
                    Debug.Log($"Arc started: {arc.Title} (ID: {arc.Id})");
                    OnArcStarted?.Invoke(arc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc started: {ex.Message}");
            }
        }
        
        private void HandleArcCompleted(WebSocketMessage message)
        {
            try
            {
                var arc = JsonConvert.DeserializeObject<ArcModel>(message.Data.ToString());
                if (arc != null)
                {
                    Debug.Log($"Arc completed: {arc.Title} (ID: {arc.Id})");
                    OnArcCompleted?.Invoke(arc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc completed: {ex.Message}");
            }
        }
        
        private void HandleArcFailed(WebSocketMessage message)
        {
            try
            {
                var arc = JsonConvert.DeserializeObject<ArcModel>(message.Data.ToString());
                if (arc != null)
                {
                    Debug.Log($"Arc failed: {arc.Title} (ID: {arc.Id})");
                    OnArcFailed?.Invoke(arc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc failed: {ex.Message}");
            }
        }
        
        private void HandleArcStalled(WebSocketMessage message)
        {
            try
            {
                var arc = JsonConvert.DeserializeObject<ArcModel>(message.Data.ToString());
                if (arc != null)
                {
                    Debug.Log($"Arc stalled: {arc.Title} (ID: {arc.Id})");
                    OnArcStalled?.Invoke(arc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc stalled: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Arc Step Handlers
        
        private void HandleStepUpdated(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("arc_id") && data.ContainsKey("step"))
                {
                    var arcId = data["arc_id"].ToString();
                    var step = JsonConvert.DeserializeObject<ArcStepModel>(data["step"].ToString());
                    if (step != null)
                    {
                        Debug.Log($"Arc step updated: {step.Title} (Arc: {arcId}, Step: {step.Id})");
                        OnStepUpdated?.Invoke(arcId, step);
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
                if (data != null && data.ContainsKey("arc_id") && data.ContainsKey("step"))
                {
                    var arcId = data["arc_id"].ToString();
                    var step = JsonConvert.DeserializeObject<ArcStepModel>(data["step"].ToString());
                    if (step != null)
                    {
                        Debug.Log($"Arc step completed: {step.Title} (Arc: {arcId}, Step: {step.Id})");
                        OnStepCompleted?.Invoke(arcId, step);
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
                if (data != null && data.ContainsKey("arc_id") && data.ContainsKey("step"))
                {
                    var arcId = data["arc_id"].ToString();
                    var step = JsonConvert.DeserializeObject<ArcStepModel>(data["step"].ToString());
                    if (step != null)
                    {
                        Debug.Log($"Arc step failed: {step.Title} (Arc: {arcId}, Step: {step.Id})");
                        OnStepFailed?.Invoke(arcId, step);
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
                if (data != null && data.ContainsKey("arc_id") && data.ContainsKey("step"))
                {
                    var arcId = data["arc_id"].ToString();
                    var step = JsonConvert.DeserializeObject<ArcStepModel>(data["step"].ToString());
                    if (step != null)
                    {
                        Debug.Log($"Arc step started: {step.Title} (Arc: {arcId}, Step: {step.Id})");
                        OnStepStarted?.Invoke(arcId, step);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling step started: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Progression Handlers
        
        private void HandleProgressionUpdated(WebSocketMessage message)
        {
            try
            {
                var progression = JsonConvert.DeserializeObject<ArcProgressionModel>(message.Data.ToString());
                if (progression != null)
                {
                    Debug.Log($"Arc progression updated: {progression.ArcId} ({progression.CompletionPercentage:F1}%)");
                    OnProgressionUpdated?.Invoke(progression);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling progression updated: {ex.Message}");
            }
        }
        
        private void HandleMilestoneReached(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("arc_id") && data.ContainsKey("milestone"))
                {
                    var arcId = data["arc_id"].ToString();
                    var milestone = data["milestone"].ToString();
                    Debug.Log($"Milestone reached in arc {arcId}: {milestone}");
                    OnMilestoneReached?.Invoke(arcId, milestone);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling milestone reached: {ex.Message}");
            }
        }
        
        private void HandleArcPhaseChanged(WebSocketMessage message)
        {
            try
            {
                var arc = JsonConvert.DeserializeObject<ArcModel>(message.Data.ToString());
                if (arc != null)
                {
                    Debug.Log($"Arc phase changed: {arc.Title} (ID: {arc.Id})");
                    OnArcPhaseChanged?.Invoke(arc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc phase changed: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Integration Handlers
        
        private void HandleQuestOpportunityCreated(WebSocketMessage message)
        {
            try
            {
                var opportunity = JsonConvert.DeserializeObject<QuestOpportunityModel>(message.Data.ToString());
                if (opportunity != null)
                {
                    Debug.Log($"Quest opportunity created: {opportunity.Title} (Arc: {opportunity.ArcId})");
                    OnQuestOpportunityCreated?.Invoke(opportunity);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling quest opportunity created: {ex.Message}");
            }
        }
        
        private void HandleArcQuestLinked(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("arc_id") && data.ContainsKey("quest_ids"))
                {
                    var arcId = data["arc_id"].ToString();
                    var questIds = JsonConvert.DeserializeObject<List<string>>(data["quest_ids"].ToString());
                    Debug.Log($"Quests linked to arc {arcId}: {string.Join(", ", questIds)}");
                    OnArcQuestLinked?.Invoke(arcId, questIds);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling arc quest linked: {ex.Message}");
            }
        }
        
        private void HandleCharacterJoinedArc(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("arc_id") && data.ContainsKey("character_id"))
                {
                    var arcId = data["arc_id"].ToString();
                    var characterId = data["character_id"].ToString();
                    Debug.Log($"Character {characterId} joined arc {arcId}");
                    OnCharacterJoinedArc?.Invoke(arcId, characterId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling character joined arc: {ex.Message}");
            }
        }
        
        private void HandleCharacterLeftArc(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                if (data != null && data.ContainsKey("arc_id") && data.ContainsKey("character_id"))
                {
                    var arcId = data["arc_id"].ToString();
                    var characterId = data["character_id"].ToString();
                    Debug.Log($"Character {characterId} left arc {arcId}");
                    OnCharacterLeftArc?.Invoke(arcId, characterId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling character left arc: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Subscription Management
        
        /// <summary>
        /// Subscribe to updates for a specific arc
        /// </summary>
        /// <param name="arcId">Arc ID to subscribe to</param>
        public async void SubscribeToArc(string arcId)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return;
                }
                
                if (_arcSubscriptions.ContainsKey(arcId))
                {
                    Debug.LogWarning($"Already subscribed to arc: {arcId}");
                    return;
                }
                
                var subscribeMessage = new
                {
                    action = "subscribe",
                    target = "arc",
                    arc_id = arcId
                };
                
                await SendMessage(subscribeMessage);
                _arcSubscriptions[arcId] = true;
                
                Debug.Log($"Subscribed to arc updates: {arcId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error subscribing to arc {arcId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Unsubscribe from updates for a specific arc
        /// </summary>
        /// <param name="arcId">Arc ID to unsubscribe from</param>
        public async void UnsubscribeFromArc(string arcId)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return;
                }
                
                if (!_arcSubscriptions.ContainsKey(arcId))
                {
                    Debug.LogWarning($"Not subscribed to arc: {arcId}");
                    return;
                }
                
                var unsubscribeMessage = new
                {
                    action = "unsubscribe",
                    target = "arc",
                    arc_id = arcId
                };
                
                await SendMessage(unsubscribeMessage);
                _arcSubscriptions.Remove(arcId);
                
                Debug.Log($"Unsubscribed from arc updates: {arcId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error unsubscribing from arc {arcId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Subscribe to updates for a specific character's arcs
        /// </summary>
        /// <param name="characterId">Character ID to subscribe to</param>
        public async void SubscribeToCharacterArcs(string characterId)
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
                    Debug.LogWarning($"Already subscribed to character arcs: {characterId}");
                    return;
                }
                
                var subscribeMessage = new
                {
                    action = "subscribe",
                    target = "character_arcs",
                    character_id = characterId
                };
                
                await SendMessage(subscribeMessage);
                _characterSubscriptions[characterId] = true;
                
                Debug.Log($"Subscribed to character arc updates: {characterId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error subscribing to character arcs {characterId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Subscribe to updates for a specific arc type
        /// </summary>
        /// <param name="arcType">Arc type to subscribe to</param>
        public async void SubscribeToArcType(ArcType arcType)
        {
            try
            {
                var typeKey = arcType.ToString().ToLower();
                
                if (_typeSubscriptions.ContainsKey(typeKey))
                {
                    Debug.LogWarning($"Already subscribed to arc type: {arcType}");
                    return;
                }
                
                var subscribeMessage = new
                {
                    action = "subscribe",
                    target = "arc_type",
                    arc_type = typeKey
                };
                
                await SendMessage(subscribeMessage);
                _typeSubscriptions[typeKey] = true;
                
                Debug.Log($"Subscribed to arc type updates: {arcType}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error subscribing to arc type {arcType}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Clear all subscriptions
        /// </summary>
        public void ClearSubscriptions()
        {
            _arcSubscriptions.Clear();
            _characterSubscriptions.Clear();
            _typeSubscriptions.Clear();
        }
        
        #endregion

        #region Data Classes

        [Serializable]
        private class WebSocketMessage
        {
            public string type;
            public string data;
        }

        #endregion
    }
} 