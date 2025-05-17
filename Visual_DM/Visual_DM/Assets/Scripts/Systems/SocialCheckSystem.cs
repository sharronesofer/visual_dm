using System;
using System.Threading.Tasks;
using UnityEngine;
using VisualDM.Network;

namespace VisualDM.Systems
{
    /// <summary>
    /// Orchestrates social skill checks between player and NPCs.
    /// </summary>
    public class SocialCheckSystem
    {
        private System.Random _rng = new System.Random();

        /// <summary>
        /// Performs a social check, including GPT analysis and skill roll.
        /// </summary>
        public async Task<SocialCheckResult> PerformSocialCheckAsync(string playerId, string npcId, string dialogue, string npcPersonality, string relationship, string history, SocialSkillType skillType, NPCTrust trust)
        {
            // 1. Analyze info type using GPT
            string gptResultJson = await GPTSocialCheckClient.AnalyzeAsync(dialogue, npcPersonality, relationship, history);
            var gptResult = JsonUtility.FromJson<SocialCheckAnalysisResult>(gptResultJson);

            // 2. Calculate base difficulty
            float baseDifficulty = CalculateBaseDifficulty(skillType, gptResult.info_type, trust.TrustValue, npcPersonality, relationship, history);

            // 3. Roll for success
            float roll = (float)_rng.NextDouble() * 100f;
            bool success = roll >= baseDifficulty;

            // 4. Update trust if failed
            if (!success)
            {
                float penalty = CalculateTrustPenalty(baseDifficulty, roll, gptResult.info_type, npcPersonality);
                trust.RecordFailedCheck(new SocialCheck
                {
                    PlayerId = playerId,
                    NpcId = npcId,
                    SkillType = skillType,
                    InfoType = gptResult.info_type,
                    BaseDifficulty = baseDifficulty,
                    Modifier = 0f,
                    Timestamp = DateTime.UtcNow,
                }, penalty, $"Failed {skillType} check: {gptResult.info_type}");
            }

            // 5. Return result
            return new SocialCheckResult
            {
                Success = success,
                Roll = roll,
                Difficulty = baseDifficulty,
                SkillType = skillType,
                InfoType = gptResult.info_type,
                Notes = gptResult.explanation
            };
        }

        private float CalculateBaseDifficulty(SocialSkillType skillType, string infoType, float trustValue, string npcPersonality, string relationship, string history)
        {
            // Example: Outlandish claims, low trust, and negative relationship increase difficulty
            float difficulty = 40f;
            if (infoType == "deception" || infoType == "threat") difficulty += 20f;
            if (trustValue < 30f) difficulty += 15f;
            if (relationship == "hostile") difficulty += 10f;
            // TODO: Use npcPersonality and history for more nuance
            return Mathf.Clamp(difficulty, 0f, 100f);
        }

        private float CalculateTrustPenalty(float difficulty, float roll, string infoType, string npcPersonality)
        {
            // Example: More severe failures and certain info types penalize trust more
            float basePenalty = (difficulty - roll) * 0.1f;
            if (infoType == "deception") basePenalty += 5f;
            if (npcPersonality.Contains("suspicious")) basePenalty += 3f;
            return Mathf.Clamp(basePenalty, 1f, 20f);
        }

        [Serializable]
        private class SocialCheckAnalysisResult
        {
            public string info_type;
            public bool benefit;
            public string explanation;
        }
    }
}