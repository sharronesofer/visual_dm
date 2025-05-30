using System.Threading.Tasks;
using System;
using VDM.Runtime.Time.Models;


namespace VDM.Runtime.Time.Services
{
    /// <summary>
    /// Interface for time management services, aligned with backend time system.
    /// </summary>
    public interface ITimeService
    {
        /// <summary>
        /// Current game time
        /// </summary>
        GameTime CurrentTime { get; }

        /// <summary>
        /// Whether time is currently paused
        /// </summary>
        bool IsPaused { get; }

        /// <summary>
        /// Current time scale multiplier
        /// </summary>
        float TimeScale { get; set; }

        /// <summary>
        /// Event fired when game time advances
        /// </summary>
        event Action<GameTime> OnTimeAdvanced;

        /// <summary>
        /// Event fired when time is paused or unpaused
        /// </summary>
        event Action<bool> OnPauseStateChanged;

        /// <summary>
        /// Event fired when time scale changes
        /// </summary>
        event Action<float> OnTimeScaleChanged;

        /// <summary>
        /// Event fired when season changes
        /// </summary>
        event Action<Season> OnSeasonChanged;

        /// <summary>
        /// Start the time service
        /// </summary>
        Task StartAsync();

        /// <summary>
        /// Stop the time service
        /// </summary>
        Task StopAsync();

        /// <summary>
        /// Pause time progression
        /// </summary>
        void Pause();

        /// <summary>
        /// Resume time progression
        /// </summary>
        void Resume();

        /// <summary>
        /// Set the current game time
        /// </summary>
        /// <param name="gameTime">New game time</param>
        void SetTime(GameTime gameTime);

        /// <summary>
        /// Advance time by specified amount
        /// </summary>
        /// <param name="ticks">Number of ticks to advance</param>
        void AdvanceTime(int ticks);

        /// <summary>
        /// Advance time by specified amount
        /// </summary>
        /// <param name="seconds">Number of seconds to advance</param>
        void AdvanceTimeBySeconds(int seconds);

        /// <summary>
        /// Advance time by specified amount
        /// </summary>
        /// <param name="minutes">Number of minutes to advance</param>
        void AdvanceTimeByMinutes(int minutes);

        /// <summary>
        /// Advance time by specified amount
        /// </summary>
        /// <param name="hours">Number of hours to advance</param>
        void AdvanceTimeByHours(int hours);

        /// <summary>
        /// Advance time by specified amount
        /// </summary>
        /// <param name="days">Number of days to advance</param>
        void AdvanceTimeByDays(int days);

        /// <summary>
        /// Synchronize with backend time
        /// </summary>
        Task SynchronizeWithBackendAsync();

        /// <summary>
        /// Get time formatted for display
        /// </summary>
        /// <param name="format">Format string</param>
        /// <returns>Formatted time string</returns>
        string GetFormattedTime(string format = null);

        /// <summary>
        /// Check if it's currently a specific time of day
        /// </summary>
        /// <param name="hour">Hour to check (0-23)</param>
        /// <param name="minute">Minute to check (0-59)</param>
        /// <returns>True if current time matches</returns>
        bool IsTimeOfDay(int hour, int minute = 0);

        /// <summary>
        /// Get time until next occurrence of specified time
        /// </summary>
        /// <param name="hour">Target hour</param>
        /// <param name="minute">Target minute</param>
        /// <returns>Time until target time</returns>
        TimeSpan GetTimeUntil(int hour, int minute = 0);
    }
} 