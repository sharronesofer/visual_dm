using System.Collections.Generic;
using System.Linq;
using UnityEngine;


namespace VDM.Runtime.Combat
{
    /// <summary>
    /// Validates combat states and action legality
    /// </summary>
    public class StateValidator
    {
        /// <summary>
        /// Validate the overall combat state
        /// </summary>
        public bool ValidateState(List<GameObject> combatants, EntityTracker entityTracker)
        {
            if (combatants == null || entityTracker == null)
                return false;
                
            // Check if all combatants are tracked
            foreach (var combatant in combatants)
            {
                if (!entityTracker.IsTracking(combatant))
                    return false;
                    
                var state = entityTracker.GetState(combatant);
                if (state == null)
                    return false;
                    
                // Validate individual entity state
                if (!ValidateEntityState(combatant, state))
                    return false;
            }
            
            // Check if there are enough alive combatants to continue
            var aliveCombatants = combatants.Where(c => 
            {
                var state = entityTracker.GetState(c);
                return state != null && state.IsAlive;
            }).ToList();
            
            // Need at least one alive combatant for valid combat
            return aliveCombatants.Count > 0;
        }
        
        /// <summary>
        /// Validate a specific entity's state
        /// </summary>
        public bool ValidateEntityState(GameObject entity, CharacterState state)
        {
            if (entity == null || state == null)
                return false;
                
            // Basic health validation
            if (state.CurrentHP < 0 || state.CurrentHP > state.MaxHP)
                return false;
                
            // If HP is 0, entity should not be alive
            if (state.CurrentHP <= 0 && state.IsAlive)
                return false;
                
            // If dead, should not be able to act
            if (!state.IsAlive && state.CanAct)
                return false;
                
            // Armor class should be reasonable
            if (state.ArmorClass < 0 || state.ArmorClass > 30) // D&D typical range
                return false;
                
            return true;
        }
        
        /// <summary>
        /// Validate if an action can be performed
        /// </summary>
        public bool ValidateAction(ActionRequest request, CharacterState actorState)
        {
            if (request == null || actorState == null)
                return false;
                
            // Dead entities cannot act
            if (!actorState.IsAlive)
                return false;
                
            // Incapacitated entities cannot act
            if (!actorState.CanAct)
                return false;
                
            // Check for specific conditions that prevent actions
            if (HasActionBlockingCondition(actorState))
                return false;
                
            // Validate specific action types
            return ValidateSpecificAction(request, actorState);
        }
        
        /// <summary>
        /// Check if the entity has conditions that block actions
        /// </summary>
        private bool HasActionBlockingCondition(CharacterState state)
        {
            var blockingConditions = new[]
            {
                "incapacitated",
                "stunned",
                "paralyzed",
                "unconscious",
                "petrified"
            };
            
            return state.Conditions.Any(condition => 
                blockingConditions.Contains(condition.ToLower()));
        }
        
        /// <summary>
        /// Validate specific action types
        /// </summary>
        private bool ValidateSpecificAction(ActionRequest request, CharacterState actorState)
        {
            switch (request.ActionType)
            {
                case ActionType.Attack:
                    return ValidateAttackAction(request, actorState);
                    
                case ActionType.Cast:
                    return ValidateCastAction(request, actorState);
                    
                case ActionType.Dodge:
                case ActionType.Dash:
                case ActionType.Disengage:
                case ActionType.Help:
                    return true; // Basic actions are usually always valid if entity can act
                    
                case ActionType.Hide:
                    return ValidateHideAction(request, actorState);
                    
                case ActionType.Ready:
                    return ValidateReadyAction(request, actorState);
                    
                case ActionType.ChainAction:
                    return ValidateChainAction(request, actorState);
                    
                default:
                    return false; // Unknown action type
            }
        }
        
        /// <summary>
        /// Validate attack actions
        /// </summary>
        private bool ValidateAttackAction(ActionRequest request, CharacterState actorState)
        {
            // Blinded entities have disadvantage but can still attack
            // Restrained entities have disadvantage but can still attack
            
            // Cannot attack if target is null for targeted attacks
            if (request.Target == null && request.Parameters?.ContainsKey("targeted") == true)
                return false;
                
            return true;
        }
        
        /// <summary>
        /// Validate spell casting actions
        /// </summary>
        private bool ValidateCastAction(ActionRequest request, CharacterState actorState)
        {
            // Cannot cast if silenced (if implemented)
            if (actorState.Conditions.Contains("silenced"))
                return false;
                
            // Cannot cast with hands restrained (simplified)
            if (actorState.Conditions.Contains("restrained"))
                return false;
                
            return true;
        }
        
        /// <summary>
        /// Validate hide actions
        /// </summary>
        private bool ValidateHideAction(ActionRequest request, CharacterState actorState)
        {
            // Cannot hide if already hidden
            if (actorState.Conditions.Contains("hidden"))
                return false;
                
            // Cannot hide if in bright light without cover (simplified)
            // This would need more complex environmental checking in a full implementation
            
            return true;
        }
        
        /// <summary>
        /// Validate ready actions
        /// </summary>
        private bool ValidateReadyAction(ActionRequest request, CharacterState actorState)
        {
            // Need to specify what action to ready
            if (request.Parameters == null || !request.Parameters.ContainsKey("readied_action"))
                return false;
                
            return true;
        }
        
        /// <summary>
        /// Validate chain actions
        /// </summary>
        private bool ValidateChainAction(ActionRequest request, CharacterState actorState)
        {
            // Chain actions might require specific abilities or conditions
            // This is a placeholder for more complex validation
            
            return true;
        }
        
        /// <summary>
        /// Validate if a target is valid for an action
        /// </summary>
        public bool ValidateTarget(GameObject actor, GameObject target, ActionType actionType)
        {
            if (actor == null || target == null)
                return false;
                
            // Cannot target self for hostile actions (simplified)
            if (actor == target && IsHostileAction(actionType))
                return false;
                
            // Check if target is in range (would need positioning system)
            // This is a placeholder for range checking
            
            return true;
        }
        
        /// <summary>
        /// Check if an action type is hostile
        /// </summary>
        private bool IsHostileAction(ActionType actionType)
        {
            return actionType == ActionType.Attack;
        }
        
        /// <summary>
        /// Validate movement (if positioning is implemented)
        /// </summary>
        public bool ValidateMovement(GameObject entity, Vector3 from, Vector3 to, CharacterState state)
        {
            if (entity == null || state == null)
                return false;
                
            // Cannot move if speed is 0
            if (state.Conditions.Contains("grappled") || state.Conditions.Contains("restrained"))
                return false;
                
            // Calculate distance
            var distance = Vector3.Distance(from, to);
            
            // Basic movement speed check (30 feet default)
            var movementSpeed = 30f;
            if (state.Stats.ContainsKey("MovementSpeed"))
                movementSpeed = state.Stats["MovementSpeed"];
                
            return distance <= movementSpeed;
        }
    }
} 