using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class PlayerDropAttemptTracker
{
    [Serializable]
    private class SerializableCounter
    {
        public string questItemId;
        public int attemptCount;
    }

    [Serializable]
    private class SerializableTrackerData
    {
        public int version = 1;
        public List<SerializableCounter> counters = new List<SerializableCounter>();
    }

    private Dictionary<string, int> attemptCounters = new Dictionary<string, int>();

    public void IncrementCounter(string questItemId)
    {
        if (string.IsNullOrEmpty(questItemId)) return;
        if (!attemptCounters.ContainsKey(questItemId))
            attemptCounters[questItemId] = 0;
        attemptCounters[questItemId]++;
    }

    public void ResetCounter(string questItemId)
    {
        if (string.IsNullOrEmpty(questItemId)) return;
        attemptCounters[questItemId] = 0;
    }

    public int GetAttemptCount(string questItemId)
    {
        if (string.IsNullOrEmpty(questItemId)) return 0;
        if (attemptCounters.TryGetValue(questItemId, out int count))
            return count;
        return 0;
    }

    public Dictionary<string, int> GetAllCounters()
    {
        return new Dictionary<string, int>(attemptCounters);
    }

    public string ToJson()
    {
        var data = new SerializableTrackerData();
        foreach (var kvp in attemptCounters)
        {
            data.counters.Add(new SerializableCounter { questItemId = kvp.Key, attemptCount = kvp.Value });
        }
        return JsonUtility.ToJson(data);
    }

    public static PlayerDropAttemptTracker FromJson(string json)
    {
        var tracker = new PlayerDropAttemptTracker();
        if (string.IsNullOrEmpty(json)) return tracker;
        var data = JsonUtility.FromJson<SerializableTrackerData>(json);
        if (data != null && data.counters != null)
        {
            foreach (var counter in data.counters)
            {
                if (!string.IsNullOrEmpty(counter.questItemId))
                    tracker.attemptCounters[counter.questItemId] = counter.attemptCount;
            }
        }
        return tracker;
    }
} 