using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Infrastructure.Core
{
    /// <summary>
    /// Processes combat actions and generates results
    /// </summary>
    public class ActionProcessor
    {
        // Events
        public event Action<ActionRequest, ActionResult> OnActionCompleted;
        public event Action<ActionRequest> OnActionStarted;
        
        /// <summary>
        /// Process a combat action and return the result
        /// </summary>
        public ActionResult ProcessAction(ActionRequest request, CharacterState actorState)
        {
            if (request == null || actorState == null)
                return CreateFailedResult("Invalid action request or actor state");
                
            OnActionStarted?.Invoke(request);
            
            ActionResult result;
            
            try
            {
                result = request.ActionType switch
                {
                    ActionType.Attack => ProcessAttackAction(request, actorState),
                    ActionType.Cast => ProcessCastAction(request, actorState),
                    ActionType.Dodge => ProcessDodgeAction(request, actorState),
                    ActionType.Dash => ProcessDashAction(request, actorState),
                    ActionType.Disengage => ProcessDisengageAction(request, actorState),
                    ActionType.Hide => ProcessHideAction(request, actorState),
                    ActionType.Help => ProcessHelpAction(request, actorState),
                    ActionType.Ready => ProcessReadyAction(request, actorState),
                    ActionType.ChainAction => ProcessChainAction(request, actorState),
                    _ => CreateFailedResult($"Unknown action type: {request.ActionType}")
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error processing action {request.ActionType}: {ex.Message}");
                result = CreateFailedResult($"Action processing failed: {ex.Message}");
            }
            
            OnActionCompleted?.Invoke(request, result);
            return result;
        }
        
        /// <summary>
        /// Process an attack action
        /// </summary>
        private ActionResult ProcessAttackAction(ActionRequest request, CharacterState actorState)
        {
            var result = new ActionResult();
            
            // Basic attack roll: d20 + ability modifier + proficiency
            var attackRoll = UnityEngine.Random.Range(1, 21);
            var abilityModifier = GetAbilityModifier(actorState, "Strength"); // Default to Strength
            var proficiencyBonus = GetProficiencyBonus(actorState);
            
            var totalAttackRoll = attackRoll + abilityModifier + proficiencyBonus;
            
            // Apply advantage/disadvantage based on conditions
            if (HasAdvantage(actorState, ActionType.Attack))
            {
                var secondRoll = UnityEngine.Random.Range(1, 21);
                attackRoll = Mathf.Max(attackRoll, secondRoll);
                totalAttackRoll = attackRoll + abilityModifier + proficiencyBonus;
            }
            else if (HasDisadvantage(actorState, ActionType.Attack))
            {
                var secondRoll = UnityEngine.Random.Range(1, 21);
                attackRoll = Mathf.Min(attackRoll, secondRoll);
                totalAttackRoll = attackRoll + abilityModifier + proficiencyBonus;
            }
            
            // Determine target AC
            var targetAC = GetTargetAC(request.Target);
            
            // Check if attack hits
            var isHit = totalAttackRoll >= targetAC || attackRoll == 20; // Natural 20 always hits
            var isCritical = attackRoll == 20;
            
            if (isHit)
            {
                // Calculate damage
                var baseDamage = CalculateWeaponDamage(actorState);
                var damageModifier = abilityModifier;
                
                var totalDamage = baseDamage + damageModifier;
                
                // Critical hit doubles dice
                if (isCritical)
                {
                    totalDamage += baseDamage; // Add base damage again for crit
                    result.Effects.Add("Critical Hit!");
                }
                
                result.Success = true;
                result.Damage = Mathf.Max(1, totalDamage); // Minimum 1 damage
                result.TargetEntity = request.Target;
                result.Message = $"Attack hits for {result.Damage} damage! (Rolled {attackRoll})";
            }
            else
            {
                result.Success = false;
                result.Damage = 0;
                result.TargetEntity = request.Target;
                result.Message = $"Attack misses! (Rolled {attackRoll}, needed {targetAC})";
            }
            
            return result;
        }
        
        /// <summary>
        /// Process a spell casting action
        /// </summary>
        private ActionResult ProcessCastAction(ActionRequest request, CharacterState actorState)
        {
            var result = new ActionResult();
            
            // Basic spell casting implementation
            // In a full system, this would check spell slots, components, etc.
            
            var spellName = request.Parameters?.ContainsKey("spell") == true 
                ? request.Parameters["spell"].ToString() 
                : "Unknown Spell";
                
            // Placeholder spell effects
            if (spellName.ToLower().Contains("heal"))
            {
                var healAmount = UnityEngine.Random.Range(5, 15);
                result.Success = true;
                result.Healing = healAmount;
                result.TargetEntity = request.Target ?? GetEntityFromId(request.EntityId);
                result.Message = $"Casts {spellName} for {healAmount} healing!";
            }
            else if (spellName.ToLower().Contains("damage") || spellName.ToLower().Contains("fire"))
            {
                var damage = UnityEngine.Random.Range(8, 16);
                result.Success = true;
                result.Damage = damage;
                result.TargetEntity = request.Target;
                result.Message = $"Casts {spellName} for {damage} damage!";
            }
            else
            {
                result.Success = true;
                result.Message = $"Casts {spellName}!";
                result.Effects.Add("Spell Effect Applied");
            }
            
            return result;
        }
        
        /// <summary>
        /// Process a dodge action
        /// </summary>
        private ActionResult ProcessDodgeAction(ActionRequest request, CharacterState actorState)
        {
            var result = new ActionResult
            {
                Success = true,
                Message = "Takes the Dodge action - attacks against them have disadvantage until next turn"
            };
            
            result.Effects.Add("Dodging");
            return result;
        }
        
        /// <summary>
        /// Process a dash action
        /// </summary>
        private ActionResult ProcessDashAction(ActionRequest request, CharacterState actorState)
        {
            var result = new ActionResult
            {
                Success = true,
                Message = "Takes the Dash action - movement speed doubled this turn"
            };
            
            result.Effects.Add("Dashing");
            return result;
        }
        
        /// <summary>
        /// Process a disengage action
        /// </summary>
        private ActionResult ProcessDisengageAction(ActionRequest request, CharacterState actorState)
        {
            var result = new ActionResult
            {
                Success = true,
                Message = "Takes the Disengage action - no opportunity attacks this turn"
            };
            
            result.Effects.Add("Disengaged");
            return result;
        }
        
        /// <summary>
        /// Process a hide action
        /// </summary>
        private ActionResult ProcessHideAction(ActionRequest request, CharacterState actorState)
        {
            // Stealth check
            var stealthRoll = UnityEngine.Random.Range(1, 21);
            var dexModifier = GetAbilityModifier(actorState, "Dexterity");
            var stealthTotal = stealthRoll + dexModifier;
            
            // Passive Perception of enemies (simplified to 10 + Wisdom modifier)
            var passivePerception = 10 + 2; // Assuming average Wisdom
            
            var result = new ActionResult();
            
            if (stealthTotal >= passivePerception)
            {
                result.Success = true;
                result.Message = $"Successfully hides! (Stealth: {stealthTotal})";
                result.Effects.Add("Hidden");
            }
            else
            {
                result.Success = false;
                result.Message = $"Fails to hide (Stealth: {stealthTotal} vs Perception: {passivePerception})";
            }
            
            return result;
        }
        
        /// <summary>
        /// Process a help action
        /// </summary>
        private ActionResult ProcessHelpAction(ActionRequest request, CharacterState actorState)
        {
            var result = new ActionResult
            {
                Success = true,
                TargetEntity = request.Target,
                Message = "Helps an ally - they have advantage on their next ability check or attack"
            };
            
            result.Effects.Add("Helping");
            return result;
        }
        
        /// <summary>
        /// Process a ready action
        /// </summary>
        private ActionResult ProcessReadyAction(ActionRequest request, CharacterState actorState)
        {
            var readiedAction = request.Parameters?.ContainsKey("readied_action") == true 
                ? request.Parameters["readied_action"].ToString() 
                : "Unknown Action";
                
            var result = new ActionResult
            {
                Success = true,
                Message = $"Readies action: {readiedAction}"
            };
            
            result.Effects.Add($"Ready:{readiedAction}");
            return result;
        }
        
        /// <summary>
        /// Process a chain action
        /// </summary>
        private ActionResult ProcessChainAction(ActionRequest request, CharacterState actorState)
        {
            var result = new ActionResult
            {
                Success = true,
                Message = "Performs a chain action"
            };
            
            result.Effects.Add("Chain Action");
            return result;
        }
        
        /// <summary>
        /// Get ability modifier from character state
        /// </summary>
        private int GetAbilityModifier(CharacterState state, string abilityName)
        {
            if (state.Stats.ContainsKey(abilityName))
            {
                var abilityScore = state.Stats[abilityName];
                return (abilityScore - 10) / 2;
            }
            
            return 0; // Default modifier
        }
        
        /// <summary>
        /// Get proficiency bonus (simplified)
        /// </summary>
        private int GetProficiencyBonus(CharacterState state)
        {
            // In D&D, proficiency bonus is based on character level
            // For simplicity, we'll use a default value
            return 2;
        }
        
        /// <summary>
        /// Check if the actor has advantage on this action type
        /// </summary>
        private bool HasAdvantage(CharacterState state, ActionType actionType)
        {
            // Check for conditions that grant advantage
            if (actionType == ActionType.Attack)
            {
                // Hidden attackers have advantage
                if (state.Conditions.Contains("hidden"))
                    return true;
                    
                // Help action grants advantage
                if (state.Conditions.Contains("helped"))
                    return true;
            }
            
            return false;
        }
        
        /// <summary>
        /// Check if the actor has disadvantage on this action type
        /// </summary>
        private bool HasDisadvantage(CharacterState state, ActionType actionType)
        {
            // Check for conditions that impose disadvantage
            if (actionType == ActionType.Attack)
            {
                if (state.Conditions.Contains("blinded") || 
                    state.Conditions.Contains("poisoned") ||
                    state.Conditions.Contains("restrained"))
                    return true;
            }
            
            return false;
        }
        
        /// <summary>
        /// Get target's armor class
        /// </summary>
        private int GetTargetAC(GameObject target)
        {
            if (target == null)
                return 10; // Default AC
                
            var combatant = target.GetComponent<CombatantComponent>();
            if (combatant != null)
                return combatant.ArmorClass;
                
            return 10; // Default AC
        }
        
        /// <summary>
        /// Calculate weapon damage
        /// </summary>
        private int CalculateWeaponDamage(CharacterState state)
        {
            // Simplified weapon damage (1d6 + modifier)
            return UnityEngine.Random.Range(1, 7);
        }
        
        /// <summary>
        /// Get entity from ID (placeholder)
        /// </summary>
        private GameObject GetEntityFromId(int entityId)
        {
            // This would need to be implemented with proper entity tracking
            return null;
        }
        
        /// <summary>
        /// Create a failed action result
        /// </summary>
        private ActionResult CreateFailedResult(string message)
        {
            return new ActionResult
            {
                Success = false,
                Message = message
            };
        }
    }
} 