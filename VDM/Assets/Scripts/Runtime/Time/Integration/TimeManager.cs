using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Events.Integration;
using VDM.Runtime.Time.Models;
using VDM.Runtime.Time.Services;


namespace VDM.Runtime.Time.Integration
{
    /// <summary>
    /// Unity MonoBehaviour manager for the Time system.
    /// Provides singleton access and Unity lifecycle integration.
    /// </summary>
    public class TimeManager : MonoBehaviour
    {
        [Header("Time Configuration")]
        [SerializeField] private bool _autoStart = true;
        [SerializeField] private float _initialTimeScale = 1.0f;
        [SerializeField] private bool _pauseOnApplicationFocus = true;
        
        [Header("Initial Time Settings")]
        [SerializeField] private int _startYear = 1;
        [SerializeField] private int _startMonth = 1;
        [SerializeField] private int _startDay = 1;
        [SerializeField] private int _startHour = 8;
        [SerializeField] private int _startMinute = 0;
        [SerializeField] private Season _startSeason = Season.Spring;

        private static TimeManager _instance;
        private ITimeService _timeService;
        private bool _isInitialized;

        /// <summary>
        /// Singleton instance of the TimeManager
        /// </summary>
        public static TimeManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<TimeManager>();
                    if (_instance == null)
                    {
                        var go = new GameObject("TimeManager");
                        _instance = go.AddComponent<TimeManager>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        /// <summary>
        /// Access to the time service
        /// </summary>
        public static ITimeService TimeService => Instance._timeService;

        /// <summary>
        /// Current game time (convenience property)
        /// </summary>
        public static GameTime CurrentTime => Instance._timeService?.CurrentTime;

        /// <summary>
        /// Whether time is paused (convenience property)
        /// </summary>
        public static bool IsPaused => Instance._timeService?.IsPaused ?? true;

        /// <summary>
        /// Current time scale (convenience property)
        /// </summary>
        public static float TimeScale
        {
            get => Instance._timeService?.TimeScale ?? 1.0f;
            set
            {
                if (Instance._timeService != null)
                    Instance._timeService.TimeScale = value;
            }
        }

        // Static event wrappers for convenience
        public static event Action<GameTime> OnTimeAdvanced
        {
            add => Instance._timeService.OnTimeAdvanced += value;
            remove => Instance._timeService.OnTimeAdvanced -= value;
        }

        public static event Action<bool> OnPauseStateChanged
        {
            add => Instance._timeService.OnPauseStateChanged += value;
            remove => Instance._timeService.OnPauseStateChanged -= value;
        }

        public static event Action<float> OnTimeScaleChanged
        {
            add => Instance._timeService.OnTimeScaleChanged += value;
            remove => Instance._timeService.OnTimeScaleChanged -= value;
        }

        public static event Action<Season> OnSeasonChanged
        {
            add => Instance._timeService.OnSeasonChanged += value;
            remove => Instance._timeService.OnSeasonChanged -= value;
        }

        private void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeAsync();
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        private async void InitializeAsync()
        {
            try
            {
                // Get event dispatcher from EventManager
                var eventDispatcher = EventManager.Instance?.EventDispatcher;
                
                // Create time service
                _timeService = new TimeService(eventDispatcher);
                
                // Set initial time
                var initialTime = new GameTime(0, 0, _startMinute, _startHour, _startDay, _startMonth, _startYear, _startSeason);
                _timeService.SetTime(initialTime);
                
                // Set initial time scale
                _timeService.TimeScale = _initialTimeScale;
                
                // Start service if auto-start is enabled
                if (_autoStart)
                {
                    await _timeService.StartAsync();
                }
                
                _isInitialized = true;
                Debug.Log($"[TimeManager] Initialized with time: {_timeService.CurrentTime}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[TimeManager] Failed to initialize: {ex.Message}");
            }
        }

        private void Update()
        {
            if (_isInitialized && _timeService is TimeService timeServiceImpl)
            {
                timeServiceImpl.Update(Time.deltaTime);
            }
        }

        private void OnApplicationFocus(bool hasFocus)
        {
            if (!_pauseOnApplicationFocus || !_isInitialized) return;
            
            if (hasFocus)
            {
                _timeService?.Resume();
            }
            else
            {
                _timeService?.Pause();
            }
        }

        private void OnApplicationPause(bool pauseStatus)
        {
            if (!_pauseOnApplicationFocus || !_isInitialized) return;
            
            if (pauseStatus)
            {
                _timeService?.Pause();
            }
            else
            {
                _timeService?.Resume();
            }
        }

        private async void OnDestroy()
        {
            if (_timeService != null)
            {
                await _timeService.StopAsync();
            }
        }

        // Static convenience methods
        
        /// <summary>
        /// Start the time service
        /// </summary>
        public static async Task StartAsync()
        {
            if (Instance._timeService != null)
                await Instance._timeService.StartAsync();
        }

        /// <summary>
        /// Stop the time service
        /// </summary>
        public static async Task StopAsync()
        {
            if (Instance._timeService != null)
                await Instance._timeService.StopAsync();
        }

        /// <summary>
        /// Pause time progression
        /// </summary>
        public static void Pause()
        {
            Instance._timeService?.Pause();
        }

        /// <summary>
        /// Resume time progression
        /// </summary>
        public static void Resume()
        {
            Instance._timeService?.Resume();
        }

        /// <summary>
        /// Set the current game time
        /// </summary>
        public static void SetTime(GameTime gameTime)
        {
            Instance._timeService?.SetTime(gameTime);
        }

        /// <summary>
        /// Advance time by specified ticks
        /// </summary>
        public static void AdvanceTime(int ticks)
        {
            Instance._timeService?.AdvanceTime(ticks);
        }

        /// <summary>
        /// Advance time by specified seconds
        /// </summary>
        public static void AdvanceTimeBySeconds(int seconds)
        {
            Instance._timeService?.AdvanceTimeBySeconds(seconds);
        }

        /// <summary>
        /// Advance time by specified minutes
        /// </summary>
        public static void AdvanceTimeByMinutes(int minutes)
        {
            Instance._timeService?.AdvanceTimeByMinutes(minutes);
        }

        /// <summary>
        /// Advance time by specified hours
        /// </summary>
        public static void AdvanceTimeByHours(int hours)
        {
            Instance._timeService?.AdvanceTimeByHours(hours);
        }

        /// <summary>
        /// Advance time by specified days
        /// </summary>
        public static void AdvanceTimeByDays(int days)
        {
            Instance._timeService?.AdvanceTimeByDays(days);
        }

        /// <summary>
        /// Get formatted time string
        /// </summary>
        public static string GetFormattedTime(string format = null)
        {
            return Instance._timeService?.GetFormattedTime(format) ?? "Unknown";
        }

        /// <summary>
        /// Check if it's currently a specific time of day
        /// </summary>
        public static bool IsTimeOfDay(int hour, int minute = 0)
        {
            return Instance._timeService?.IsTimeOfDay(hour, minute) ?? false;
        }

        /// <summary>
        /// Get time until next occurrence of specified time
        /// </summary>
        public static TimeSpan GetTimeUntil(int hour, int minute = 0)
        {
            return Instance._timeService?.GetTimeUntil(hour, minute) ?? TimeSpan.Zero;
        }

        /// <summary>
        /// Synchronize with backend time
        /// </summary>
        public static async Task SynchronizeWithBackendAsync()
        {
            if (Instance._timeService != null)
                await Instance._timeService.SynchronizeWithBackendAsync();
        }
    }
} 