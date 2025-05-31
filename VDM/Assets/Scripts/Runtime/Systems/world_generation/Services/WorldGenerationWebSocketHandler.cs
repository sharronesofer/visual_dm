using NativeWebSocket;
using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.Systems.Worldgeneration.Models;
using VDM.Systems.Region.Models;


namespace VDM.Systems.Worldgeneration.Services
{
    /// <summary>
    /// WebSocket handler for real-time world generation updates
    /// Handles progress updates, completion notifications, and error reporting
    /// </summary>
    public class WorldGenerationWebSocketHandler : BaseWebSocketHandler
    {
        // Core events
        public event Action<WorldGenerationProgress> OnProgressUpdate;
        public event Action<WorldGenerationResult> OnGenerationComplete;
        public event Action<string> OnGenerationError;
        
        // Error events
        public event Action<string> OnError;
        
        // Generation events
        public event Action<string> OnGenerationStarted;
        public event Action<string, float> OnGenerationProgress;
        public event Action<string> OnGenerationCompleted;
        public event Action<string, string> OnGenerationFailed;
        
        // Entity creation events (UI compatibility)
        public event Action<ContinentModel> OnContinentCreated;
        public event Action<string, int> OnRegionGenerated; // (continentId, regionCount)
        
        // Entity creation events (detailed)
        public event Action<ContinentDTO> OnContinentGenerated;
        public event Action<VDM.Systems.WorldGeneration.Models.RegionDTO> OnRegionGeneratedDetailed;
        public event Action<List<VDM.Systems.WorldGeneration.Models.RegionDTO>> OnRegionsGenerated;
        public event Action<BiomeConfigDTO> OnBiomeUpdate;

        protected override void HandleMessage(string message)
        {
            try
            {
                var messageData = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
                
                if (!messageData.TryGetValue("type", out var messageType))
                {
                    Debug.LogWarning("WorldGeneration WebSocket message missing type field");
                    return;
                }

                var type = messageType.ToString();
                
                switch (type)
                {
                    case "generation_progress":
                        if (messageData.TryGetValue("data", out var progressData))
                        {
                            var progressJson = JsonConvert.SerializeObject(progressData);
                            var progress = JsonConvert.DeserializeObject<WorldGenerationProgress>(progressJson);
                            if (progress != null)
                            {
                                OnProgressUpdate?.Invoke(progress);
                            }
                        }
                        break;

                    case "generation_complete":
                        if (messageData.TryGetValue("data", out var resultData))
                        {
                            var resultJson = JsonConvert.SerializeObject(resultData);
                            var result = JsonConvert.DeserializeObject<WorldGenerationResult>(resultJson);
                            if (result != null)
                            {
                                OnGenerationComplete?.Invoke(result);
                            }
                        }
                        break;

                    case "generation_error":
                        if (messageData.TryGetValue("error", out var errorObj))
                        {
                            var error = errorObj.ToString();
                            OnGenerationError?.Invoke(error);
                            OnError?.Invoke(error);
                        }
                        break;

                    case "continent_generated":
                        if (messageData.TryGetValue("data", out var continentData))
                        {
                            var continentJson = JsonConvert.SerializeObject(continentData);
                            var continent = JsonConvert.DeserializeObject<ContinentDTO>(continentJson);
                            if (continent != null)
                            {
                                OnContinentGenerated?.Invoke(continent);
                            }
                        }
                        break;

                    case "continent_created":
                        if (messageData.TryGetValue("data", out var continentCreatedData))
                        {
                            var continentJson = JsonConvert.SerializeObject(continentCreatedData);
                            var continent = JsonConvert.DeserializeObject<ContinentModel>(continentJson);
                            if (continent != null)
                            {
                                OnContinentCreated?.Invoke(continent);
                            }
                        }
                        break;

                    case "region_generated":
                        if (messageData.TryGetValue("data", out var regionData))
                        {
                            var regionJson = JsonConvert.SerializeObject(regionData);
                            var region = JsonConvert.DeserializeObject<VDM.Systems.WorldGeneration.Models.RegionDTO>(regionJson);
                            if (region != null)
                            {
                                OnRegionGeneratedDetailed?.Invoke(region);
                                
                                // Also trigger UI-compatible event with continent ID and count
                                if (!string.IsNullOrEmpty(region.ContinentId))
                                {
                                    OnRegionGenerated?.Invoke(region.ContinentId, 1);
                                }
                            }
                        }
                        break;

                    case "biome_updated":
                        if (messageData.TryGetValue("data", out var biomeData))
                        {
                            var biomeJson = JsonConvert.SerializeObject(biomeData);
                            var biome = JsonConvert.DeserializeObject<BiomeConfigDTO>(biomeJson);
                            if (biome != null)
                            {
                                OnBiomeUpdate?.Invoke(biome);
                            }
                        }
                        break;

                    default:
                        Debug.LogWarning($"Unknown world generation WebSocket message type: {type}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling world generation WebSocket message: {ex.Message}");
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

        #region Public API for Manager Access

        /// <summary>
        /// Connect to WebSocket server - public wrapper
        /// </summary>
        public void Connect()
        {
            base.Connect("ws://localhost:8000/ws/worldgen");
        }

        /// <summary>
        /// Disconnect from WebSocket server - public wrapper
        /// </summary>
        public new void Disconnect()
        {
            base.Disconnect();
        }

        /// <summary>
        /// Get connection status - public property
        /// </summary>
        public new bool IsConnected => base.IsConnected;

        #endregion
    }
} 