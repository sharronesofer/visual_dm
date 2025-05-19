using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
{
    public class EventNotificationSystem
    {
        private Queue<string> notifications = new Queue<string>();
        public event Action<string> OnNotification;
        public void Notify(string message)
        {
            notifications.Enqueue(message);
            OnNotification?.Invoke(message);
        }
        public void CheckUpcomingEvents(RecurringEventSystem eventSystem, WorldTimeSystem time)
        {
            foreach (var evt in eventSystem.GetSerializableData())
            {
                if (!evt.Triggered && IsSoon(evt, time))
                {
                    Notify($"Event '{evt.Name}' is coming up soon!");
                }
            }
        }
        private bool IsSoon(RecurringEventSystem.ScheduledEvent evt, WorldTimeSystem time)
        {
            // Notify if event is within next in-game hour
            if (evt.Year == time.Year && evt.Month == time.Month && evt.Day == time.Day)
            {
                int eventSeconds = evt.Hour * 3600 + evt.Minute * 60 + evt.Second;
                int nowSeconds = time.Hour * 3600 + time.Minute * 60 + time.Second;
                return eventSeconds - nowSeconds <= 3600 && eventSeconds - nowSeconds > 0;
            }
            return false;
        }
        public void CatchUpMissedEvents(RecurringEventSystem eventSystem, WorldTimeSystem lastTime, WorldTimeSystem currentTime)
        {
            // For each event, if it should have triggered between lastTime and currentTime, trigger it
            foreach (var evt in eventSystem.GetSerializableData())
            {
                if (!evt.Triggered && WasMissed(evt, lastTime, currentTime))
                {
                    evt.OnEvent?.Invoke();
                    Notify($"Missed event '{evt.Name}' triggered during catch-up.");
                }
            }
        }
        private bool WasMissed(RecurringEventSystem.ScheduledEvent evt, WorldTimeSystem last, WorldTimeSystem current)
        {
            // Simple check: event time is after last and before or equal to current
            DateTime lastDt = new DateTime(last.Year, last.Month, last.Day, last.Hour, last.Minute, last.Second);
            DateTime evtDt = new DateTime(evt.Year, evt.Month, evt.Day, evt.Hour, evt.Minute, evt.Second);
            DateTime currDt = new DateTime(current.Year, current.Month, current.Day, current.Hour, current.Minute, current.Second);
            return evtDt > lastDt && evtDt <= currDt;
        }
    }
} 