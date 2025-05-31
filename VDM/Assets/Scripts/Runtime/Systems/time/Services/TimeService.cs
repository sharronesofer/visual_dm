using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Systems.Time.Models;
using VDM.Infrastructure.Services;
using VDM.Systems.Events.Services;


namespace VDM.Systems.Time.Services
{
    /// <summary>
    /// Time service implementation with Unity integration and backend synchronization.
    /// </summary>
    public class TimeService : ITimeService
    {
        private GameTime _currentTime;
        private bool _isPaused;
        private float _timeScale = 1.0f;
        private bool _isRunning;
        private Season _lastSeason;
        
        private readonly IEventDispatcher _eventDispatcher;
        
        // Time progression settings
        private const float DefaultTickInterval = 0.1f; // 10 ticks per second
        private float _tickAccumulator;

        public GameTime CurrentTime => _currentTime?.Clone();
        public bool IsPaused => _isPaused;
        
        public float TimeScale 
        { 
            get => _timeScale;
            set
            {
                if (Math.Abs(_timeScale - value) > 0.001f)
                {
                    _timeScale = Mathf.Max(0f, value);
                    OnTimeScaleChanged?.Invoke(_timeScale);
                }
            }
        }

        public event Action<GameTime> OnTimeAdvanced;
        public event Action<bool> OnPauseStateChanged;
        public event Action<float> OnTimeScaleChanged;
        public event Action<Season> OnSeasonChanged;

        /// <summary>
        /// Create a new time service
        /// </summary>
        public TimeService(IEventDispatcher eventDispatcher = null)
        {
            _eventDispatcher = eventDispatcher;
            _currentTime = new GameTime();
            _lastSeason = _currentTime.Season;
            _isPaused = false;
            _isRunning = false;
        }

        public async Task StartAsync()
        {
            if (_isRunning) return;
            
            _isRunning = true;
            _tickAccumulator = 0f;
            
            Debug.Log("[TimeService] Time service started");
            
            // Start time progression in Unity's update loop
            // This will be handled by TimeManager MonoBehaviour
            
            await Task.CompletedTask;
        }

        public async Task StopAsync()
        {
            if (!_isRunning) return;
            
            _isRunning = false;
            
            Debug.Log("[TimeService] Time service stopped");
            
            await Task.CompletedTask;
        }

        public void Pause()
        {
            if (_isPaused) return;
            
            _isPaused = true;
            OnPauseStateChanged?.Invoke(true);
            
            Debug.Log("[TimeService] Time paused");
        }

        public void Resume()
        {
            if (!_isPaused) return;
            
            _isPaused = false;
            OnPauseStateChanged?.Invoke(false);
            
            Debug.Log("[TimeService] Time resumed");
        }

        public void SetTime(GameTime gameTime)
        {
            if (gameTime == null) return;
            
            var oldSeason = _currentTime?.Season ?? Season.Spring;
            _currentTime = gameTime.Clone();
            
            CheckSeasonChange(oldSeason, _currentTime.Season);
            OnTimeAdvanced?.Invoke(_currentTime);
            
            Debug.Log($"[TimeService] Time set to: {_currentTime}");
        }

        public void AdvanceTime(int ticks)
        {
            if (_isPaused || !_isRunning || ticks <= 0) return;
            
            var oldSeason = _currentTime.Season;
            _currentTime.AddTicks(ticks);
            
            CheckSeasonChange(oldSeason, _currentTime.Season);
            OnTimeAdvanced?.Invoke(_currentTime);
            
            // Publish time event
            PublishTimeEvent(TimeEventType.Tick, $"Advanced {ticks} ticks");
        }

        public void AdvanceTimeBySeconds(int seconds)
        {
            if (_isPaused || !_isRunning || seconds <= 0) return;
            
            var oldSeason = _currentTime.Season;
            _currentTime.AddSeconds(seconds);
            
            CheckSeasonChange(oldSeason, _currentTime.Season);
            OnTimeAdvanced?.Invoke(_currentTime);
            
            PublishTimeEvent(TimeEventType.Second, $"Advanced {seconds} seconds");
        }

        public void AdvanceTimeByMinutes(int minutes)
        {
            if (_isPaused || !_isRunning || minutes <= 0) return;
            
            var oldSeason = _currentTime.Season;
            _currentTime.AddMinutes(minutes);
            
            CheckSeasonChange(oldSeason, _currentTime.Season);
            OnTimeAdvanced?.Invoke(_currentTime);
            
            PublishTimeEvent(TimeEventType.Minute, $"Advanced {minutes} minutes");
        }

        public void AdvanceTimeByHours(int hours)
        {
            if (_isPaused || !_isRunning || hours <= 0) return;
            
            var oldSeason = _currentTime.Season;
            _currentTime.AddHours(hours);
            
            CheckSeasonChange(oldSeason, _currentTime.Season);
            OnTimeAdvanced?.Invoke(_currentTime);
            
            PublishTimeEvent(TimeEventType.Hour, $"Advanced {hours} hours");
        }

        public void AdvanceTimeByDays(int days)
        {
            if (_isPaused || !_isRunning || days <= 0) return;
            
            var oldSeason = _currentTime.Season;
            _currentTime.AddDays(days);
            
            CheckSeasonChange(oldSeason, _currentTime.Season);
            OnTimeAdvanced?.Invoke(_currentTime);
            
            PublishTimeEvent(TimeEventType.Day, $"Advanced {days} days");
        }

        public async Task SynchronizeWithBackendAsync()
        {
            try
            {
                // TODO: Implement backend synchronization
                // This would fetch current time from backend API
                Debug.Log("[TimeService] Backend synchronization not yet implemented");
                await Task.CompletedTask;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[TimeService] Failed to synchronize with backend: {ex.Message}");
            }
        }

        public string GetFormattedTime(string format = null)
        {
            if (_currentTime == null) return "Unknown";
            
            return format switch
            {
                "short" => $"{_currentTime.Hour:D2}:{_currentTime.Minute:D2}",
                "long" => $"Year {_currentTime.Year}, {_currentTime.Season}, Month {_currentTime.Month}, Day {_currentTime.Day} - {_currentTime.Hour:D2}:{_currentTime.Minute:D2}",
                "time" => $"{_currentTime.Hour:D2}:{_currentTime.Minute:D2}:{_currentTime.Second:D2}",
                "date" => $"Year {_currentTime.Year}, Month {_currentTime.Month}, Day {_currentTime.Day}",
                _ => _currentTime.ToString()
            };
        }

        public bool IsTimeOfDay(int hour, int minute = 0)
        {
            return _currentTime != null && 
                   _currentTime.Hour == hour && 
                   _currentTime.Minute == minute;
        }

        public TimeSpan GetTimeUntil(int hour, int minute = 0)
        {
            if (_currentTime == null) return TimeSpan.Zero;
            
            var currentMinutes = _currentTime.Hour * 60 + _currentTime.Minute;
            var targetMinutes = hour * 60 + minute;
            
            // If target is earlier in the day, it's tomorrow
            if (targetMinutes <= currentMinutes)
            {
                targetMinutes += 24 * 60; // Add 24 hours
            }
            
            var minutesUntil = targetMinutes - currentMinutes;
            return TimeSpan.FromMinutes(minutesUntil);
        }

        /// <summary>
        /// Update method to be called from Unity's Update loop
        /// </summary>
        public void Update(float deltaTime)
        {
            if (_isPaused || !_isRunning) return;
            
            _tickAccumulator += deltaTime * _timeScale;
            
            while (_tickAccumulator >= DefaultTickInterval)
            {
                _tickAccumulator -= DefaultTickInterval;
                AdvanceTime(1);
            }
        }

        private void CheckSeasonChange(Season oldSeason, Season newSeason)
        {
            if (oldSeason != newSeason)
            {
                OnSeasonChanged?.Invoke(newSeason);
                PublishTimeEvent(TimeEventType.SeasonChange, $"Season changed from {oldSeason} to {newSeason}");
                Debug.Log($"[TimeService] Season changed from {oldSeason} to {newSeason}");
            }
        }

        private void PublishTimeEvent(TimeEventType eventType, string description)
        {
            if (_eventDispatcher == null) return;
            
            var timeEvent = new TimeEvent(eventType, _currentTime, description);
            _eventDispatcher.Publish(timeEvent);
        }
    }
} 