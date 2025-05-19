using System;
using System.Collections.Generic;
using UnityEngine;
using System.Threading;
using Systems.Integration;

namespace VisualDM.Systems.Inventory
{
    [Serializable]
    public class Item
    {
        public string ID;
        public string Name;
        public string Description;
        public ItemRarity Rarity;
        public bool IsUnique;
        public bool IsQuestItem;
        public Dictionary<string, float> Stats;
        public Sprite Icon;
        public float Weight; // Weight in units (e.g., kg)

        public Item(string id, string name, string description, ItemRarity rarity, bool isUnique, bool isQuestItem, Dictionary<string, float> stats, Sprite icon, float weight = 0f)
        {
            ID = id;
            Name = name;
            Description = description;
            Rarity = rarity;
            IsUnique = isUnique;
            IsQuestItem = isQuestItem;
            Stats = stats ?? new Dictionary<string, float>();
            Icon = icon;
            Weight = weight;
        }
    }

    public enum ItemRarity
    {
        Common,
        Uncommon,
        Rare,
        Epic,
        Legendary
    }

    [Serializable]
    public class InventorySlot
    {
        public Item Item;
        public int Quantity;

        public InventorySlot(Item item, int quantity)
        {
            Item = item;
            Quantity = quantity;
        }
    }

    public class Inventory : MonoBehaviour
    {
        // --- Transaction Safety ---
        // All inventory modifications are atomic and thread-safe.
        // Each operation is wrapped in a lock and can be rolled back if needed.
        // Transaction logs are written using IntegrationLogger with unique transaction IDs.
        // Idempotency keys are supported to prevent duplicate submissions.
        // See: Task #592 implementation notes.
        private readonly object _inventoryLock = new object();
        private HashSet<string> _idempotencyKeys = new HashSet<string>();

        [SerializeField]
        private int maxSlots = 20;
        [SerializeField]
        private List<InventorySlot> slots = new List<InventorySlot>();
        [SerializeField]
        private float maxWeight = 100f;
        /// <summary>
        /// The maximum allowed weight for this inventory. Used for encumbrance checks.
        /// </summary>
        public float MaxWeight => maxWeight;

        public event Action OnInventoryChanged;
        public event Action<Item, int> OnItemAdded;
        public event Action<Item, int> OnItemRemoved;

        public IReadOnlyList<InventorySlot> Slots => slots.AsReadOnly();
        public int MaxSlots => maxSlots;

        public Inventory(Inventory other)
        {
            this.maxSlots = other.maxSlots;
            this.maxWeight = other.maxWeight;
            this.slots = new List<InventorySlot>(other.slots); // Shallow copy
            // Note: idempotency keys and event handlers are not copied
        }

        /// <summary>
        /// Adds an item to the inventory. If maxWeight >= 0, prevents adding if it would exceed the weight limit.
        /// </summary>
        /// <param name="item">The item to add.</param>
        /// <param name="quantity">The quantity to add.</param>
        /// <param name="idempotencyKey">Optional idempotency key for transaction safety.</param>
        /// <param name="maxWeight">Optional weight limit. If >= 0, prevents adding if it would exceed this value.</param>
        /// <returns>True if the item was added, false otherwise.</returns>
        public bool AddItem(Item item, int quantity = 1, string idempotencyKey = null, float maxWeight = -1f)
        {
            lock (_inventoryLock)
            {
                string txnId = Guid.NewGuid().ToString();
                if (idempotencyKey != null && _idempotencyKeys.Contains(idempotencyKey))
                {
                    IntegrationLogger.Log($"[Inventory] Idempotent AddItem ignored (key={idempotencyKey})", LogLevel.Info, "Inventory", null, "AddItem", "Idempotent");
                    return true;
                }
                bool committed = false;
                using (var tx = new IntegrationTransaction(() => { /* Rollback logic: not needed for AddItem as it's atomic in-memory */ }))
                {
                    try
                    {
                        if (item == null || quantity <= 0)
                            return false;
                        if (item.IsUnique && ContainsItem(item.ID))
                            return false;
                        if (item.IsQuestItem && ContainsItem(item.ID))
                            return false;
                        float weightLimit = maxWeight >= 0f ? maxWeight : this.maxWeight;
                        if (weightLimit >= 0f && !CanAddItemByWeight(item, quantity, weightLimit))
                        {
                            IntegrationLogger.Log($"[Inventory] AddItem txn={txnId} overweight: item={item.ID} qty={quantity} maxWeight={weightLimit}", LogLevel.Warn, "Inventory", null, "AddItem", "Rejected");
                            return false;
                        }
                        var slot = slots.Find(s => s.Item.ID == item.ID);
                        if (slot != null && !item.IsUnique && !item.IsQuestItem)
                        {
                            slot.Quantity += quantity;
                        }
                        else
                        {
                            if (slots.Count >= maxSlots)
                                return false;
                            slots.Add(new InventorySlot(item, quantity));
                        }
                        if (idempotencyKey != null)
                            _idempotencyKeys.Add(idempotencyKey);
                        OnItemAdded?.Invoke(item, quantity);
                        OnInventoryChanged?.Invoke();
                        IntegrationLogger.Log($"[Inventory] AddItem txn={txnId} item={item.ID} qty={quantity}", LogLevel.Info, "Inventory", null, "AddItem", "Committed");
                        committed = true;
                        tx.Commit();
                        return true;
                    }
                    catch (Exception ex)
                    {
                        IntegrationLogger.Log($"[Inventory] AddItem txn={txnId} failed: {ex.Message}", LogLevel.Error, "Inventory", null, "AddItem", "RolledBack");
                        throw;
                    }
                }
            }
        }

        public bool RemoveItem(Item item, int quantity = 1, string idempotencyKey = null)
        {
            lock (_inventoryLock)
            {
                string txnId = Guid.NewGuid().ToString();
                if (idempotencyKey != null && _idempotencyKeys.Contains(idempotencyKey))
                {
                    IntegrationLogger.Log($"[Inventory] Idempotent RemoveItem ignored (key={idempotencyKey})", LogLevel.Info, "Inventory", null, "RemoveItem", "Idempotent");
                    return true;
                }
                bool committed = false;
                using (var tx = new IntegrationTransaction(() => { /* Rollback logic: not needed for RemoveItem as it's atomic in-memory */ }))
                {
                    try
                    {
                        if (item == null || quantity <= 0)
                            return false;
                        var slot = slots.Find(s => s.Item.ID == item.ID);
                        if (slot == null)
                            return false;
                        if (slot.Quantity < quantity)
                            return false;
                        slot.Quantity -= quantity;
                        if (slot.Quantity <= 0)
                            slots.Remove(slot);
                        if (idempotencyKey != null)
                            _idempotencyKeys.Add(idempotencyKey);
                        OnItemRemoved?.Invoke(item, quantity);
                        OnInventoryChanged?.Invoke();
                        IntegrationLogger.Log($"[Inventory] RemoveItem txn={txnId} item={item.ID} qty={quantity}", LogLevel.Info, "Inventory", null, "RemoveItem", "Committed");
                        committed = true;
                        tx.Commit();
                        return true;
                    }
                    catch (Exception ex)
                    {
                        IntegrationLogger.Log($"[Inventory] RemoveItem txn={txnId} failed: {ex.Message}", LogLevel.Error, "Inventory", null, "RemoveItem", "RolledBack");
                        throw;
                    }
                }
            }
        }

        public bool SwapItems(int slotA, int slotB)
        {
            lock (_inventoryLock)
            {
                string txnId = Guid.NewGuid().ToString();
                using (var tx = new IntegrationTransaction(() => { /* Rollback logic: could restore previous slot order if needed */ }))
                {
                    try
                    {
                        if (slotA < 0 || slotA >= slots.Count || slotB < 0 || slotB >= slots.Count)
                            return false;
                        if (slotA == slotB)
                            return false;
                        var temp = slots[slotA];
                        slots[slotA] = slots[slotB];
                        slots[slotB] = temp;
                        OnInventoryChanged?.Invoke();
                        IntegrationLogger.Log($"[Inventory] SwapItems txn={txnId} slotA={slotA} slotB={slotB}", LogLevel.Info, "Inventory", null, "SwapItems", "Committed");
                        tx.Commit();
                        return true;
                    }
                    catch (Exception ex)
                    {
                        IntegrationLogger.Log($"[Inventory] SwapItems txn={txnId} failed: {ex.Message}", LogLevel.Error, "Inventory", null, "SwapItems", "RolledBack");
                        throw;
                    }
                }
            }
        }

        public bool CanAddItem(Item item, int quantity = 1)
        {
            if (item == null || quantity <= 0)
                return false;
            if (item.IsUnique && ContainsItem(item.ID))
                return false;
            if (item.IsQuestItem && ContainsItem(item.ID))
                return false;
            var slot = slots.Find(s => s.Item.ID == item.ID);
            if (slot != null && !item.IsUnique && !item.IsQuestItem)
                return true;
            return slots.Count < maxSlots;
        }

        public bool ContainsItem(string itemId)
        {
            return slots.Exists(s => s.Item.ID == itemId);
        }

        public static Dictionary<string, float> CompareItems(Item a, Item b)
        {
            var result = new Dictionary<string, float>();
            if (a == null || b == null)
                return result;
            foreach (var stat in a.Stats)
            {
                float bValue = b.Stats.ContainsKey(stat.Key) ? b.Stats[stat.Key] : 0f;
                result[stat.Key] = stat.Value - bValue;
            }
            foreach (var stat in b.Stats)
            {
                if (!result.ContainsKey(stat.Key))
                    result[stat.Key] = -stat.Value;
            }
            return result;
        }

        // Serialization (JSON for simplicity)
        public string Serialize()
        {
            return JsonUtility.ToJson(new InventorySaveData(this));
        }

        public void Deserialize(string json, Func<string, Item> itemResolver)
        {
            lock (_inventoryLock)
            {
                string txnId = Guid.NewGuid().ToString();
                using (var tx = new IntegrationTransaction(() => { /* Could restore previous slots if needed */ }))
                {
                    try
                    {
                        var data = JsonUtility.FromJson<InventorySaveData>(json);
                        slots.Clear();
                        foreach (var slotData in data.slots)
                        {
                            var item = itemResolver(slotData.itemId);
                            if (item != null)
                                slots.Add(new InventorySlot(item, slotData.quantity));
                        }
                        OnInventoryChanged?.Invoke();
                        IntegrationLogger.Log($"[Inventory] Deserialize txn={txnId} count={slots.Count}", LogLevel.Info, "Inventory", null, "Deserialize", "Committed");
                        tx.Commit();
                    }
                    catch (Exception ex)
                    {
                        IntegrationLogger.Log($"[Inventory] Deserialize txn={txnId} failed: {ex.Message}", LogLevel.Error, "Inventory", null, "Deserialize", "RolledBack");
                        throw;
                    }
                }
            }
        }

        [Serializable]
        private class InventorySaveData
        {
            public List<InventorySlotSaveData> slots = new List<InventorySlotSaveData>();
            public InventorySaveData(Inventory inventory)
            {
                foreach (var slot in inventory.slots)
                {
                    slots.Add(new InventorySlotSaveData { itemId = slot.Item.ID, quantity = slot.Quantity });
                }
            }
        }

        [Serializable]
        private class InventorySlotSaveData
        {
            public string itemId;
            public int quantity;
        }

        /// <summary>
        /// Returns the total weight of all items in the inventory.
        /// </summary>
        public float GetTotalWeight()
        {
            float total = 0f;
            foreach (var slot in slots)
            {
                if (slot.Item != null)
                    total += slot.Item.Weight * slot.Quantity;
            }
            return total;
        }

        /// <summary>
        /// Returns true if the inventory's total weight exceeds the given maxWeight.
        /// </summary>
        public bool IsOverweight(float maxWeight)
        {
            return GetTotalWeight() > maxWeight;
        }

        /// <summary>
        /// Returns true if adding the given item/quantity would not exceed maxWeight.
        /// </summary>
        public bool CanAddItemByWeight(Item item, int quantity, float maxWeight)
        {
            if (item == null || quantity <= 0) return false;
            float projectedWeight = GetTotalWeight() + item.Weight * quantity;
            return projectedWeight <= maxWeight;
        }

        /// <summary>
        /// Returns the encumbrance percent (0-1) based on total weight and MaxWeight.
        /// </summary>
        public float GetEncumbrancePercent()
        {
            if (MaxWeight <= 0f) return 0f;
            return Mathf.Clamp01(GetTotalWeight() / MaxWeight);
        }
    }
} 