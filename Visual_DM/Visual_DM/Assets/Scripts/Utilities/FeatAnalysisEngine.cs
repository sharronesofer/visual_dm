using System;
using System.Collections.Generic;
using System.Linq;
using Visual_DM.Timeline.Models;
using Newtonsoft.Json;

namespace Visual_DM.Utilities
{
    public class FeatAnalysisEngine
    {
        public class FeatAnalysisResult
        {
            public string FeatId { get; set; }
            public string FeatName { get; set; }
            public float PowerScore { get; set; }
            public string ImbalanceType { get; set; } // Overpowered, Underpowered, Situational
            public string Reasoning { get; set; }
            public string Suggestion { get; set; }
        }

        public class FeatAnalysisReport
        {
            public DateTime Timestamp { get; set; } = DateTime.UtcNow;
            public float Mean { get; set; }
            public float StdDev { get; set; }
            public List<FeatAnalysisResult> FlaggedFeats { get; set; } = new List<FeatAnalysisResult>();
            public Dictionary<string, float> AllScores { get; set; } = new Dictionary<string, float>();
        }

        private readonly FeatPowerCalculator _calculator;
        private readonly float _stddevThreshold;
        private readonly float? _minScore;
        private readonly float? _maxScore;

        public FeatAnalysisEngine(FeatPowerCalculator calculator, float stddevThreshold = 2.0f, float? minScore = null, float? maxScore = null)
        {
            _calculator = calculator;
            _stddevThreshold = stddevThreshold;
            _minScore = minScore;
            _maxScore = maxScore;
        }

        public FeatAnalysisReport Analyze(IEnumerable<Feat> feats)
        {
            var scores = _calculator.CalculateAllScores(feats);
            var values = scores.Values.ToList();
            float mean = values.Average();
            float stddev = (float)Math.Sqrt(values.Average(v => Math.Pow(v - mean, 2)));
            var flagged = new List<FeatAnalysisResult>();
            foreach (var kvp in scores)
            {
                var featId = kvp.Key;
                var score = kvp.Value;
                var imbalance = CategorizeImbalance(score, mean, stddev);
                if (imbalance != null)
                {
                    var feat = feats.FirstOrDefault(f => f.Id == featId);
                    flagged.Add(new FeatAnalysisResult
                    {
                        FeatId = featId,
                        FeatName = feat?.Name,
                        PowerScore = score,
                        ImbalanceType = imbalance,
                        Reasoning = GenerateReasoning(feat, score, mean, stddev, imbalance),
                        Suggestion = GenerateSuggestion(feat, imbalance)
                    });
                }
            }
            return new FeatAnalysisReport
            {
                Mean = mean,
                StdDev = stddev,
                FlaggedFeats = flagged,
                AllScores = scores
            };
        }

        private string CategorizeImbalance(float score, float mean, float stddev)
        {
            if (_minScore.HasValue && score < _minScore.Value) return "Underpowered";
            if (_maxScore.HasValue && score > _maxScore.Value) return "Overpowered";
            if (score > mean + _stddevThreshold * stddev) return "Overpowered";
            if (score < mean - _stddevThreshold * stddev) return "Underpowered";
            // Optionally, add more logic for situational
            return null;
        }

        private string GenerateReasoning(Feat feat, float score, float mean, float stddev, string imbalance)
        {
            return $"Score: {score:F2}, Mean: {mean:F2}, StdDev: {stddev:F2}. This feat is flagged as {imbalance} because its score is an outlier.";
        }

        private string GenerateSuggestion(Feat feat, string imbalance)
        {
            if (imbalance == "Overpowered")
                return "Consider increasing resource cost, reducing effect value, or adding prerequisites.";
            if (imbalance == "Underpowered")
                return "Consider decreasing resource cost, increasing effect value, or removing prerequisites.";
            return "Review feat for situational balance issues.";
        }

        public string GenerateJsonReport(FeatAnalysisReport report)
        {
            return JsonConvert.SerializeObject(report, Formatting.Indented);
        }
    }
} 