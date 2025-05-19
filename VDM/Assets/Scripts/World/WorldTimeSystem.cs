using System;
using UnityEngine;

namespace VisualDM.World
{
    public class WorldTimeSystem
    {
        public int Year { get; private set; }
        public int Month { get; private set; }
        public int Day { get; private set; }
        public int Hour { get; private set; }
        public int Minute { get; private set; }
        public int Second { get; private set; }

        public int DaysPerMonth { get; private set; } = 30;
        public int MonthsPerYear { get; private set; } = 12;
        public int HoursPerDay { get; private set; } = 24;
        public int MinutesPerHour { get; private set; } = 60;
        public int SecondsPerMinute { get; private set; } = 60;

        private float timeAccumulator = 0f;
        public event Action OnTimeChanged;

        public float TimeScale { get; set; } = 1f;
        public bool IsPaused { get; set; } = false;
        public string TimeZone { get; set; } = "Default"; // For future extensibility

        public WorldTimeSystem(int startYear = 1, int startMonth = 1, int startDay = 1, int startHour = 0, int startMinute = 0, int startSecond = 0)
        {
            Year = startYear;
            Month = startMonth;
            Day = startDay;
            Hour = startHour;
            Minute = startMinute;
            Second = startSecond;
        }

        public void Tick(float deltaTime)
        {
            if (IsPaused) return;
            timeAccumulator += deltaTime * TimeScale;
            while (timeAccumulator >= 1f)
            {
                AdvanceSecond();
                timeAccumulator -= 1f;
            }
        }

        private void AdvanceSecond()
        {
            Second++;
            if (Second >= SecondsPerMinute)
            {
                Second = 0;
                Minute++;
                if (Minute >= MinutesPerHour)
                {
                    Minute = 0;
                    Hour++;
                    if (Hour >= HoursPerDay)
                    {
                        Hour = 0;
                        Day++;
                        if (Day > DaysPerMonth)
                        {
                            Day = 1;
                            Month++;
                            if (Month > MonthsPerYear)
                            {
                                Month = 1;
                                Year++;
                            }
                        }
                    }
                }
            }
            OnTimeChanged?.Invoke();
        }

        public void SetCalendar(int daysPerMonth, int monthsPerYear, int hoursPerDay, int minutesPerHour, int secondsPerMinute)
        {
            DaysPerMonth = daysPerMonth;
            MonthsPerYear = monthsPerYear;
            HoursPerDay = hoursPerDay;
            MinutesPerHour = minutesPerHour;
            SecondsPerMinute = secondsPerMinute;
        }

        public float RealSecondsToGameSeconds(float realSeconds) => realSeconds * TimeScale;
        public float GameSecondsToRealSeconds(float gameSeconds) => gameSeconds / TimeScale;

        public WorldTimeData GetSerializableData() => new WorldTimeData {
            Year = Year, Month = Month, Day = Day, Hour = Hour, Minute = Minute, Second = Second, TimeScale = TimeScale, IsPaused = IsPaused, TimeZone = TimeZone
        };
        public void LoadFromData(WorldTimeData data)
        {
            Year = data.Year; Month = data.Month; Day = data.Day; Hour = data.Hour; Minute = data.Minute; Second = data.Second; TimeScale = data.TimeScale; IsPaused = data.IsPaused; TimeZone = data.TimeZone;
        }

        [Serializable]
        public class WorldTimeData {
            public int Year, Month, Day, Hour, Minute, Second;
            public float TimeScale;
            public bool IsPaused;
            public string TimeZone;
        }
    }
} 