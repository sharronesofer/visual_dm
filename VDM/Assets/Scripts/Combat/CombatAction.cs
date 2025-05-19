using System;

namespace VDM.Combat
{
    /// <summary>
    /// Represents a combat action (attack, defend, special ability, etc.).
    /// </summary>
    [Serializable]
    public class CombatAction
    {
        /// <summary>
        /// The type of combat action (attack, defend, special, etc.).
        /// </summary>
        public CombatActionType ActionType;
        /// <summary>
        /// The source combatant performing the action.
        /// </summary>
        public ICombatant Source;
        /// <summary>
        /// The target combatant of the action.
        /// </summary>
        public ICombatant Target;
        /// <summary>
        /// The timestamp when the action was created.
        /// </summary>
        public float Timestamp;
        /// <summary>
        /// The priority of the action (for resolution order).
        /// </summary>
        public int Priority;
        /// <summary>
        /// Optional payload for extensibility (e.g., ability data).
        /// </summary>
        public object Payload; // For extensibility (e.g., ability data)
    }
} 