using System;
using System.Collections.Generic;

namespace VisualDM.Systems
{
    /// <summary>
    /// Represents the trust relationship between an NPC and a player.
    /// </summary>
    public class NPCTrust
    {
        public string NpcId { get; set; }
        public string PlayerId { get; set; }
        /// <summary>
        /// Trust value, typically in range [0, 100].
        /// </summary>
        public float TrustValue { get; private set; } = 50f;
        /// <summary>
        /// History of failed social checks (timestamps and reasons).
        /// </summary>
        public List<FailedCheckRecord> FailedChecks { get; private set; } = new List<FailedCheckRecord>();

        public NPCTrust(string npcId, string playerId, float initialTrust = 50f)
        {
            NpcId = npcId;
            PlayerId = playerId;
            TrustValue = initialTrust;
        }

        /// <summary>
        /// Adjusts trust value by a delta, clamped to [0, 100].
        /// </summary>
        public void AdjustTrust(float delta)
        {
            TrustValue = Math.Clamp(TrustValue + delta, 0f, 100f);
        }

        /// <summary>
        /// Records a failed social check and applies trust penalty.
        /// </summary>
        public void RecordFailedCheck(SocialCheck check, float penalty, string reason)
        {
            FailedChecks.Add(new FailedCheckRecord
            {
                Timestamp = DateTime.UtcNow,
                Check = check,
                Penalty = penalty,
                Reason = reason
            });
            AdjustTrust(-penalty);
        }
    }

    /// <summary>
    /// Record of a failed social check for trust/memory purposes.
    /// </summary>
    public class FailedCheckRecord
    {
        public DateTime Timestamp { get; set; }
        public SocialCheck Check { get; set; }
        public float Penalty { get; set; }
        public string Reason { get; set; }
    }
}