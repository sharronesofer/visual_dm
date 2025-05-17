using System;
using UnityEngine;

namespace VisualDM.World
{
    public class WeatherSystem
    {
        public enum WeatherType { Clear, Rain, Storm, Snow, Fog, Cloudy }
        public WeatherType CurrentWeather { get; private set; }
        private System.Random rng = new System.Random();
        private float weatherChangeTimer = 0f;
        private float weatherChangeInterval = 300f; // seconds

        public WeatherSystem(WorldTimeSystem time, SeasonSystem season)
        {
            UpdateWeather(time, season);
        }

        public void UpdateWeather(WorldTimeSystem time, SeasonSystem season)
        {
            weatherChangeTimer += Time.deltaTime;
            if (weatherChangeTimer >= weatherChangeInterval)
            {
                CurrentWeather = GenerateWeather(season.CurrentSeason);
                weatherChangeTimer = 0f;
            }
        }

        private WeatherType GenerateWeather(SeasonSystem.Season season)
        {
            // Example: simple probabilities by season
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
} 