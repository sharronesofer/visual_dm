using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
{
    public class RecurringEventSystem
    {
        public enum RecurrenceType { None, Daily, Weekly, Monthly, Yearly }
        [Serializable]
        public class ScheduledEvent
        {
            public string Name;
            public int Year, Month, Day, Hour, Minute, Second;
            public RecurrenceType Recurrence;
            public int RecurrenceInterval = 1; // e.g., every 2 days
            public Action OnEvent;
            public bool Triggered;
            public int Priority;
        }
        private SortedSet<ScheduledEvent> eventQueue = new SortedSet<ScheduledEvent>(new EventComparer());
        public event Action<ScheduledEvent> OnEventTriggered;
        public void ScheduleEvent(string name, int year, int month, int day, int hour, int minute, int second, RecurrenceType recurrence, int interval, Action onEvent, int priority = 0)
        {
            eventQueue.Add(new ScheduledEvent {
                Name = name, Year = year, Month = month, Day = day, Hour = hour, Minute = minute, Second = second,
                Recurrence = recurrence, RecurrenceInterval = interval, OnEvent = onEvent, Triggered = false, Priority = priority
            });
        }
        public void UpdateEvents(WorldTimeSystem time)
        {
            foreach (var evt in eventQueue)
            {
                if (!evt.Triggered && IsTimeToTrigger(evt, time))
                {
                    evt.OnEvent?.Invoke();
                    OnEventTriggered?.Invoke(evt);
                    if (evt.Recurrence == RecurrenceType.None)
                        evt.Triggered = true;
                    else
                        Reschedule(evt, time);
                }
            }
        }
        private bool IsTimeToTrigger(ScheduledEvent evt, WorldTimeSystem time)
        {
            return time.Year == evt.Year && time.Month == evt.Month && time.Day == evt.Day && time.Hour == evt.Hour && time.Minute == evt.Minute && time.Second == evt.Second;
        }
        private void Reschedule(ScheduledEvent evt, WorldTimeSystem time)
        {
            switch (evt.Recurrence)
            {
                case RecurrenceType.Daily:
                    AddDays(evt, evt.RecurrenceInterval, time);
                    break;
                case RecurrenceType.Weekly:
                    AddDays(evt, 7 * evt.RecurrenceInterval, time);
                    break;
                case RecurrenceType.Monthly:
                    AddMonths(evt, evt.RecurrenceInterval, time);
                    break;
                case RecurrenceType.Yearly:
                    evt.Year += evt.RecurrenceInterval;
                    break;
            }
        }
        private void AddDays(ScheduledEvent evt, int days, WorldTimeSystem time)
        {
            evt.Day += days;
            while (evt.Day > time.DaysPerMonth)
            {
                evt.Day -= time.DaysPerMonth;
                evt.Month++;
                if (evt.Month > time.MonthsPerYear)
                {
                    evt.Month = 1;
                    evt.Year++;
                }
            }
        }
        private void AddMonths(ScheduledEvent evt, int months, WorldTimeSystem time)
        {
            evt.Month += months;
            while (evt.Month > time.MonthsPerYear)
            {
                evt.Month -= time.MonthsPerYear;
                evt.Year++;
            }
        }
        // Serialization for save/load
        public List<ScheduledEvent> GetSerializableData() => new List<ScheduledEvent>(eventQueue);
        public void LoadFromData(List<ScheduledEvent> data) { eventQueue = new SortedSet<ScheduledEvent>(data, new EventComparer()); }
        // EventComparer for priority queue
        private class EventComparer : IComparer<ScheduledEvent>
        {
            public int Compare(ScheduledEvent a, ScheduledEvent b)
            {
                int cmp = a.Priority.CompareTo(b.Priority);
                if (cmp != 0) return cmp;
                cmp = a.Year.CompareTo(b.Year);
                if (cmp != 0) return cmp;
                cmp = a.Month.CompareTo(b.Month);
                if (cmp != 0) return cmp;
                cmp = a.Day.CompareTo(b.Day);
                if (cmp != 0) return cmp;
                cmp = a.Hour.CompareTo(b.Hour);
                if (cmp != 0) return cmp;
                cmp = a.Minute.CompareTo(b.Minute);
                if (cmp != 0) return cmp;
                return a.Second.CompareTo(b.Second);
            }
        }
    }
} 