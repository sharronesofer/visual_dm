using System;
using System.Collections.Generic;
using System.Linq;

namespace VDM.NPC
{
    /// <summary>
    /// Handles NPC responses to rumors, including priority queuing, behavior triggers, and verification seeking.
    /// </summary>
    public class RumorResponseHandler
    {
        private class QueuedRumor
        {
            public RumorData Rumor;
            public float Believability;
            public float Priority;
        }

        private List<QueuedRumor> rumorQueue = new();
        private int npcId;

        public RumorResponseHandler(int npcId)
        {
            this.npcId = npcId;
        }

        /// <summary>
        /// Process a new rumor for this NPC.
        /// </summary>
        public void ReceiveRumor(RumorData rumor)
        {
            float believability = rumor.BelievabilityScores.ContainsKey(npcId) ? rumor.BelievabilityScores[npcId] : 0.5f;
            float priority = CalculatePriority(rumor, believability);
            rumorQueue.Add(new QueuedRumor { Rumor = rumor, Believability = believability, Priority = priority });
            rumorQueue = rumorQueue.OrderByDescending(r => r.Priority).ToList();
            TryTriggerBehavior(rumor, believability);
        }

        /// <summary>
        /// Calculate priority based on rumor type and believability.
        /// </summary>
        private float CalculatePriority(RumorData rumor, float believability)
        {
            float basePriority = believability;
            if (rumor.Category == RumorCategory.Danger) basePriority += 0.5f;
            if (rumor.Category == RumorCategory.Opportunity) basePriority += 0.2f;
            // TODO: Add motif/personality weighting
            return basePriority;
        }

        /// <summary>
        /// Attempt to trigger a behavior based on rumor content and believability.
        /// </summary>
        private void TryTriggerBehavior(RumorData rumor, float believability)
        {
            // Example: Flee if danger and believability > 0.7
            if (rumor.Category == RumorCategory.Danger && believability > 0.7f)
            {
                // TODO: Call NPC flee behavior
                // e.g., npc.FleeFrom(rumor.SourceNpcId);
            }
            // Example: Investigate if mystery and believability > 0.5
            if (rumor.Category == RumorCategory.Mystery && believability > 0.5f)
            {
                // TODO: Call NPC investigate behavior
            }
            // TODO: Integrate with motif/personality system
        }

        /// <summary>
        /// NPC seeks verification for important rumors.
        /// </summary>
        public void SeekVerification(RumorData rumor)
        {
            // TODO: Ask other NPCs or check world state
        }

        /// <summary>
        /// Get the highest-priority rumor in the queue.
        /// </summary>
        public RumorData GetTopRumor()
        {
            return rumorQueue.Count > 0 ? rumorQueue[0].Rumor : null;
        }
    }
} 