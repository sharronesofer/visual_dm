using System;
using UnityEngine;
using VisualDM.Inventory;
using VisualDM.Bounty;

namespace VisualDM.Theft
{
    public class TheftBountyCalculator : MonoBehaviour
    {
        public static float CalculateBounty(Item item, int repeatOffenses, string factionId = null)
        {
            float baseValue = ItemValueManager.Instance.GetItemValue(item);
            float bounty = baseValue * 2f; // Double value for theft
            float repeatMultiplier = 1f + 0.5f * repeatOffenses;
            bounty *= repeatMultiplier;
            if (!string.IsNullOrEmpty(factionId))
            {
                // Example: Faction-specific modifier lookup
                float factionMod = GetFactionModifier(factionId, item);
                bounty *= factionMod;
            }
            return bounty;
        }

        private static float GetFactionModifier(string factionId, Item item)
        {
            // TODO: Implement actual faction logic
            return 1f;
        }

        public static float ApplyDecay(float bounty, float timeSinceTheft, float halfLife = 600f)
        {
            // Exponential decay: bounty halves every halfLife seconds
            return bounty * Mathf.Pow(0.5f, timeSinceTheft / halfLife);
        }
    }
} 