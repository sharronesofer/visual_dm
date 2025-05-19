using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.Input
{
    public class QueuePerformanceMonitor : MonoBehaviour
    {
        public ActionQueue ActionQueue;
        public float LogInterval = 1.0f;
        private float lastLogTime = 0f;
        private List<float> processingTimes = new List<float>();

        void Update()
        {
            float start = Time.realtimeSinceStartup;
            // Simulate processing (replace with actual queue processing if needed)
            var snapshot = ActionQueue?.GetQueueSnapshot();
            float end = Time.realtimeSinceStartup;
            float elapsed = (end - start) * 1000f; // ms
            processingTimes.Add(elapsed);

            if (Time.time - lastLogTime > LogInterval)
            {
                LogPerformance();
                lastLogTime = Time.time;
            }
        }

        private void LogPerformance()
        {
            if (processingTimes.Count == 0) return;
            float avg = 0f;
            foreach (var t in processingTimes) avg += t;
            avg /= processingTimes.Count;
            Debug.Log($"[ActionQueue] Avg processing time: {avg:F2} ms over {processingTimes.Count} frames");
            processingTimes.Clear();
        }
    }
} 