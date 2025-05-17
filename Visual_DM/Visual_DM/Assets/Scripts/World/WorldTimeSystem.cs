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
            timeAccumulator += deltaTime;
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
    }
} 