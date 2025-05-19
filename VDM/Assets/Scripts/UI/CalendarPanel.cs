using UnityEngine;
using VisualDM.World;
using System.Collections.Generic;

namespace VisualDM.UI
{
    public class CalendarPanel : MonoBehaviour
    {
        private Time.TimeSystemFacade timeFacade;
        private GameObject panel;
        private RuntimeTextLabel label;
        private List<string> notifications = new List<string>();
        public void Initialize(Time.TimeSystemFacade timeFacade)
        {
            this.timeFacade = timeFacade;
            CreatePanel();
            SubscribeToUpdates();
        }
        private void CreatePanel()
        {
            panel = UIManager.Instance.CreatePanel("CalendarPanel", new Vector2(400, 300), new Vector2(0, 0), Color.gray);
            label = panel.AddComponent<RuntimeTextLabel>();
            label.SetText(GetCalendarText());
            panel.SetActive(false);
        }
        private void SubscribeToUpdates()
        {
            timeFacade.TimeSystem.OnTimeChanged += UpdateCalendarText;
            timeFacade.RecurringEventSystem.OnEventTriggered += evt => UpdateCalendarText();
        }
        private void UpdateCalendarText()
        {
            if (label != null)
                label.SetText(GetCalendarText());
        }
        private string GetCalendarText()
        {
            var time = timeFacade.TimeSystem;
            var date = $"Date: {time.Year}/{time.Month}/{time.Day} {time.Hour:D2}:{time.Minute:D2}:{time.Second:D2}\n";
            var events = "Upcoming Events:\n";
            foreach (var evt in timeFacade.RecurringEventSystem.GetSerializableData())
            {
                if (!evt.Triggered)
                    events += $"- {evt.Name} at {evt.Year}/{evt.Month}/{evt.Day} {evt.Hour:D2}:{evt.Minute:D2}\n";
            }
            return date + events;
        }
        public void Show() { panel.SetActive(true); }
        public void Hide() { panel.SetActive(false); }
        public void Notify(string message)
        {
            notifications.Add(message);
            // Show notification (could be a popup or label update)
        }
        // Navigation methods
        public void NextDay()
        {
            // Advance time by one day (for UI preview only, not actual game time)
            // Could be extended to preview future events
        }
        public void PrevDay()
        {
            // Go back one day (for UI preview only)
        }
        public void NextMonth() { }
        public void PrevMonth() { }
    }
} 