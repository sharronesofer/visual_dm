using Newtonsoft.Json;
using System;
using UnityEngine;


namespace VDM.Runtime.Time.Models
{
    /// <summary>
    /// Represents a point in game time, aligned with backend time system.
    /// </summary>
    [Serializable]
    public class GameTime
    {
        [SerializeField] private int _tick;
        [SerializeField] private int _second;
        [SerializeField] private int _minute;
        [SerializeField] private int _hour;
        [SerializeField] private int _day;
        [SerializeField] private int _month;
        [SerializeField] private int _year;
        [SerializeField] private Season _season;

        /// <summary>
        /// Tick component (sub-second precision)
        /// </summary>
        [JsonProperty("tick")]
        public int Tick
        {
            get => _tick;
            set => _tick = Mathf.Max(0, value);
        }

        /// <summary>
        /// Second component (0-59)
        /// </summary>
        [JsonProperty("second")]
        public int Second
        {
            get => _second;
            set => _second = Mathf.Clamp(value, 0, 59);
        }

        /// <summary>
        /// Minute component (0-59)
        /// </summary>
        [JsonProperty("minute")]
        public int Minute
        {
            get => _minute;
            set => _minute = Mathf.Clamp(value, 0, 59);
        }

        /// <summary>
        /// Hour component (0-23)
        /// </summary>
        [JsonProperty("hour")]
        public int Hour
        {
            get => _hour;
            set => _hour = Mathf.Clamp(value, 0, 23);
        }

        /// <summary>
        /// Day component (1-30)
        /// </summary>
        [JsonProperty("day")]
        public int Day
        {
            get => _day;
            set => _day = Mathf.Clamp(value, 1, 30);
        }

        /// <summary>
        /// Month component (1-12)
        /// </summary>
        [JsonProperty("month")]
        public int Month
        {
            get => _month;
            set => _month = Mathf.Clamp(value, 1, 12);
        }

        /// <summary>
        /// Year component
        /// </summary>
        [JsonProperty("year")]
        public int Year
        {
            get => _year;
            set => _year = Mathf.Max(1, value);
        }

        /// <summary>
        /// Current season
        /// </summary>
        [JsonProperty("season")]
        public Season Season
        {
            get => _season;
            set => _season = value;
        }

        /// <summary>
        /// Get whether it is currently daytime (between 6:00 and 18:00)
        /// </summary>
        public bool IsDaytime => Hour >= 6 && Hour < 18;

        /// <summary>
        /// Get whether it is currently dawn (between 5:00 and 7:00)
        /// </summary>
        public bool IsDawn => Hour >= 5 && Hour < 7;

        /// <summary>
        /// Get whether it is currently dusk (between 17:00 and 19:00)
        /// </summary>
        public bool IsDusk => Hour >= 17 && Hour < 19;

        /// <summary>
        /// Get whether it is currently night (between 18:00 and 6:00)
        /// </summary>
        public bool IsNight => Hour >= 18 || Hour < 6;

        /// <summary>
        /// Get total ticks since year 1
        /// </summary>
        public long TotalTicks
        {
            get
            {
                long ticks = _tick;
                ticks += _second * 10; // Assuming 10 ticks per second
                ticks += _minute * 600; // 60 seconds * 10 ticks
                ticks += _hour * 36000; // 60 minutes * 600 ticks
                ticks += (_day - 1) * 864000; // 24 hours * 36000 ticks
                ticks += (_month - 1) * 25920000; // 30 days * 864000 ticks
                ticks += (_year - 1) * 311040000; // 12 months * 25920000 ticks
                return ticks;
            }
        }

        /// <summary>
        /// Create a new game time at the default starting point
        /// </summary>
        public GameTime()
        {
            _tick = 0;
            _second = 0;
            _minute = 0;
            _hour = 8;
            _day = 1;
            _month = 1;
            _year = 1;
            _season = Season.Spring;
        }

        /// <summary>
        /// Create a new game time with specified values
        /// </summary>
        public GameTime(int tick, int second, int minute, int hour, int day, int month, int year, Season season = Season.Spring)
        {
            Tick = tick;
            Second = second;
            Minute = minute;
            Hour = hour;
            Day = day;
            Month = month;
            Year = year;
            Season = season;
        }

        /// <summary>
        /// Create a copy of this game time
        /// </summary>
        /// <returns>A new GameTime instance with the same values</returns>
        public GameTime Clone()
        {
            return new GameTime(_tick, _second, _minute, _hour, _day, _month, _year, _season);
        }

        /// <summary>
        /// Add time to this GameTime instance
        /// </summary>
        /// <param name="ticks">Number of ticks to add</param>
        public void AddTicks(int ticks)
        {
            _tick += ticks;
            NormalizeTicks();
        }

        /// <summary>
        /// Add seconds to this GameTime instance
        /// </summary>
        /// <param name="seconds">Number of seconds to add</param>
        public void AddSeconds(int seconds)
        {
            _second += seconds;
            NormalizeSeconds();
        }

        /// <summary>
        /// Add minutes to this GameTime instance
        /// </summary>
        /// <param name="minutes">Number of minutes to add</param>
        public void AddMinutes(int minutes)
        {
            _minute += minutes;
            NormalizeMinutes();
        }

        /// <summary>
        /// Add hours to this GameTime instance
        /// </summary>
        /// <param name="hours">Number of hours to add</param>
        public void AddHours(int hours)
        {
            _hour += hours;
            NormalizeHours();
        }

        /// <summary>
        /// Add days to this GameTime instance
        /// </summary>
        /// <param name="days">Number of days to add</param>
        public void AddDays(int days)
        {
            _day += days;
            NormalizeDays();
        }

        private void NormalizeTicks()
        {
            if (_tick >= 10) // Assuming 10 ticks per second
            {
                _second += _tick / 10;
                _tick %= 10;
                NormalizeSeconds();
            }
        }

        private void NormalizeSeconds()
        {
            if (_second >= 60)
            {
                _minute += _second / 60;
                _second %= 60;
                NormalizeMinutes();
            }
        }

        private void NormalizeMinutes()
        {
            if (_minute >= 60)
            {
                _hour += _minute / 60;
                _minute %= 60;
                NormalizeHours();
            }
        }

        private void NormalizeHours()
        {
            if (_hour >= 24)
            {
                _day += _hour / 24;
                _hour %= 24;
                NormalizeDays();
            }
        }

        private void NormalizeDays()
        {
            if (_day > 30) // Simplified 30-day months
            {
                _month += (_day - 1) / 30;
                _day = ((_day - 1) % 30) + 1;
                NormalizeMonths();
            }
        }

        private void NormalizeMonths()
        {
            if (_month > 12)
            {
                _year += (_month - 1) / 12;
                _month = ((_month - 1) % 12) + 1;
            }
            UpdateSeason();
        }

        private void UpdateSeason()
        {
            int dayOfYear = (_month - 1) * 30 + _day;
            _season = dayOfYear switch
            {
                >= 1 and < 91 => Season.Spring,
                >= 91 and < 181 => Season.Summer,
                >= 181 and < 271 => Season.Fall,
                _ => Season.Winter
            };
        }

        public override string ToString()
        {
            return $"Year {_year}, {_season}, Month {_month}, Day {_day} - {_hour:D2}:{_minute:D2}:{_second:D2}.{_tick}";
        }

        public override bool Equals(object obj)
        {
            if (obj is GameTime other)
            {
                return _tick == other._tick && _second == other._second && _minute == other._minute &&
                       _hour == other._hour && _day == other._day && _month == other._month && _year == other._year;
            }
            return false;
        }

        public override int GetHashCode()
        {
            return HashCode.Combine(_tick, _second, _minute, _hour, _day, _month, _year);
        }

        /// <summary>
        /// Create a GameTime from backend data
        /// </summary>
        public static GameTime FromBackendData(dynamic data)
        {
            var gameTime = new GameTime();
            
            if (data.tick != null) gameTime.Tick = (int)data.tick;
            if (data.second != null) gameTime.Second = (int)data.second;
            if (data.minute != null) gameTime.Minute = (int)data.minute;
            if (data.hour != null) gameTime.Hour = (int)data.hour;
            if (data.day != null) gameTime.Day = (int)data.day;
            if (data.month != null) gameTime.Month = (int)data.month;
            if (data.year != null) gameTime.Year = (int)data.year;
            if (data.season != null) gameTime.Season = SeasonExtensions.FromBackendString(data.season.ToString());

            return gameTime;
        }

        /// <summary>
        /// Convert to backend-compatible format
        /// </summary>
        public object ToBackendData()
        {
            return new
            {
                tick = Tick,
                second = Second,
                minute = Minute,
                hour = Hour,
                day = Day,
                month = Month,
                year = Year,
                season = Season.ToBackendString()
            };
        }
    }
} 