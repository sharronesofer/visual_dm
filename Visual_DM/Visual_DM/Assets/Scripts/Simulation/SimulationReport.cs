using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;

namespace VisualDM.Simulation
{
    [Serializable]
    public class SimulationReport
    {
        public string ReportName;
        public DateTime GeneratedAt;
        public int Version;
        public List<TestCase> TestCases;
        public Dictionary<string, float> SummaryStats;
        public List<string> Outliers;
        public List<BalanceRecommendation> Recommendations;
        public List<VisualizationData> Visualizations;
        public string TemplateName;
        public string DashboardData;

        public SimulationReport(string name, int version, List<TestCase> testCases)
        {
            ReportName = name;
            GeneratedAt = DateTime.UtcNow;
            Version = version;
            TestCases = testCases;
            SummaryStats = new Dictionary<string, float>();
            Outliers = new List<string>();
            Recommendations = new List<BalanceRecommendation>();
            Visualizations = new List<VisualizationData>();
            TemplateName = "Default";
            DashboardData = string.Empty;
        }

        // Generate summary statistics
        public void GenerateSummary()
        {
            var dps = new List<float>();
            foreach (var tc in TestCases)
                dps.Add(StatisticalAnalysis.ComputeDPS(tc));
            SummaryStats["MeanDPS"] = StatisticalAnalysis.Mean(dps);
            SummaryStats["StdDevDPS"] = StatisticalAnalysis.StdDev(dps);
            Outliers = StatisticalAnalysis.DetectOutliers(dps).ConvertAll(i => TestCases[i].Name);
        }

        // Generate recommendations
        public void GenerateRecommendations()
        {
            var broken = StatisticalAnalysis.DetectBrokenCombos(TestCases);
            foreach (var feat in broken)
                Recommendations.Add(new BalanceRecommendation { FeatName = feat, Action = "Review for balance" });
        }

        // Generate visualization data (stub)
        public void GenerateVisualizations()
        {
            Visualizations.Add(new VisualizationData { Type = "BarChart", Data = "DPS by Build" });
            // Add more as needed
        }

        // Export to JSON (simple)
        public string ExportJson()
        {
            return JsonUtility.ToJson(this, true);
        }

        // Export to CSV (simple)
        public string ExportCsv()
        {
            var sb = new StringBuilder();
            sb.AppendLine("TestCase,MeanDPS,StdDevDPS");
            foreach (var tc in TestCases)
            {
                float dps = StatisticalAnalysis.ComputeDPS(tc);
                sb.AppendLine($"{tc.Name},{dps},{SummaryStats["StdDevDPS"]}");
            }
            return sb.ToString();
        }

        // Comparative reporting (stub)
        public void CompareWith(SimulationReport previous)
        {
            // TODO: Implement delta analysis
        }

        // Dashboard data (stub)
        public void GenerateDashboardData()
        {
            DashboardData = "Dashboard summary (stub)";
        }

        // Templating (stub)
        public void ApplyTemplate(string templateName)
        {
            TemplateName = templateName;
        }

        // Automated reporting (stub)
        public static void ScheduleReportGeneration(Action<SimulationReport> callback)
        {
            // TODO: Implement scheduling
        }
    }

    [Serializable]
    public class BalanceRecommendation
    {
        public string FeatName;
        public string Action;
        public float Confidence;
    }

    [Serializable]
    public class VisualizationData
    {
        public string Type;
        public string Data;
    }
} 