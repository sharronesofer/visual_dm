using UnityEngine;
using VisualDM.CombatSystem;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Static class for validating if a combat action can be performed.
    /// </summary>
    public static class CombatActionValidator
    {
        public static bool CanPerformAction(CombatActionHandler handler, CombatResourceManager resourceManager)
        {
            if (handler == null || handler.Actor == null)
            {
                handler?.ReportError(ActionErrorType.InvalidTarget, "Action or actor is null.");
                return false;
            }

            // Check cooldown
            if (resourceManager.GetCooldown(handler.Actor) > 0f)
            {
                handler.ReportError(ActionErrorType.StateConflict, "Action is on cooldown.");
                return false;
            }

            // Check resources
            if (handler.ResourceCost > 0f)
            {
                // Example: check both mana and stamina, allow either
                bool hasMana = resourceManager.GetMana(handler.Actor) >= handler.ResourceCost;
                bool hasStamina = resourceManager.GetStamina(handler.Actor) >= handler.ResourceCost;
                if (!hasMana && !hasStamina)
                {
                    handler.ReportError(ActionErrorType.InsufficientResources, "Not enough mana or stamina for action.");
                    return false;
                }
            }

            // Additional state checks can be added here
            return true;
        }
    }
} 