using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Handles defend combat actions.
    /// </summary>
    public class DefendActionHandler : CombatActionHandler
    {
        public float DefenseValue { get; private set; }

        public DefendActionHandler(GameObject actor, GameObject target, float cooldown, float resourceCost, float defenseValue)
            : base(actor, target, cooldown, resourceCost)
        {
            DefenseValue = defenseValue;
        }

        public override void StartAction()
        {
            base.StartAction();
            // Trigger defend animation or logic here
        }

        public override void UpdateAction(float deltaTime)
        {
            // Update defend logic, e.g., maintain defense state
        }

        public override void EndAction()
        {
            base.EndAction();
            // Finalize defend, apply defense buff to actor
            ApplyDefense();
        }

        public void ApplyDefense()
        {
            // Example: send defense buff to actor's defense component
            var defense = Actor.GetComponent<IDefenseComponent>();
            if (defense != null)
            {
                defense.ApplyDefense(DefenseValue);
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