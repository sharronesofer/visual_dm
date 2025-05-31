using System;
using UnityEngine;
using VDM.DTOs.Common;

namespace VDM.Systems.Time.Services
{
    public class TimeSystemFacade : MonoBehaviour
    {
        private static TimeSystemFacade _instance;
        public static TimeSystemFacade Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<TimeSystemFacade>();
                    if (_instance == null)
                    {
                        GameObject go = new GameObject("TimeSystemFacade");
                        _instance = go.AddComponent<TimeSystemFacade>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        [Header("Time System Settings")]
        public float timeScale = 1.0f;
        public bool isPaused = false;
        public bool enableLogging = true;
        
        private GameTimeDTO currentGameTime;
        private DateTime startTime;
        
        void Start()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            InitializeTimeSystem();
        }
        
        void Update()
        {
            if (!isPaused)
            {
                UpdateGameTime();
            }
        }
        
        private void InitializeTimeSystem()
        {
            startTime = DateTime.UtcNow;
            currentGameTime = new GameTimeDTO
            {
                year = 1000,
                month = 1,
                day = 1,
                hour = 12,
                minute = 0,
                second = 0,
                timeZone = "GMT",
                timeScale = timeScale,
                isPaused = isPaused
            };
            
            if (enableLogging)
                Debug.Log("TimeSystemFacade: Time system initialized");
        }
        
        private void UpdateGameTime()
        {
            float deltaTime = UnityEngine.Time.deltaTime * timeScale;
            
            // Update seconds
            currentGameTime.second += (int)(deltaTime);
            
            // Handle time overflow
            if (currentGameTime.second >= 60)
            {
                currentGameTime.minute += currentGameTime.second / 60;
                currentGameTime.second %= 60;
            }
            
            if (currentGameTime.minute >= 60)
            {
                currentGameTime.hour += currentGameTime.minute / 60;
                currentGameTime.minute %= 60;
            }
            
            if (currentGameTime.hour >= 24)
            {
                currentGameTime.day += currentGameTime.hour / 24;
                currentGameTime.hour %= 24;
            }
            
            // Simplified month/year handling
            if (currentGameTime.day > 30)
            {
                currentGameTime.month += currentGameTime.day / 30;
                currentGameTime.day = (currentGameTime.day % 30) + 1;
            }
            
            if (currentGameTime.month > 12)
            {
                currentGameTime.year += currentGameTime.month / 12;
                currentGameTime.month = (currentGameTime.month % 12) + 1;
            }
            
            currentGameTime.realWorldTime = DateTime.UtcNow;
        }
        
        public GameTimeDTO GetCurrentTime()
        {
            return currentGameTime;
        }
        
        public void SetTimeScale(float newTimeScale)
        {
            timeScale = newTimeScale;
            currentGameTime.timeScale = timeScale;
            
            if (enableLogging)
                Debug.Log($"TimeSystemFacade: Time scale set to {timeScale}");
        }
        
        public void PauseTime()
        {
            isPaused = true;
            currentGameTime.isPaused = true;
            
            if (enableLogging)
                Debug.Log("TimeSystemFacade: Time paused");
        }
        
        public void ResumeTime()
        {
            isPaused = false;
            currentGameTime.isPaused = false;
            
            if (enableLogging)
                Debug.Log("TimeSystemFacade: Time resumed");
        }
        
        public void SetGameTime(GameTimeDTO newTime)
        {
            if (newTime != null)
            {
                currentGameTime = newTime;
                timeScale = newTime.timeScale;
                isPaused = newTime.isPaused;
                
                if (enableLogging)
                    Debug.Log($"TimeSystemFacade: Game time set to {newTime.year}-{newTime.month}-{newTime.day} {newTime.hour}:{newTime.minute}:{newTime.second}");
            }
        }
        
        public string GetFormattedTime()
        {
            return $"{currentGameTime.year:D4}-{currentGameTime.month:D2}-{currentGameTime.day:D2} {currentGameTime.hour:D2}:{currentGameTime.minute:D2}:{currentGameTime.second:D2}";
        }
        
        public float GetTimeOfDay()
        {
            return (currentGameTime.hour * 3600 + currentGameTime.minute * 60 + currentGameTime.second) / 86400f;
        }
        
        public bool IsDay()
        {
            return currentGameTime.hour >= 6 && currentGameTime.hour < 18;
        }
        
        public bool IsNight()
        {
            return !IsDay();
        }
    }
} 