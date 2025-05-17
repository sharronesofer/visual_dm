using System;
using System.Collections.Generic;

namespace AI
{
    public class HookAnalytics
    {
        private readonly Dictionary<HookEventType, int> _eventCounts = new Dictionary<HookEventType, int>();
        private readonly Dictionary<HookEventType, int> _questConversions = new Dictionary<HookEventType, int>();
        private readonly Dictionary<HookEventType, int> _playerEngagements = new Dictionary<HookEventType, int>();

        public void LogEvent(HookEventType type)
        {
            if (!_eventCounts.ContainsKey(type)) _eventCounts[type] = 0;
            _eventCounts[type]++;
        }

        public void LogQuestConversion(HookEventType type)
        {
            if (!_questConversions.ContainsKey(type)) _questConversions[type] = 0;
            _questConversions[type]++;
        }

        public void LogPlayerEngagement(HookEventType type)
        {
            if (!_playerEngagements.ContainsKey(type)) _playerEngagements[type] = 0;
            _playerEngagements[type]++;
        }

        public int GetEventCount(HookEventType type) => _eventCounts.TryGetValue(type, out var count) ? count : 0;
        public int GetQuestConversionCount(HookEventType type) => _questConversions.TryGetValue(type, out var count) ? count : 0;
        public int GetPlayerEngagementCount(HookEventType type) => _playerEngagements.TryGetValue(type, out var count) ? count : 0;

        public double GetConversionRate(HookEventType type)
        {
            int events = GetEventCount(type);
            int conversions = GetQuestConversionCount(type);
            return events > 0 ? (double)conversions / events : 0.0;
        }

        public void ReportAll()
        {
            foreach (var type in Enum.GetValues(typeof(HookEventType)))
            {
                var t = (HookEventType)type;
                Console.WriteLine($"Event: {t}, Count: {GetEventCount(t)}, Conversions: {GetQuestConversionCount(t)}, Engagements: {GetPlayerEngagementCount(t)}, Conversion Rate: {GetConversionRate(t):P2}");
            }
        }
    }
} 