using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.POI
{
    /// <summary>
    /// Tracks population metrics, trends, and significant changes for a POI.
    /// </summary>
    [Serializable]
    public class PopulationMetricsTracker
    {
        [SerializeField] private int historySize = 30; // Number of samples to keep (e.g., 30 seconds)
        [SerializeField] private float significantDropThreshold = 0.2f; // 20% drop
        [SerializeField] private float updateInterval = 1f; // seconds

        private Queue<int> populationHistory = new Queue<int>();
        private float lastUpdateTime = 0f;
        private int lastPopulation = 0;

        public event Action<float> OnSignificantDrop; // Passes drop percentage
        public event Action OnDisaster;
        public event Action OnMigration;

        public int CurrentPopulation { get; private set; }
        public int MaxPopulation { get; private set; }
        public float PopulationChangeRate { get; private set; }
        public float CurrentPopulationPercent => MaxPopulation > 0 ? (float)CurrentPopulation / MaxPopulation : 0f;

        public void Initialize(int initialPopulation, int maxPopulation)
        {
            CurrentPopulation = initialPopulation;
            MaxPopulation = maxPopulation;
            lastPopulation = initialPopulation;
            populationHistory.Clear();
            populationHistory.Enqueue(initialPopulation);
            lastUpdateTime = Time.time;
        }

        public void UpdateMetrics(int newPopulation, int maxPopulation)
        {
            float now = Time.time;
            if (now - lastUpdateTime < updateInterval) return;
            lastUpdateTime = now;

            MaxPopulation = maxPopulation;
            PopulationChangeRate = (newPopulation - lastPopulation) / updateInterval;
            lastPopulation = newPopulation;
            CurrentPopulation = newPopulation;

            populationHistory.Enqueue(newPopulation);
            if (populationHistory.Count > historySize)
                populationHistory.Dequeue();

            // Detect significant drop
            if (populationHistory.Count == historySize)
            {
                int oldest = populationHistory.Peek();
                float drop = oldest > 0 ? (float)(oldest - newPopulation) / oldest : 0f;
                if (drop >= significantDropThreshold)
                {
                    OnSignificantDrop?.Invoke(drop);
                }
            }
        }

        public float GetAverageChangeRate()
        {
            if (populationHistory.Count < 2) return 0f;
            int[] arr = populationHistory.ToArray();
            float total = 0f;
            for (int i = 1; i < arr.Length; i++)
                total += arr[i] - arr[i - 1];
            return total / ((arr.Length - 1) * updateInterval);
        }

        // For future: methods to trigger OnDisaster, OnMigration, etc.
    }
} 