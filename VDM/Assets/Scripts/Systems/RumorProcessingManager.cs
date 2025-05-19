using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.AI
{
    /// <summary>
    /// Processes queued events, transforms them into rumors, and stores the results.
    /// </summary>
    public class RumorProcessingManager : MonoBehaviour
    {
        public RumorTransformationConfig config;
        public float processInterval = 1.0f; // seconds between processing events

        private IGPTRumorService rumorService;
        private List<RumorRecord> rumorRecords = new List<RumorRecord>();
        private Dictionary<string, string> rumorCache = new Dictionary<string, string>(); // eventData+params → rumor
        private int maxBatchSize = 5;
        private float lastRequestTime = 0f;
        private float minRequestInterval = 0.2f; // seconds between backend requests

        public IReadOnlyList<RumorRecord> RumorRecords => rumorRecords;

        private void Awake()
        {
            rumorService = new GPTRumorService();
            if (config == null)
            {
                Debug.LogWarning("RumorProcessingManager: No config assigned, using defaults.");
                config = ScriptableObject.CreateInstance<RumorTransformationConfig>();
            }
            StartCoroutine(ProcessRumorEventsLoop());
        }

        private IEnumerator ProcessRumorEventsLoop()
        {
            while (true)
            {
                int processed = 0;
                while (EventCaptureManager.Instance != null && EventCaptureManager.Instance.TryDequeueEvent(out RumorEvent evt) && processed < maxBatchSize)
                {
                    var parameters = new RumorParameters
                    {
                        DistortionLevel = config.DefaultDistortionLevel,
                        NpcPersonality = config.DefaultNpcPersonality,
                        Theme = config.DefaultTheme,
                        RetellingCount = config.DefaultRetellingCount,
                        TimeSinceEvent = config.DefaultTimeSinceEvent
                    };
                    string cacheKey = evt.EventType + ":" + string.Join(",", evt.Actors) + ":" + evt.Location + ":" + evt.Context + ":" + parameters.DistortionLevel;
                    if (rumorCache.TryGetValue(cacheKey, out var cachedRumor))
                    {
                        if (config.EnableDebugLogs)
                            Debug.Log($"[RumorProcessing] Cache hit for event: {cacheKey}");
                        float truth = RumorTruthEvaluator.CalculateTruthValue(evt.Context, cachedRumor);
                        rumorRecords.Add(new RumorRecord(evt, cachedRumor, truth));
                        processed++;
                        continue;
                    }
                    // Throttle backend requests
                    float now = Time.time;
                    if (now - lastRequestTime < minRequestInterval)
                    {
                        if (config.EnableDebugLogs)
                            Debug.Log("[RumorProcessing] Throttling backend request.");
                        yield return new WaitForSeconds(minRequestInterval - (now - lastRequestTime));
                    }
                    lastRequestTime = Time.time;
                    // Send to backend
                    var task = rumorService.TransformRumorAsync(JsonUtility.ToJson(evt), parameters);
                    while (!task.IsCompleted) yield return null;
                    string rumor = task.Result;
                    rumorCache[cacheKey] = rumor;
                    float truthValue = RumorTruthEvaluator.CalculateTruthValue(evt.Context, rumor);
                    rumorRecords.Add(new RumorRecord(evt, rumor, truthValue));
                    if (config.EnableDebugLogs)
                        Debug.Log($"[RumorProcessing] Processed rumor for event: {cacheKey}");
                    processed++;
                }
                if (processed > 1 && config.EnableDebugLogs)
                    Debug.Log($"[RumorProcessing] Batch processed {processed} events.");
                yield return new WaitForSeconds(processInterval);
            }
        }

        // Runtime test for functional validation
        [ContextMenu("Run Rumor Pipeline Test")]
        public void RunRumorPipelineTest()
        {
            var testEvent = new RumorEvent
            {
                EventType = "gossip",
                Actors = new[] { "NPC_A", "NPC_B" },
                Location = "Tavern",
                Timestamp = System.DateTime.Now,
                Context = "NPC_A saw NPC_B steal a coin.",
                SourceNpcId = "NPC_A",
                TargetNpcId = "NPC_B"
            };
            EventCaptureManager.Instance?.RecordEvent(testEvent);
            Debug.Log("[RumorPipelineTest] Enqueued test event for rumor processing.");
        }
    }
}