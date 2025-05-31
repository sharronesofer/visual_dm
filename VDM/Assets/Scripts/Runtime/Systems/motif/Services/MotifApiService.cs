using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using VDM.Systems.Motifs.Models;
using Newtonsoft.Json;

namespace VDM.Systems.Motifs.Services
{
    /// <summary>
    /// Service for communicating with the backend motif API
    /// </summary>
    public class MotifApiService : MonoBehaviour
    {
        [Header("API Configuration")]
        [SerializeField] private string baseUrl = "http://localhost:8000/api/motifs";
        [SerializeField] private float requestTimeout = 30f;
        [SerializeField] private int maxRetries = 3;
        [SerializeField] private bool enableLogging = true;

        // Events
        public event Action<List<Motif>> OnMotifsUpdated;
        public event Action<Motif> OnMotifCreated;
        public event Action<Motif> OnMotifUpdated;
        public event Action<string> OnMotifDeleted;
        public event Action<string> OnApiError;

        private static MotifApiService _instance;
        public static MotifApiService Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<MotifApiService>();
                    if (_instance == null)
                    {
                        var go = new GameObject("MotifApiService");
                        _instance = go.AddComponent<MotifApiService>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        private void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        #region Public API Methods

        /// <summary>
        /// Get all motifs with optional filtering
        /// </summary>
        public async Task<MotifResponse<List<Motif>>> GetMotifsAsync(MotifFilter filter = null)
        {
            try
            {
                string url = baseUrl;
                if (filter != null)
                {
                    url += BuildQueryString(filter);
                }

                var response = await SendGetRequestAsync<List<Motif>>(url);
                
                if (response.success && response.data != null)
                {
                    OnMotifsUpdated?.Invoke(response.data);
                }

                return response;
            }
            catch (Exception ex)
            {
                LogError($"Failed to get motifs: {ex.Message}");
                return CreateErrorResponse<List<Motif>>(ex.Message);
            }
        }

        /// <summary>
        /// Get a specific motif by ID
        /// </summary>
        public async Task<MotifResponse<Motif>> GetMotifAsync(string id)
        {
            try
            {
                string url = $"{baseUrl}/{id}";
                return await SendGetRequestAsync<Motif>(url);
            }
            catch (Exception ex)
            {
                LogError($"Failed to get motif {id}: {ex.Message}");
                return CreateErrorResponse<Motif>(ex.Message);
            }
        }

        /// <summary>
        /// Create a new motif
        /// </summary>
        public async Task<MotifResponse<Motif>> CreateMotifAsync(MotifCreateData createData)
        {
            try
            {
                var response = await SendPostRequestAsync<Motif>(baseUrl, createData);
                
                if (response.success && response.data != null)
                {
                    OnMotifCreated?.Invoke(response.data);
                }

                return response;
            }
            catch (Exception ex)
            {
                LogError($"Failed to create motif: {ex.Message}");
                return CreateErrorResponse<Motif>(ex.Message);
            }
        }

        /// <summary>
        /// Update an existing motif
        /// </summary>
        public async Task<MotifResponse<Motif>> UpdateMotifAsync(string id, MotifUpdateData updateData)
        {
            try
            {
                string url = $"{baseUrl}/{id}";
                var response = await SendPutRequestAsync<Motif>(url, updateData);
                
                if (response.success && response.data != null)
                {
                    OnMotifUpdated?.Invoke(response.data);
                }

                return response;
            }
            catch (Exception ex)
            {
                LogError($"Failed to update motif {id}: {ex.Message}");
                return CreateErrorResponse<Motif>(ex.Message);
            }
        }

        /// <summary>
        /// Delete a motif
        /// </summary>
        public async Task<MotifResponse<bool>> DeleteMotifAsync(string id)
        {
            try
            {
                string url = $"{baseUrl}/{id}";
                var response = await SendDeleteRequestAsync(url);
                
                if (response.success)
                {
                    OnMotifDeleted?.Invoke(id);
                }

                return response;
            }
            catch (Exception ex)
            {
                LogError($"Failed to delete motif {id}: {ex.Message}");
                return CreateErrorResponse<bool>(ex.Message);
            }
        }

        /// <summary>
        /// Get motif context for a location
        /// </summary>
        public async Task<MotifResponse<MotifNarrativeContext>> GetMotifContextAsync(Vector2? position = null, string regionId = null)
        {
            try
            {
                string url = $"{baseUrl}/context";
                var queryParams = new List<string>();
                
                if (position.HasValue)
                {
                    queryParams.Add($"x={position.Value.x}");
                    queryParams.Add($"y={position.Value.y}");
                }
                
                if (!string.IsNullOrEmpty(regionId))
                {
                    queryParams.Add($"region_id={regionId}");
                }

                if (queryParams.Count > 0)
                {
                    url += "?" + string.Join("&", queryParams);
                }

                return await SendGetRequestAsync<MotifNarrativeContext>(url);
            }
            catch (Exception ex)
            {
                LogError($"Failed to get motif context: {ex.Message}");
                return CreateErrorResponse<MotifNarrativeContext>(ex.Message);
            }
        }

        /// <summary>
        /// Generate a random motif
        /// </summary>
        public async Task<MotifResponse<Motif>> GenerateRandomMotifAsync(MotifScope scope, string regionId = null)
        {
            try
            {
                string url = $"{baseUrl}/random";
                var data = new { scope = scope.ToString().ToLower(), region_id = regionId };
                
                var response = await SendPostRequestAsync<Motif>(url, data);
                
                if (response.success && response.data != null)
                {
                    OnMotifCreated?.Invoke(response.data);
                }

                return response;
            }
            catch (Exception ex)
            {
                LogError($"Failed to generate random motif: {ex.Message}");
                return CreateErrorResponse<Motif>(ex.Message);
            }
        }

        /// <summary>
        /// Trigger chaos event
        /// </summary>
        public async Task<MotifResponse<object>> TriggerChaosAsync(string entityId, string regionId = null)
        {
            try
            {
                string url = $"{baseUrl}/chaos/trigger/{entityId}";
                var data = new { region_id = regionId };
                
                return await SendPostRequestAsync<object>(url, data);
            }
            catch (Exception ex)
            {
                LogError($"Failed to trigger chaos: {ex.Message}");
                return CreateErrorResponse<object>(ex.Message);
            }
        }

        #endregion

        #region HTTP Request Methods

        private async Task<MotifResponse<T>> SendGetRequestAsync<T>(string url)
        {
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.timeout = (int)requestTimeout;
                request.SetRequestHeader("Content-Type", "application/json");

                var operation = request.SendWebRequest();
                
                while (!operation.isDone)
                {
                    await Task.Yield();
                }

                return ProcessResponse<T>(request);
            }
        }

        private async Task<MotifResponse<T>> SendPostRequestAsync<T>(string url, object data)
        {
            string jsonData = JsonConvert.SerializeObject(data);
            
            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.timeout = (int)requestTimeout;
                request.SetRequestHeader("Content-Type", "application/json");

                var operation = request.SendWebRequest();
                
                while (!operation.isDone)
                {
                    await Task.Yield();
                }

                return ProcessResponse<T>(request);
            }
        }

        private async Task<MotifResponse<T>> SendPutRequestAsync<T>(string url, object data)
        {
            string jsonData = JsonConvert.SerializeObject(data);
            
            using (UnityWebRequest request = new UnityWebRequest(url, "PUT"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.timeout = (int)requestTimeout;
                request.SetRequestHeader("Content-Type", "application/json");

                var operation = request.SendWebRequest();
                
                while (!operation.isDone)
                {
                    await Task.Yield();
                }

                return ProcessResponse<T>(request);
            }
        }

        private async Task<MotifResponse<bool>> SendDeleteRequestAsync(string url)
        {
            using (UnityWebRequest request = UnityWebRequest.Delete(url))
            {
                request.timeout = (int)requestTimeout;

                var operation = request.SendWebRequest();
                
                while (!operation.isDone)
                {
                    await Task.Yield();
                }

                var response = new MotifResponse<bool>();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    response.success = true;
                    response.data = true;
                    response.message = "Motif deleted successfully";
                }
                else
                {
                    response.success = false;
                    response.data = false;
                    response.message = request.error;
                    response.errors.Add(request.error);
                }

                return response;
            }
        }

        #endregion

        #region Helper Methods

        private MotifResponse<T> ProcessResponse<T>(UnityWebRequest request)
        {
            var response = new MotifResponse<T>();

            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    string responseText = request.downloadHandler.text;
                    
                    if (enableLogging)
                    {
                        Debug.Log($"API Response: {responseText}");
                    }

                    response.data = JsonConvert.DeserializeObject<T>(responseText);
                    response.success = true;
                    response.message = "Request successful";
                }
                catch (Exception ex)
                {
                    response.success = false;
                    response.message = $"Failed to parse response: {ex.Message}";
                    response.errors.Add(ex.Message);
                    LogError(response.message);
                }
            }
            else
            {
                response.success = false;
                response.message = request.error;
                response.errors.Add(request.error);
                LogError($"API Request failed: {request.error}");
                OnApiError?.Invoke(request.error);
            }

            return response;
        }

        private string BuildQueryString(MotifFilter filter)
        {
            var queryParams = new List<string>();

            if (filter.categories?.Count > 0)
            {
                foreach (var category in filter.categories)
                {
                    queryParams.Add($"category={category.ToString().ToLower()}");
                }
            }

            if (filter.scopes?.Count > 0)
            {
                foreach (var scope in filter.scopes)
                {
                    queryParams.Add($"scope={scope.ToString().ToLower()}");
                }
            }

            if (filter.lifecycles?.Count > 0)
            {
                foreach (var lifecycle in filter.lifecycles)
                {
                    queryParams.Add($"lifecycle={lifecycle.ToString().ToLower()}");
                }
            }

            if (filter.minIntensity.HasValue)
                queryParams.Add($"min_intensity={filter.minIntensity.Value}");

            if (filter.maxIntensity.HasValue)
                queryParams.Add($"max_intensity={filter.maxIntensity.Value}");

            if (!string.IsNullOrEmpty(filter.regionId))
                queryParams.Add($"region_id={filter.regionId}");

            if (!string.IsNullOrEmpty(filter.effectType))
                queryParams.Add($"effect_type={filter.effectType}");

            queryParams.Add($"active_only={filter.activeOnly.ToString().ToLower()}");

            if (filter.isGlobal.HasValue)
                queryParams.Add($"is_global={filter.isGlobal.Value.ToString().ToLower()}");

            return queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
        }

        private MotifResponse<T> CreateErrorResponse<T>(string errorMessage)
        {
            return new MotifResponse<T>
            {
                success = false,
                message = errorMessage,
                errors = new List<string> { errorMessage }
            };
        }

        private void LogError(string message)
        {
            if (enableLogging)
            {
                Debug.LogError($"[MotifApiService] {message}");
            }
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Set the base URL for the API
        /// </summary>
        public void SetBaseUrl(string url)
        {
            baseUrl = url;
        }

        /// <summary>
        /// Set the request timeout
        /// </summary>
        public void SetTimeout(float timeout)
        {
            requestTimeout = timeout;
        }

        /// <summary>
        /// Enable or disable logging
        /// </summary>
        public void SetLogging(bool enabled)
        {
            enableLogging = enabled;
        }

        #endregion
    }
} 