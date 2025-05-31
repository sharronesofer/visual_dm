using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.DTOs.Common
{
    [Serializable]
    public class GameTimeDTO
    {
        public int year;
        public int month;
        public int day;
        public int hour;
        public int minute;
        public int second;
        public string timeZone;
        public float timeScale;
        public bool isPaused;
        public DateTime realWorldTime;
        
        public GameTimeDTO()
        {
            timeScale = 1.0f;
            isPaused = false;
            realWorldTime = DateTime.UtcNow;
        }
    }

    [Serializable]
    public class TimeUnitDTO
    {
        public string name;
        public int value;
        public string unit;
        public string description;
    }

    [Serializable]
    public class SaveGameMetadataDTO
    {
        public string id;
        public string name;
        public string description;
        public DateTime createdAt;
        public DateTime lastSaved;
        public string version;
        public long fileSize;
        public string checksum;
        public Dictionary<string, object> metadata;
        
        public SaveGameMetadataDTO()
        {
            metadata = new Dictionary<string, object>();
        }
    }

    [Serializable]
    public class GameSaveDataDTO
    {
        public SaveGameMetadataDTO metadata;
        public GameTimeDTO gameTime;
        public string worldState;
        public List<string> characterIds;
        public Dictionary<string, object> systemStates;
        
        public GameSaveDataDTO()
        {
            characterIds = new List<string>();
            systemStates = new Dictionary<string, object>();
        }
    }

    [Serializable]
    public class WeatherPattern
    {
        public string id;
        public string name;
        public string description;
        public float temperature;
        public float humidity;
        public float windSpeed;
        public string windDirection;
        public float precipitation;
        public string visibility;
        public Dictionary<string, float> conditions;
        
        public WeatherPattern()
        {
            conditions = new Dictionary<string, float>();
        }
    }

    [Serializable]
    public class WeatherForecast
    {
        public string regionId;
        public List<WeatherPattern> forecast;
        public int daysAhead;
        public float accuracy;
        public DateTime generatedAt;
        
        public WeatherForecast()
        {
            forecast = new List<WeatherPattern>();
        }
    }

    [Serializable]
    public class ResponseDTO<T>
    {
        public bool success;
        public string message;
        public T data;
        public List<string> errors;
        public DateTime timestamp;
        
        public ResponseDTO()
        {
            errors = new List<string>();
            timestamp = DateTime.UtcNow;
        }
    }

    [Serializable]
    public class PaginatedResponseDTO<T>
    {
        public List<T> items;
        public int totalCount;
        public int page;
        public int pageSize;
        public int totalPages;
        public bool hasNext;
        public bool hasPrevious;
        
        public PaginatedResponseDTO()
        {
            items = new List<T>();
        }
    }
} 