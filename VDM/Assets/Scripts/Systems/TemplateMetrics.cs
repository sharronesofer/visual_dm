using System;
using System.Collections.Generic;

namespace VisualDM.AI
{
    public class TemplateMetrics
    {
        private readonly Dictionary<string, TemplateMetricData> _metrics = new Dictionary<string, TemplateMetricData>();

        public void LogUsage(string templateId)
        {
            GetOrCreate(templateId).UsageCount++;
        }

        public void LogEngagement(string templateId)
        {
            GetOrCreate(templateId).EngagementCount++;
        }

        public void LogCompletion(string templateId)
        {
            GetOrCreate(templateId).CompletionCount++;
        }

        public void LogSystems(string templateId, int score)
        {
            var data = GetOrCreate(templateId);
            data.SystemsScores.Add(score);
        }

        public TemplateMetricData GetMetrics(string templateId)
        {
            return _metrics.TryGetValue(templateId, out var data) ? data : null;
        }

        public void ReportAll()
        {
            foreach (var kvp in _metrics)
            {
                Console.WriteLine($"Template: {kvp.Key}, Usage: {kvp.Value.UsageCount}, Engagement: {kvp.Value.EngagementCount}, Completion: {kvp.Value.CompletionCount}, Avg Systems: {kvp.Value.AverageSystems():F2}");
            }
        }

        private TemplateMetricData GetOrCreate(string templateId)
        {
            if (!_metrics.ContainsKey(templateId))
                _metrics[templateId] = new TemplateMetricData();
            return _metrics[templateId];
        }
    }

    public class TemplateMetricData
    {
        public int UsageCount { get; set; }
        public int EngagementCount { get; set; }
        public int CompletionCount { get; set; }
        public List<int> SystemsScores { get; set; } = new List<int>();
        public double AverageSystems() => SystemsScores.Count > 0 ? (double)SystemsScores.Sum() / SystemsScores.Count : 0.0;
    }
} 