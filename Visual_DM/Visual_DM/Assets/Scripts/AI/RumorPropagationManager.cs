using System.Collections.Generic;
using UnityEngine;
using VisualDM.NPC;
using VisualDM.Dialogue;
using VisualDM.Systems.Rivalry;

namespace Visual_DM.AI
{
    /// <summary>
    /// Manages rumor decay and propagation between NPCs.
    /// </summary>
    public class RumorPropagationManager : MonoBehaviour
    {
        public RumorDecayConfig decayConfig;
        public float updateInterval = 5.0f; // seconds between decay updates

        // Example: Dictionary<NPCId, List<RumorRecord>>
        private Dictionary<string, List<RumorRecord>> npcRumors = new Dictionary<string, List<RumorRecord>>();

        private void Start()
        {
            InvokeRepeating(nameof(UpdateRumorDecay), updateInterval, updateInterval);
        }

        /// <summary>
        /// Adds a rumor to an NPC's memory.
        /// </summary>
        public void AddRumorToNpc(string npcId, RumorRecord rumor, string npcPersonality)
        {
            // Add to local rumor memory
            if (!npcRumors.ContainsKey(npcId))
                npcRumors[npcId] = new List<RumorRecord>();
            npcRumors[npcId].Add(rumor);

            // Integration: Update NPC memory
            var npcObj = FindNpcById(npcId);
            if (npcObj != null)
            {
                string rumorId = GenerateRumorId(rumor);
                var memory = new RumorMemory { RumorId = rumorId, MemoryStrength = 1.0f, IsForgotten = false };
                npcObj.LearnRumor(rumorId, memory);
                Debug.Log($"[RumorPropagation] {npcId} learned rumor: {rumor.Rumor}");

                // Integration: Inject rumor into dialogue context
                DialogueContextManager.Instance.AddLine(npcId, $"Rumor: {rumor.Rumor}");
                Debug.Log($"[RumorPropagation] Injected rumor into {npcId}'s dialogue context.");

                // Integration: Adjust relationship if rumor is negative
                if (rumor.Rumor.ToLower().Contains("betray") || rumor.Rumor.ToLower().Contains("crime") || rumor.TruthValue < 0.5f)
                {
                    // Example: Decrease relationship with target NPC if rumor is about them
                    if (!string.IsNullOrEmpty(rumor.OriginalEvent?.TargetNpcId))
                    {
                        npcObj.RegisterRelationshipEvent(rumor.OriginalEvent.TargetNpcId, -10f);
                        Debug.Log($"[RumorPropagation] Adjusted relationship: {npcId} → {rumor.OriginalEvent.TargetNpcId}");
                        // Optionally, add a grudge
                        GrudgePointManager.Instance.AddGrudgePoints(npcId, rumor.OriginalEvent.TargetNpcId, 5, "Rumor spread", "Gossip");
                    }
                }
            }
        }

        /// <summary>
        /// Updates rumor truth values for all NPCs, applying decay based on config and traits.
        /// </summary>
        private void UpdateRumorDecay()
        {
            foreach (var kvp in npcRumors)
            {
                string npcId = kvp.Key;
                List<RumorRecord> rumors = kvp.Value;
                string personality = GetNpcPersonality(npcId); // Implement as needed
                float modifier = GetPersonalityModifier(personality);
                foreach (var rumor in rumors)
                {
                    // Decay by time
                    rumor.TruthValue -= decayConfig.DecayPerHour * updateInterval / 3600f * modifier;
                    // Decay by retellings (if tracked)
                    // rumor.TruthValue -= decayConfig.DecayPerRetelling * rumor.RetellingCount * modifier;
                    rumor.TruthValue = Mathf.Clamp01(rumor.TruthValue);
                }
            }
        }

        /// <summary>
        /// Propagates a rumor from one NPC to another, applying distortion and decay.
        /// </summary>
        public void PropagateRumor(string fromNpcId, string toNpcId, RumorRecord rumor, string toNpcPersonality)
        {
            // Optionally: apply additional distortion or decay on propagation
            var newRumor = new RumorRecord(
                rumor.OriginalEvent,
                rumor.Rumor, // Optionally: re-transform with more distortion
                rumor.TruthValue - decayConfig.DecayPerRetelling * GetPersonalityModifier(toNpcPersonality)
            );
            AddRumorToNpc(toNpcId, newRumor, toNpcPersonality);
        }

        private float GetPersonalityModifier(string personality)
        {
            switch (personality)
            {
                case "gossip": return decayConfig.GossipModifier;
                case "truth-teller": return decayConfig.TruthTellerModifier;
                default: return decayConfig.NeutralModifier;
            }
        }

        private string GetNpcPersonality(string npcId)
        {
            // TODO: Integrate with NPC data system
            return "neutral";
        }

        // Helper to find NPC by ID (runtime only)
        private NPCBase FindNpcById(string npcId)
        {
            foreach (var npc in GameObject.FindObjectsOfType<NPCBase>())
            {
                if (npc.NPCName == npcId)
                    return npc;
            }
            return null;
        }

        // Helper to generate a unique rumor ID (hash of content)
        private string GenerateRumorId(RumorRecord rumor)
        {
            return rumor.Rumor.GetHashCode().ToString();
        }

        // Optionally: expose rumor data for UI/debugging
        public IReadOnlyDictionary<string, List<RumorRecord>> NpcRumors => npcRumors;

        /// <summary>
        /// Handles a player attempting to spread a rumor to an NPC, using a social check.
        /// </summary>
        public async System.Threading.Tasks.Task<bool> TrySpreadRumorFromPlayerAsync(
            string playerId,
            string npcId,
            RumorRecord rumor,
            string dialogue,
            string npcPersonality,
            string relationship,
            string history,
            VisualDM.Systems.SocialSkillType skillType,
            VisualDM.Systems.SocialCheckSystem socialCheckSystem)
        {
            var npcObj = FindNpcById(npcId);
            if (npcObj == null) return false;
            var trust = npcObj.GetOrCreateTrust(playerId);
            var result = await socialCheckSystem.PerformSocialCheckAsync(
                playerId, npcId, dialogue, npcPersonality, relationship, history, skillType, trust);
            if (result.Success)
            {
                AddRumorToNpc(npcId, rumor, npcPersonality);
                Debug.Log($"[RumorPropagation] Player {playerId} successfully spread rumor to {npcId}.");
                return true;
            }
            else
            {
                Debug.Log($"[RumorPropagation] Player {playerId} failed to spread rumor to {npcId}. Trust reduced.");
                // Trust penalty is already handled in SocialCheckSystem
                return false;
            }
        }
    }
}