using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace VDM.Infrastructure.Services
{
    /// <summary>
    /// Base HTTP service for Unity frontend API communication
    /// Provides common HTTP methods for all services
    /// </summary>
    public abstract class BaseHttpService
    {
        protected string BaseUrl { get; set; } = "http://localhost:8000/api";
        protected Dictionary<string, string> DefaultHeaders { get; set; } = new Dictionary<string, string>();

        protected BaseHttpService()
        {
            // Set default headers
            DefaultHeaders["Content-Type"] = "application/json";
            DefaultHeaders["Accept"] = "application/json";
        }

        /// <summary>
        /// Generic GET request
        /// </summary>
        protected async Task<T> GetAsync<T>(string endpoint)
        {
            try
            {
                var url = GetFullUrl(endpoint);
                Debug.Log($"GET request to: {url}");
                
                // Simulate HTTP request for now
                await Task.Delay(100);
                
                // Return default value for compilation
                return default(T);
            }
            catch (Exception ex)
            {
                Debug.LogError($"GET request failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Generic POST request
        /// </summary>
        protected async Task<T> PostAsync<T>(string endpoint, object data = null)
        {
            try
            {
                var url = GetFullUrl(endpoint);
                var json = data != null ? JsonConvert.SerializeObject(data) : "{}";
                Debug.Log($"POST request to: {url} with data: {json}");
                
                // Simulate HTTP request for now
                await Task.Delay(100);
                
                // Return default value for compilation
                return default(T);
            }
            catch (Exception ex)
            {
                Debug.LogError($"POST request failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Generic PUT request
        /// </summary>
        protected async Task<T> PutAsync<T>(string endpoint, object data = null)
        {
            try
            {
                var url = GetFullUrl(endpoint);
                var json = data != null ? JsonConvert.SerializeObject(data) : "{}";
                Debug.Log($"PUT request to: {url} with data: {json}");
                
                // Simulate HTTP request for now
                await Task.Delay(100);
                
                // Return default value for compilation
                return default(T);
            }
            catch (Exception ex)
            {
                Debug.LogError($"PUT request failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Generic DELETE request
        /// </summary>
        protected async Task<T> DeleteAsync<T>(string endpoint)
        {
            try
            {
                var url = GetFullUrl(endpoint);
                Debug.Log($"DELETE request to: {url}");
                
                // Simulate HTTP request for now
                await Task.Delay(100);
                
                // Return default value for compilation
                return default(T);
            }
            catch (Exception ex)
            {
                Debug.LogError($"DELETE request failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Simple DELETE request without return value
        /// </summary>
        protected async Task DeleteAsync(string endpoint)
        {
            try
            {
                var url = GetFullUrl(endpoint);
                Debug.Log($"DELETE request to: {url}");
                
                // Simulate HTTP request for now
                await Task.Delay(100);
            }
            catch (Exception ex)
            {
                Debug.LogError($"DELETE request failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Set authentication header
        /// </summary>
        protected void SetAuthToken(string token)
        {
            if (!string.IsNullOrEmpty(token))
            {
                DefaultHeaders["Authorization"] = $"Bearer {token}";
            }
            else
            {
                DefaultHeaders.Remove("Authorization");
            }
        }

        /// <summary>
        /// Set custom header
        /// </summary>
        protected void SetHeader(string key, string value)
        {
            DefaultHeaders[key] = value;
        }

        /// <summary>
        /// Get full URL for endpoint
        /// </summary>
        private string GetFullUrl(string endpoint)
        {
            if (endpoint.StartsWith("http"))
            {
                return endpoint;
            }
            
            return BaseUrl.TrimEnd('/') + "/" + endpoint.TrimStart('/');
        }
    }
} 