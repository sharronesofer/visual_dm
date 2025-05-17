using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Handles attack combat actions.
    /// </summary>
    public class AttackActionHandler : CombatActionHandler
    {
        public float Damage { get; private set; }

        public AttackActionHandler(GameObject actor, GameObject target, float cooldown, float resourceCost, float damage)
            : base(actor, target, cooldown, resourceCost)
        {
            Damage = damage;
        }

        public override void StartAction()
        {
            base.StartAction();
            // Trigger attack animation or logic here
        }

        public override void UpdateAction(float deltaTime)
        {
            // Update attack logic, e.g., check for hit, apply effects
        }

        public override void EndAction()
        {
            base.EndAction();
            // Finalize attack, apply damage to target
            ApplyDamage();
        }

        public void ApplyDamage()
        {
            // Example: send damage to target's health component
            var health = Target.GetComponent<IHealthComponent>();
            if (health != null)
            {
                health.TakeDamage(Damage);
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