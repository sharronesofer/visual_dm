using VisualDM.Inventory;
using VisualDM.Bounty;

namespace VisualDM.Entities.BountyHunter
{
    public static class BountyHunterRewardSystem
    {
        public static void GrantReward(BountyHunterNPC hunter)
        {
            // TODO: Integrate with InventorySystem to grant loot
            // TODO: Integrate with BountyManager to reduce bounty if needed
            // Example: InventorySystem.Instance.AddItem("HunterLoot", 1);
        }
    }
} 