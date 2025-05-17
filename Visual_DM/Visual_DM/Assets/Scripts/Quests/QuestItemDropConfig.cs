using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "QuestItemDropConfig", menuName = "Quests/Quest Item Drop Config", order = 1)]
public class QuestItemDropConfig : ScriptableObject
{
    [Tooltip("Unique identifier for this quest item.")]
    public string ItemId;

    [Tooltip("Base drop rate (0-1)."), Range(0f, 1f)]
    public float BaseDropRate = 0.05f;

    [Tooltip("Minimum drop rate (0-1)."), Range(0f, 1f)]
    public float MinDropRate = 0.01f;

    [Tooltip("Maximum drop rate (0-1)."), Range(0f, 1f)]
    public float MaxDropRate = 0.5f;

    [Tooltip("Drop rate modifiers by item rarity.")]
    public List<RarityModifier> RarityModifiers = new List<RarityModifier>();

    [Tooltip("Drop rate modifiers by enemy type.")]
    public List<EnemyTypeModifier> EnemyTypeModifiers = new List<EnemyTypeModifier>();

    [Tooltip("Number of failed attempts before pity mechanics activate.")]
    public int PityActivationThreshold = 3;

    [Tooltip("Scaling factor for pity increase per failed attempt (e.g., 0.05 = 5% per fail).")]
    public float PityScalingFactor = 0.05f;

    [System.Serializable]
    public class RarityModifier
    {
        public ItemRarity Rarity;
        [Range(0f, 10f)] public float Modifier = 1f;
    }

    [System.Serializable]
    public class EnemyTypeModifier
    {
        public EnemyType EnemyType;
        [Range(0f, 10f)] public float Modifier = 1f;
    }
} 