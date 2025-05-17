using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Factory for creating combat action handlers based on action type.
    /// </summary>
    public static class CombatActionFactory
    {
        public enum CombatActionType { Attack, Defend, SpecialAbility }

        public static CombatActionHandler CreateHandler(CombatActionType actionType, GameObject actor, GameObject target, float cooldown, float resourceCost, object extra = null)
        {
            switch (actionType)
            {
                case CombatActionType.Attack:
                    float damage = extra is float d ? d : 10f;
                    return new AttackActionHandler(actor, target, cooldown, resourceCost, damage);
                case CombatActionType.Defend:
                    float defense = extra is float df ? df : 5f;
                    return new DefendActionHandler(actor, target, cooldown, resourceCost, defense);
                case CombatActionType.SpecialAbility:
                    var tuple = extra as (string, object)?;
                    string abilityName = tuple?.Item1 ?? "Special";
                    object abilityData = tuple?.Item2;
                    return new SpecialAbilityHandler(actor, target, cooldown, resourceCost, abilityName, abilityData);
                default:
                    return null;
            }
        }
    }
} 