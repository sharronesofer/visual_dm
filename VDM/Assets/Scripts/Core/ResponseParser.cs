using System;
using System.Text.Json;
using UnityEngine;

namespace VisualDM.Core
{
    public class ResponseParser
    {
        private readonly GptLogger _logger = new GptLogger();

        public T ParseResponse<T>(string json)
        {
            if (string.IsNullOrWhiteSpace(json))
            {
                _logger.LogError($"Core JSON is null or empty for type {typeof(T).Name}");
                return GetFallback<T>();
            }
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
                _logger.LogError($"Failed to parse GPT response for type {typeof(T).Name}: {ex.Message}\nCore: {json}");
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