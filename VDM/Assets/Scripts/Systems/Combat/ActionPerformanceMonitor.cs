using System;
using System.Collections.Generic;
using UnityEngine;

public class ActionPerformanceMonitor
{
    private static ActionPerformanceMonitor _instance;
    public static ActionPerformanceMonitor Instance => _instance ?? (_instance = new ActionPerformanceMonitor());

    private Dictionary<string, List<float>> _timings = new Dictionary<string, List<float>>();
    private Dictionary<string, float> _lastStart = new Dictionary<string, float>();
    public bool MonitoringEnabled = true;

    public void StartTiming(string actionKey)
    {
        if (!MonitoringEnabled) return;
        _lastStart[actionKey] = Time.realtimeSinceStartup;
    }

    public void StopTiming(string actionKey, ActionType type)
    {
        if (!MonitoringEnabled) return;
        if (!_lastStart.ContainsKey(actionKey)) return;
        float elapsed = (Time.realtimeSinceStartup - _lastStart[actionKey]) * 1000f;
        if (!_timings.ContainsKey(actionKey)) _timings[actionKey] = new List<float>();
        _timings[actionKey].Add(elapsed);
        LogTiming(actionKey, elapsed, type);
        _lastStart.Remove(actionKey);
    }

    private void LogTiming(string actionKey, float elapsed, ActionType type)
    {
        int target = TimingConfiguration.Instance.GetTimingMs(type);
        string msg = $"[Perf] {actionKey} took {elapsed:F2} ms (target: {target} ms)";
        if (elapsed > target)
        {
            Debug.LogWarning($"[Perf][WARN] {msg} - EXCEEDED TARGET");
        }
        else
        {
            Debug.Log(msg);
        }
    }

    public (float min, float max, float avg) GetStats(string actionKey)
    {
        if (!_timings.ContainsKey(actionKey) || _timings[actionKey].Count == 0)
            return (0, 0, 0);
        var list = _timings[actionKey];
        float min = float.MaxValue, max = float.MinValue, sum = 0;
        foreach (var t in list)
        {
            if (t < min) min = t;
            if (t > max) max = t;
            sum += t;
        }
        return (min, max, sum / list.Count);
    }

    public void Clear()
    {
        _timings.Clear();
        _lastStart.Clear();
    }

    // Analytics: Identify problematic actions
    public List<string> GetActionsExceedingTarget(float thresholdMs = 0)
    {
        var result = new List<string>();
        foreach (var kvp in _timings)
        {
            foreach (var t in kvp.Value)
            {
                int target = TimingConfiguration.Instance.GetTimingMs(ParseActionType(kvp.Key));
                if (t > target + thresholdMs)
                {
                    result.Add(kvp.Key);
                    break;
                }
            }
        }
        return result;
    }

    /// <summary>
    /// Export performance data for dashboard integration (stub).
    /// </summary>
    public string ExportPerformanceDataJson()
    {
        // TODO: Implement JSON export for dashboard
        return "{}";
    }

    private ActionType ParseActionType(string key)
    {
        // Simple parser, expects key to contain ActionType name
        if (key.Contains("Basic")) return ActionType.BasicAttack;
        if (key.Contains("Special")) return ActionType.SpecialAbility;
        if (key.Contains("Contextual")) return ActionType.ContextualAction;
        return ActionType.BasicAttack;
    }
} 