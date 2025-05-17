using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.CombatSystem;
using VisualDM.Systems.EventSystem;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Manages turn order, transitions, and the turn queue for turn-based combat.
    /// </summary>
    public class TurnManager : MonoBehaviour
    {
        public static TurnManager Instance { get; private set; }

        private readonly List<GameObject> turnOrder = new List<GameObject>();
        private int currentTurnIndex = -1;
        private CombatActionPriorityQueue actionQueue = new CombatActionPriorityQueue();
        private bool isTurnActive = false;

        public event Action<GameObject> OnTurnStarted;
        public event Action<GameObject> OnTurnEnded;
        public event Action OnRoundCompleted;

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        /// <summary>
        /// Initializes the turn order based on active combatants and their initiative/priority.
        /// </summary>
        public void InitializeTurnOrder(List<GameObject> combatants)
        {
            turnOrder.Clear();
            // TODO: Sort by initiative/priority, for now just add all
            turnOrder.AddRange(combatants);
            currentTurnIndex = -1;
        }

        /// <summary>
        /// Starts the next turn in the order.
        /// </summary>
        public void StartNextTurn()
        {
            if (turnOrder.Count == 0) return;
            currentTurnIndex = (currentTurnIndex + 1) % turnOrder.Count;
            var current = turnOrder[currentTurnIndex];
            isTurnActive = true;
            OnTurnStarted?.Invoke(current);
            // Optionally: Broadcast event via EventBus
            EventBus.Instance.Publish(new TurnStartedEvent(current));
        }

        /// <summary>
        /// Ends the current turn and triggers the next.
        /// </summary>
        public void EndCurrentTurn()
        {
            if (!isTurnActive) return;
            var current = turnOrder[currentTurnIndex];
            isTurnActive = false;
            OnTurnEnded?.Invoke(current);
            EventBus.Instance.Publish(new TurnEndedEvent(current));
            if (currentTurnIndex == turnOrder.Count - 1)
                OnRoundCompleted?.Invoke();
            StartNextTurn();
        }

        /// <summary>
        /// Interrupts the turn order to insert an out-of-turn action.
        /// </summary>
        public void InterruptTurn(GameObject combatant)
        {
            // Insert combatant at next position
            if (!turnOrder.Contains(combatant))
                turnOrder.Insert(currentTurnIndex + 1, combatant);
        }

        /// <summary>
        /// Removes a combatant from the turn order.
        /// </summary>
        public void RemoveCombatant(GameObject combatant)
        {
            int idx = turnOrder.IndexOf(combatant);
            if (idx >= 0)
            {
                turnOrder.RemoveAt(idx);
                if (currentTurnIndex >= idx)
                    currentTurnIndex--;
            }
        }

        /// <summary>
        /// Adds a combatant to the turn order (e.g., mid-combat).
        /// </summary>
        public void AddCombatant(GameObject combatant, int? position = null)
        {
            if (position.HasValue)
                turnOrder.Insert(position.Value, combatant);
            else
                turnOrder.Add(combatant);
        }

        /// <summary>
        /// Gets the current combatant whose turn it is.
        /// </summary>
        public GameObject GetCurrentCombatant()
        {
            if (currentTurnIndex < 0 || currentTurnIndex >= turnOrder.Count) return null;
            return turnOrder[currentTurnIndex];
        }

        /// <summary>
        /// Returns a copy of the current turn order.
        /// </summary>
        public List<GameObject> GetTurnOrderSnapshot()
        {
            return new List<GameObject>(turnOrder);
        }
    }

    // Event types for turn transitions
    public class TurnStartedEvent
    {
        public GameObject Combatant;
        public TurnStartedEvent(GameObject combatant) { Combatant = combatant; }
    }
    public class TurnEndedEvent
    {
        public GameObject Combatant;
        public TurnEndedEvent(GameObject combatant) { Combatant = combatant; }
    }
} 