using System.Collections.Generic;
using UnityEngine;


namespace VDM.Infrastructure.Core
{
    /// <summary>
    /// Tracks entity states and information during combat
    /// </summary>
    public class EntityTracker
    {
        private Dictionary<GameObject, CharacterState> _trackedEntities = new Dictionary<GameObject, CharacterState>();
        
        /// <summary>
        /// Start tracking an entity
        /// </summary>
        public void TrackEntity(GameObject entity)
        {
            if (entity == null || _trackedEntities.ContainsKey(entity))
                return;
                
            var state = CreateCharacterState(entity);
            _trackedEntities[entity] = state;
        }
        
        /// <summary>
        /// Stop tracking an entity
        /// </summary>
        public void UntrackEntity(GameObject entity)
        {
            if (entity == null)
                return;
                
            _trackedEntities.Remove(entity);
        }
        
        /// <summary>
        /// Get the character state for an entity
        /// </summary>
        public CharacterState GetState(GameObject entity)
        {
            if (entity == null || !_trackedEntities.ContainsKey(entity))
                return null;
                
            return _trackedEntities[entity];
        }
        
        /// <summary>
        /// Update the state for an entity
        /// </summary>
        public void UpdateState(GameObject entity, CharacterState state)
        {
            if (entity == null || state == null)
                return;
                
            _trackedEntities[entity] = state;
        }
        
        /// <summary>
        /// Get all tracked entities
        /// </summary>
        public List<GameObject> GetTrackedEntities()
        {
            return new List<GameObject>(_trackedEntities.Keys);
        }
        
        /// <summary>
        /// Get all alive entities
        /// </summary>
        public List<GameObject> GetAliveEntities()
        {
            var aliveEntities = new List<GameObject>();
            foreach (var kvp in _trackedEntities)
            {
                if (kvp.Value.IsAlive)
                {
                    aliveEntities.Add(kvp.Key);
                }
            }
            return aliveEntities;
        }
        
        /// <summary>
        /// Check if an entity is being tracked
        /// </summary>
        public bool IsTracking(GameObject entity)
        {
            return entity != null && _trackedEntities.ContainsKey(entity);
        }
        
        /// <summary>
        /// Clear all tracking
        /// </summary>
        public void ClearTracking()
        {
            _trackedEntities.Clear();
        }
        
        /// <summary>
        /// Get the number of tracked entities
        /// </summary>
        public int TrackedEntityCount => _trackedEntities.Count;
        
        /// <summary>
        /// Create a character state from an entity's components
        /// </summary>
        private CharacterState CreateCharacterState(GameObject entity)
        {
            var state = new CharacterState();
            
            // Try to get stats from CombatantComponent
            var combatant = entity.GetComponent<CombatantComponent>();
            if (combatant != null)
            {
                state.MaxHP = combatant.MaxHP;
                state.CurrentHP = combatant.CurrentHP;
                state.ArmorClass = combatant.ArmorClass;
                state.Initiative = combatant.Initiative;
                state.IsAlive = combatant.IsAlive;
                
                // Populate attributes dictionary
                state.Attributes["Dexterity"] = combatant.Dexterity;
            }
            
            // Try to get additional attributes from CharacterComponent
            var character = entity.GetComponent<CharacterComponent>();
            if (character != null)
            {
                state.Attributes["Strength"] = character.Strength;
                state.Attributes["Dexterity"] = character.Dexterity;
                state.Attributes["Constitution"] = character.Constitution;
                state.Attributes["Intelligence"] = character.Intelligence;
                state.Attributes["Wisdom"] = character.Wisdom;
                state.Attributes["Charisma"] = character.Charisma;
            }
            
            return state;
        }
        
        /// <summary>
        /// Apply damage to an entity
        /// </summary>
        public bool ApplyDamage(GameObject entity, int damage)
        {
            var state = GetState(entity);
            if (state == null)
                return false;
                
            state.CurrentHP = Mathf.Max(0, state.CurrentHP - damage);
            if (state.CurrentHP <= 0)
            {
                state.IsAlive = false;
                state.CanAct = false;
            }
            
            // Update component if it exists
            var combatant = entity.GetComponent<CombatantComponent>();
            if (combatant != null)
            {
                combatant.TakeDamage(damage);
            }
            
            return true;
        }
        
        /// <summary>
        /// Apply healing to an entity
        /// </summary>
        public bool ApplyHealing(GameObject entity, int healing)
        {
            var state = GetState(entity);
            if (state == null)
                return false;
                
            state.CurrentHP = Mathf.Min(state.MaxHP, state.CurrentHP + healing);
            if (state.CurrentHP > 0)
            {
                state.IsAlive = true;
                state.CanAct = true;
            }
            
            // Update component if it exists
            var combatant = entity.GetComponent<CombatantComponent>();
            if (combatant != null)
            {
                combatant.Heal(healing);
            }
            
            return true;
        }
        
        /// <summary>
        /// Add a condition to an entity
        /// </summary>
        public void AddCondition(GameObject entity, string condition)
        {
            var state = GetState(entity);
            if (state == null || string.IsNullOrEmpty(condition))
                return;
                
            if (!state.Conditions.Contains(condition))
            {
                state.Conditions.Add(condition);
                ApplyConditionEffects(state, condition, true);
            }
        }
        
        /// <summary>
        /// Remove a condition from an entity
        /// </summary>
        public void RemoveCondition(GameObject entity, string condition)
        {
            var state = GetState(entity);
            if (state == null || string.IsNullOrEmpty(condition))
                return;
                
            if (state.Conditions.Remove(condition))
            {
                ApplyConditionEffects(state, condition, false);
            }
        }
        
        /// <summary>
        /// Apply the effects of a condition
        /// </summary>
        private void ApplyConditionEffects(CharacterState state, string condition, bool applying)
        {
            switch (condition.ToLower())
            {
                case "incapacitated":
                case "stunned":
                case "paralyzed":
                case "unconscious":
                    state.CanAct = !applying;
                    break;
                    
                case "dead":
                    if (applying)
                    {
                        state.IsAlive = false;
                        state.CanAct = false;
                        state.CurrentHP = 0;
                    }
                    break;
            }
        }
    }
} 