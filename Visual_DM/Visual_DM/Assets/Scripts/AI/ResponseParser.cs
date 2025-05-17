using System;
using System.Text.Json;
using UnityEngine;

namespace AI
{
    public class ResponseParser
    {
        private readonly GptLogger _logger = new GptLogger();

        public T ParseResponse<T>(string json)
        {
            try
            {
#if UNITY_2021_2_OR_NEWER
                return JsonSerializer.Deserialize<T>(json);
#else
                return JsonUtility.FromJson<T>(json);
#endif
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to parse GPT response: {ex.Message}\n{json}");
                return GetFallback<T>();
            }
        }

        public T GetFallback<T>() where T : new()
        {
            // Return a default instance as fallback
            _logger.LogWarning($"Returning fallback instance for type {typeof(T).Name}");
            return new T();
        }
    }
} 