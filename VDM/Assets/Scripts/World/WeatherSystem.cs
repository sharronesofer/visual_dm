using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace VisualDM.World
{
    public class WeatherSystem
    {
        public enum WeatherType { Clear, Rain, Storm, Snow, Fog, Cloudy }
        public WeatherType CurrentWeather { get; private set; }
        private System.Random rng = new System.Random();
        private float weatherChangeTimer = 0f;
        private float weatherChangeInterval = 300f; // seconds

        // Ushuaia, Argentina as the real-world origin
        public Vector2 realWorldOrigin = new Vector2(-54.80194f, -68.30306f); // Ushuaia
        public Vector2 gameOrigin = Vector2.zero;
        public float unitsPerDegree = 100f; // Adjust to fit your world scale
        private WeatherType? cachedWeather = null;
        private float cacheTimestamp = -9999f;
        private float cacheDuration = 600f; // 10 minutes
        private string openWeatherApiKey = "YOUR_API_KEY"; // Set this in your config

        public WeatherSystem(WorldTimeSystem time, SeasonSystem season)
        {
            UpdateWeather(time, season);
        }

        public void UpdateWeather(WorldTimeSystem time, SeasonSystem season)
        {
            weatherChangeTimer += Time.deltaTime;
            if (weatherChangeTimer >= weatherChangeInterval)
            {
                // Use cached real-world weather if available and not expired
                if (cachedWeather.HasValue && Time.time - cacheTimestamp < cacheDuration)
                {
                    CurrentWeather = cachedWeather.Value;
                }
                else
                {
                    // Start coroutine to fetch real-world weather for origin
                    CoroutineRunner.Instance.StartCoroutine(FetchAndApplyRealWorldWeather(gameOrigin));
                }
                weatherChangeTimer = 0f;
            }
        }

        /// <summary>
        /// Fetches real-world weather for a given game position, maps it to WeatherType, and updates CurrentWeather.
        /// </summary>
        public IEnumerator FetchAndApplyRealWorldWeather(Vector2 gamePos)
        {
            Vector2 realWorldCoords = GameToRealWorldCoords(gamePos);
            string url = $"https://api.openweathermap.org/data/2.5/weather?lat={realWorldCoords.x}&lon={realWorldCoords.y}&appid={openWeatherApiKey}&units=metric";
            using (UnityWebRequest req = UnityWebRequest.Get(url))
            {
                yield return req.SendWebRequest();
                if (req.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        var weather = ParseWeatherJson(req.downloadHandler.text);
                        CurrentWeather = weather;
                        cachedWeather = weather;
                        cacheTimestamp = Time.time;
                    }
                    catch
                    {
                        // Fallback to procedural
                        CurrentWeather = GenerateWeather(SeasonSystem.Season.Winter); // Use season as fallback
                    }
                }
                else
                {
                    // Fallback to procedural
                    CurrentWeather = GenerateWeather(SeasonSystem.Season.Winter);
                }
            }
        }

        /// <summary>
        /// Converts a game position to real-world latitude/longitude, using Ushuaia as origin.
        /// </summary>
        private Vector2 GameToRealWorldCoords(Vector2 gamePos)
        {
            float lat = realWorldOrigin.x + (gamePos.x - gameOrigin.x) / unitsPerDegree;
            float lon = realWorldOrigin.y + (gamePos.y - gameOrigin.y) / unitsPerDegree;
            return new Vector2(lat, lon);
        }

        /// <summary>
        /// Parses OpenWeatherMap JSON and maps to WeatherType.
        /// </summary>
        private WeatherType ParseWeatherJson(string json)
        {
            var node = JsonUtility.FromJson<OpenWeatherResponse>(json);
            string main = node.weather[0].main.ToLower();
            if (main.Contains("rain")) return WeatherType.Rain;
            if (main.Contains("snow")) return WeatherType.Snow;
            if (main.Contains("storm") || main.Contains("thunder")) return WeatherType.Storm;
            if (main.Contains("fog") || main.Contains("mist") || main.Contains("haze")) return WeatherType.Fog;
            if (main.Contains("cloud")) return WeatherType.Cloudy;
            return WeatherType.Clear;
        }

        [Serializable]
        private class OpenWeatherResponse
        {
            public WeatherEntry[] weather;
        }
        [Serializable]
        private class WeatherEntry
        {
            public string main;
        }

        // Fallback procedural weather
        private WeatherType GenerateWeather(SeasonSystem.Season season)
        {
            switch (season)
            {
                case SeasonSystem.Season.Winter:
                    return WeightedRandom(new[] { WeatherType.Snow, WeatherType.Clear, WeatherType.Cloudy, WeatherType.Storm }, new[] { 0.5f, 0.2f, 0.2f, 0.1f });
                case SeasonSystem.Season.Spring:
                    return WeightedRandom(new[] { WeatherType.Rain, WeatherType.Clear, WeatherType.Cloudy, WeatherType.Fog }, new[] { 0.4f, 0.3f, 0.2f, 0.1f });
                case SeasonSystem.Season.Summer:
                    return WeightedRandom(new[] { WeatherType.Clear, WeatherType.Rain, WeatherType.Storm, WeatherType.Cloudy }, new[] { 0.5f, 0.2f, 0.1f, 0.2f });
                case SeasonSystem.Season.Autumn:
                    return WeightedRandom(new[] { WeatherType.Rain, WeatherType.Cloudy, WeatherType.Fog, WeatherType.Clear }, new[] { 0.3f, 0.3f, 0.2f, 0.2f });
                default:
                    return WeatherType.Clear;
            }
        }

        private WeatherType WeightedRandom(WeatherType[] types, float[] weights)
        {
            float total = 0f;
            foreach (var w in weights) total += w;
            float r = (float)rng.NextDouble() * total;
            float sum = 0f;
            for (int i = 0; i < types.Length; i++)
            {
                sum += weights[i];
                if (r <= sum) return types[i];
            }
            return types[0];
        }
    }

    /// <summary>
    /// Helper MonoBehaviour to run coroutines from non-MonoBehaviour classes.
    /// </summary>
    public class CoroutineRunner : MonoBehaviour
    {
        private static CoroutineRunner _instance;
        public static CoroutineRunner Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("CoroutineRunner");
                    _instance = go.AddComponent<CoroutineRunner>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }
    }
} 