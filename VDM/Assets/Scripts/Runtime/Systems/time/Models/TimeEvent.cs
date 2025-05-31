using Newtonsoft.Json;
using System;
using UnityEngine;
using VDM.Systems.Events.Models;


namespace VDM.Systems.Time.Models
{
    /// <summary>
    /// Time-related event types aligned with backend.
    /// </summary>
    [Serializable]
    public enum TimeEventType
    {
        [JsonProperty("tick")]
        Tick,
        
        [JsonProperty("second")]
        Second,
        
        [JsonProperty("minute")]
        Minute,
        
        [JsonProperty("hour")]
        Hour,
        
        [JsonProperty("day")]
        Day,
        
        [JsonProperty("month")]
        Month,
        
        [JsonProperty("year")]
        Year,
        
        [JsonProperty("season_change")]
        SeasonChange
    }

    /// <summary>
    /// Time-related event that occurs at specific intervals, aligned with backend TimeEvent model.
    /// </summary>
    [Serializable]
    public class TimeEvent : BaseEvent
    {
        [SerializeField] private TimeEventType _timeEventType;
        [SerializeField] private GameTime _gameTime;
        [SerializeField] private string _description;

        /// <summary>
        /// Type of time event
        /// </summary>
        [JsonProperty("time_event_type")]
        public TimeEventType TimeEventType
        {
            get => _timeEventType;
            set => _timeEventType = value;
        }

        /// <summary>
        /// Game time when this event occurred
        /// </summary>
        [JsonProperty("game_time")]
        public GameTime GameTime
        {
            get => _gameTime;
            set => _gameTime = value;
        }

        /// <summary>
        /// Description of the time event
        /// </summary>
        [JsonProperty("description")]
        public string Description
        {
            get => _description;
            set => _description = value;
        }

        /// <summary>
        /// Create a new time event
        /// </summary>
        public TimeEvent() : base()
        {
            EventType = EventTypes.Time;
            _timeEventType = TimeEventType.Tick;
            _gameTime = new GameTime();
            _description = string.Empty;
        }

        /// <summary>
        /// Create a new time event with specified parameters
        /// </summary>
        public TimeEvent(TimeEventType timeEventType, GameTime gameTime, string description = "") : base()
        {
            EventType = EventTypes.Time;
            _timeEventType = timeEventType;
            _gameTime = gameTime?.Clone() ?? new GameTime();
            _description = description ?? string.Empty;
        }

        /// <summary>
        /// Create a time event from backend data
        /// </summary>
        public static TimeEvent FromBackendData(dynamic data)
        {
            var timeEvent = new TimeEvent();
            
            if (data.time_event_type != null)
            {
                timeEvent.TimeEventType = ParseTimeEventType(data.time_event_type.ToString());
            }
            
            if (data.game_time != null)
            {
                timeEvent.GameTime = GameTime.FromBackendData(data.game_time);
            }
            
            if (data.description != null)
            {
                timeEvent.Description = data.description.ToString();
            }

            return timeEvent;
        }

        /// <summary>
        /// Convert to backend-compatible format
        /// </summary>
        public object ToBackendData()
        {
            return new
            {
                time_event_type = TimeEventType.ToString().ToLowerInvariant(),
                game_time = GameTime?.ToBackendData(),
                description = Description
            };
        }

        private static TimeEventType ParseTimeEventType(string typeString)
        {
            return typeString?.ToLowerInvariant() switch
            {
                "tick" => TimeEventType.Tick,
                "second" => TimeEventType.Second,
                "minute" => TimeEventType.Minute,
                "hour" => TimeEventType.Hour,
                "day" => TimeEventType.Day,
                "month" => TimeEventType.Month,
                "year" => TimeEventType.Year,
                "season_change" => TimeEventType.SeasonChange,
                _ => TimeEventType.Tick
            };
        }

        public override string ToString()
        {
            return $"TimeEvent: {TimeEventType} at {GameTime} - {Description}";
        }
    }
} 