using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using Cysharp.Threading.Tasks;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.Networking;
using VisualDM.Core;

namespace VisualDM.API
{
    /// <summary>
    /// Client for communicating with the backend API
    /// </summary>
    public class ApiClient
    {
        private readonly ApiConfig _config;
        private string _authToken;
        
        public ApiClient(ApiConfig config)
        {
            _config = config;
        }
        
        #region Authentication
        
        /// <summary>
        /// Authenticates with the backend and returns a token
        /// </summary>
        public async UniTask<bool> AuthenticateAsync(string username, string password, CancellationToken cancellationToken = default)
        {
            try
            {
                var payload = new Dictionary<string, string>
                {
                    {"username", username},
                    {"password", password}
                };
                
                var response = await PostAsync<AuthResponse>(_config.AuthEndpoint, payload, false, cancellationToken);
                if (response != null && !string.IsNullOrEmpty(response.Token))
                {
                    _authToken = response.Token;
                    EventSystem.Publish(new AuthenticationSuccessEvent { Username = username });
                    return true;
                }
                
                Debug.LogError("Authentication failed: Invalid response");
                EventSystem.Publish(new AuthenticationFailedEvent { Reason = "Invalid response from server" });
                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Authentication failed: {ex.Message}");
                EventSystem.Publish(new AuthenticationFailedEvent { Reason = ex.Message });
                return false;
            }
        }
        
        private class AuthResponse
        {
            [JsonProperty("token")]
            public string Token { get; set; }
        }
        
        #endregion
        
        #region HTTP Methods
        
        /// <summary>
        /// Sends a GET request to the specified endpoint
        /// </summary>
        public async UniTask<T> GetAsync<T>(string endpoint, bool useAuth = true, CancellationToken cancellationToken = default)
        {
            var requestUrl = endpoint;
            var currentAttempt = 0;
            
            while (currentAttempt < _config.MaxRetryAttempts)
            {
                try
                {
                    using var request = UnityWebRequest.Get(requestUrl);
                    request.timeout = _config.TimeoutSeconds;
                    
                    // Add authentication if required
                    if (useAuth && _config.UseAuthentication)
                    {
                        if (string.IsNullOrEmpty(_authToken))
                        {
                            throw new Exception("Authentication token is missing. Please authenticate first.");
                        }
                        request.SetRequestHeader("Authorization", $"Bearer {_authToken}");
                    }
                    
                    request.SetRequestHeader("Content-Type", "application/json");
                    
                    await request.SendWebRequest().WithCancellation(cancellationToken);
                    
                    if (request.result == UnityWebRequest.Result.Success)
                    {
                        var json = request.downloadHandler.text;
                        return JsonConvert.DeserializeObject<T>(json);
                    }
                    
                    // Handle specific error cases
                    if (request.responseCode == 401)
                    {
                        EventSystem.Publish(new AuthenticationExpiredEvent());
                        throw new Exception("Authentication expired");
                    }
                    
                    // Exponential backoff for retries
                    if (++currentAttempt < _config.MaxRetryAttempts)
                    {
                        await UniTask.Delay(TimeSpan.FromSeconds(Math.Pow(2, currentAttempt)), cancellationToken: cancellationToken);
                        continue;
                    }
                    
                    throw new Exception($"Request failed: {request.error} - {request.downloadHandler?.text}");
                }
                catch (OperationCanceledException)
                {
                    Debug.Log("Request was canceled");
                    throw;
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Error in GET request to {endpoint}: {ex.Message}");
                    
                    if (++currentAttempt < _config.MaxRetryAttempts)
                    {
                        await UniTask.Delay(TimeSpan.FromSeconds(Math.Pow(2, currentAttempt)), cancellationToken: cancellationToken);
                        continue;
                    }
                    
                    throw;
                }
            }
            
            throw new Exception($"Request to {endpoint} failed after {_config.MaxRetryAttempts} attempts");
        }
        
        /// <summary>
        /// Sends a POST request to the specified endpoint with the given payload
        /// </summary>
        public async UniTask<T> PostAsync<T>(string endpoint, object payload, bool useAuth = true, CancellationToken cancellationToken = default)
        {
            var requestUrl = endpoint;
            var jsonPayload = JsonConvert.SerializeObject(payload);
            var currentAttempt = 0;
            
            while (currentAttempt < _config.MaxRetryAttempts)
            {
                try
                {
                    using var request = new UnityWebRequest(requestUrl, "POST");
                    request.timeout = _config.TimeoutSeconds;
                    
                    var bodyRaw = Encoding.UTF8.GetBytes(jsonPayload);
                    request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                    request.downloadHandler = new DownloadHandlerBuffer();
                    
                    // Add authentication if required
                    if (useAuth && _config.UseAuthentication)
                    {
                        if (string.IsNullOrEmpty(_authToken))
                        {
                            throw new Exception("Authentication token is missing. Please authenticate first.");
                        }
                        request.SetRequestHeader("Authorization", $"Bearer {_authToken}");
                    }
                    
                    request.SetRequestHeader("Content-Type", "application/json");
                    
                    await request.SendWebRequest().WithCancellation(cancellationToken);
                    
                    if (request.result == UnityWebRequest.Result.Success)
                    {
                        var json = request.downloadHandler.text;
                        return JsonConvert.DeserializeObject<T>(json);
                    }
                    
                    // Handle specific error cases
                    if (request.responseCode == 401)
                    {
                        EventSystem.Publish(new AuthenticationExpiredEvent());
                        throw new Exception("Authentication expired");
                    }
                    
                    // Exponential backoff for retries
                    if (++currentAttempt < _config.MaxRetryAttempts)
                    {
                        await UniTask.Delay(TimeSpan.FromSeconds(Math.Pow(2, currentAttempt)), cancellationToken: cancellationToken);
                        continue;
                    }
                    
                    throw new Exception($"Request failed: {request.error} - {request.downloadHandler?.text}");
                }
                catch (OperationCanceledException)
                {
                    Debug.Log("Request was canceled");
                    throw;
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Error in POST request to {endpoint}: {ex.Message}");
                    
                    if (++currentAttempt < _config.MaxRetryAttempts)
                    {
                        await UniTask.Delay(TimeSpan.FromSeconds(Math.Pow(2, currentAttempt)), cancellationToken: cancellationToken);
                        continue;
                    }
                    
                    throw;
                }
            }
            
            throw new Exception($"Request to {endpoint} failed after {_config.MaxRetryAttempts} attempts");
        }
        
        #endregion
    }
    
    #region Events
    
    public class AuthenticationSuccessEvent
    {
        public string Username { get; set; }
    }
    
    public class AuthenticationFailedEvent
    {
        public string Reason { get; set; }
    }
    
    public class AuthenticationExpiredEvent
    {
    }
    
    #endregion
} 