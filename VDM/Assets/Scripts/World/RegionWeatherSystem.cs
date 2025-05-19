using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System;

namespace VisualDM.World
{
    public class RegionWeatherSystem : MonoBehaviour
    {
        private Dictionary<string, WeatherData> weatherCache = new Dictionary<string, WeatherData>();
        private float cacheDuration = 3600f; // 1 hour
        private Dictionary<string, float> cacheTimestamps = new Dictionary<string, float>();
        private string backendUrl = "http://localhost:8000/weather"; // Update as needed

        [Serializable]
        public class WeatherData
        {
            public float lat;
            public float lon;
            public string weather;
        }

        public IEnumerator GetWeather(int regionX, int regionY, Action<WeatherData> callback)
        {
            string key = $"{regionX}_{regionY}";
            if (weatherCache.ContainsKey(key) && Time.time - cacheTimestamps[key] < cacheDuration)
            {
                callback(weatherCache[key]);
                yield break;
            }
            string url = $"{backendUrl}/{regionX}/{regionY}";
            using (UnityWebRequest req = UnityWebRequest.Get(url))
            {
                yield return req.SendWebRequest();
                if (req.result == UnityWebRequest.Result.Success)
                {
                    WeatherData data = JsonUtility.FromJson<WeatherData>(req.downloadHandler.text);
                    weatherCache[key] = data;
                    cacheTimestamps[key] = Time.time;
                    callback(data);
                }
                else
                {
                    // Fallback to procedural weather
                    WeatherData fallback = new WeatherData { lat = 0, lon = 0, weather = "Clear" };
                    callback(fallback);
                }
            }
        }
    }
} 