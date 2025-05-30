using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core.Services;
using VDM.Runtime.Dialogue.Models;


namespace VDM.Runtime.Dialogue.Services
{
    /// <summary>
    /// Service for handling dialogue and conversation operations via HTTP API
    /// </summary>
    public class DialogueService : BaseHttpService
    {
        private const string BaseEndpoint = "/api/dialogue";
        
        #region Conversation Management
        
        /// <summary>
        /// Start a new conversation
        /// </summary>
        public async Task<ConversationModel> StartConversationAsync(StartConversationRequest request)
        {
            try
            {
                var response = await PostAsync<ConversationModel>($"{BaseEndpoint}/conversations/start", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to start conversation: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get conversation by ID
        /// </summary>
        public async Task<ConversationModel> GetConversationAsync(string conversationId)
        {
            try
            {
                var response = await GetAsync<ConversationModel>($"{BaseEndpoint}/conversations/{conversationId}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get conversation {conversationId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get all active conversations for a participant
        /// </summary>
        public async Task<List<ConversationModel>> GetActiveConversationsAsync(string participantId)
        {
            try
            {
                var response = await GetAsync<List<ConversationModel>>($"{BaseEndpoint}/conversations/active/{participantId}");
                return response ?? new List<ConversationModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get active conversations for {participantId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// End a conversation
        /// </summary>
        public async Task<bool> EndConversationAsync(string conversationId)
        {
            try
            {
                await PostAsync($"{BaseEndpoint}/conversations/{conversationId}/end", null);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to end conversation {conversationId}: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Message Exchange
        
        /// <summary>
        /// Send a message in a conversation
        /// </summary>
        public async Task<DialogueActionResponse> SendMessageAsync(string conversationId, SendMessageRequest request)
        {
            try
            {
                var response = await PostAsync<DialogueActionResponse>($"{BaseEndpoint}/conversations/{conversationId}/messages", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to send message in conversation {conversationId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Generate an AI response from an NPC
        /// </summary>
        public async Task<DialogueActionResponse> GenerateResponseAsync(string conversationId, GenerateResponseRequest request)
        {
            try
            {
                var response = await PostAsync<DialogueActionResponse>($"{BaseEndpoint}/conversations/{conversationId}/generate-response", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate response for conversation {conversationId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get conversation history with pagination
        /// </summary>
        public async Task<ConversationHistoryResponse> GetConversationHistoryAsync(string conversationId, int page = 1, int pageSize = 50)
        {
            try
            {
                var response = await GetAsync<ConversationHistoryResponse>($"{BaseEndpoint}/conversations/{conversationId}/history?page={page}&page_size={pageSize}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get conversation history for {conversationId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Select a dialogue option
        /// </summary>
        public async Task<DialogueActionResponse> SelectDialogueOptionAsync(string conversationId, string optionId, Dictionary<string, object> metadata = null)
        {
            try
            {
                var request = new
                {
                    option_id = optionId,
                    metadata = metadata ?? new Dictionary<string, object>()
                };
                
                var response = await PostAsync<DialogueActionResponse>($"{BaseEndpoint}/conversations/{conversationId}/select-option", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to select dialogue option {optionId}: {ex.Message}");
                throw;
            }
        }
        
        #endregion
        
        #region Dialogue Trees
        
        /// <summary>
        /// Get all available dialogue trees
        /// </summary>
        public async Task<List<DialogueTreeModel>> GetDialogueTreesAsync()
        {
            try
            {
                var response = await GetAsync<List<DialogueTreeModel>>($"{BaseEndpoint}/trees");
                return response ?? new List<DialogueTreeModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get dialogue trees: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get a specific dialogue tree
        /// </summary>
        public async Task<DialogueTreeModel> GetDialogueTreeAsync(string treeId)
        {
            try
            {
                var response = await GetAsync<DialogueTreeModel>($"{BaseEndpoint}/trees/{treeId}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get dialogue tree {treeId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get dialogue trees for a specific character
        /// </summary>
        public async Task<List<DialogueTreeModel>> GetDialogueTreesForCharacterAsync(string characterId)
        {
            try
            {
                var response = await GetAsync<List<DialogueTreeModel>>($"{BaseEndpoint}/trees/character/{characterId}");
                return response ?? new List<DialogueTreeModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get dialogue trees for character {characterId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Create a new dialogue tree
        /// </summary>
        public async Task<DialogueTreeModel> CreateDialogueTreeAsync(DialogueTreeModel tree)
        {
            try
            {
                var response = await PostAsync<DialogueTreeModel>($"{BaseEndpoint}/trees", tree);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create dialogue tree: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Update an existing dialogue tree
        /// </summary>
        public async Task<DialogueTreeModel> UpdateDialogueTreeAsync(string treeId, DialogueTreeModel tree)
        {
            try
            {
                var response = await PutAsync<DialogueTreeModel>($"{BaseEndpoint}/trees/{treeId}", tree);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update dialogue tree {treeId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Delete a dialogue tree
        /// </summary>
        public async Task<bool> DeleteDialogueTreeAsync(string treeId)
        {
            try
            {
                await DeleteAsync($"{BaseEndpoint}/trees/{treeId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete dialogue tree {treeId}: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Dialogue Options
        
        /// <summary>
        /// Get available dialogue options for current conversation state
        /// </summary>
        public async Task<List<DialogueOptionModel>> GetAvailableOptionsAsync(string conversationId)
        {
            try
            {
                var response = await GetAsync<List<DialogueOptionModel>>($"{BaseEndpoint}/conversations/{conversationId}/options");
                return response ?? new List<DialogueOptionModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get available options for conversation {conversationId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Evaluate dialogue option conditions
        /// </summary>
        public async Task<List<DialogueOptionModel>> EvaluateOptionsAsync(string conversationId, string characterId)
        {
            try
            {
                var request = new { character_id = characterId };
                var response = await PostAsync<List<DialogueOptionModel>>($"{BaseEndpoint}/conversations/{conversationId}/evaluate-options", request);
                return response ?? new List<DialogueOptionModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to evaluate options for conversation {conversationId}: {ex.Message}");
                throw;
            }
        }
        
        #endregion
        
        #region Character Relationships
        
        /// <summary>
        /// Update relationship level between characters
        /// </summary>
        public async Task<bool> UpdateRelationshipAsync(string characterId, string targetId, float change)
        {
            try
            {
                var request = new
                {
                    character_id = characterId,
                    target_id = targetId,
                    relationship_change = change
                };
                
                await PostAsync($"{BaseEndpoint}/relationships/update", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update relationship between {characterId} and {targetId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Get relationship level between characters
        /// </summary>
        public async Task<float> GetRelationshipAsync(string characterId, string targetId)
        {
            try
            {
                var response = await GetAsync<object>($"{BaseEndpoint}/relationships/{characterId}/{targetId}");
                if (response is Dictionary<string, object> dict && dict.TryGetValue("relationship_level", out var level))
                {
                    return Convert.ToSingle(level);
                }
                return 0f;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get relationship between {characterId} and {targetId}: {ex.Message}");
                return 0f;
            }
        }
        
        #endregion
        
        #region Context and Memory
        
        /// <summary>
        /// Update conversation context
        /// </summary>
        public async Task<bool> UpdateConversationContextAsync(string conversationId, ConversationContextModel context)
        {
            try
            {
                await PutAsync($"{BaseEndpoint}/conversations/{conversationId}/context", context);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update conversation context for {conversationId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Get conversation context
        /// </summary>
        public async Task<ConversationContextModel> GetConversationContextAsync(string conversationId)
        {
            try
            {
                var response = await GetAsync<ConversationContextModel>($"{BaseEndpoint}/conversations/{conversationId}/context");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get conversation context for {conversationId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Add key point to conversation memory
        /// </summary>
        public async Task<bool> AddConversationMemoryAsync(string conversationId, string keyPoint, Dictionary<string, object> metadata = null)
        {
            try
            {
                var request = new
                {
                    key_point = keyPoint,
                    metadata = metadata ?? new Dictionary<string, object>()
                };
                
                await PostAsync($"{BaseEndpoint}/conversations/{conversationId}/memory", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to add conversation memory for {conversationId}: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Analytics
        
        /// <summary>
        /// Get dialogue analytics for a conversation
        /// </summary>
        public async Task<DialogueAnalyticsModel> GetDialogueAnalyticsAsync(string conversationId)
        {
            try
            {
                var response = await GetAsync<DialogueAnalyticsModel>($"{BaseEndpoint}/analytics/conversation/{conversationId}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get dialogue analytics for {conversationId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get dialogue analytics for a character
        /// </summary>
        public async Task<List<DialogueAnalyticsModel>> GetCharacterDialogueAnalyticsAsync(string characterId)
        {
            try
            {
                var response = await GetAsync<List<DialogueAnalyticsModel>>($"{BaseEndpoint}/analytics/character/{characterId}");
                return response ?? new List<DialogueAnalyticsModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get character dialogue analytics for {characterId}: {ex.Message}");
                throw;
            }
        }
        
        #endregion
        
        #region Voice and Audio
        
        /// <summary>
        /// Get voice settings for a character
        /// </summary>
        public async Task<Dictionary<string, object>> GetCharacterVoiceSettingsAsync(string characterId)
        {
            try
            {
                var response = await GetAsync<Dictionary<string, object>>($"{BaseEndpoint}/voice/character/{characterId}");
                return response ?? new Dictionary<string, object>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get voice settings for character {characterId}: {ex.Message}");
                return new Dictionary<string, object>();
            }
        }
        
        /// <summary>
        /// Update voice settings for a character
        /// </summary>
        public async Task<bool> UpdateCharacterVoiceSettingsAsync(string characterId, Dictionary<string, object> voiceSettings)
        {
            try
            {
                await PutAsync($"{BaseEndpoint}/voice/character/{characterId}", voiceSettings);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update voice settings for character {characterId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Generate speech audio for text
        /// </summary>
        public async Task<string> GenerateSpeechAsync(string text, string characterId, Dictionary<string, object> options = null)
        {
            try
            {
                var request = new
                {
                    text = text,
                    character_id = characterId,
                    options = options ?? new Dictionary<string, object>()
                };
                
                var response = await PostAsync<Dictionary<string, object>>($"{BaseEndpoint}/voice/generate", request);
                if (response != null && response.TryGetValue("audio_url", out var audioUrl))
                {
                    return audioUrl.ToString();
                }
                return null;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate speech for character {characterId}: {ex.Message}");
                return null;
            }
        }
        
        #endregion
        
        #region Search and Filtering
        
        /// <summary>
        /// Search conversations by criteria
        /// </summary>
        public async Task<List<ConversationModel>> SearchConversationsAsync(string query, string participantId = null, DateTime? startDate = null, DateTime? endDate = null)
        {
            try
            {
                var queryParams = new List<string>();
                
                if (!string.IsNullOrEmpty(query))
                    queryParams.Add($"q={Uri.EscapeDataString(query)}");
                
                if (!string.IsNullOrEmpty(participantId))
                    queryParams.Add($"participant_id={participantId}");
                
                if (startDate.HasValue)
                    queryParams.Add($"start_date={startDate.Value:yyyy-MM-dd}");
                
                if (endDate.HasValue)
                    queryParams.Add($"end_date={endDate.Value:yyyy-MM-dd}");
                
                var queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await GetAsync<List<ConversationModel>>($"{BaseEndpoint}/conversations/search{queryString}");
                return response ?? new List<ConversationModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to search conversations: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Search dialogue trees by tags and criteria
        /// </summary>
        public async Task<List<DialogueTreeModel>> SearchDialogueTreesAsync(string query, List<string> tags = null, string characterId = null)
        {
            try
            {
                var queryParams = new List<string>();
                
                if (!string.IsNullOrEmpty(query))
                    queryParams.Add($"q={Uri.EscapeDataString(query)}");
                
                if (tags != null && tags.Count > 0)
                    queryParams.Add($"tags={string.Join(",", tags)}");
                
                if (!string.IsNullOrEmpty(characterId))
                    queryParams.Add($"character_id={characterId}");
                
                var queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await GetAsync<List<DialogueTreeModel>>($"{BaseEndpoint}/trees/search{queryString}");
                return response ?? new List<DialogueTreeModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to search dialogue trees: {ex.Message}");
                throw;
            }
        }
        
        #endregion
    }
} 