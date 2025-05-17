using System;
using UnityEngine;
using VisualDM.Utilities;
using VisualDM.Systems.EventSystem;
using System.Collections.Generic;

namespace VisualDM.NPC
{
    public class NPCBase : MonoBehaviour
    {
        public string NPCName;
        public PersonalityProfile Personality { get; private set; }
        public NPCMood Mood { get; private set; }
        private NPCBehaviorModifier _behaviorModifier;
        public RelationshipStateMachine RelationshipStateMachine { get; private set; }

        // Rumor memory: maps rumor ID/hash to this NPC's memory of the rumor
        public Dictionary<string, VisualDM.AI.RumorMemory> RumorMemories { get; private set; } = new();

        // Trust relationships: maps player ID to NPCTrust object
        private Dictionary<string, VisualDM.Systems.NPCTrust> _trustRelationships = new();

        // --- Nemesis/Rival System Extensions ---
        public Dictionary<string, VisualDM.NPC.RivalProfile> RivalProfiles { get; private set; } = new();
        public Dictionary<string, VisualDM.NPC.NemesisProfile> NemesisProfiles { get; private set; } = new();
        public Dictionary<string, VisualDM.Systems.Rivalry.RivalRelationship> RivalRelationships { get; private set; } = new();
        public Dictionary<string, VisualDM.Systems.Rivalry.NemesisRelationship> NemesisRelationships { get; private set; } = new();

        // Initialization with random or template-based personality
        public void Initialize(INPCTemplate template = null, System.Random rng = null)
        {
            if (template != null)
                Personality = NPCTraitGenerator.GenerateFromTemplate(template, 0.1f, rng);
            else
                Personality = NPCTraitGenerator.GenerateRandomProfile(rng);
            Mood = new NPCMood();
            _behaviorModifier = new NPCBehaviorModifier(Personality, Mood);
            RelationshipStateMachine = new RelationshipStateMachine(NPCName);
        }

        // Expose behavior weights
        public float GetAggressionWeight() => _behaviorModifier.GetAggressionWeight();
        public float GetSociabilityWeight() => _behaviorModifier.GetSociabilityWeight();
        public float GetCuriosityWeight() => _behaviorModifier.GetCuriosityWeight();
        // Add more as needed

        // Event-driven mood change
        public void OnEventAffectingMood(MoodState mood, float intensity = 1f)
        {
            Mood.ApplyMood(mood, intensity);
        }

        // Call this in Update or via a manager to decay mood
        public void UpdateMood(float deltaTime)
        {
            Mood.DecayMood(deltaTime);
        }

        // Register a relationship-impacting event (e.g., combat, quest, dialogue)
        public void RegisterRelationshipEvent(string targetId, float eventScore)
        {
            try
            {
                RelationshipStateMachine?.RegisterEvent(targetId, eventScore);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[NPCBase] Error registering relationship event for {NPCName} → {targetId}: {ex}");
            }
        }

        // Decay all relationship intensities (call periodically, e.g., in Update or via manager)
        public void DecayRelationships(float deltaMinutes)
        {
            RelationshipStateMachine?.DecayAll(deltaMinutes);
        }

        // Persistence hooks
        public Dictionary<string, object> SaveRelationshipState()
        {
            return RelationshipStateMachine?.SaveState();
        }
        public void LoadRelationshipState(Dictionary<string, object> data)
        {
            RelationshipStateMachine?.LoadState(data);
        }

        // For debugging
        public override string ToString()
        {
            return $"NPC: {NPCName}, Personality: {Personality.ToDictionary()}, Mood: {Mood}";
        }

        // Triggers a GPT-driven dialogue exchange with this NPC
        public async void TriggerDialogue(string playerPrompt)
        {
            // Show loading in UI
            VisualDM.UI.UIManager.Instance.ShowDialogue($"Talking to {NPCName}...", loading: true);
            // Add player prompt to context
            VisualDM.Dialogue.DialogueContextManager.Instance.AddLine(NPCName, $"Player: {playerPrompt}");
            // Gather context
            var context = VisualDM.Dialogue.DialogueContextManager.Instance.GetContext(NPCName);
            // Find DialogueGenerationService
            var dialogueService = GameObject.FindObjectOfType<VisualDM.Dialogue.DialogueGenerationService>();
            if (dialogueService == null)
            {
                VisualDM.UI.UIManager.Instance.ShowDialogue("[Error: Dialogue system unavailable]", error: "DialogueGenerationService not found!");
                Debug.LogError("DialogueGenerationService not found!");
                return;
            }
            // Call GPT
            var response = await dialogueService.GenerateDialogueAsync(playerPrompt, context);
            if (!string.IsNullOrEmpty(response.error))
            {
                VisualDM.UI.UIManager.Instance.ShowDialogue("[Error: Could not fetch dialogue]", error: response.error);
                Debug.LogError($"Dialogue error: {response.error}");
                return;
            }
            // Add NPC response to context
            VisualDM.Dialogue.DialogueContextManager.Instance.AddLine(NPCName, $"{NPCName}: {response.text}");
            // Show response in UI
            VisualDM.UI.UIManager.Instance.ShowDialogue(response.text);
        }

        // Learn a new rumor (or reinforce if already known)
        public void LearnRumor(string rumorId, VisualDM.AI.RumorMemory memory)
        {
            if (RumorMemories.ContainsKey(rumorId))
            {
                // Reinforce memory if already known
                ReinforceRumor(rumorId);
            }
            else
            {
                RumorMemories[rumorId] = memory;
            }
        }

        // Reinforce a rumor (e.g., when discussed again)
        public void ReinforceRumor(string rumorId, float reinforcementAmount = 1.0f)
        {
            if (RumorMemories.TryGetValue(rumorId, out var memory))
            {
                memory.MemoryStrength += reinforcementAmount;
                memory.IsForgotten = false;
            }
        }

        // Calculate memory retention rate based on personality traits (higher = slower decay)
        public float GetMemoryRetentionRate()
        {
            // Example: Intelligence and Discipline increase retention, Curiosity decreases it
            float baseRate = 1.0f;
            if (Personality != null)
            {
                baseRate += Personality.Intelligence * 0.5f;
                baseRate += Personality.Discipline * 0.3f;
                baseRate -= Personality.Curiosity * 0.2f;
            }
            return Mathf.Clamp(baseRate, 0.5f, 2.0f); // Clamp to reasonable range
        }

        // Decay all rumor memories (to be called periodically)
        public void DecayRumorMemories(float deltaTime, float baseDecayRate = 0.01f)
        {
            foreach (var kvp in RumorMemories)
            {
                var rumorId = kvp.Key;
                var memory = kvp.Value;
                // Try to get rumor importance (if available)
                float importance = 0.5f;
                VisualDM.AI.Rumor rumor = null;
                // If you have a global rumor registry, fetch the rumor object here
                // For now, assume importance is 0.5 unless rumor is available
                // e.g., if (RumorRegistry.TryGet(rumorId, out rumor)) importance = rumor.Importance;
                if (rumor != null) importance = rumor.Importance;
                float retention = GetMemoryRetentionRate();
                float decay = baseDecayRate * deltaTime * (1.0f - importance) / retention;
                memory.MemoryStrength -= decay;
                if (memory.MemoryStrength <= 0)
                {
                    memory.MemoryStrength = 0;
                    memory.IsForgotten = true;
                }
            }
        }

        // Forget a rumor explicitly
        public void ForgetRumor(string rumorId)
        {
            if (RumorMemories.TryGetValue(rumorId, out var memory))
            {
                memory.IsForgotten = true;
                memory.MemoryStrength = 0;
            }
        }

        // Query if this NPC knows a rumor
        public bool KnowsRumor(string rumorId)
        {
            return RumorMemories.TryGetValue(rumorId, out var memory) && !memory.IsForgotten;
        }

        // Determines if this NPC will share a rumor with another NPC
        public bool CanShareRumorWith(string rumorId, NPCBase otherNpc, float minRelationship = 0.2f)
        {
            if (!KnowsRumor(rumorId) || otherNpc == null || otherNpc == this)
                return false;
            // Example: Use relationship strength and rumor importance
            float relationship = 0.5f;
            if (RelationshipStateMachine != null && otherNpc.NPCName != null)
                relationship = RelationshipStateMachine.GetRelationshipStrength(otherNpc.NPCName);
            float importance = 0.5f;
            VisualDM.AI.Rumor rumor = null;
            // If you have a global rumor registry, fetch the rumor object here
            // e.g., if (RumorRegistry.TryGet(rumorId, out rumor)) importance = rumor.Importance;
            if (rumor != null) importance = rumor.Importance;
            // Probability: higher for strong relationships and important rumors
            float probability = Mathf.Clamp01(relationship * 0.7f + importance * 0.5f);
            return relationship >= minRelationship && UnityEngine.Random.value < probability;
        }

        // Async version: Share a rumor with another NPC, using GPT transformation if provided
        public async System.Threading.Tasks.Task ShareRumorWithAsync(string rumorId, NPCBase otherNpc, VisualDM.AI.IGPTRumorService gptRumorService = null, float initialMemoryStrength = 1.0f)
        {
            if (otherNpc == null || otherNpc == this) return;
            if (!KnowsRumor(rumorId)) return;
            var myMemory = RumorMemories[rumorId];
            string newContent = null;
            VisualDM.AI.RumorParameters parameters = new VisualDM.AI.RumorParameters
            {
                DistortionLevel = 0.2f, // Example: could be based on traits or context
                NpcPersonality = Personality != null ? Personality.ToDictionary().ToString() : "",
                Theme = "general",
                RetellingCount = myMemory.Transformations.Count + 1,
                TimeSinceEvent = (float)(DateTime.UtcNow - myMemory.LearnedTimestamp).TotalMinutes
            };
            if (gptRumorService != null)
            {
                // Use GPT to transform the rumor content
                newContent = await gptRumorService.TransformRumorAsync(myMemory.Transformations.Count > 0 ? myMemory.Transformations[^1].NewContent : "", parameters);
            }
            else
            {
                // No transformation, use last known content
                newContent = myMemory.Transformations.Count > 0 ? myMemory.Transformations[^1].NewContent : "";
            }
            var newTransformation = new VisualDM.AI.RumorTransformation
            {
                NpcId = otherNpc.NPCName,
                Timestamp = DateTime.UtcNow,
                TransformationType = gptRumorService != null ? "gpt_transform" : "retell",
                NewContent = newContent,
                DistortionLevel = parameters.DistortionLevel
            };
            if (!otherNpc.RumorMemories.ContainsKey(rumorId))
            {
                // Recipient learns the rumor
                var newMemory = new VisualDM.AI.RumorMemory
                {
                    LearnedTimestamp = DateTime.UtcNow,
                    MemoryStrength = initialMemoryStrength,
                    IsForgotten = false,
                    Transformations = new List<VisualDM.AI.RumorTransformation> { newTransformation }
                };
                otherNpc.RumorMemories[rumorId] = newMemory;
            }
            else
            {
                var theirMemory = otherNpc.RumorMemories[rumorId];
                if (theirMemory.IsForgotten)
                {
                    // Re-remember the rumor
                    theirMemory.IsForgotten = false;
                    theirMemory.MemoryStrength = initialMemoryStrength;
                }
                // Add transformation
                theirMemory.Transformations.Add(newTransformation);
            }
            // Optionally, update global rumor transformation history if available
        }

        // PERFORMANCE NOTE:
        // - RumorMemories is a Dictionary for O(1) lookup by rumor ID.
        // - For large populations, batch decay and propagation in a manager system (not per-NPC Update).
        // - For serialization, only store rumor IDs and essential memory fields (avoid serializing full rumor objects).

        // Removes forgotten rumors from memory to save space
        public void ClearForgottenRumors()
        {
            var toRemove = new List<string>();
            foreach (var kvp in RumorMemories)
            {
                if (kvp.Value.IsForgotten)
                    toRemove.Add(kvp.Key);
            }
            foreach (var id in toRemove)
                RumorMemories.Remove(id);
        }

        /// <summary>
        /// Get or create the trust relationship with a player.
        /// </summary>
        public VisualDM.Systems.NPCTrust GetOrCreateTrust(string playerId)
        {
            if (!_trustRelationships.TryGetValue(playerId, out var trust))
            {
                trust = new VisualDM.Systems.NPCTrust(NPCName, playerId);
                _trustRelationships[playerId] = trust;
            }
            return trust;
        }

        // Example usage in dialogue or rumor systems:
        // var trust = npc.GetOrCreateTrust(playerId);
        // var result = await socialCheckSystem.PerformSocialCheckAsync(playerId, npc.NPCName, dialogue, ... , trust);
        // if (!result.Success) { /* trust.FailedChecks contains memory of failed checks */ }

        private void OnEnable()
        {
            EventBus.Instance.Subscribe<RelationshipEventTrigger>(OnRelationshipEventTrigger);
        }
        private void OnDisable()
        {
            EventBus.Instance.Unsubscribe<RelationshipEventTrigger>(OnRelationshipEventTrigger);
        }
        private void OnRelationshipEventTrigger(RelationshipEventTrigger evt)
        {
            if (evt.NPCId == NPCName)
            {
                RegisterRelationshipEvent(evt.TargetId, evt.EventScore);
                Debug.Log($"[NPCBase] {NPCName} received RelationshipEventTrigger for {evt.TargetId} (score: {evt.EventScore}, type: {evt.EventType})");
            }
        }

        public void AddRival(string targetId)
        {
            if (!RivalProfiles.ContainsKey(targetId))
                RivalProfiles[targetId] = new VisualDM.NPC.RivalProfile();
            if (!RivalRelationships.ContainsKey(targetId))
                RivalRelationships[targetId] = new VisualDM.Systems.Rivalry.RivalRelationship(NPCName, targetId);
            RelationshipStateMachine?.PromoteToRival(targetId);
        }
        public void AddNemesis(string targetId)
        {
            if (!NemesisProfiles.ContainsKey(targetId))
                NemesisProfiles[targetId] = new VisualDM.NPC.NemesisProfile();
            if (!NemesisRelationships.ContainsKey(targetId))
                NemesisRelationships[targetId] = new VisualDM.Systems.Rivalry.NemesisRelationship(NPCName, targetId);
            RelationshipStateMachine?.PromoteToNemesis(targetId);
        }
        public bool IsRival(string targetId) => RelationshipStateMachine?.IsRival(targetId) ?? false;
        public bool IsNemesis(string targetId) => RelationshipStateMachine?.IsNemesis(targetId) ?? false;
    }
}