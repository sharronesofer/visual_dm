using UnityEngine;

namespace VisualDM.AI
{
    /// <summary>
    /// ScriptableObject for configuring rumor decay rates.
    /// </summary>
    [CreateAssetMenu(fileName = "RumorDecayConfig", menuName = "AI/Rumor Decay Config")]
    public class RumorDecayConfig : ScriptableObject
    {
        [Header("Base Decay Rates")]
        [Tooltip("Base decay per retelling (0 = no decay, 1 = instant forget)")]
        [Range(0f, 1f)] public float DecayPerRetelling = 0.05f;
        [Tooltip("Base decay per in-game hour")]
        [Range(0f, 1f)] public float DecayPerHour = 0.01f;

        [Header("NPC Personality Modifiers")]
        [Tooltip("Decay modifier for gossips (lower = rumors last longer)")]
        [Range(0.1f, 2f)] public float GossipModifier = 0.7f;
        [Tooltip("Decay modifier for truth-tellers (higher = rumors decay faster)")]
        [Range(0.1f, 2f)] public float TruthTellerModifier = 1.2f;
        [Tooltip("Decay modifier for neutral NPCs")]
        [Range(0.1f, 2f)] public float NeutralModifier = 1.0f;
        // Add more traits as needed
    }
}