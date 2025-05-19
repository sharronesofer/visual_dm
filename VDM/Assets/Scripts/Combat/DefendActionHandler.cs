namespace VDM.Combat
{
    /// <summary>
    /// Handles defend combat actions.
    /// </summary>
    public class DefendActionHandler : ICombatActionHandler
    {
        public bool CanHandle(CombatAction action)
        {
            return action.ActionType == CombatActionType.Defend;
        }

        public void Handle(CombatAction action)
        {
            if (action.Source == null) return;
            // Example: Apply defense buff to actor
            CombatLogger.Log($"{action.Source.Name} defends and gains a temporary defense buff.");
            // You would implement actual buff logic elsewhere
        }

        public int GetPriority(CombatAction action)
        {
            return 2; // Higher than attack, lower than special
        }
    }
} 