namespace VDM.Combat
{
    /// <summary>
    /// Interface for combat action handlers (attack, defend, special, etc.).
    /// </summary>
    public interface ICombatActionHandler
    {
        bool CanHandle(CombatAction action);
        void Handle(CombatAction action);
        int GetPriority(CombatAction action);
    }
} 