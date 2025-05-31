using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System.Text;
using System;
using UnityEngine.Networking;
using UnityEngine;


namespace VDM.Infrastructure.Services
{
    /// <summary>
    /// Base HTTP client providing common functionality for all Visual DM service clients
    /// Handles request/response patterns, error handling, authentication, and retry logic
    /// </summary>
    public abstract class BaseHTTPClient : MonoBehaviour
    {
        [Header("Base Configuration")]
        [SerializeField] protected string baseUrl = "http://localhost:8000";
        [SerializeField] protected float requestTimeout = 30f;
        [SerializeField] protected int maxRetryAttempts = 3;
        [SerializeField] protected bool debugLogging = true;

        protected string authToken = "";
        protected Dictionary<string, string> defaultHeaders;
        protected bool isInitialized = false;

        // Common events
        public event Action<string> OnError;
        public event Action<bool> OnConnectionStatusChanged;

        protected virtual void InitializeClient()
        {
            if (isInitialized) return;

            defaultHeaders = new Dictionary<string, string>
            {
                ["Content-Type"] = "application/json",
                ["Accept"] = "application/json"
            };

            if (debugLogging)
                Debug.Log($"[{GetClientName()}] Initialized with base URL: {baseUrl}");

            isInitialized = true;
        }

        protected abstract string GetClientName();

        #region Common HTTP Methods

        protected IEnumerator GetRequestCoroutine(string endpoint, Action<bool, string> callback, int retryCount = 0)
        {
            string url = $"{baseUrl}{endpoint}";
            
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                SetHeaders(request);
                request.timeout = (int)requestTimeout;

                yield return request.SendWebRequest();

                bool success = request.result == UnityWebRequest.Result.Success;
                string response = success ? request.downloadHandler.text : null;

                if (!success && retryCount < maxRetryAttempts)
                {
                    if (debugLogging)
                        Debug.LogWarning($"[{GetClientName()}] GET {endpoint} failed, retrying... ({retryCount + 1}/{maxRetryAttempts})");
                    
                    yield return new WaitForSeconds(Mathf.Pow(2, retryCount)); // Exponential backoff
                    yield return GetRequestCoroutine(endpoint, callback, retryCount + 1);
                    yield break;
                }

                LogRequest("GET", endpoint, success, request.error);
                callback?.Invoke(success, response);

                if (!success)
                    OnError?.Invoke($"GET {endpoint} failed: {request.error}");
            }
        }

        protected IEnumerator PostRequestCoroutine(string endpoint, object data, Action<bool, string> callback, int retryCount = 0)
        {
            string url = $"{baseUrl}{endpoint}";
            string jsonData = data != null ? JsonConvert.SerializeObject(data) : "{}";

            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                
                SetHeaders(request);
                request.timeout = (int)requestTimeout;

                yield return request.SendWebRequest();

                bool success = request.result == UnityWebRequest.Result.Success;
                string response = success ? request.downloadHandler.text : null;

                if (!success && retryCount < maxRetryAttempts)
                {
                    if (debugLogging)
                        Debug.LogWarning($"[{GetClientName()}] POST {endpoint} failed, retrying... ({retryCount + 1}/{maxRetryAttempts})");
                    
                    yield return new WaitForSeconds(Mathf.Pow(2, retryCount)); // Exponential backoff
                    yield return PostRequestCoroutine(endpoint, data, callback, retryCount + 1);
                    yield break;
                }

                LogRequest("POST", endpoint, success, request.error);
                callback?.Invoke(success, response);

                if (!success)
                    OnError?.Invoke($"POST {endpoint} failed: {request.error}");
            }
        }

        protected IEnumerator PutRequestCoroutine(string endpoint, object data, Action<bool, string> callback, int retryCount = 0)
        {
            string url = $"{baseUrl}{endpoint}";
            string jsonData = JsonConvert.SerializeObject(data);

            using (UnityWebRequest request = new UnityWebRequest(url, "PUT"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                
                SetHeaders(request);
                request.timeout = (int)requestTimeout;

                yield return request.SendWebRequest();

                bool success = request.result == UnityWebRequest.Result.Success;
                string response = success ? request.downloadHandler.text : null;

                if (!success && retryCount < maxRetryAttempts)
                {
                    if (debugLogging)
                        Debug.LogWarning($"[{GetClientName()}] PUT {endpoint} failed, retrying... ({retryCount + 1}/{maxRetryAttempts})");
                    
                    yield return new WaitForSeconds(Mathf.Pow(2, retryCount)); // Exponential backoff
                    yield return PutRequestCoroutine(endpoint, data, callback, retryCount + 1);
                    yield break;
                }

                LogRequest("PUT", endpoint, success, request.error);
                callback?.Invoke(success, response);

                if (!success)
                    OnError?.Invoke($"PUT {endpoint} failed: {request.error}");
            }
        }

        protected IEnumerator DeleteRequestCoroutine(string endpoint, Action<bool, string> callback, int retryCount = 0)
        {
            string url = $"{baseUrl}{endpoint}";

            using (UnityWebRequest request = UnityWebRequest.Delete(url))
            {
                SetHeaders(request);
                request.timeout = (int)requestTimeout;

                yield return request.SendWebRequest();

                bool success = request.result == UnityWebRequest.Result.Success;
                string response = success ? request.downloadHandler.text : null;

                if (!success && retryCount < maxRetryAttempts)
                {
                    if (debugLogging)
                        Debug.LogWarning($"[{GetClientName()}] DELETE {endpoint} failed, retrying... ({retryCount + 1}/{maxRetryAttempts})");
                    
                    yield return new WaitForSeconds(Mathf.Pow(2, retryCount)); // Exponential backoff
                    yield return DeleteRequestCoroutine(endpoint, callback, retryCount + 1);
                    yield break;
                }

                LogRequest("DELETE", endpoint, success, request.error);
                callback?.Invoke(success, response);

                if (!success)
                    OnError?.Invoke($"DELETE {endpoint} failed: {request.error}");
            }
        }

        #endregion

        #region Helper Methods

        protected virtual void SetHeaders(UnityWebRequest request)
        {
            foreach (var header in defaultHeaders)
            {
                request.SetRequestHeader(header.Key, header.Value);
            }

            if (!string.IsNullOrEmpty(authToken))
            {
                request.SetRequestHeader("Authorization", $"Bearer {authToken}");
            }
        }

        protected void LogRequest(string method, string endpoint, bool success, string error = null)
        {
            if (!debugLogging) return;

            if (success)
                Debug.Log($"[{GetClientName()}] {method} {endpoint} successful");
            else
                Debug.LogError($"[{GetClientName()}] {method} {endpoint} failed: {error}");
        }

        protected T SafeDeserialize<T>(string json, T defaultValue = default(T)) where T : class
        {
            try
            {
                return JsonConvert.DeserializeObject<T>(json);
            }
            catch (Exception e)
            {
                Debug.LogError($"[{GetClientName()}] Failed to deserialize {typeof(T).Name}: {e.Message}");
                OnError?.Invoke($"Deserialization failed: {e.Message}");
                return defaultValue;
            }
        }

        protected List<T> SafeDeserializeList<T>(string json) where T : class
        {
            try
            {
                return JsonConvert.DeserializeObject<List<T>>(json) ?? new List<T>();
            }
            catch (Exception e)
            {
                Debug.LogError($"[{GetClientName()}] Failed to deserialize List<{typeof(T).Name}>: {e.Message}");
                OnError?.Invoke($"List deserialization failed: {e.Message}");
                return new List<T>();
            }
        }

        #endregion

        #region Public Properties & Methods

        public virtual void SetAuthToken(string token)
        {
            authToken = token;
            if (debugLogging && !string.IsNullOrEmpty(token))
                Debug.Log($"[{GetClientName()}] Auth token updated");
        }

        public string BaseUrl => baseUrl;
        public bool IsInitialized => isInitialized;

        /// <summary>
        /// Test connection to the server
        /// </summary>
        public virtual void TestConnection(Action<bool, string> callback = null)
        {
            StartCoroutine(TestConnectionCoroutine(callback));
        }

        protected virtual IEnumerator TestConnectionCoroutine(Action<bool, string> callback)
        {
            yield return GetRequestCoroutine("/", (success, response) =>
            {
                OnConnectionStatusChanged?.Invoke(success);
                callback?.Invoke(success, success ? "Connection successful" : "Connection failed");
            });
        }

        #endregion
    }
} 