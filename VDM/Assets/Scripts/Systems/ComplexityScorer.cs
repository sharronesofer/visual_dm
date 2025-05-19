using System;
using System.Collections.Generic;

namespace VisualDM.AI
{
    public enum QuestDifficulty { Easy, Medium, Hard }

    public class ComplexityScorer
    {
        public int ScoreQuest(QuestData quest)
        {
            // Example scoring: steps + branches + narrative depth
            int score = 0;
            score += quest.Steps.Count;
            score += quest.Branches;
            score += quest.NarrativeDepth * 2;
            return score;
        }

        public QuestDifficulty MapScoreToDifficulty(int score)
        {
            if (score < 5) return QuestDifficulty.Easy;
            if (score < 10) return QuestDifficulty.Medium;
            return QuestDifficulty.Hard;
        }

        // Calibration method for tuning thresholds
        public void Calibrate(List<QuestData> sampleQuests)
        {
            // Analyze sample quests to adjust thresholds (stub)
        }
    }

    // Example quest data structure for scoring
    public class QuestData
    {
        public List<string> Steps { get; set; } = new List<string>();
        public int Branches { get; set; }
        public int NarrativeDepth { get; set; }
    }
} 