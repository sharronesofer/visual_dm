using NativeWebSocket;
using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Infrastructure.Services.Websocket;
using VDM.Systems.Dialogue.Models;


namespace VDM.Systems.Dialogue.Services
{
    /// <summary>
    /// WebSocket handler for real-time dialogue and conversation events
    /// </summary>
    public class DialogueWebSocketHandler : BaseWebSocketHandler
    {
        // Conversation lifecycle events
        public event Action<ConversationModel> OnConversationStarted;
        public event Action<ConversationModel> OnConversationEnded;
        public event Action<ConversationModel> OnConversationUpdated;
        public event Action<string> OnConversationError;
        
        // Message events
        public event Action<ConversationEntryModel> OnMessageReceived;
        public event Action<ConversationEntryModel> OnMessageSent;
        public event Action<string, ConversationEntryModel> OnMessageUpdated;
        public event Action<string, string> OnMessageDeleted;
        
        // Dialogue option events
        public event Action<string, List<DialogueOptionModel>> OnDialogueOptionsUpdated;
        public event Action<string, DialogueOptionModel> OnDialogueOptionSelected;
        public event Action<string, List<DialogueOptionModel>> OnDialogueOptionsEvaluated;
        
        // Context and state events
        public event Action<string, ConversationContextModel> OnContextUpdated;
        public event Action<string, string> OnCurrentSpeakerChanged;
        public event Action<string, Dictionary<string, object>> OnConversationStateChanged;
        
        // Relationship events
        public event Action<string, string, float> OnRelationshipChanged;
        public event Action<string, Dictionary<string, float>> OnRelationshipsUpdated;
        
        // Voice and audio events
        public event Action<string, string> OnVoiceAudioGenerated;
        public event Action<string, Dictionary<string, object>> OnVoiceSettingsUpdated;
        
        // Analytics events
        public event Action<string, DialogueAnalyticsModel> OnDialogueAnalyticsUpdated;
        
        // Subscription management
        private HashSet<string> subscribedConversations = new HashSet<string>();
        private HashSet<string> subscribedCharacters = new HashSet<string>();
        
        #region Initialization
        
        protected override void HandleMessage(string message)
        {
            Debug.Log("Dialogue WebSocket message received");
            // Parse the message and route to appropriate handlers
            try
            {
                var data = JsonUtility.FromJson<Dictionary<string, object>>(message);
                if (data.ContainsKey("type"))
                {
                    string eventType = data["type"].ToString();
                    HandleDialogueEvent(eventType, data);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error parsing dialogue WebSocket message: {ex.Message}");
            }
        }
        
        private void OnConnected()
        {
            Debug.Log("Dialogue WebSocket connected");
            
            // Re-subscribe to previous subscriptions
            foreach (var conversationId in subscribedConversations)
            {
                SubscribeToConversation(conversationId);
            }
            
            foreach (var characterId in subscribedCharacters)
            {
                SubscribeToCharacter(characterId);
            }
        }
        
        private void OnDisconnected()
        {
            Debug.Log("Dialogue WebSocket disconnected");
        }
        
        #endregion
        
        #region Message Handling
        
        protected void HandleDialogueEvent(string eventType, Dictionary<string, object> data)
        {
            try
            {
                switch (eventType)
                {
                    // Conversation lifecycle events
                    case "conversation_started":
                        HandleConversationStarted(data);
                        break;
                    case "conversation_ended":
                        HandleConversationEnded(data);
                        break;
                    case "conversation_updated":
                        HandleConversationUpdated(data);
                        break;
                    case "conversation_error":
                        HandleConversationError(data);
                        break;
                    
                    // Message events
                    case "message_received":
                        HandleMessageReceived(data);
                        break;
                    case "message_sent":
                        HandleMessageSent(data);
                        break;
                    case "message_updated":
                        HandleMessageUpdated(data);
                        break;
                    case "message_deleted":
                        HandleMessageDeleted(data);
                        break;
                    
                    // Dialogue option events
                    case "dialogue_options_updated":
                        HandleDialogueOptionsUpdated(data);
                        break;
                    case "dialogue_option_selected":
                        HandleDialogueOptionSelected(data);
                        break;
                    case "dialogue_options_evaluated":
                        HandleDialogueOptionsEvaluated(data);
                        break;
                    
                    // Context and state events
                    case "context_updated":
                        HandleContextUpdated(data);
                        break;
                    case "current_speaker_changed":
                        HandleCurrentSpeakerChanged(data);
                        break;
                    case "conversation_state_changed":
                        HandleConversationStateChanged(data);
                        break;
                    
                    // Relationship events
                    case "relationship_changed":
                        HandleRelationshipChanged(data);
                        break;
                    case "relationships_updated":
                        HandleRelationshipsUpdated(data);
                        break;
                    
                    // Voice and audio events
                    case "voice_audio_generated":
                        HandleVoiceAudioGenerated(data);
                        break;
                    case "voice_settings_updated":
                        HandleVoiceSettingsUpdated(data);
                        break;
                    
                    // Analytics events
                    case "dialogue_analytics_updated":
                        HandleDialogueAnalyticsUpdated(data);
                        break;
                    
                    default:
                        Debug.LogWarning($"Unknown dialogue event type: {eventType}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling dialogue event {eventType}: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Event Handlers
        
        private void HandleConversationStarted(Dictionary<string, object> data)
        {
            try
            {
                var conversation = DeserializeData<ConversationModel>(data);
                OnConversationStarted?.Invoke(conversation);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling conversation started: {ex.Message}");
            }
        }
        
        private void HandleConversationEnded(Dictionary<string, object> data)
        {
            try
            {
                var conversation = DeserializeData<ConversationModel>(data);
                OnConversationEnded?.Invoke(conversation);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling conversation ended: {ex.Message}");
            }
        }
        
        private void HandleConversationUpdated(Dictionary<string, object> data)
        {
            try
            {
                var conversation = DeserializeData<ConversationModel>(data);
                OnConversationUpdated?.Invoke(conversation);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling conversation updated: {ex.Message}");
            }
        }
        
        private void HandleConversationError(Dictionary<string, object> data)
        {
            try
            {
                var errorMessage = GetStringValue(data, "error") ?? "Unknown conversation error";
                OnConversationError?.Invoke(errorMessage);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling conversation error: {ex.Message}");
            }
        }
        
        private void HandleMessageReceived(Dictionary<string, object> data)
        {
            try
            {
                var message = DeserializeData<ConversationEntryModel>(data);
                OnMessageReceived?.Invoke(message);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling message received: {ex.Message}");
            }
        }
        
        private void HandleMessageSent(Dictionary<string, object> data)
        {
            try
            {
                var message = DeserializeData<ConversationEntryModel>(data);
                OnMessageSent?.Invoke(message);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling message sent: {ex.Message}");
            }
        }
        
        private void HandleMessageUpdated(Dictionary<string, object> data)
        {
            try
            {
                var conversationId = GetStringValue(data, "conversation_id");
                var message = DeserializeData<ConversationEntryModel>(data);
                OnMessageUpdated?.Invoke(conversationId, message);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling message updated: {ex.Message}");
            }
        }
        
        private void HandleMessageDeleted(Dictionary<string, object> data)
        {
            try
            {
                var conversationId = GetStringValue(data, "conversation_id");
                var messageId = GetStringValue(data, "message_id");
                OnMessageDeleted?.Invoke(conversationId, messageId);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling message deleted: {ex.Message}");
            }
        }
        
        private void HandleDialogueOptionsUpdated(Dictionary<string, object> data)
        {
            try
            {
                var conversationId = GetStringValue(data, "conversation_id");
                var options = DeserializeData<List<DialogueOptionModel>>(data, "options");
                OnDialogueOptionsUpdated?.Invoke(conversationId, options);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling dialogue options updated: {ex.Message}");
            }
        }
        
        private void HandleDialogueOptionSelected(Dictionary<string, object> data)
        {
            try
            {
                var conversationId = GetStringValue(data, "conversation_id");
                var option = DeserializeData<DialogueOptionModel>(data, "option");
                OnDialogueOptionSelected?.Invoke(conversationId, option);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling dialogue option selected: {ex.Message}");
            }
        }
        
        private void HandleDialogueOptionsEvaluated(Dictionary<string, object> data)
        {
            try
            {
                var conversationId = GetStringValue(data, "conversation_id");
                var options = DeserializeData<List<DialogueOptionModel>>(data, "options");
                OnDialogueOptionsEvaluated?.Invoke(conversationId, options);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling dialogue options evaluated: {ex.Message}");
            }
        }
        
        private void HandleContextUpdated(Dictionary<string, object> data)
        {
            try
            {
                var conversationId = GetStringValue(data, "conversation_id");
                var context = DeserializeData<ConversationContextModel>(data, "context");
                OnContextUpdated?.Invoke(conversationId, context);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling context updated: {ex.Message}");
            }
        }
        
        private void HandleCurrentSpeakerChanged(Dictionary<string, object> data)
        {
            try
            {
                var conversationId = GetStringValue(data, "conversation_id");
                var speakerId = GetStringValue(data, "speaker_id");
                OnCurrentSpeakerChanged?.Invoke(conversationId, speakerId);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling current speaker changed: {ex.Message}");
            }
        }
        
        private void HandleConversationStateChanged(Dictionary<string, object> data)
        {
            try
            {
                var conversationId = GetStringValue(data, "conversation_id");
                var state = GetDictionaryValue(data, "state");
                OnConversationStateChanged?.Invoke(conversationId, state);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling conversation state changed: {ex.Message}");
            }
        }
        
        private void HandleRelationshipChanged(Dictionary<string, object> data)
        {
            try
            {
                var characterId = GetStringValue(data, "character_id");
                var targetId = GetStringValue(data, "target_id");
                var newLevel = GetFloatValue(data, "new_level");
                OnRelationshipChanged?.Invoke(characterId, targetId, newLevel);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling relationship changed: {ex.Message}");
            }
        }
        
        private void HandleRelationshipsUpdated(Dictionary<string, object> data)
        {
            try
            {
                var characterId = GetStringValue(data, "character_id");
                var relationships = GetDictionaryValue(data, "relationships");
                var relationshipLevels = new Dictionary<string, float>();
                
                foreach (var kvp in relationships)
                {
                    if (float.TryParse(kvp.Value?.ToString(), out var level))
                    {
                        relationshipLevels[kvp.Key] = level;
                    }
                }
                
                OnRelationshipsUpdated?.Invoke(characterId, relationshipLevels);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling relationships updated: {ex.Message}");
            }
        }
        
        private void HandleVoiceAudioGenerated(Dictionary<string, object> data)
        {
            try
            {
                var characterId = GetStringValue(data, "character_id");
                var audioUrl = GetStringValue(data, "audio_url");
                OnVoiceAudioGenerated?.Invoke(characterId, audioUrl);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling voice audio generated: {ex.Message}");
            }
        }
        
        private void HandleVoiceSettingsUpdated(Dictionary<string, object> data)
        {
            try
            {
                var characterId = GetStringValue(data, "character_id");
                var settings = GetDictionaryValue(data, "voice_settings");
                OnVoiceSettingsUpdated?.Invoke(characterId, settings);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling voice settings updated: {ex.Message}");
            }
        }
        
        private void HandleDialogueAnalyticsUpdated(Dictionary<string, object> data)
        {
            try
            {
                var conversationId = GetStringValue(data, "conversation_id");
                var analytics = DeserializeData<DialogueAnalyticsModel>(data, "analytics");
                OnDialogueAnalyticsUpdated?.Invoke(conversationId, analytics);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling dialogue analytics updated: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Subscription Management
        
        /// <summary>
        /// Subscribe to events for a specific conversation
        /// </summary>
        public void SubscribeToConversation(string conversationId)
        {
            if (string.IsNullOrEmpty(conversationId))
                return;
            
            try
            {
                SendMessage("subscribe_conversation", new { conversation_id = conversationId });
                subscribedConversations.Add(conversationId);
                Debug.Log($"Subscribed to conversation: {conversationId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to subscribe to conversation {conversationId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Unsubscribe from events for a specific conversation
        /// </summary>
        public void UnsubscribeFromConversation(string conversationId)
        {
            if (string.IsNullOrEmpty(conversationId))
                return;
            
            try
            {
                SendMessage("unsubscribe_conversation", new { conversation_id = conversationId });
                subscribedConversations.Remove(conversationId);
                Debug.Log($"Unsubscribed from conversation: {conversationId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to unsubscribe from conversation {conversationId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Subscribe to events for a specific character
        /// </summary>
        public void SubscribeToCharacter(string characterId)
        {
            if (string.IsNullOrEmpty(characterId))
                return;
            
            try
            {
                SendMessage("subscribe_character", new { character_id = characterId });
                subscribedCharacters.Add(characterId);
                Debug.Log($"Subscribed to character: {characterId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to subscribe to character {characterId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Unsubscribe from events for a specific character
        /// </summary>
        public void UnsubscribeFromCharacter(string characterId)
        {
            if (string.IsNullOrEmpty(characterId))
                return;
            
            try
            {
                SendMessage("unsubscribe_character", new { character_id = characterId });
                subscribedCharacters.Remove(characterId);
                Debug.Log($"Unsubscribed from character: {characterId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to unsubscribe from character {characterId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Subscribe to general dialogue events
        /// </summary>
        public void SubscribeToDialogueEvents()
        {
            try
            {
                SendMessage("subscribe_dialogue_events", new { });
                Debug.Log("Subscribed to general dialogue events");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to subscribe to dialogue events: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Unsubscribe from general dialogue events
        /// </summary>
        public void UnsubscribeFromDialogueEvents()
        {
            try
            {
                SendMessage("unsubscribe_dialogue_events", new { });
                Debug.Log("Unsubscribed from general dialogue events");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to unsubscribe from dialogue events: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Get list of currently subscribed conversations
        /// </summary>
        public HashSet<string> GetSubscribedConversations()
        {
            return new HashSet<string>(subscribedConversations);
        }
        
        /// <summary>
        /// Get list of currently subscribed characters
        /// </summary>
        public HashSet<string> GetSubscribedCharacters()
        {
            return new HashSet<string>(subscribedCharacters);
        }
        
        /// <summary>
        /// Clear all subscriptions
        /// </summary>
        public void ClearAllSubscriptions()
        {
            foreach (var conversationId in subscribedConversations.ToArray())
            {
                UnsubscribeFromConversation(conversationId);
            }
            
            foreach (var characterId in subscribedCharacters.ToArray())
            {
                UnsubscribeFromCharacter(characterId);
            }
            
            UnsubscribeFromDialogueEvents();
        }
        
        #endregion
        
        #region Public Interface
        
        /// <summary>
        /// Send a real-time message in a conversation
        /// </summary>
        public void SendRealtimeMessage(string conversationId, string senderId, string content, string emotion = null)
        {
            try
            {
                var messageData = new
                {
                    conversation_id = conversationId,
                    sender_id = senderId,
                    content = content,
                    emotion = emotion,
                    timestamp = DateTime.UtcNow
                };
                
                SendMessage("send_realtime_message", messageData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to send realtime message: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Signal typing status in a conversation
        /// </summary>
        public void SendTypingStatus(string conversationId, string senderId, bool isTyping)
        {
            try
            {
                var typingData = new
                {
                    conversation_id = conversationId,
                    sender_id = senderId,
                    is_typing = isTyping
                };
                
                SendMessage("typing_status", typingData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to send typing status: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Request real-time dialogue option evaluation
        /// </summary>
        public void RequestOptionEvaluation(string conversationId, string characterId)
        {
            try
            {
                var evaluationData = new
                {
                    conversation_id = conversationId,
                    character_id = characterId
                };
                
                SendMessage("request_option_evaluation", evaluationData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to request option evaluation: {ex.Message}");
            }
        }
        
        #endregion
    }
} 