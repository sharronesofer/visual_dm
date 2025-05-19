namespace VDM.Combat
{
    /// <summary>
    /// Handles attack combat actions.
    /// </summary>
    public class AttackActionHandler : ICombatActionHandler
    {
        public bool CanHandle(CombatAction action)
        {
            return action.ActionType == CombatActionType.Attack;
        }

        public void Handle(CombatAction action)
        {
            if (action.Source == null || action.Target == null) return;
            // Example: Apply damage to target
            if (action.Target is Combatant target)
            {
                int damage = action.Payload is int d ? d : 10;
                target.Health -= damage;
                CombatLogger.Log($"{action.Source.Name} attacks {action.Target.Name} for {damage} damage.");
            }
        }

        public int GetPriority(CombatAction action)
        {
            return 1; // Standard priority for attacks
        }
    }
} 