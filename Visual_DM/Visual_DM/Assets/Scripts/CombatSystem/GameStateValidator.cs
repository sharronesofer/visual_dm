using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Utilities;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Provides comprehensive game state validation and debugging tools for the turn-based system.
    /// </summary>
    public class GameStateValidator
    {
        public bool ValidateState(List<GameObject> combatants, EntityTurnStateTracker tracker)
        {
            foreach (var entity in combatants)
            {
                var state = tracker.GetState(entity);
                if (state == null || !state.IsAlive)
                {
                    LogError($"Invalid state: Entity {entity.name} is null or not alive.");
                    return false;
                }
            }
            // Add more validation as needed
            return true;
        }

        public void ResolveInvalidState(List<GameObject> combatants, EntityTurnStateTracker tracker)
        {
            // Example: Remove dead or invalid entities
            foreach (var entity in new List<GameObject>(combatants))
            {
                var state = tracker.GetState(entity);
                if (state == null || !state.IsAlive)
                {
                    tracker.RemoveEntity(entity);
                    Debug.LogWarning($"Removed invalid entity from turn order: {entity.name}");
                }
            }
        }

        public void LogError(string message)
        {
            Debug.LogError($"[GameStateValidator] {message}");
            ErrorHandlingService.Instance?.IncrementErrorCount();
        }

        public void LogState(List<GameObject> combatants, EntityTurnStateTracker tracker)
        {
            foreach (var entity in combatants)
            {
                var state = tracker.GetState(entity);
                Debug.Log($"Entity: {entity.name}, Active: {state?.IsActive}, Alive: {state?.IsAlive}, TurnCount: {state?.TurnCount}");
            }
        }
    }
} 