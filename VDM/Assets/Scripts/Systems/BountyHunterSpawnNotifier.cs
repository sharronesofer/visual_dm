using UnityEngine;
using VisualDM.UI;
using VisualDM.Bounty;

namespace VisualDM.Entities.BountyHunter
{
    public static class BountyHunterSpawnNotifier
    {
        public static void NotifyHunterSpawned(float bounty, bool isElite)
        {
            string message = isElite ?
                $"Elite Bounty Hunter dispatched! Bounty: {bounty}" :
                $"Bounty Hunter dispatched! Bounty: {bounty}";
            UIManager.Instance.ShowNotification(message, NotificationLevel.Warning);
            BountyNotificationSystem.Instance?.ShowBountyHunterAlert(message);
            // TODO: Play audio/visual cue
        }
    }
} 