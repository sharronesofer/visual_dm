using System;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

namespace VDM.Runtime.Core.Services.Http
{
    /// <summary>
    /// Base class for HTTP service implementations
    /// </summary>
    public abstract class BaseHttpService : MonoBehaviour
    {
        [Header("HTTP Configuration")]
        [SerializeField] protected string baseUrl = "http://localhost:8000";
        [SerializeField] protected int timeoutSeconds = 30;
        
        protected virtual string ApiEndpoint => "";
        
        protected async Task<T> GetAsync<T>(string endpoint)
        {
            string url = $"{baseUrl}/{endpoint}";
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.timeout = timeoutSeconds;
                var operation = request.SendWebRequest();
                
                while (!operation.isDone)
                {
                    await Task.Yield();
                }
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    string json = request.downloadHandler.text;
                    return JsonUtility.FromJson<T>(json);
                }
                else
                {
                    Debug.LogError($"HTTP GET failed: {request.error}");
                    return default(T);
                }
            }
        }
        
        protected async Task<T> PostAsync<T>(string endpoint, object data)
        {
            string url = $"{baseUrl}/{endpoint}";
            string json = JsonUtility.ToJson(data);
            
            using (UnityWebRequest request = UnityWebRequest.Post(url, json, "application/json"))
            {
                request.timeout = timeoutSeconds;
                var operation = request.SendWebRequest();
                
                while (!operation.isDone)
                {
                    await Task.Yield();
                }
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    string responseJson = request.downloadHandler.text;
                    return JsonUtility.FromJson<T>(responseJson);
                }
                else
                {
                    Debug.LogError($"HTTP POST failed: {request.error}");
                    return default(T);
                }
            }
        }
    }
} 