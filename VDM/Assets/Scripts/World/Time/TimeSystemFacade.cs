using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.World;

namespace VisualDM.World.Time
{
    // Canonical time units: Tick, Second, Minute, Hour, Day, Month, Year, Season
    public enum TimeUnit { Tick, Second, Minute, Hour, Day, Month, Year, Season }
    // Canonical event types: OneTime, RecurringDaily, RecurringWeekly, RecurringMonthly, RecurringYearly, SeasonChange, SpecialDate
    public enum EventType { OneTime, RecurringDaily, RecurringWeekly, RecurringMonthly, RecurringYearly, SeasonChange, SpecialDate }

    [Serializable]
    public class ScheduledEvent
    {
        public EventType Type;
        public DateTime ScheduledTime;
        public Action Callback;
        public int Priority;
        public TimeSpan RecurrenceInterval;
        public string Name;
        // Extend with additional fields as needed
    }

    public class TimeSystemFacade : MonoBehaviour
    {
        public WorldTimeSystem TimeSystem { get; private set; }
        public CalendarSystem CalendarSystem { get; private set; }
        public RecurringEventSystem RecurringEventSystem { get; private set; }
        public SeasonSystem SeasonSystem { get; private set; }
        public DateTime CurrentTime { get; private set; } = new DateTime(1, 1, 1, 0, 0, 0);
        public float TimeScale { get; set; } = 1.0f;
        public int DaysPerMonth { get; private set; } = 30;
        public int MonthsPerYear { get; private set; } = 12;
        public int LeapYearInterval { get; private set; } = 4;
        public event Action<ScheduledEvent> OnEventTriggered;
        public event Action<DateTime> OnTimeAdvanced;

        private readonly List<ScheduledEvent> eventQueue = new List<ScheduledEvent>();
        private float accumulatedTime = 0f;

        public TimeSystemFacade()
        {
            TimeSystem = new WorldTimeSystem();
            CalendarSystem = new CalendarSystem();
            RecurringEventSystem = new RecurringEventSystem();
            SeasonSystem = new SeasonSystem(TimeSystem);
        }

        public void Tick(float deltaTime)
        {
            accumulatedTime += deltaTime * TimeScale;
            while (accumulatedTime >= 1f)
            {
                AdvanceTime(TimeSpan.FromSeconds(1));
                accumulatedTime -= 1f;
            }
        }

        public void AdvanceTime(TimeSpan span)
        {
            CurrentTime = CurrentTime.Add(span);
            OnTimeAdvanced?.Invoke(CurrentTime);
            CheckAndTriggerEvents();
        }

        public void ConfigureCalendar(int daysPerMonth, int monthsPerYear, bool useLeapYears = false, int leapYearInterval = 4)
        {
            CalendarSystem.ConfigureCalendar(daysPerMonth, monthsPerYear, useLeapYears, leapYearInterval);
            TimeSystem.SetCalendar(daysPerMonth, monthsPerYear, TimeSystem.HoursPerDay, TimeSystem.MinutesPerHour, TimeSystem.SecondsPerMinute);
        }

        public void ScheduleEvent(EventType type, DateTime date, TimeSpan? recurrence = null, Action callback = null, int priority = 0, string name = null)
        {
            eventQueue.Add(new ScheduledEvent
            {
                Type = type,
                ScheduledTime = date,
                Callback = callback,
                Priority = priority,
                RecurrenceInterval = recurrence ?? TimeSpan.Zero,
                Name = name
            });
            eventQueue.Sort((a, b) => a.ScheduledTime.CompareTo(b.ScheduledTime));
        }

        private void CheckAndTriggerEvents()
        {
            for (int i = eventQueue.Count - 1; i >= 0; i--)
            {
                var evt = eventQueue[i];
                if (CurrentTime >= evt.ScheduledTime)
                {
                    evt.Callback?.Invoke();
                    OnEventTriggered?.Invoke(evt);
                    if (evt.RecurrenceInterval > TimeSpan.Zero)
                    {
                        evt.ScheduledTime = evt.ScheduledTime.Add(evt.RecurrenceInterval);
                        // Keep recurring event in queue
                    }
                    else
                    {
                        eventQueue.RemoveAt(i);
                    }
                }
            }
        }

        public void AddImportantDate(string name, int year, int month, int day)
        {
            ScheduleEvent(EventType.SpecialDate, new DateTime(year, month, day), null, null, 1, name);
        }

        // Add more unified methods as needed (e.g., scheduling events, querying seasons, etc.)
    }
} 