using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Game.Time
{
    /// <summary>
    /// Time units used in the game system
    /// </summary>
    public enum TimeUnitDTO
    {
        Tick,
        Second,
        Minute,
        Hour,
        Day,
        Month,
        Year,
        Season
    }

    /// <summary>
    /// Seasons in the game calendar
    /// </summary>
    public enum SeasonDTO
    {
        Spring,
        Summer,
        Autumn,
        Winter
    }

    /// <summary>
    /// Months in the game calendar
    /// </summary>
    public enum MonthDTO
    {
        January = 1,
        February = 2,
        March = 3,
        April = 4,
        May = 5,
        June = 6,
        July = 7,
        August = 8,
        September = 9,
        October = 10,
        November = 11,
        December = 12
    }

    /// <summary>
    /// Days of the week
    /// </summary>
    public enum DayOfWeekDTO
    {
        Monday,
        Tuesday,
        Wednesday,
        Thursday,
        Friday,
        Saturday,
        Sunday
    }

    /// <summary>
    /// Weather conditions
    /// </summary>
    public enum WeatherStateDTO
    {
        Clear,
        PartlyCloudy,
        Overcast,
        LightRain,
        HeavyRain,
        Storm,
        Snow,
        Blizzard,
        Fog,
        Windy
    }

    /// <summary>
    /// Event types for scheduled events
    /// </summary>
    public enum EventTypeDTO
    {
        OneTime,
        RecurringDaily,
        RecurringWeekly,
        RecurringMonthly,
        RecurringYearly,
        SeasonChange,
        SpecialDate
    }

    /// <summary>
    /// Calendar event types
    /// </summary>
    public enum CalendarEventTypeDTO
    {
        Holiday,
        Seasonal,
        Festival,
        Custom,
        Recurring,
        Worldgen
    }

    /// <summary>
    /// Time speed settings
    /// </summary>
    public enum TimeSpeedDTO
    {
        Paused = 0,
        Slow = 1,
        Normal = 2,
        Fast = 3,
        Fastest = 4
    }

    /// <summary>
    /// Core game time representation
    /// </summary>
    [Serializable]
    public class GameTimeDTO
    {
        public long Tick { get; set; } = 0;
        public int Second { get; set; } = 0;
        public int Minute { get; set; } = 0;
        public int Hour { get; set; } = 0;
        public int Day { get; set; } = 1;
        public int Month { get; set; } = 1;
        public int Year { get; set; } = 1;
        public SeasonDTO Season { get; set; } = SeasonDTO.Spring;
        public WeatherStateDTO Weather { get; set; } = WeatherStateDTO.Clear;
        public float Temperature { get; set; } = 20.0f;

        public string FormattedTime => $"{Hour:D2}:{Minute:D2}:{Second:D2}";
        public string FormattedDate => $"{Year}-{Month:D2}-{Day:D2}";
        public bool IsDaytime => Hour >= 6 && Hour < 18;
    }

    /// <summary>
    /// Time system configuration
    /// </summary>
    [Serializable]
    public class TimeConfigDTO
    {
        public int TicksPerSecond { get; set; } = 20;
        public int SecondsPerMinute { get; set; } = 60;
        public int MinutesPerHour { get; set; } = 60;
        public int HoursPerDay { get; set; } = 24;
        public int DaysPerMonth { get; set; } = 30;
        public int MonthsPerYear { get; set; } = 12;
        public int SeasonsPerYear { get; set; } = 4;
        public int LeapYearInterval { get; set; } = 4;
        public bool HasLeapYear { get; set; } = true;
        public float TimeScale { get; set; } = 1.0f;
        public bool AutoAdvance { get; set; } = true;
        public bool IsPaused { get; set; } = false;
        public Dictionary<SeasonDTO, int> SeasonBoundaries { get; set; } = new Dictionary<SeasonDTO, int>
        {
            { SeasonDTO.Spring, 3 },
            { SeasonDTO.Summer, 6 },
            { SeasonDTO.Autumn, 9 },
            { SeasonDTO.Winter, 12 }
        };
    }

    /// <summary>
    /// Calendar data and configuration
    /// </summary>
    [Serializable]
    public class CalendarDataDTO
    {
        public int CurrentDay { get; set; } = 1;
        public MonthDTO CurrentMonth { get; set; } = MonthDTO.January;
        public int CurrentYear { get; set; } = 1;
        public int CurrentHour { get; set; } = 0;
        public int CurrentMinute { get; set; } = 0;
        public int CurrentSecond { get; set; } = 0;
        public SeasonDTO CurrentSeason { get; set; } = SeasonDTO.Spring;
        public List<CalendarEventDTO> Events { get; set; } = new List<CalendarEventDTO>();
        public Dictionary<string, List<ImportantDateDTO>> ImportantDates { get; set; } = new Dictionary<string, List<ImportantDateDTO>>();
        public int MonthsPerYear { get; set; } = 12;
        public int LeapYearInterval { get; set; } = 4;
        public bool HasLeapYear { get; set; } = true;
        public int BaseDaysPerMonth { get; set; } = 30;
        public Dictionary<MonthDTO, int> DaysPerMonth { get; set; } = new Dictionary<MonthDTO, int>();
    }

    /// <summary>
    /// Weather data and conditions
    /// </summary>
    [Serializable]
    public class WeatherDataDTO
    {
        public WeatherStateDTO CurrentCondition { get; set; } = WeatherStateDTO.Clear;
        public float Temperature { get; set; } = 20.0f;
        public float Humidity { get; set; } = 50.0f;
        public float WindSpeed { get; set; } = 0.0f;
        public float WindDirection { get; set; } = 0.0f;
        public float Precipitation { get; set; } = 0.0f;
        public float Visibility { get; set; } = 100.0f;
        public Dictionary<SeasonDTO, float> SeasonModifiers { get; set; } = new Dictionary<SeasonDTO, float>();
        public Dictionary<WeatherStateDTO, float> TransitionProbabilities { get; set; } = new Dictionary<WeatherStateDTO, float>();
        public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Scheduled time event
    /// </summary>
    [Serializable]
    public class TimeEventDTO
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public EventTypeDTO EventType { get; set; } = EventTypeDTO.OneTime;
        public DateTime ScheduledTime { get; set; } = DateTime.UtcNow;
        public GameTimeDTO TriggerTime { get; set; }
        public TimeSpan? RecurrenceInterval { get; set; }
        public int Priority { get; set; } = 50;
        public bool IsActive { get; set; } = true;
        public bool IsRepeating { get; set; } = false;
        public int? MaxRepetitions { get; set; }
        public int CurrentRepetitions { get; set; } = 0;
        public string CallbackName { get; set; }
        public Dictionary<string, object> CallbackData { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime? LastTriggered { get; set; }
        public DateTime? NextTrigger { get; set; }
    }

    /// <summary>
    /// Calendar event (holidays, festivals, etc.)
    /// </summary>
    [Serializable]
    public class CalendarEventDTO
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public CalendarEventTypeDTO EventType { get; set; } = CalendarEventTypeDTO.Custom;
        public int Month { get; set; } = 1;
        public int Day { get; set; } = 1;
        public int? Year { get; set; } // null means every year
        public string StartTime { get; set; } // "HH:MM" format
        public string EndTime { get; set; } // "HH:MM" format
        public bool IsHoliday { get; set; } = false;
        public bool IsRecurring { get; set; } = true;
        public string RegionId { get; set; }
        public Dictionary<string, object> Effects { get; set; } = new Dictionary<string, object>();
        public bool IsAnnual => Year == null;
    }

    /// <summary>
    /// Important date marker
    /// </summary>
    [Serializable]
    public class ImportantDateDTO
    {
        public string Name { get; set; } = string.Empty;
        public int Year { get; set; } = 1;
        public int Month { get; set; } = 1;
        public int Day { get; set; } = 1;
        public string Description { get; set; }
        public string Category { get; set; } = "general";
    }

    /// <summary>
    /// Complete world time state
    /// </summary>
    [Serializable]
    public class WorldTimeDTO : MetadataDTO
    {
        public GameTimeDTO GameTime { get; set; } = new GameTimeDTO();
        public CalendarDataDTO Calendar { get; set; } = new CalendarDataDTO();
        public TimeConfigDTO Config { get; set; } = new TimeConfigDTO();
        public WeatherDataDTO Weather { get; set; }
        public List<TimeEventDTO> Events { get; set; } = new List<TimeEventDTO>();
        public List<CalendarEventDTO> CalendarEvents { get; set; } = new List<CalendarEventDTO>();
        public Dictionary<string, List<ImportantDateDTO>> ImportantDates { get; set; } = new Dictionary<string, List<ImportantDateDTO>>();
        public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
        public string TimeZone { get; set; } = "UTC";
        public float RealTimeMultiplier { get; set; } = 1.0f;
        public DateTime LastRealTimeUpdate { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Request to advance time
    /// </summary>
    [Serializable]
    public class AdvanceTimeRequestDTO
    {
        public int Amount { get; set; } = 1;
        public TimeUnitDTO Unit { get; set; } = TimeUnitDTO.Minute;
        public bool ForceAdvance { get; set; } = false;
        public bool TriggerEvents { get; set; } = true;
        public bool UpdateWeather { get; set; } = true;
    }

    /// <summary>
    /// Request to schedule an event
    /// </summary>
    [Serializable]
    public class ScheduleEventRequestDTO
    {
        public TimeEventDTO Event { get; set; } = new TimeEventDTO();
        public bool RelativeToCurrentTime { get; set; } = false;
        public TimeSpan? TimeDelta { get; set; }
    }

    /// <summary>
    /// Request to configure time system
    /// </summary>
    [Serializable]
    public class ConfigureTimeRequestDTO
    {
        public TimeConfigDTO Config { get; set; } = new TimeConfigDTO();
        public bool PreserveCurrentTime { get; set; } = true;
    }

    /// <summary>
    /// Time system status response
    /// </summary>
    [Serializable]
    public class TimeSystemStatusDTO : SuccessResponseDTO
    {
        public WorldTimeDTO WorldTime { get; set; }
        public TimeSpeedDTO TimeSpeed { get; set; } = TimeSpeedDTO.Normal;
        public bool IsPaused { get; set; } = false;
        public int PendingEvents { get; set; } = 0;
        public TimeEventDTO NextEvent { get; set; }
        public WeatherDataDTO CurrentWeather { get; set; }
        public TimeSpan Uptime { get; set; } = TimeSpan.Zero;
        public long TotalTicks { get; set; } = 0;
    }

    /// <summary>
    /// Calendar query request
    /// </summary>
    [Serializable]
    public class CalendarQueryRequestDTO
    {
        public DateTime? StartDate { get; set; }
        public DateTime? EndDate { get; set; }
        public List<CalendarEventTypeDTO> EventTypes { get; set; }
        public bool IncludeHolidays { get; set; } = true;
        public bool IncludeFestivals { get; set; } = true;
        public string RegionId { get; set; }
    }

    /// <summary>
    /// Calendar query response
    /// </summary>
    [Serializable]
    public class CalendarQueryResponseDTO : SuccessResponseDTO
    {
        public List<CalendarEventDTO> Events { get; set; } = new List<CalendarEventDTO>();
        public List<ImportantDateDTO> ImportantDates { get; set; } = new List<ImportantDateDTO>();
        public Dictionary<string, DateTime> DateRange { get; set; } = new Dictionary<string, DateTime>();
        public int TotalEvents { get; set; } = 0;
    }

    /// <summary>
    /// Weather forecast request
    /// </summary>
    [Serializable]
    public class WeatherForecastRequestDTO
    {
        public int DaysAhead { get; set; } = 7;
        public string RegionId { get; set; }
        public bool IncludeHourly { get; set; } = false;
    }

    /// <summary>
    /// Weather forecast response
    /// </summary>
    [Serializable]
    public class WeatherForecastResponseDTO : SuccessResponseDTO
    {
        public WeatherDataDTO CurrentWeather { get; set; }
        public List<WeatherDataDTO> DailyForecast { get; set; } = new List<WeatherDataDTO>();
        public List<WeatherDataDTO> HourlyForecast { get; set; }
        public float ForecastAccuracy { get; set; } = 0.8f;
        public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    }
} 