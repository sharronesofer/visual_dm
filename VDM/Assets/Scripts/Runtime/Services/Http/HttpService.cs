using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace VDM.Runtime.Services.Http
{
    /// <summary>
    /// HTTP service for making API calls to the backend
    /// </summary>
    public class HttpService : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string baseUrl = "http://localhost:8000/api";
        [SerializeField] private float timeoutSeconds = 30.0f;
        [SerializeField] private int maxRetries = 3;

        private List<float> latencyHistory = new List<float>();
        private const int maxLatencyHistory = 100;

        /// <summary>
        /// HTTP Response wrapper
        /// </summary>
        public class HttpResponse
        {
            public bool IsSuccess { get; set; }
            public string Data { get; set; }
            public string Error { get; set; }
            public int StatusCode { get; set; }
        }

        /// <summary>
        /// GET request
        /// </summary>
        public async Task<HttpResponse> GetAsync(string endpoint)
        {
            var startTime = Time.realtimeSinceStartup;
            var url = endpoint.StartsWith("http") ? endpoint : $"{baseUrl}/{endpoint.TrimStart('/')}";
            
            try
            {
                using (var request = UnityWebRequest.Get(url))
                {
                    request.timeout = (int)timeoutSeconds;
                    request.SetRequestHeader("Content-Type", "application/json");
                    
                    var operation = request.SendWebRequest();
                    while (!operation.isDone)
                    {
                        await Task.Yield();
                    }

                    RecordLatency(Time.realtimeSinceStartup - startTime);

                    if (request.result == UnityWebRequest.Result.Success)
                    {
                        return new HttpResponse
                        {
                            IsSuccess = true,
                            Data = request.downloadHandler.text,
                            StatusCode = (int)request.responseCode
                        };
                    }
                    else
                    {
                        return new HttpResponse
                        {
                            IsSuccess = false,
                            Error = request.error,
                            StatusCode = (int)request.responseCode
                        };
                    }
                }
            }
            catch (Exception ex)
            {
                return new HttpResponse
                {
                    IsSuccess = false,
                    Error = ex.Message,
                    StatusCode = -1
                };
            }
        }

        /// <summary>
        /// POST request
        /// </summary>
        public async Task<HttpResponse> PostAsync(string endpoint, object data)
        {
            var startTime = Time.realtimeSinceStartup;
            var url = endpoint.StartsWith("http") ? endpoint : $"{baseUrl}/{endpoint.TrimStart('/')}";
            var jsonData = JsonConvert.SerializeObject(data);
            
            try
            {
                using (var request = new UnityWebRequest(url, "POST"))
                {
                    request.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(jsonData));
                    request.downloadHandler = new DownloadHandlerBuffer();
                    request.timeout = (int)timeoutSeconds;
                    request.SetRequestHeader("Content-Type", "application/json");
                    
                    var operation = request.SendWebRequest();
                    while (!operation.isDone)
                    {
                        await Task.Yield();
                    }

                    RecordLatency(Time.realtimeSinceStartup - startTime);

                    if (request.result == UnityWebRequest.Result.Success)
                    {
                        return new HttpResponse
                        {
                            IsSuccess = true,
                            Data = request.downloadHandler.text,
                            StatusCode = (int)request.responseCode
                        };
                    }
                    else
                    {
                        return new HttpResponse
                        {
                            IsSuccess = false,
                            Error = request.error,
                            StatusCode = (int)request.responseCode
                        };
                    }
                }
            }
            catch (Exception ex)
            {
                return new HttpResponse
                {
                    IsSuccess = false,
                    Error = ex.Message,
                    StatusCode = -1
                };
            }
        }

        /// <summary>
        /// PUT request
        /// </summary>
        public async Task<HttpResponse> PutAsync(string endpoint, object data)
        {
            var startTime = Time.realtimeSinceStartup;
            var url = endpoint.StartsWith("http") ? endpoint : $"{baseUrl}/{endpoint.TrimStart('/')}";
            var jsonData = JsonConvert.SerializeObject(data);
            
            try
            {
                using (var request = new UnityWebRequest(url, "PUT"))
                {
                    request.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(jsonData));
                    request.downloadHandler = new DownloadHandlerBuffer();
                    request.timeout = (int)timeoutSeconds;
                    request.SetRequestHeader("Content-Type", "application/json");
                    
                    var operation = request.SendWebRequest();
                    while (!operation.isDone)
                    {
                        await Task.Yield();
                    }

                    RecordLatency(Time.realtimeSinceStartup - startTime);

                    if (request.result == UnityWebRequest.Result.Success)
                    {
                        return new HttpResponse
                        {
                            IsSuccess = true,
                            Data = request.downloadHandler.text,
                            StatusCode = (int)request.responseCode
                        };
                    }
                    else
                    {
                        return new HttpResponse
                        {
                            IsSuccess = false,
                            Error = request.error,
                            StatusCode = (int)request.responseCode
                        };
                    }
                }
            }
            catch (Exception ex)
            {
                return new HttpResponse
                {
                    IsSuccess = false,
                    Error = ex.Message,
                    StatusCode = -1
                };
            }
        }

        /// <summary>
        /// DELETE request
        /// </summary>
        public async Task<HttpResponse> DeleteAsync(string endpoint)
        {
            var startTime = Time.realtimeSinceStartup;
            var url = endpoint.StartsWith("http") ? endpoint : $"{baseUrl}/{endpoint.TrimStart('/')}";
            
            try
            {
                using (var request = UnityWebRequest.Delete(url))
                {
                    request.timeout = (int)timeoutSeconds;
                    request.SetRequestHeader("Content-Type", "application/json");
                    
                    var operation = request.SendWebRequest();
                    while (!operation.isDone)
                    {
                        await Task.Yield();
                    }

                    RecordLatency(Time.realtimeSinceStartup - startTime);

                    if (request.result == UnityWebRequest.Result.Success)
                    {
                        return new HttpResponse
                        {
                            IsSuccess = true,
                            Data = request.downloadHandler.text,
                            StatusCode = (int)request.responseCode
                        };
                    }
                    else
                    {
                        return new HttpResponse
                        {
                            IsSuccess = false,
                            Error = request.error,
                            StatusCode = (int)request.responseCode
                        };
                    }
                }
            }
            catch (Exception ex)
            {
                return new HttpResponse
                {
                    IsSuccess = false,
                    Error = ex.Message,
                    StatusCode = -1
                };
            }
        }

        /// <summary>
        /// Get average network latency
        /// </summary>
        public float GetAverageLatency()
        {
            if (latencyHistory.Count == 0) return 0f;
            
            var sum = 0f;
            foreach (var latency in latencyHistory)
            {
                sum += latency;
            }
            return sum / latencyHistory.Count;
        }

        private void RecordLatency(float latency)
        {
            latencyHistory.Add(latency);
            if (latencyHistory.Count > maxLatencyHistory)
            {
                latencyHistory.RemoveAt(0);
            }
        }
    }
} 