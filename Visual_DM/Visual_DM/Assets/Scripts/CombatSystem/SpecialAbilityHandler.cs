using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Handles special ability combat actions.
    /// </summary>
    public class SpecialAbilityHandler : CombatActionHandler
    {
        public string AbilityName { get; private set; }
        public object AbilityData { get; private set; }

        public SpecialAbilityHandler(GameObject actor, GameObject target, float cooldown, float resourceCost, string abilityName, object abilityData = null)
            : base(actor, target, cooldown, resourceCost)
        {
            AbilityName = abilityName;
            AbilityData = abilityData;
        }

        public override void StartAction()
        {
            base.StartAction();
            // Trigger special ability logic here
        }

        public override void UpdateAction(float deltaTime)
        {
            // Update special ability logic, e.g., charge up, apply effects
        }

        public override void EndAction()
        {
            base.EndAction();
            // Finalize special ability, apply effects
            ApplySpecialAbility();
        }

        public void ApplySpecialAbility()
        {
            // Example: send ability data to a component or system
            var abilityComponent = Actor.GetComponent<ISpecialAbilityComponent>();
            if (abilityComponent != null)
            {
                abilityComponent.ExecuteAbility(AbilityName, AbilityData, Target);
            }
        }

        public void ProcessAction()
        {
            StartAction();
        }

        public void ResolveAction()
        {
            EndAction();
        }
    }
} 