namespace VDM.Combat
{
    /// <summary>
    /// Handles special combat actions.
    /// </summary>
    public class SpecialActionHandler : ICombatActionHandler
    {
        public bool CanHandle(CombatAction action)
        {
            return action.ActionType == CombatActionType.Special;
        }

        public void Handle(CombatAction action)
        {
            if (action.Source == null || action.Target == null) return;
            // Example: Apply a special effect (e.g., stun)
            var effect = new StunEffect(); // Assume StunEffect : CombatEffect
            // You would implement StunEffect elsewhere
            // Apply effect to target using EffectPipeline (not shown here)
            CombatLogger.Log($"{action.Source.Name} uses a special ability on {action.Target.Name} (stunned).");
        }

        public int GetPriority(CombatAction action)
        {
            return 3; // Highest priority for specials
        }
    }
} 