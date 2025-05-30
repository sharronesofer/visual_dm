using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.Magic.Models
{
    /// <summary>
    /// Magic schools for spell categorization
    /// </summary>
    public enum MagicSchool
    {
        Abjuration,
        Conjuration,
        Divination,
        Enchantment,
        Evocation,
        Illusion,
        Necromancy,
        Transmutation
    }

    /// <summary>
    /// Magic domains for different sources of power
    /// </summary>
    public enum MagicDomain
    {
        Arcane,
        Divine,
        Nature,
        Occult
    }

    /// <summary>
    /// Types of spell components required for casting
    /// </summary>
    public enum ComponentType
    {
        Verbal,
        Somatic,
        Material,
        Focus
    }

    /// <summary>
    /// Types of spell effects
    /// </summary>
    public enum SpellEffectType
    {
        Damage,
        Healing,
        Buff,
        Debuff,
        Control,
        Utility,
        Summoning,
        Teleportation
    }

    /// <summary>
    /// Spell casting result types
    /// </summary>
    public enum CastingResult
    {
        Success,
        Failure,
        CriticalSuccess,
        CriticalFailure,
        InsufficientMana,
        ComponentMissing,
        Interrupted,
        CounterSpelled
    }

    /// <summary>
    /// Represents a magic spell with all its properties
    /// </summary>
    [Serializable]
    public class Spell
    {
        [Header("Basic Info")]
        public string Id;
        public string Name;
        public string Description;
        public int Level;
        public MagicSchool School;
        public MagicDomain Domain;

        [Header("Casting Requirements")]
        public int ManaCost;
        public int ConcentrationCost;
        public float CastingTime;
        public float Range;
        public float Duration;
        public List<ComponentType> Components = new List<ComponentType>();
        public string MaterialComponent;

        [Header("Effects")]
        public List<SpellEffect> Effects = new List<SpellEffect>();
        public string TargetType; // Self, Single, Multiple, Area
        public bool RequiresLineOfSight;
        public bool RequiresConcentration;

        [Header("Scaling")]
        public bool CanUpcast;
        public Dictionary<string, object> UpcastEffects = new Dictionary<string, object>();

        /// <summary>
        /// Calculate the total mana cost including upcasting
        /// </summary>
        public int CalculateManaCost(int upcastLevel = 0)
        {
            return ManaCost + (upcastLevel * 2); // Base cost + 2 per upcast level
        }

        /// <summary>
        /// Check if the spell can be cast with available resources
        /// </summary>
        public bool CanCast(Spellcaster caster, int upcastLevel = 0)
        {
            int totalCost = CalculateManaCost(upcastLevel);
            return caster.CurrentMana >= totalCost && 
                   caster.CurrentConcentration >= ConcentrationCost &&
                   caster.KnownSpells.Contains(this.Id);
        }
    }

    /// <summary>
    /// Represents a spell effect with its properties
    /// </summary>
    [Serializable]
    public class SpellEffect
    {
        public SpellEffectType Type;
        public string Description;
        public int Value;
        public float Duration;
        public string DamageType;
        public bool RequiresSavingThrow;
        public string SavingThrowType;
        public int SavingThrowDC;
        public Dictionary<string, object> Properties = new Dictionary<string, object>();

        /// <summary>
        /// Apply this effect to a target
        /// </summary>
        public void Apply(GameObject target, Spellcaster caster)
        {
            // Implementation would depend on the specific effect type
            switch (Type)
            {
                case SpellEffectType.Damage:
                    ApplyDamage(target, Value, DamageType);
                    break;
                case SpellEffectType.Healing:
                    ApplyHealing(target, Value);
                    break;
                case SpellEffectType.Buff:
                case SpellEffectType.Debuff:
                    ApplyStatusEffect(target, Duration);
                    break;
                // Add other effect types as needed
            }
        }

        private void ApplyDamage(GameObject target, int damage, string damageType)
        {
            // Damage application logic
            Debug.Log($"Applying {damage} {damageType} damage to {target.name}");
        }

        private void ApplyHealing(GameObject target, int healing)
        {
            // Healing application logic
            Debug.Log($"Healing {target.name} for {healing} points");
        }

        private void ApplyStatusEffect(GameObject target, float duration)
        {
            // Status effect application logic
            Debug.Log($"Applying {Type} effect to {target.name} for {duration} seconds");
        }
    }

    /// <summary>
    /// Represents a character capable of casting spells
    /// </summary>
    [Serializable]
    public class Spellcaster
    {
        [Header("Basic Info")]
        public string Name;
        public int Level;
        public MagicDomain PrimaryDomain;
        public List<MagicDomain> SecondaryDomains = new List<MagicDomain>();

        [Header("Resources")]
        public int MaxMana;
        public int CurrentMana;
        public int MaxConcentration;
        public int CurrentConcentration;
        public int ManaRegenRate;
        public int ConcentrationRegenRate;

        [Header("Spells")]
        public List<string> KnownSpells = new List<string>();
        public List<string> PreparedSpells = new List<string>();
        public Dictionary<int, int> SpellSlots = new Dictionary<int, int>(); // Level -> Available slots
        public List<ActiveSpellEffect> ActiveEffects = new List<ActiveSpellEffect>();

        [Header("Abilities")]
        public int SpellAttackBonus;
        public int SpellSaveDC;
        public int SpellcastingAbilityModifier;

        /// <summary>
        /// Attempt to cast a spell
        /// </summary>
        public CastingResult CastSpell(Spell spell, GameObject target = null, int upcastLevel = 0)
        {
            // Check if spell can be cast
            if (!spell.CanCast(this, upcastLevel))
            {
                return CastingResult.InsufficientMana;
            }

            // Check if spell is prepared (if using preparation system)
            if (PreparedSpells.Count > 0 && !PreparedSpells.Contains(spell.Id))
            {
                return CastingResult.Failure;
            }

            // Consume resources
            int totalManaCost = spell.CalculateManaCost(upcastLevel);
            CurrentMana -= totalManaCost;
            CurrentConcentration -= spell.ConcentrationCost;

            // Apply spell effects
            foreach (var effect in spell.Effects)
            {
                effect.Apply(target, this);
            }

            // Add concentration effect if needed
            if (spell.RequiresConcentration)
            {
                var concentrationEffect = new ActiveSpellEffect
                {
                    SpellId = spell.Id,
                    Duration = spell.Duration,
                    RemainingDuration = spell.Duration,
                    RequiresConcentration = true
                };
                ActiveEffects.Add(concentrationEffect);
            }

            return CastingResult.Success;
        }

        /// <summary>
        /// Restore mana over time
        /// </summary>
        public void RegenerateMana(float deltaTime)
        {
            if (CurrentMana < MaxMana)
            {
                CurrentMana = Mathf.Min(MaxMana, CurrentMana + Mathf.RoundToInt(ManaRegenRate * deltaTime));
            }
        }

        /// <summary>
        /// Restore concentration over time
        /// </summary>
        public void RegenerateConcentration(float deltaTime)
        {
            if (CurrentConcentration < MaxConcentration)
            {
                CurrentConcentration = Mathf.Min(MaxConcentration, 
                    CurrentConcentration + Mathf.RoundToInt(ConcentrationRegenRate * deltaTime));
            }
        }

        /// <summary>
        /// Update active spell effects
        /// </summary>
        public void UpdateActiveEffects(float deltaTime)
        {
            for (int i = ActiveEffects.Count - 1; i >= 0; i--)
            {
                var effect = ActiveEffects[i];
                effect.RemainingDuration -= deltaTime;
                
                if (effect.RemainingDuration <= 0)
                {
                    // Effect expired
                    if (effect.RequiresConcentration)
                    {
                        CurrentConcentration += effect.ConcentrationCost;
                    }
                    ActiveEffects.RemoveAt(i);
                }
            }
        }

        /// <summary>
        /// Learn a new spell
        /// </summary>
        public bool LearnSpell(string spellId)
        {
            if (!KnownSpells.Contains(spellId))
            {
                KnownSpells.Add(spellId);
                return true;
            }
            return false;
        }

        /// <summary>
        /// Prepare a spell for casting
        /// </summary>
        public bool PrepareSpell(string spellId)
        {
            if (KnownSpells.Contains(spellId) && !PreparedSpells.Contains(spellId))
            {
                PreparedSpells.Add(spellId);
                return true;
            }
            return false;
        }
    }

    /// <summary>
    /// Represents an active spell effect on a target
    /// </summary>
    [Serializable]
    public class ActiveSpellEffect
    {
        public string SpellId;
        public string EffectId;
        public float Duration;
        public float RemainingDuration;
        public bool RequiresConcentration;
        public int ConcentrationCost;
        public GameObject Target;
        public Spellcaster Caster;
        public Dictionary<string, object> Properties = new Dictionary<string, object>();

        /// <summary>
        /// Check if the effect is still active
        /// </summary>
        public bool IsActive => RemainingDuration > 0;

        /// <summary>
        /// Dispel this effect
        /// </summary>
        public void Dispel()
        {
            RemainingDuration = 0;
            if (RequiresConcentration && Caster != null)
            {
                Caster.CurrentConcentration += ConcentrationCost;
            }
        }
    }

    /// <summary>
    /// Result of a spell casting attempt
    /// </summary>
    [Serializable]
    public class SpellCastingResult
    {
        public CastingResult Result;
        public Spell Spell;
        public Spellcaster Caster;
        public GameObject Target;
        public int UpcastLevel;
        public List<SpellEffect> AppliedEffects = new List<SpellEffect>();
        public string Message;
        public float Timestamp;

        public SpellCastingResult(CastingResult result, Spell spell, Spellcaster caster)
        {
            Result = result;
            Spell = spell;
            Caster = caster;
            Timestamp = Time.time;
        }
    }

    /// <summary>
    /// Magic event for system communication
    /// </summary>
    [Serializable]
    public class MagicEvent
    {
        public string EventType;
        public Spellcaster Caster;
        public Spell Spell;
        public GameObject Target;
        public SpellCastingResult Result;
        public float Timestamp;
        public Dictionary<string, object> Data = new Dictionary<string, object>();

        public MagicEvent(string eventType)
        {
            EventType = eventType;
            Timestamp = Time.time;
        }
    }

    /// <summary>
    /// Magic system state for tracking overall magic activity
    /// </summary>
    [Serializable]
    public class MagicSystemState
    {
        public List<Spellcaster> ActiveCasters = new List<Spellcaster>();
        public List<ActiveSpellEffect> GlobalEffects = new List<ActiveSpellEffect>();
        public Dictionary<string, Spell> SpellDatabase = new Dictionary<string, Spell>();
        public List<MagicEvent> RecentEvents = new List<MagicEvent>();
        public bool MagicSuppressed;
        public float MagicIntensity = 1.0f;

        /// <summary>
        /// Add a magic event to the system
        /// </summary>
        public void AddEvent(MagicEvent magicEvent)
        {
            RecentEvents.Add(magicEvent);
            
            // Keep only recent events (last 100)
            if (RecentEvents.Count > 100)
            {
                RecentEvents.RemoveAt(0);
            }
        }

        /// <summary>
        /// Update all active effects in the system
        /// </summary>
        public void UpdateSystem(float deltaTime)
        {
            // Update all casters
            foreach (var caster in ActiveCasters)
            {
                caster.RegenerateMana(deltaTime);
                caster.RegenerateConcentration(deltaTime);
                caster.UpdateActiveEffects(deltaTime);
            }

            // Update global effects
            for (int i = GlobalEffects.Count - 1; i >= 0; i--)
            {
                var effect = GlobalEffects[i];
                effect.RemainingDuration -= deltaTime;
                
                if (effect.RemainingDuration <= 0)
                {
                    GlobalEffects.RemoveAt(i);
                }
            }
        }
    }
} 