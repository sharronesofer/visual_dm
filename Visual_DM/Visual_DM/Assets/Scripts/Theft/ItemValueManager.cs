using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Inventory;
using VisualDM.World;

namespace VisualDM.Theft
{
    public class ItemValueManager : MonoBehaviour
    {
        public static ItemValueManager Instance { get; private set; }

        private Dictionary<string, float> valueCache = new();
        private float cacheDuration = 60f; // seconds
        private Dictionary<string, float> cacheTimestamps = new();
        private EconomySystem economySystem;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            economySystem = new EconomySystem(); // Or inject if needed
        }

        public float GetItemValue(Item item)
        {
            if (item == null) return 0f;
            if (valueCache.TryGetValue(item.ID, out float cachedValue))
            {
                if (Time.time - cacheTimestamps[item.ID] < cacheDuration)
                    return cachedValue;
            }
            float value = CalculateItemValue(item);
            valueCache[item.ID] = value;
            cacheTimestamps[item.ID] = Time.time;
            return value;
        }

        private float CalculateItemValue(Item item)
        {
            float baseValue = 10f;
            switch (item.Rarity)
            {
                case ItemRarity.Common: baseValue = 10f; break;
                case ItemRarity.Uncommon: baseValue = 25f; break;
                case ItemRarity.Rare: baseValue = 100f; break;
                case ItemRarity.Epic: baseValue = 500f; break;
                case ItemRarity.Legendary: baseValue = 2000f; break;
            }
            float condition = item.Stats != null && item.Stats.TryGetValue("Condition", out float cond) ? cond : 1f;
            float market = economySystem.GetMarketPrice(item.Name);
            float fluctuation = Mathf.PerlinNoise(Time.time * 0.001f, item.ID.GetHashCode() * 0.0001f);
            float value = baseValue * condition * market * (0.9f + 0.2f * fluctuation);
            return Mathf.Max(1f, value);
        }

        public void InvalidateCache(string itemId)
        {
            valueCache.Remove(itemId);
            cacheTimestamps.Remove(itemId);
        }
    }
} 