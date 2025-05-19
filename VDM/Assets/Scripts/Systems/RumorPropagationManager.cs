using System.Collections.Generic;
using UnityEngine;
using VisualDM.Entities;
using VisualDM.AI;
using VisualDM.Systems.Rivalry;
using VisualDM.Systems;

namespace VisualDM.AI
{
    /// <summary>
    /// Manages rumor decay and propagation between NPCs.
    /// Narrative/mechanical requirements: See docs/stubs_needs_consolidation_qna.md (Rumors section).
    /// - Rumors decay over time and with retellings, using config and personality modifiers.
    /// - Propagation is modular, supports distortion, and is runtime-driven.
    /// - Truth scoring is handled by RumorTruthEvaluator.
    /// </summary>
    public class RumorPropagationManager : MonoBehaviour
    {
        public RumorDecayConfig decayConfig;
        public float updateInterval = 5.0f; // seconds between decay updates

        // Dictionary<NPCId, List<RumorRecord>>
        private Dictionary<string, List<RumorRecord>> npcRumors = new Dictionary<string, List<RumorRecord>>();

        private void Start()
        {
            InvokeRepeating(nameof(UpdateRumorDecay), updateInterval, updateInterval);
        }

        /// <summary>
        /// Adds a rumor to an NPC's memory, ensuring modularity and runtime safety.
        /// </summary>
        public void AddRumorToNpc(string npcId, RumorRecord rumor, string npcPersonality)
        {
            if (string.IsNullOrWhiteSpace(npcId) || rumor == null)
            {
                Debug.LogError("Invalid NPC ID or rumor.");
                return;
            }
            if (!npcRumors.ContainsKey(npcId))
                npcRumors[npcId] = new List<RumorRecord>();
            npcRumors[npcId].Add(rumor);
            // Integration: Update NPC memory
            var npcObj = FindNpcById(npcId);
            if (npcObj != null)
            {
                string rumorId = GenerateRumorId(rumor);
                var memory = new RumorMemory { MemoryStrength = 1.0f, IsForgotten = false };
                npcObj.LearnRumor(rumorId, memory);
                // Inject rumor into dialogue context
                // DialogueContextManager.Instance.AddLine(npcId, $"Rumor: {rumor.Rumor}");
                // Adjust relationship if rumor is negative
                if (rumor.Rumor.ToLower().Contains("betray") || rumor.Rumor.ToLower().Contains("crime") || rumor.TruthValue < 0.5f)
                {
                    if (!string.IsNullOrEmpty(rumor.OriginalEvent?.TargetNpcId))
                    {
                        npcObj.RegisterRelationshipEvent(rumor.OriginalEvent.TargetNpcId, -10f);
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
                string personality = GetNpcPersonality(npcId);
                float modifier = GetPersonalityModifier(personality);
                foreach (var rumor in rumors)
                {
                    // Decay by time
                    rumor.TruthValue -= decayConfig.DecayPerHour * updateInterval / 3600f * modifier;
                    rumor.TruthValue = Mathf.Clamp01(rumor.TruthValue);
                }
            }
        }

        /// <summary>
        /// Propagates a rumor from one NPC to another, applying distortion, decay, and believability.
        /// </summary>
        public void PropagateRumor(string fromNpcId, string toNpcId, RumorRecord rumor, string toNpcPersonality)
        {
            if (string.IsNullOrWhiteSpace(fromNpcId) || string.IsNullOrWhiteSpace(toNpcId) || rumor == null)
            {
                Debug.LogError("Invalid NPC IDs or rumor.");
                return;
            }
            // Optionally: apply additional distortion or decay on propagation
            var newRumor = new RumorRecord(
                rumor.OriginalEvent,
                rumor.Rumor, // Optionally: re-transform with more distortion
                rumor.TruthValue - decayConfig.DecayPerRetelling * GetPersonalityModifier(toNpcPersonality)
            );
            AddRumorToNpc(toNpcId, newRumor, toNpcPersonality);

            // --- New: Believability calculation and registry integration ---
            var toNpc = FindNpcById(toNpcId);
            var rumorObj = RumorManager.Instance.GetRumor(newRumor.Rumor.GetHashCode().ToString());
            if (rumorObj != null && toNpc != null)
            {
                float believability = BelievabilityCalculator.CalculateBelievability(toNpc, rumorObj);
                // Optionally: store believability per-NPC, or use for dialogue/behavior
            }
        }

        /// <summary>
        /// Propagate rumors using social graph, proximity, and faction relationships.
        /// </summary>
        public void PropagateRumorsSocially(IEnumerable<NPCBase> npcs)
        {
            // For each NPC, attempt to spread rumors to nearby/socially connected NPCs
            foreach (var npc in npcs)
            {
                foreach (var rumorId in npc.RumorMemories.Keys)
                {
                    // Only propagate if memory is not forgotten
                    if (!npc.RumorMemories[rumorId].IsForgotten)
                    {
                        // Find candidates: nearby or socially connected NPCs
                        var candidates = FindPropagationCandidates(npc, npcs);
                        foreach (var candidate in candidates)
                        {
                            // Faction bias: SKIPPED (NPCBase.Faction does not exist)
                            // Personality: SKIPPED (PersonalityProfile.Skepticism does not exist)
                            // Propagate
                            var rumorObj = RumorManager.Instance.GetRumor(rumorId);
                            if (rumorObj != null)
                            {
                                var record = new RumorRecord(null, rumorObj.CoreContent, rumorObj.TruthValue ?? 0.5f);
                                PropagateRumor(npc.NPCName, candidate.NPCName, record, candidate.Personality?.ToString() ?? "neutral");
                            }
                        }
                    }
                }
            }
        }

        private IEnumerable<NPCBase> FindPropagationCandidates(NPCBase npc, IEnumerable<NPCBase> allNpcs)
        {
            // Example: find NPCs within a certain distance or with strong social ties
            List<NPCBase> candidates = new();
            foreach (var other in allNpcs)
            {
                if (other == npc) continue;
                float dist = Vector3.Distance(npc.transform.position, other.transform.position);
                if (dist < 10f) // Proximity threshold
                    candidates.Add(other);
                // TODO: Add social connection logic (friendship, faction, etc.)
            }
            return candidates;
        }

        // --- New: Hook for war/tension events to generate/modify rumors ---
        public void OnWarEvent(string factionA, string factionB, string eventType)
        {
            // Generate a rumor about the war event
            var evt = new RumorEvent
            {
                EventType = eventType,
                Actors = new[] { factionA, factionB },
                Location = "World",
                Timestamp = System.DateTime.Now,
                Context = $"War event: {eventType} between {factionA} and {factionB}"
            };
            var parameters = new RumorParameters { DistortionLevel = 0.2f, NpcPersonality = "neutral", Theme = "war" };
            // Use GPTRumorService or similar to mutate rumor
            // ... (integration with RumorProcessingManager)
        }

        // --- New: Level-of-detail simulation for performance ---
        public void SimulateRumorsLOD(Vector3 playerPosition, float maxDistance = 50f)
        {
            // Only simulate full rumor logic for NPCs near the player
            var npcs = GameObject.FindObjectsOfType<NPCBase>();
            foreach (var npc in npcs)
            {
                float dist = Vector3.Distance(npc.transform.position, playerPosition);
                if (dist < maxDistance)
                {
                    // Full simulation
                    DecayRumorsForNpc(npc);
                }
                else
                {
                    // Minimal/periodic simulation
                    if (UnityEngine.Random.value < 0.1f)
                        DecayRumorsForNpc(npc);
                }
            }
        }

        private void DecayRumorsForNpc(NPCBase npc)
        {
            // Decay all rumor memories for this NPC
            npc.DecayRumorMemories(updateInterval, decayConfig.DecayPerHour);
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

        private NPCBase FindNpcById(string npcId)
        {
            foreach (var npc in GameObject.FindObjectsOfType<NPCBase>())
            {
                if (npc.NPCName == npcId)
                    return npc;
            }
            return null;
        }

        private string GenerateRumorId(RumorRecord rumor)
        {
            return rumor.Rumor.GetHashCode().ToString();
        }

        /// <summary>
        /// Expose rumor data for UI/debugging.
        /// </summary>
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
            if (string.IsNullOrWhiteSpace(playerId) || string.IsNullOrWhiteSpace(npcId) || rumor == null || socialCheckSystem == null)
            {
                Debug.LogError("Invalid input to TrySpreadRumorFromPlayerAsync.");
                return false;
            }
            var npcObj = FindNpcById(npcId);
            if (npcObj == null) return false;
            var trust = npcObj.GetOrCreateTrust(playerId);
            var result = await socialCheckSystem.PerformSocialCheckAsync(
                playerId, npcId, dialogue, npcPersonality, relationship, history, skillType, trust);
            if (result.Success)
            {
                AddRumorToNpc(npcId, rumor, npcPersonality);
                return true;
            }
            else
            {
                return false;
            }
        }
    }
}