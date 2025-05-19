namespace VDM.Combat
{
    /// <summary>
    /// Interface for all combat participants (player, NPC, etc.).
    /// </summary>
    public interface ICombatant
    {
        int Initiative { get; }
        bool IsAlive { get; }
        string Name { get; }
        // Add more properties/methods as needed for combat integration.
    }

    /// <summary>
    /// Concrete implementation of a combatant (player, NPC, etc.).
    /// </summary>
    public class Combatant : ICombatant
    {
        public int Initiative { get; set; }
        public bool IsAlive { get; set; } = true;
        public string Name { get; set; }
        // Additional extensible stats and properties
        public int Health { get; set; }
        public int MaxHealth { get; set; }
        public int Mana { get; set; }
        public int Stamina { get; set; }
        // Add more as needed
    }
} 