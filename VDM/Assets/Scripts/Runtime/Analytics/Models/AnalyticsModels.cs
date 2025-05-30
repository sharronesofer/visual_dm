using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.Analytics.Models
{
    /// <summary>
    /// Analytics event types matching backend canonical structure
    /// </summary>
    public enum AnalyticsEventType
    {
        GameStart = 1,
        GameEnd = 2,
        MemoryEvent = 3,
        RumorEvent = 4,
        MotifEvent = 5,
        PopulationEvent = 6,
        POIStateEvent = 7,
        FactionEvent = 8,
        QuestEvent = 9,
        CombatEvent = 10,
        TimeEvent = 11,
        StorageEvent = 12,
        RelationshipEvent = 13,
        WorldStateEvent = 14,
        CustomEvent = 15
    }

    /// <summary>
    /// Base analytics event model
    /// </summary>
    [Serializable]
    public class AnalyticsEvent
    {
        public string id;
        public AnalyticsEventType eventType;
        public DateTime timestamp;
        public string sessionId;
        public string worldId;
        public Dictionary<string, object> data;
        public float processingTime;
        public int eventCount;

        public AnalyticsEvent()
        {
            id = Guid.NewGuid().ToString();
            timestamp = DateTime.UtcNow;
            data = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Performance metrics for system monitoring
    /// </summary>
    [Serializable]
    public class PerformanceMetrics
    {
        public float averageFrameRate;
        public float memoryUsage;
        public float cpuUsage;
        public float networkLatency;
        public Dictionary<string, float> systemLoad;
        public DateTime lastUpdated;

        public PerformanceMetrics()
        {
            systemLoad = new Dictionary<string, float>();
            lastUpdated = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Analytics report data structure
    /// </summary>
    [Serializable]
    public class AnalyticsReport
    {
        public string reportId;
        public string title;
        public DateTime startDate;
        public DateTime endDate;
        public Dictionary<AnalyticsEventType, int> eventCounts;
        public PerformanceMetrics performanceData;
        public List<string> insights;
        public byte[] chartData;

        public AnalyticsReport()
        {
            reportId = Guid.NewGuid().ToString();
            eventCounts = new Dictionary<AnalyticsEventType, int>();
            insights = new List<string>();
        }
    }

    /// <summary>
    /// Real-time analytics dashboard data
    /// </summary>
    [Serializable]
    public class DashboardData
    {
        public List<AnalyticsEvent> recentEvents;
        public PerformanceMetrics currentMetrics;
        public Dictionary<string, float> alertLevels;
        public List<string> activeAlerts;
        public DateTime lastRefresh;

        public DashboardData()
        {
            recentEvents = new List<AnalyticsEvent>();
            alertLevels = new Dictionary<string, float>();
            activeAlerts = new List<string>();
            lastRefresh = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// User behavior analytics
    /// </summary>
    [Serializable]
    public class UserBehaviorData
    {
        public string userId;
        public int totalSessions;
        public TimeSpan totalPlayTime;
        public Dictionary<string, int> featureUsage;
        public List<string> preferredSystems;
        public float engagementScore;

        public UserBehaviorData()
        {
            featureUsage = new Dictionary<string, int>();
            preferredSystems = new List<string>();
        }
    }

    /// <summary>
    /// System health status
    /// </summary>
    [Serializable]
    public class SystemHealthStatus
    {
        public string systemName;
        public HealthLevel healthLevel;
        public string status;
        public List<string> warnings;
        public List<string> errors;
        public DateTime lastCheck;
        public float uptime;

        public SystemHealthStatus()
        {
            warnings = new List<string>();
            errors = new List<string>();
            lastCheck = DateTime.UtcNow;
        }
    }

    public enum HealthLevel
    {
        Healthy,
        Warning,
        Critical,
        Offline
    }
} 