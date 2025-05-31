using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;
using VDM.Systems.Motifs.Models;

namespace VDM.Systems.Motifs.Services
{
    /// <summary>
    /// REST API client for motif operations with the backend.
    /// Handles authentication, serialization, error handling, and retry logic.
    /// </summary>
    public class MotifApiClient
    {
        private readonly string _baseUrl;
        private readonly string _apiKey;
        private readonly int _maxRetries;
        private readonly float _retryDelay;
        private readonly JsonSerializerSettings _jsonSettings;

        public MotifApiClient(string baseUrl, string apiKey = null, int maxRetries = 3, float retryDelay = 1.0f)
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _apiKey = apiKey;
            _maxRetries = maxRetries;
            _retryDelay = retryDelay;
            
            _jsonSettings = new JsonSerializerSettings
            {
                DateFormatHandling = DateFormatHandling.IsoDateFormat,
                NullValueHandling = NullValueHandling.Ignore,
                DefaultValueHandling = DefaultValueHandling.Ignore
            };
        }

        #region Core HTTP Methods

        private async Task<string> SendRequestAsync(string endpoint, string method, string jsonData = null)
        {
            string url = _baseUrl + endpoint;
            
            for (int attempt = 0; attempt <= _maxRetries; attempt++)
            {
                UnityWebRequest request = null;
                
                try
                {
                    // Create request based on method
                    switch (method.ToUpper())
                    {
                        case "GET":
                            request = UnityWebRequest.Get(url);
                            break;
                        case "POST":
                            request = new UnityWebRequest(url, "POST");
                            if (!string.IsNullOrEmpty(jsonData))
                            {
                                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                            }
                            request.downloadHandler = new DownloadHandlerBuffer();
                            break;
                        case "PUT":
                            request = UnityWebRequest.Put(url, jsonData ?? "");
                            break;
                        case "DELETE":
                            request = UnityWebRequest.Delete(url);
                            break;
                        default:
                            throw new ArgumentException($"Unsupported HTTP method: {method}");
                    }

                    // Set headers
                    request.SetRequestHeader("Content-Type", "application/json");
                    if (!string.IsNullOrEmpty(_apiKey))
                    {
                        request.SetRequestHeader("Authorization", $"Bearer {_apiKey}");
                    }

                    // Send request
                    var operation = request.SendWebRequest();
                    while (!operation.isDone)
                    {
                        await Task.Yield();
                    }

                    // Handle response
                    if (request.result == UnityWebRequest.Result.Success)
                    {
                        return request.downloadHandler.text;
                    }
                    else if (attempt < _maxRetries && IsRetryableError(request))
                    {
                        Debug.LogWarning($"MotifApiClient: Request failed (attempt {attempt + 1}/{_maxRetries + 1}): {request.error}");
                        await Task.Delay(TimeSpan.FromSeconds(_retryDelay * (attempt + 1)));
                        continue;
                    }
                    else
                    {
                        string errorMsg = $"Request failed: {request.error}. Response: {request.downloadHandler?.text}";
                        Debug.LogError($"MotifApiClient: {errorMsg}");
                        throw new Exception(errorMsg);
                    }
                }
                finally
                {
                    request?.Dispose();
                }
            }

            throw new Exception("Max retries exceeded");
        }

        private bool IsRetryableError(UnityWebRequest request)
        {
            // Retry on network errors and server errors (5xx), but not client errors (4xx)
            return request.result == UnityWebRequest.Result.ConnectionError ||
                   request.result == UnityWebRequest.Result.DataProcessingError ||
                   (request.responseCode >= 500 && request.responseCode < 600);
        }

        #endregion

        #region Motif CRUD Operations

        /// <summary>
        /// Get all motifs with optional filtering
        /// </summary>
        public async Task<List<Motif>> GetMotifsAsync(MotifFilter filter = null)
        {
            try
            {
                string endpoint = "/motifs";
                
                // Add query parameters if filter is provided
                if (filter != null)
                {
                    var queryParams = BuildQueryParams(filter);
                    if (queryParams.Count > 0)
                    {
                        endpoint += "?" + string.Join("&", queryParams);
                    }
                }

                string responseJson = await SendRequestAsync(endpoint, "GET");
                var response = JsonConvert.DeserializeObject<MotifResponse<List<Motif>>>(responseJson, _jsonSettings);
                
                if (response.success)
                {
                    return response.data ?? new List<Motif>();
                }
                else
                {
                    Debug.LogError($"MotifApiClient: Failed to get motifs: {response.message}");
                    return new List<Motif>();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"MotifApiClient: Exception getting motifs: {ex.Message}");
                return new List<Motif>();
            }
        }

        /// <summary>
        /// Get a specific motif by ID
        /// </summary>
        public async Task<Motif> GetMotifAsync(string motifId)
        {
            try
            {
                string endpoint = $"/motifs/{motifId}";
                string responseJson = await SendRequestAsync(endpoint, "GET");
                var response = JsonConvert.DeserializeObject<MotifResponse<Motif>>(responseJson, _jsonSettings);
                
                if (response.success)
                {
                    return response.data;
                }
                else
                {
                    Debug.LogError($"MotifApiClient: Failed to get motif {motifId}: {response.message}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"MotifApiClient: Exception getting motif {motifId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Create a new motif
        /// </summary>
        public async Task<Motif> CreateMotifAsync(MotifCreateData motifData)
        {
            try
            {
                string endpoint = "/motifs";
                string jsonData = JsonConvert.SerializeObject(motifData, _jsonSettings);
                string responseJson = await SendRequestAsync(endpoint, "POST", jsonData);
                var response = JsonConvert.DeserializeObject<MotifResponse<Motif>>(responseJson, _jsonSettings);
                
                if (response.success)
                {
                    return response.data;
                }
                else
                {
                    Debug.LogError($"MotifApiClient: Failed to create motif: {response.message}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"MotifApiClient: Exception creating motif: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update an existing motif
        /// </summary>
        public async Task<Motif> UpdateMotifAsync(string motifId, MotifUpdateData updateData)
        {
            try
            {
                string endpoint = $"/motifs/{motifId}";
                string jsonData = JsonConvert.SerializeObject(updateData, _jsonSettings);
                string responseJson = await SendRequestAsync(endpoint, "PUT", jsonData);
                var response = JsonConvert.DeserializeObject<MotifResponse<Motif>>(responseJson, _jsonSettings);
                
                if (response.success)
                {
                    return response.data;
                }
                else
                {
                    Debug.LogError($"MotifApiClient: Failed to update motif {motifId}: {response.message}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"MotifApiClient: Exception updating motif {motifId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Delete a motif
        /// </summary>
        public async Task<bool> DeleteMotifAsync(string motifId)
        {
            try
            {
                string endpoint = $"/motifs/{motifId}";
                string responseJson = await SendRequestAsync(endpoint, "DELETE");
                var response = JsonConvert.DeserializeObject<MotifResponse<object>>(responseJson, _jsonSettings);
                return response.success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"MotifApiClient: Exception deleting motif {motifId}: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Specialized Queries

        /// <summary>
        /// Get motifs affecting a specific position
        /// </summary>
        public async Task<List<Motif>> GetMotifsAtPositionAsync(Vector2 position, float radius = 0)
        {
            try
            {
                string endpoint = $"/motifs/position?x={position.x}&y={position.y}&radius={radius}";
                string responseJson = await SendRequestAsync(endpoint, "GET");
                var response = JsonConvert.DeserializeObject<MotifResponse<List<Motif>>>(responseJson, _jsonSettings);
                
                if (response.success)
                {
                    return response.data ?? new List<Motif>();
                }
                else
                {
                    Debug.LogError($"MotifApiClient: Failed to get motifs at position: {response.message}");
                    return new List<Motif>();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"MotifApiClient: Exception getting motifs at position: {ex.Message}");
                return new List<Motif>();
            }
        }

        /// <summary>
        /// Get global motifs
        /// </summary>
        public async Task<List<Motif>> GetGlobalMotifsAsync()
        {
            var filter = new MotifFilter
            {
                scopes = new List<MotifScope> { MotifScope.Global },
                activeOnly = true
            };
            return await GetMotifsAsync(filter);
        }

        /// <summary>
        /// Get regional motifs for a specific region
        /// </summary>
        public async Task<List<Motif>> GetRegionalMotifsAsync(string regionId)
        {
            var filter = new MotifFilter
            {
                scopes = new List<MotifScope> { MotifScope.Regional },
                regionIds = new List<string> { regionId },
                activeOnly = true
            };
            return await GetMotifsAsync(filter);
        }

        /// <summary>
        /// Get narrative context for motifs at a location
        /// </summary>
        public async Task<MotifNarrativeContext> GetNarrativeContextAsync(Vector2? position = null, string regionId = null)
        {
            try
            {
                string endpoint = "/motifs/narrative-context";
                var queryParams = new List<string>();
                
                if (position.HasValue)
                {
                    queryParams.Add($"x={position.Value.x}");
                    queryParams.Add($"y={position.Value.y}");
                }
                
                if (!string.IsNullOrEmpty(regionId))
                {
                    queryParams.Add($"regionId={regionId}");
                }
                
                if (queryParams.Count > 0)
                {
                    endpoint += "?" + string.Join("&", queryParams);
                }

                string responseJson = await SendRequestAsync(endpoint, "GET");
                var response = JsonConvert.DeserializeObject<MotifResponse<MotifNarrativeContext>>(responseJson, _jsonSettings);
                
                if (response.success)
                {
                    return response.data ?? new MotifNarrativeContext();
                }
                else
                {
                    Debug.LogError($"MotifApiClient: Failed to get narrative context: {response.message}");
                    return new MotifNarrativeContext();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"MotifApiClient: Exception getting narrative context: {ex.Message}");
                return new MotifNarrativeContext();
            }
        }

        #endregion

        #region Helper Methods

        private List<string> BuildQueryParams(MotifFilter filter)
        {
            var queryParams = new List<string>();

            if (filter.categories != null && filter.categories.Count > 0)
            {
                queryParams.Add($"categories={string.Join(",", filter.categories)}");
            }

            if (filter.scopes != null && filter.scopes.Count > 0)
            {
                queryParams.Add($"scopes={string.Join(",", filter.scopes)}");
            }

            if (filter.lifecycles != null && filter.lifecycles.Count > 0)
            {
                queryParams.Add($"lifecycles={string.Join(",", filter.lifecycles)}");
            }

            if (filter.minIntensity.HasValue)
            {
                queryParams.Add($"minIntensity={filter.minIntensity.Value}");
            }

            if (filter.maxIntensity.HasValue)
            {
                queryParams.Add($"maxIntensity={filter.maxIntensity.Value}");
            }

            if (!string.IsNullOrEmpty(filter.regionId))
            {
                queryParams.Add($"regionId={filter.regionId}");
            }

            if (filter.activeOnly)
            {
                queryParams.Add("activeOnly=true");
            }

            if (filter.ids != null && filter.ids.Count > 0)
            {
                queryParams.Add($"ids={string.Join(",", filter.ids)}");
            }

            if (filter.themes != null && filter.themes.Count > 0)
            {
                queryParams.Add($"themes={string.Join(",", filter.themes)}");
            }

            if (filter.regionIds != null && filter.regionIds.Count > 0)
            {
                queryParams.Add($"regionIds={string.Join(",", filter.regionIds)}");
            }

            if (filter.isGlobal.HasValue)
            {
                queryParams.Add($"isGlobal={filter.isGlobal.Value}");
            }

            if (filter.tags != null && filter.tags.Count > 0)
            {
                queryParams.Add($"tags={string.Join(",", filter.tags)}");
            }

            return queryParams;
        }

        #endregion
    }
} 