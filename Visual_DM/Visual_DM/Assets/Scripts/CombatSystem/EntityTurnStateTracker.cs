using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Tracks and manages the state of all active entities in the turn order.
    /// </summary>
    public class EntityTurnStateTracker
    {
        private readonly Dictionary<GameObject, EntityTurnState> entityStates = new Dictionary<GameObject, EntityTurnState>();

        public void AddEntity(GameObject entity)
        {
            if (!entityStates.ContainsKey(entity))
                entityStates[entity] = new EntityTurnState(entity);
        }

        public void RemoveEntity(GameObject entity)
        {
            if (entityStates.ContainsKey(entity))
                entityStates.Remove(entity);
        }

        public EntityTurnState GetState(GameObject entity)
        {
            entityStates.TryGetValue(entity, out var state);
            return state;
        }

        public List<GameObject> GetAllEntities()
        {
            return new List<GameObject>(entityStates.Keys);
        }

        public void UpdateEntityState(GameObject entity, EntityTurnState newState)
        {
            entityStates[entity] = newState;
        }

        // AI integration point
        public void UpdateAIForEntity(GameObject entity)
        {
            // TODO: Integrate with AI decision-making system
        }
    }

    /// <summary>
    /// Represents the turn-related state for an entity.
    /// </summary>
    public class EntityTurnState
    {
        public GameObject Entity { get; }
        public bool IsActive { get; set; }
        public bool IsAlive { get; set; }
        public int TurnCount { get; set; }
        public object CustomData { get; set; }

        public EntityTurnState(GameObject entity)
        {
            Entity = entity;
            IsActive = true;
            IsAlive = true;
            TurnCount = 0;
        }
    }
} 