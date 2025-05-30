using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.Combat.Models
{
    /// <summary>
    /// Represents a participant in combat with stats and abilities
    /// </summary>
    [Serializable]
    public class Combatant
    {
        [Header("Basic Info")]
        public string Name;
        public int Level;
        public GameObject GameObject;
        
        [Header("Combat Stats")]
        public int MaxHealth;
        public int CurrentHealth;
        public int ArmorClass;
        public int Initiative;
        public int Speed;
        
        [Header("Attributes")]
        public int Strength;
        public int Dexterity;
        public int Constitution;
        public int Intelligence;
        public int Wisdom;
        public int Charisma;
        
        [Header("Combat State")]
        public bool IsAlive => CurrentHealth > 0;
        public bool IsConscious => CurrentHealth > 0;
        public List<StatusEffect> StatusEffects = new List<StatusEffect>();
        public List<CombatAction> AvailableActions = new List<CombatAction>();
        
        /// <summary>
        /// Calculate initiative for turn order
        /// </summary>
        public int CalculateInitiative()
        {
            int dexModifier = (Dexterity - 10) / 2;
            int roll = UnityEngine.Random.Range(1, 21); // d20
            return roll + dexModifier + Initiative;
        }
        
        /// <summary>
        /// Apply damage to this combatant
        /// </summary>
        public void TakeDamage(int damage, DamageType damageType = DamageType.Physical)
        {
            // Apply damage reduction based on armor and resistances
            int finalDamage = CalculateFinalDamage(damage, damageType);
            CurrentHealth = Mathf.Max(0, CurrentHealth - finalDamage);
        }
        
        /// <summary>
        /// Heal this combatant
        /// </summary>
        public void Heal(int amount)
        {
            CurrentHealth = Mathf.Min(MaxHealth, CurrentHealth + amount);
        }
        
        private int CalculateFinalDamage(int baseDamage, DamageType damageType)
        {
            // Basic damage reduction from armor class
            int damageReduction = ArmorClass / 2;
            
            // Apply status effect modifiers
            foreach (var effect in StatusEffects)
            {
                if (effect.Type == StatusEffectType.DamageResistance && effect.DamageType == damageType)
                {
                    baseDamage = baseDamage / 2;
                }
                else if (effect.Type == StatusEffectType.DamageVulnerability && effect.DamageType == damageType)
                {
                    baseDamage = baseDamage * 2;
                }
            }
            
            return Mathf.Max(1, baseDamage - damageReduction);
        }
    }
    
    /// <summary>
    /// Represents an action that can be taken in combat
    /// </summary>
    [Serializable]
    public class CombatAction
    {
        public string Name;
        public string Description;
        public ActionType Type;
        public int Range;
        public int Damage;
        public DamageType DamageType;
        public int ManaCost;
        public float CooldownTime;
        public List<StatusEffect> AppliedEffects = new List<StatusEffect>();
        
        /// <summary>
        /// Check if this action can be used by the given combatant
        /// </summary>
        public bool CanUse(Combatant user)
        {
            // Check mana/resource requirements
            // Check cooldowns
            // Check status effects that might prevent action
            return true; // Simplified for now
        }
        
        /// <summary>
        /// Execute this action against a target
        /// </summary>
        public CombatResult Execute(Combatant user, Combatant target)
        {
            var result = new CombatResult
            {
                Action = this,
                User = user,
                Target = target,
                Success = true
            };
            
            // Calculate hit chance
            if (Type == ActionType.Attack)
            {
                int attackRoll = UnityEngine.Random.Range(1, 21);
                int attackBonus = (user.Strength - 10) / 2; // Simplified
                int totalAttack = attackRoll + attackBonus;
                
                result.Success = totalAttack >= target.ArmorClass;
                
                if (result.Success)
                {
                    int damage = CalculateDamage(user);
                    target.TakeDamage(damage, DamageType);
                    result.Damage = damage;
                }
            }
            
            // Apply status effects
            foreach (var effect in AppliedEffects)
            {
                target.StatusEffects.Add(effect);
            }
            
            return result;
        }
        
        private int CalculateDamage(Combatant user)
        {
            // Base damage plus modifiers
            int baseDamage = Damage;
            
            // Add attribute modifiers based on action type
            if (Type == ActionType.Attack)
            {
                baseDamage += (user.Strength - 10) / 2;
            }
            else if (Type == ActionType.Spell)
            {
                baseDamage += (user.Intelligence - 10) / 2;
            }
            
            return Mathf.Max(1, baseDamage);
        }
    }
    
    /// <summary>
    /// Result of a combat action
    /// </summary>
    [Serializable]
    public class CombatResult
    {
        public CombatAction Action;
        public Combatant User;
        public Combatant Target;
        public bool Success;
        public int Damage;
        public List<StatusEffect> EffectsApplied = new List<StatusEffect>();
        public string Message;
    }
    
    /// <summary>
    /// Represents a status effect affecting a combatant
    /// </summary>
    [Serializable]
    public class StatusEffect
    {
        public string Name;
        public string Description;
        public StatusEffectType Type;
        public DamageType DamageType;
        public int Duration; // in rounds
        public int Magnitude;
        public bool IsBuff;
        
        /// <summary>
        /// Apply this effect's impact for one round
        /// </summary>
        public void ApplyEffect(Combatant target)
        {
            switch (Type)
            {
                case StatusEffectType.Poison:
                    target.TakeDamage(Magnitude, DamageType.Poison);
                    break;
                case StatusEffectType.Regeneration:
                    target.Heal(Magnitude);
                    break;
                case StatusEffectType.Stunned:
                    // Handled by combat system
                    break;
            }
            
            Duration--;
        }
        
        /// <summary>
        /// Check if this effect has expired
        /// </summary>
        public bool IsExpired => Duration <= 0;
    }
    
    /// <summary>
    /// Combat event for logging and UI updates
    /// </summary>
    [Serializable]
    public class CombatEvent
    {
        public CombatEventType Type;
        public Combatant Participant;
        public CombatAction Action;
        public string Message;
        public float Timestamp;
        
        public CombatEvent()
        {
            Timestamp = Time.time;
        }
    }
    
    // Enums
    public enum ActionType
    {
        Attack,
        Spell,
        Skill,
        Item,
        Move,
        Defend,
        Wait
    }
    
    public enum DamageType
    {
        Physical,
        Slashing,
        Piercing,
        Bludgeoning,
        Fire,
        Ice,
        Lightning,
        Poison,
        Psychic,
        Necrotic,
        Radiant,
        Force,
        Acid,
        Thunder,
        True
    }
    
    public enum StatusEffectType
    {
        Poison,
        Regeneration,
        Stunned,
        Paralyzed,
        Blinded,
        Charmed,
        Frightened,
        Grappled,
        Incapacitated,
        Invisible,
        Prone,
        Restrained,
        Unconscious,
        DamageResistance,
        DamageVulnerability,
        AttributeBoost,
        AttributePenalty
    }
    
    public enum CombatEventType
    {
        CombatStarted,
        CombatEnded,
        TurnStarted,
        TurnEnded,
        ActionTaken,
        DamageTaken,
        StatusEffectApplied,
        StatusEffectRemoved,
        ParticipantAdded,
        ParticipantRemoved,
        ParticipantDefeated
    }
} 