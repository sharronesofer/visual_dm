using System;
using System.Collections.Generic;

namespace VDM.Combat
{
    /// <summary>
    /// Snapshot of combat state for rollback and history.
    /// </summary>
    [Serializable]
    public class CombatStateSnapshot
    {
        public List<Combatant> Combatants;
        public List<CombatAction> CurrentActions;
        public List<CombatEffect> ActiveEffects;
    }
} 