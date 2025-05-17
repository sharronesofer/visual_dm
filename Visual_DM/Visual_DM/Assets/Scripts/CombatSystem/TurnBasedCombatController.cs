using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Orchestrates the turn-based action resolution system.
    /// </summary>
    public class TurnBasedCombatController : MonoBehaviour
    {
        public TurnManager TurnManager { get; private set; }
        public ActionResolutionPipeline ActionPipeline { get; private set; }
        public EntityTurnStateTracker EntityTracker { get; private set; }
        public GameStateValidator StateValidator { get; private set; }

        private List<GameObject> combatants = new List<GameObject>();
        private bool combatActive = false;

        void Awake()
        {
            TurnManager = FindObjectOfType<TurnManager>() ?? gameObject.AddComponent<TurnManager>();
            ActionPipeline = new ActionResolutionPipeline(new DefaultPreProcess(), new DefaultExecution(), new DefaultPostProcess());
            EntityTracker = new EntityTurnStateTracker();
            StateValidator = new GameStateValidator();
        }

        public void StartCombat(List<GameObject> initialCombatants)
        {
            combatants = new List<GameObject>(initialCombatants);
            foreach (var entity in combatants)
                EntityTracker.AddEntity(entity);
            TurnManager.InitializeTurnOrder(combatants);
            combatActive = true;
            TurnManager.OnTurnStarted += OnTurnStarted;
            TurnManager.OnTurnEnded += OnTurnEnded;
            TurnManager.OnRoundCompleted += OnRoundCompleted;
            TurnManager.StartNextTurn();
        }

        private void OnTurnStarted(GameObject combatant)
        {
            // Example: AI or player input
            var state = EntityTracker.GetState(combatant);
            if (state != null && state.IsAlive)
            {
                // TODO: Request action from AI or player
            }
        }

        private void OnTurnEnded(GameObject combatant)
        {
            // Post-turn processing
            StateValidator.LogState(combatants, EntityTracker);
        }

        private void OnRoundCompleted()
        {
            // End-of-round logic
            StateValidator.ValidateState(combatants, EntityTracker);
        }

        public void ProcessAction(ActionRequest request, CharacterState state)
        {
            if (!combatActive) return;
            if (ActionPipeline.Run(request, state))
            {
                // Action succeeded, end turn
                TurnManager.EndCurrentTurn();
            }
            else
            {
                // Action failed, allow retry or handle error
            }
        }

        public void AddCombatant(GameObject entity)
        {
            combatants.Add(entity);
            EntityTracker.AddEntity(entity);
            TurnManager.AddCombatant(entity);
        }

        public void RemoveCombatant(GameObject entity)
        {
            combatants.Remove(entity);
            EntityTracker.RemoveEntity(entity);
            TurnManager.RemoveCombatant(entity);
        }

        public void EndCombat()
        {
            combatActive = false;
            TurnManager.OnTurnStarted -= OnTurnStarted;
            TurnManager.OnTurnEnded -= OnTurnEnded;
            TurnManager.OnRoundCompleted -= OnRoundCompleted;
        }
    }
} 