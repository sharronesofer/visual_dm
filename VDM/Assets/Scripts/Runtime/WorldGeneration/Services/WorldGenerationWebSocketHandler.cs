using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Runtime.Core.Services;
using VDM.Runtime.WorldGeneration.Models;


namespace VDM.Runtime.WorldGeneration.Services
{
    /// <summary>
    /// WebSocket handler for real-time world generation updates
    /// Handles progress updates, completion notifications, and error reporting
    /// </summary>
    public class WorldGenerationWebSocketHandler : BaseWebSocketHandler
    {
        public event Action<WorldGenerationProgress> OnProgressUpdate;
        public event Action<WorldGenerationResult> OnGenerationComplete;
        public event Action<string> OnGenerationError;
        public event Action<ContinentModel> OnContinentCreated;
        public event Action<List<VisualDM.DTOs.World.Region.RegionDTO>> OnRegionsGenerated;

        protected override void HandleMessage(string messageType, string data)
        {
            try
            {
                switch (messageType)
                {
                    case "worldgen_progress":
                        HandleProgressUpdate(data);
                        break;
                    case "worldgen_complete":
                        HandleGenerationComplete(data);
                        break;
                    case "worldgen_error":
                        HandleGenerationError(data);
                        break;
                    case "continent_created":
                        HandleContinentCreated(data);
                        break;
                    case "regions_generated":
                        HandleRegionsGenerated(data);
                        break;
                    default:
                        Debug.LogWarning($"Unknown world generation message type: {messageType}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling world generation WebSocket message: {ex.Message}");
            }
        }

        private void HandleProgressUpdate(string data)
        {
            try
            {
                var progress = JsonConvert.DeserializeObject<WorldGenerationProgress>(data);
                OnProgressUpdate?.Invoke(progress);
                
                Debug.Log($"World generation progress: {progress.Stage} - {progress.OverallProgress:P1}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to parse progress update: {ex.Message}");
            }
        }

        private void HandleGenerationComplete(string data)
        {
            try
            {
                var result = JsonConvert.DeserializeObject<WorldGenerationResult>(data);
                OnGenerationComplete?.Invoke(result);
                
                Debug.Log($"World generation complete: {result.Message}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to parse generation complete: {ex.Message}");
            }
        }

        private void HandleGenerationError(string data)
        {
            try
            {
                var errorData = JsonConvert.DeserializeObject<Dictionary<string, object>>(data);
                var errorMessage = errorData.ContainsKey("error") ? errorData["error"].ToString() : "Unknown error";
                
                OnGenerationError?.Invoke(errorMessage);
                Debug.LogError($"World generation error: {errorMessage}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to parse generation error: {ex.Message}");
                OnGenerationError?.Invoke("Failed to parse error message");
            }
        }

        private void HandleContinentCreated(string data)
        {
            try
            {
                var continent = JsonConvert.DeserializeObject<ContinentModel>(data);
                OnContinentCreated?.Invoke(continent);
                
                Debug.Log($"Continent created: {continent.Name} ({continent.ContinentId})");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to parse continent created: {ex.Message}");
            }
        }

        private void HandleRegionsGenerated(string data)
        {
            try
            {
                var regions = JsonConvert.DeserializeObject<List<VisualDM.DTOs.World.Region.RegionDTO>>(data);
                OnRegionsGenerated?.Invoke(regions);
                
                Debug.Log($"Regions generated: {regions.Count} regions");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to parse regions generated: {ex.Message}");
            }
        }

        /// <summary>
        /// Subscribe to world generation events for a specific generation session
        /// </summary>
        public void SubscribeToGeneration(string generationId)
        {
            var subscribeMessage = new
            {
                action = "subscribe",
                channel = "worldgen",
                generation_id = generationId
            };

            SendMessage(subscribeMessage);
        }

        /// <summary>
        /// Unsubscribe from world generation events
        /// </summary>
        public void UnsubscribeFromGeneration(string generationId)
        {
            var unsubscribeMessage = new
            {
                action = "unsubscribe",
                channel = "worldgen",
                generation_id = generationId
            };

            SendMessage(unsubscribeMessage);
        }

        /// <summary>
        /// Request current progress for a generation session
        /// </summary>
        public void RequestProgress(string generationId)
        {
            var requestMessage = new
            {
                action = "get_progress",
                generation_id = generationId
            };

            SendMessage(requestMessage);
        }
    }
} 