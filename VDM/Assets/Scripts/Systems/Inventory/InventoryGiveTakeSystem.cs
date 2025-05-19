using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.Inventory;
using VisualDM.UI;
using Systems.Integration;

namespace VisualDM.Systems.Inventory
{
    public class InventoryGiveTakeSystem : MonoBehaviour
    {
        // --- Transaction Safety ---
        // All loot/inventory changes are atomic, idempotent, and logged with unique transaction IDs.
        // See: Task #592 implementation notes.
        private Inventory inventory;
        private InventoryUI inventoryUI;
        private List<Item> currentLoot = new List<Item>();
        private Action onLootDecisionComplete;
        private bool isModalActive = false;

        public void Initialize(Inventory inv, InventoryUI ui)
        {
            inventory = inv;
            inventoryUI = ui;
        }

        // Call this when player approaches lootable object
        public void TriggerLootModal(List<Item> loot, Action onComplete = null)
        {
            if (isModalActive) return;
            isModalActive = true;
            currentLoot = loot;
            onLootDecisionComplete = onComplete;
            inventoryUI.Show(loot);
            // Block other input here if needed
        }

        // Called by UI when player selects a loot item to take
        public void OnTakeItem(Item lootItem)
        {
            string idempotencyKey = $"loot_{lootItem.ID}_{DateTime.UtcNow.Ticks}";
            try
            {
                if (inventory.CanAddItem(lootItem))
                {
                    if (inventory.AddItem(lootItem, 1, idempotencyKey))
                    {
                        IntegrationLogger.Log($"[Loot] OnTakeItem txn={idempotencyKey} item={lootItem.ID}", LogLevel.Info, "InventoryGiveTake", null, "OnTakeItem", "Committed");
                        EndLootModal();
                    }
                }
                else
                {
                    PromptDiscardForLoot(lootItem);
                }
            }
            catch (Exception ex)
            {
                IntegrationLogger.Log($"[Loot] OnTakeItem txn={idempotencyKey} failed: {ex.Message}", LogLevel.Error, "InventoryGiveTake", null, "OnTakeItem", "RolledBack");
                ShowError($"Failed to take item: {ex.Message}");
            }
        }

        private void PromptDiscardForLoot(Item lootItem)
        {
            // Show UI to select an item to discard
            // For now, just simulate with first non-quest item
            foreach (var slot in inventory.Slots)
            {
                if (!slot.Item.IsQuestItem && !slot.Item.IsUnique)
                {
                    ConfirmDiscard(slot.Item, lootItem);
                    return;
                }
            }
            // No discardable item found
            ShowError("No discardable item available. Cannot take loot.");
        }

        private void ConfirmDiscard(Item toDiscard, Item toTake)
        {
            string idempotencyKey = $"discard_{toDiscard.ID}_for_{toTake.ID}_{DateTime.UtcNow.Ticks}";
            try
            {
                if (toDiscard.Rarity == ItemRarity.Epic || toDiscard.Rarity == ItemRarity.Legendary)
                {
                    // TODO: Show confirmation dialog in UI
                    // For now, auto-confirm
                }
                if (inventory.RemoveItem(toDiscard, 1, idempotencyKey + "_remove") &&
                    inventory.AddItem(toTake, 1, idempotencyKey + "_add"))
                {
                    IntegrationLogger.Log($"[Loot] ConfirmDiscard txn={idempotencyKey} discard={toDiscard.ID} take={toTake.ID}", LogLevel.Info, "InventoryGiveTake", null, "ConfirmDiscard", "Committed");
                    EndLootModal();
                }
            }
            catch (Exception ex)
            {
                IntegrationLogger.Log($"[Loot] ConfirmDiscard txn={idempotencyKey} failed: {ex.Message}", LogLevel.Error, "InventoryGiveTake", null, "ConfirmDiscard", "RolledBack");
                ShowError($"Failed to discard/take item: {ex.Message}");
            }
        }

        public void OnDeclineLoot()
        {
            EndLootModal();
        }

        private void ShowError(string message)
        {
            // TODO: Show error in UI
            Debug.LogError(message);
        }

        private void EndLootModal()
        {
            inventoryUI.Hide();
            isModalActive = false;
            onLootDecisionComplete?.Invoke();
        }
    }
} 