using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public enum ItemRarity
{
    Common,
    Uncommon,
    Rare,
    Epic,
    Legendary
}

[Serializable]
public enum EnemyType
{
    Normal,
    Elite,
    Boss
}

[Serializable]
public class QuestItemDropData
{
    public string ItemId;
    [Range(0f, 1f)] public float BaseDropRate;
    [Range(0f, 1f)] public float MinDropRate;
    [Range(0f, 1f)] public float MaxDropRate;
    public Dictionary<ItemRarity, float> RarityModifiers = new Dictionary<ItemRarity, float>();
    public Dictionary<EnemyType, float> EnemyTypeModifiers = new Dictionary<EnemyType, float>();
} 