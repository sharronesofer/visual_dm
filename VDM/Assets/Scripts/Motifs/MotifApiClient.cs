using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using System.Text.Json;
using UnityEngine.Networking;
using UnityEngine;

namespace VDM.Motifs
{
    /// <summary>
    /// REST client for querying and manipulating motifs from the backend API.
    /// </summary>
    public class MotifApiClient
    {
        private readonly string _baseUrl;
        private readonly int _maxRetries;
        private readonly float _retryDelay;
        private readonly JsonSerializerOptions _jsonOptions;

        public MotifApiClient(string baseUrl, int maxRetries = 3, float retryDelay = 1.0f)
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _maxRetries = maxRetries;
            _retryDelay = retryDelay;
            _jsonOptions = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
        }

        /// <summary>
        /// Get a list of motifs with optional query params.
        /// </summary>
        public async Task<List<Motif>> GetMotifsAsync(string query = "")
        {
            string url = _baseUrl + "/motifs" + (string.IsNullOrEmpty(query) ? "" : "?" + query);
            string json = await SendRequestAsync(url, "GET");
            return JsonSerializer.Deserialize<List<Motif>>(json, _jsonOptions);
        }

        /// <summary>
        /// Get a motif by ID.
        /// </summary>
        public async Task<Motif> GetMotifByIdAsync(int id)
        {
            string url = _baseUrl + $"/motifs/{id}";
            string json = await SendRequestAsync(url, "GET");
            return JsonSerializer.Deserialize<Motif>(json, _jsonOptions);
        }

        /// <summary>
        /// Create a new motif.
        /// </summary>
        public async Task<Motif> CreateMotifAsync(Motif motif)
        {
            string url = _baseUrl + "/motifs";
            string body = JsonSerializer.Serialize(motif, _jsonOptions);
            string json = await SendRequestAsync(url, "POST", body);
            return JsonSerializer.Deserialize<Motif>(json, _jsonOptions);
        }

        /// <summary>
        /// Update a motif by ID.
        /// </summary>
        public async Task<Motif> UpdateMotifAsync(int id, Motif motif)
        {
            string url = _baseUrl + $"/motifs/{id}";
            string body = JsonSerializer.Serialize(motif, _jsonOptions);
            string json = await SendRequestAsync(url, "PUT", body);
            return JsonSerializer.Deserialize<Motif>(json, _jsonOptions);
        }

        /// <summary>
        /// Delete a motif by ID.
        /// </summary>
        public async Task<bool> DeleteMotifAsync(int id)
        {
            string url = _baseUrl + $"/motifs/{id}";
            await SendRequestAsync(url, "DELETE");
            return true;
        }

        /// <summary>
        /// Batch create motifs.
        /// </summary>
        public async Task<List<Motif>> BatchCreateMotifsAsync(List<Motif> motifs)
        {
            string url = _baseUrl + "/motifs/batch";
            string body = JsonSerializer.Serialize(motifs, _jsonOptions);
            string json = await SendRequestAsync(url, "POST", body);
            return JsonSerializer.Deserialize<List<Motif>>(json, _jsonOptions);
        }

        /// <summary>
        /// Batch update motifs.
        /// </summary>
        public async Task<List<Motif>> BatchUpdateMotifsAsync(List<Motif> motifs)
        {
            string url = _baseUrl + "/motifs/batch";
            string body = JsonSerializer.Serialize(motifs, _jsonOptions);
            string json = await SendRequestAsync(url, "PUT", body);
            return JsonSerializer.Deserialize<List<Motif>>(json, _jsonOptions);
        }

        /// <summary>
        /// Batch delete motifs by IDs.
        /// </summary>
        public async Task<bool> BatchDeleteMotifsAsync(List<int> ids)
        {
            string url = _baseUrl + "/motifs/batch";
            string body = JsonSerializer.Serialize(ids, _jsonOptions);
            await SendRequestAsync(url, "DELETE", body);
            return true;
        }

        /// <summary>
        /// Send a UnityWebRequest with retries and error handling.
        /// </summary>
        private async Task<string> SendRequestAsync(string url, string method, string body = null)
        {
            int attempt = 0;
            while (true)
            {
                using (UnityWebRequest req = new UnityWebRequest(url, method))
                {
                    if (method == "POST" || method == "PUT" || method == "DELETE")
                    {
                        byte[] bodyRaw = Encoding.UTF8.GetBytes(body ?? "");
                        req.uploadHandler = new UploadHandlerRaw(bodyRaw);
                        req.SetRequestHeader("Content-Type", "application/json");
                    }
                    req.downloadHandler = new DownloadHandlerBuffer();
                    var op = req.SendWebRequest();
                    while (!op.isDone)
                        await Task.Yield();
                    if (req.result == UnityWebRequest.Result.Success)
                        return req.downloadHandler.text;
                    // Retry on transient errors
                    if (++attempt > _maxRetries || !IsTransientError(req))
                        throw new Exception($"Motif API error: {req.responseCode} {req.error} {req.downloadHandler.text}");
                    await Task.Delay(TimeSpan.FromSeconds(_retryDelay));
                }
            }
        }

        private bool IsTransientError(UnityWebRequest req)
        {
            // Retry on 408, 429, 5xx
            return req.responseCode == 408 || req.responseCode == 429 || (req.responseCode >= 500 && req.responseCode < 600);
        }
    }
} 