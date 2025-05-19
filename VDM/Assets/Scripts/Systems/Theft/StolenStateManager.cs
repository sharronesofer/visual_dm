using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Inventory;

namespace VisualDM.Theft
{
    public enum StolenState { Legitimate, Stolen, Recovered }

    [Serializable]
    public class StolenItemData
    {
        public string ItemId;
        public StolenState State;
        public float StolenTimestamp;
        public string OriginalOwnerId;
        public string CurrentOwnerId;
    }

    public class StolenStateManager : MonoBehaviour
    {
        public static StolenStateManager Instance { get; private set; }
        private Dictionary<string, StolenItemData> stolenItems = new();
        private float decayDuration = 600f; // 10 minutes for normalization

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        public void MarkItemStolen(Item item, string originalOwnerId, string currentOwnerId)
        {
            if (item == null) return;
            stolenItems[item.ID] = new StolenItemData
            {
                ItemId = item.ID,
                State = StolenState.Stolen,
                StolenTimestamp = Time.time,
                OriginalOwnerId = originalOwnerId,
                CurrentOwnerId = currentOwnerId
            };
        }

        public void Update()
        {
            List<string> toNormalize = new();
            foreach (var kvp in stolenItems)
            {
                if (kvp.Value.State == StolenState.Stolen && (Time.time - kvp.Value.StolenTimestamp) > decayDuration)
                {
                    toNormalize.Add(kvp.Key);
                }
            }
            foreach (var id in toNormalize)
            {
                stolenItems[id].State = StolenState.Legitimate;
            }
        }

        public StolenState GetItemState(string itemId)
        {
            if (stolenItems.TryGetValue(itemId, out var data))
                return data.State;
            return StolenState.Legitimate;
        }

        public void RecoverItem(string itemId)
        {
            if (stolenItems.TryGetValue(itemId, out var data))
                data.State = StolenState.Recovered;
        }

        public void SerializeStolenStates()
        {
            // Implement save logic (e.g., PlayerPrefs, file, or custom save system)
        }

        public void DeserializeStolenStates()
        {
            // Implement load logic
        }

        public string GetOriginalOwner(string itemId)
        {
            if (stolenItems.TryGetValue(itemId, out var data))
                return data.OriginalOwnerId;
            return null;
        }

        public string GetCurrentOwner(string itemId)
        {
            if (stolenItems.TryGetValue(itemId, out var data))
                return data.CurrentOwnerId;
            return null;
        }
    }
} 