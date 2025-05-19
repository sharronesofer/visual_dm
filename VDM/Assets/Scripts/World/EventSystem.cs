using System;
using System.Collections.Generic;

namespace VisualDM.World
{
    public class EventSystem
    {
        public class WorldEvent
        {
            public string Name;
            public int TriggerYear;
            public int TriggerMonth;
            public int TriggerDay;
            public Action OnEvent;
            public bool Triggered;
        }

        private List<WorldEvent> eventQueue = new List<WorldEvent>();

        public void ScheduleEvent(string name, int year, int month, int day, Action onEvent)
        {
            eventQueue.Add(new WorldEvent { Name = name, TriggerYear = year, TriggerMonth = month, TriggerDay = day, OnEvent = onEvent, Triggered = false });
        }

        public void UpdateEvents(WorldTimeSystem time)
        {
            foreach (var evt in eventQueue)
            {
                if (!evt.Triggered &&
                    (time.Year > evt.TriggerYear ||
                    (time.Year == evt.TriggerYear && time.Month > evt.TriggerMonth) ||
                    (time.Year == evt.TriggerYear && time.Month == evt.TriggerMonth && time.Day >= evt.TriggerDay)))
                {
                    evt.OnEvent?.Invoke();
                    evt.Triggered = true;
                }
            }
        }

        public IEnumerable<WorldEvent> GetUpcomingEvents(WorldTimeSystem time)
        {
            foreach (var evt in eventQueue)
            {
                if (!evt.Triggered &&
                    (time.Year < evt.TriggerYear ||
                    (time.Year == evt.TriggerYear && time.Month < evt.TriggerMonth) ||
                    (time.Year == evt.TriggerYear && time.Month == evt.TriggerMonth && time.Day < evt.TriggerDay)))
                {
                    yield return evt;
                }
            }
        }
    }
} 