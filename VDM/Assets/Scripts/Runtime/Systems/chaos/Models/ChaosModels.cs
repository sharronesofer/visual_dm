using NativeWebSocket;
using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Systems.Chaos.Models
{
    /// <summary>
    /// Base DTO for chaos system data
    /// </summary>
    [Serializable]
    public class BaseChaosDTO
    {
        public string Id { get; set; }
        public DateTime Timestamp { get; set; }
        public string Version { get; set; } = "1.0";
    }

    /// <summary>
    /// DTO for chaos events received from the backend
    /// </summary>
    [Serializable]
    public class ChaosEventDTO : BaseChaosDTO
    {
        public string EventType { get; set; }
        public string Description { get; set; }
        public float Intensity { get; set; }
        public string RegionId { get; set; }
        public string SourceSystem { get; set; }
        public Dictionary<string, object> EventData { get; set; } = new Dictionary<string, object>();
        public List<string> AffectedSystems { get; set; } = new List<string>();
        public ChaosEventStatus Status { get; set; }
        public DateTime TriggeredAt { get; set; }
        public DateTime? ResolvedAt { get; set; }
        public List<ChaosEventEffect> Effects { get; set; } = new List<ChaosEventEffect>();
    }

    /// <summary>
    /// DTO for pressure source data
    /// </summary>
    [Serializable]
    public class PressureSourceDTO : BaseChaosDTO
    {
        public string SystemName { get; set; }
        public float CurrentPressure { get; set; }
        public float MaxPressure { get; set; }
        public float Weight { get; set; }
        public PressureType Type { get; set; }
        public string RegionId { get; set; }
        public List<PressureFactor> Factors { get; set; } = new List<PressureFactor>();
        public DateTime LastUpdated { get; set; }
        public float ChangeRate { get; set; }
        public PressureTrend Trend { get; set; }
    }

    /// <summary>
    /// DTO for chaos metrics and analytics
    /// </summary>
    [Serializable]
    public class ChaosMetricsDTO : BaseChaosDTO
    {
        public float GlobalChaosLevel { get; set; }
        public Dictionary<string, float> RegionalChaosLevels { get; set; } = new Dictionary<string, float>();
        public Dictionary<string, float> SystemPressures { get; set; } = new Dictionary<string, float>();
        public int TotalEventsToday { get; set; }
        public int ActiveEvents { get; set; }
        public float AverageMitigationEffectiveness { get; set; }
        public List<ChaosHotspot> Hotspots { get; set; } = new List<ChaosHotspot>();
        public ChaosSystemHealth SystemHealth { get; set; }
        public List<ChaosAlert> Alerts { get; set; } = new List<ChaosAlert>();
    }

    /// <summary>
    /// DTO for chaos system configuration
    /// </summary>
    [Serializable]
    public class ChaosConfigurationDTO : BaseChaosDTO
    {
        public Dictionary<string, float> SystemWeights { get; set; } = new Dictionary<string, float>();
        public Dictionary<string, float> ThresholdSettings { get; set; } = new Dictionary<string, float>();
        public Dictionary<string, float> MitigationFactors { get; set; } = new Dictionary<string, float>();
        public bool IsEnabled { get; set; }
        public float GlobalMultiplier { get; set; } = 1.0f;
        public ChaosConfigurationStatus Status { get; set; }
        public string LastModifiedBy { get; set; }
        public DateTime LastModified { get; set; }
    }

    /// <summary>
    /// DTO for historical chaos data
    /// </summary>
    [Serializable]
    public class ChaosHistoryDTO : BaseChaosDTO
    {
        public DateTime StartTime { get; set; }
        public DateTime EndTime { get; set; }
        public List<ChaosDataPoint> DataPoints { get; set; } = new List<ChaosDataPoint>();
        public Dictionary<string, List<float>> SystemTrends { get; set; } = new Dictionary<string, List<float>>();
        public List<ChaosEventDTO> Events { get; set; } = new List<ChaosEventDTO>();
        public ChaosStatistics Statistics { get; set; }
    }

    /// <summary>
    /// Real-time chaos update from WebSocket
    /// </summary>
    [Serializable]
    public class ChaosUpdateDTO : BaseChaosDTO
    {
        public ChaosUpdateType UpdateType { get; set; }
        public string TargetId { get; set; }
        public Dictionary<string, object> UpdateData { get; set; } = new Dictionary<string, object>();
        public float Priority { get; set; }
        public bool RequiresAcknowledgment { get; set; }
    }

    // Supporting Data Structures

    [Serializable]
    public class ChaosEventEffect
    {
        public string SystemId { get; set; }
        public string EffectType { get; set; }
        public float Magnitude { get; set; }
        public Duration Duration { get; set; }
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
    }

    [Serializable]
    public class PressureFactor
    {
        public string Name { get; set; }
        public float Contribution { get; set; }
        public string Source { get; set; }
        public bool IsTemporary { get; set; }
        public DateTime? ExpiresAt { get; set; }
    }

    [Serializable]
    public class ChaosHotspot
    {
        public string RegionId { get; set; }
        public string RegionName { get; set; }
        public float IntensityLevel { get; set; }
        public List<string> ActiveEventTypes { get; set; } = new List<string>();
        public Vector2 Coordinates { get; set; }
        public float Radius { get; set; }
    }

    [Serializable]
    public class ChaosAlert
    {
        public string AlertType { get; set; }
        public string Message { get; set; }
        public AlertSeverity Severity { get; set; }
        public DateTime CreatedAt { get; set; }
        public bool IsAcknowledged { get; set; }
        public string SourceSystem { get; set; }
    }

    [Serializable]
    public class ChaosSystemHealth
    {
        public SystemStatus OverallStatus { get; set; }
        public Dictionary<string, SystemStatus> ComponentStatuses { get; set; } = new Dictionary<string, SystemStatus>();
        public float PerformanceScore { get; set; }
        public List<string> Issues { get; set; } = new List<string>();
        public DateTime LastHealthCheck { get; set; }
    }

    [Serializable]
    public class ChaosDataPoint
    {
        public DateTime Timestamp { get; set; }
        public float Value { get; set; }
        public string MetricType { get; set; }
        public string Source { get; set; }
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    [Serializable]
    public class ChaosStatistics
    {
        public float AverageChaosLevel { get; set; }
        public float PeakChaosLevel { get; set; }
        public int TotalEvents { get; set; }
        public float MostActiveSystem { get; set; }
        public Dictionary<string, int> EventTypeCounts { get; set; } = new Dictionary<string, int>();
        public TimeSpan AverageEventDuration { get; set; }
    }

    [Serializable]
    public class Duration
    {
        public DurationType Type { get; set; }
        public float Value { get; set; }
        public DateTime? StartTime { get; set; }
        public DateTime? EndTime { get; set; }
    }

    // Enums

    public enum ChaosEventStatus
    {
        Pending,
        Active,
        Escalating,
        Resolving,
        Resolved,
        Cancelled
    }

    public enum PressureType
    {
        Economic,
        Political,
        Military,
        Social,
        Environmental,
        Diplomatic,
        Cultural,
        Religious,
        Territorial
    }

    public enum PressureTrend
    {
        Increasing,
        Decreasing,
        Stable,
        Volatile,
        Critical
    }

    public enum ChaosConfigurationStatus
    {
        Active,
        Pending,
        Testing,
        Disabled,
        Error
    }

    public enum ChaosUpdateType
    {
        PressureUpdate,
        EventTriggered,
        EventResolved,
        ConfigurationChanged,
        SystemAlert,
        MetricsUpdate,
        HealthCheck
    }

    public enum AlertSeverity
    {
        Info,
        Warning,
        Error,
        Critical
    }

    public enum SystemStatus
    {
        Healthy,
        Warning,
        Error,
        Critical,
        Offline
    }

    public enum DurationType
    {
        Immediate,
        Temporary,
        Extended,
        Permanent,
        Custom
    }
} 