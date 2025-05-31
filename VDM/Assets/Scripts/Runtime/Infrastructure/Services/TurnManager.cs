using System.Collections.Generic;
using System.Linq;
using System;
using UnityEngine;


namespace VDM.Infrastructure.Core
{
    /// <summary>
    /// Manages turn order and initiative for turn-based combat
    /// </summary>
    public class TurnManager
    {
        private List<GameObject> _combatants = new List<GameObject>();
        private List<GameObject> _turnOrder = new List<GameObject>();
        private int _currentTurnIndex = 0;
        private bool _combatActive = false;
        
        // Events
        public event Action<GameObject> OnTurnStarted;
        public event Action<GameObject> OnTurnEnded;
        public event Action OnRoundCompleted;
        
        /// <summary>
        /// Current entity whose turn it is
        /// </summary>
        public GameObject CurrentTurn => _turnOrder.Count > 0 && _currentTurnIndex < _turnOrder.Count 
            ? _turnOrder[_currentTurnIndex] 
            : null;
        
        /// <summary>
        /// Add a combatant to the turn management system
        /// </summary>
        public void AddCombatant(GameObject combatant)
        {
            if (combatant == null || _combatants.Contains(combatant))
                return;
                
            _combatants.Add(combatant);
            
            // If combat is active, insert into turn order based on initiative
            if (_combatActive)
            {
                InsertIntoTurnOrder(combatant);
            }
        }
        
        /// <summary>
        /// Remove a combatant from the turn management system
        /// </summary>
        public void RemoveCombatant(GameObject combatant)
        {
            if (combatant == null)
                return;
                
            _combatants.Remove(combatant);
            
            if (_turnOrder.Contains(combatant))
            {
                var index = _turnOrder.IndexOf(combatant);
                _turnOrder.Remove(combatant);
                
                // Adjust current turn index if necessary
                if (index < _currentTurnIndex)
                {
                    _currentTurnIndex--;
                }
                else if (index == _currentTurnIndex && _currentTurnIndex >= _turnOrder.Count)
                {
                    _currentTurnIndex = 0; // Wrap to beginning
                }
            }
        }
        
        /// <summary>
        /// Initialize turn order based on initiative values
        /// </summary>
        public void InitializeTurnOrder()
        {
            _turnOrder.Clear();
            _currentTurnIndex = 0;
            
            // Sort combatants by initiative (higher goes first)
            var sortedCombatants = _combatants
                .Where(c => c != null)
                .OrderByDescending(GetInitiative)
                .ThenByDescending(GetDexterity) // Tiebreaker
                .ToList();
                
            _turnOrder.AddRange(sortedCombatants);
            _combatActive = true;
            
            // Start the first turn
            if (_turnOrder.Count > 0)
            {
                OnTurnStarted?.Invoke(CurrentTurn);
            }
        }
        
        /// <summary>
        /// End the current turn and advance to the next
        /// </summary>
        public void EndCurrentTurn()
        {
            if (!_combatActive || _turnOrder.Count == 0)
                return;
                
            var currentEntity = CurrentTurn;
            OnTurnEnded?.Invoke(currentEntity);
            
            // Advance to next turn
            _currentTurnIndex++;
            
            // Check if round completed
            if (_currentTurnIndex >= _turnOrder.Count)
            {
                _currentTurnIndex = 0;
                OnRoundCompleted?.Invoke();
            }
            
            // Start next turn
            if (_turnOrder.Count > 0)
            {
                OnTurnStarted?.Invoke(CurrentTurn);
            }
        }
        
        /// <summary>
        /// Get a snapshot of the current turn order
        /// </summary>
        public List<GameObject> GetTurnOrderSnapshot()
        {
            return new List<GameObject>(_turnOrder);
        }
        
        /// <summary>
        /// Reset the turn manager
        /// </summary>
        public void Reset()
        {
            _combatants.Clear();
            _turnOrder.Clear();
            _currentTurnIndex = 0;
            _combatActive = false;
        }
        
        /// <summary>
        /// Check if it's a specific entity's turn
        /// </summary>
        public bool IsEntityTurn(GameObject entity)
        {
            return CurrentTurn == entity;
        }
        
        /// <summary>
        /// Get the initiative value for an entity
        /// </summary>
        private int GetInitiative(GameObject entity)
        {
            // Try to get initiative from various components
            var combatant = entity.GetComponent<CombatantComponent>();
            if (combatant != null)
                return combatant.Initiative;
                
            var character = entity.GetComponent<CharacterComponent>();
            if (character != null)
                return character.GetInitiative();
                
            // Default initiative calculation: DEX modifier + d20
            var dex = GetDexterity(entity);
            var dexModifier = (dex - 10) / 2;
            return UnityEngine.Random.Range(1, 21) + dexModifier;
        }
        
        /// <summary>
        /// Get the dexterity value for an entity (used for initiative tiebreaking)
        /// </summary>
        private int GetDexterity(GameObject entity)
        {
            var combatant = entity.GetComponent<CombatantComponent>();
            if (combatant != null)
                return combatant.Dexterity;
                
            var character = entity.GetComponent<CharacterComponent>();
            if (character != null)
                return character.GetDexterity();
                
            // Default dexterity
            return 10;
        }
        
        /// <summary>
        /// Insert a combatant into the existing turn order based on initiative
        /// </summary>
        private void InsertIntoTurnOrder(GameObject combatant)
        {
            var initiative = GetInitiative(combatant);
            var dexterity = GetDexterity(combatant);
            
            // Find the correct position to insert
            int insertIndex = _turnOrder.Count;
            for (int i = 0; i < _turnOrder.Count; i++)
            {
                var existingInitiative = GetInitiative(_turnOrder[i]);
                var existingDexterity = GetDexterity(_turnOrder[i]);
                
                if (initiative > existingInitiative || 
                    (initiative == existingInitiative && dexterity > existingDexterity))
                {
                    insertIndex = i;
                    break;
                }
            }
            
            _turnOrder.Insert(insertIndex, combatant);
            
            // Adjust current turn index if necessary
            if (insertIndex <= _currentTurnIndex)
            {
                _currentTurnIndex++;
            }
        }
    }
    
    /// <summary>
    /// Component for basic combatant data
    /// </summary>
    public class CombatantComponent : MonoBehaviour
    {
        [Header("Combat Stats")]
        public int Initiative = 0;
        public int Dexterity = 10;
        public int ArmorClass = 10;
        public int MaxHP = 100;
        
        [Header("Current State")]
        public int CurrentHP = 100;
        public bool IsAlive = true;
        
        private void Awake()
        {
            CurrentHP = MaxHP;
        }
        
        public void TakeDamage(int damage)
        {
            CurrentHP = Mathf.Max(0, CurrentHP - damage);
            if (CurrentHP <= 0)
            {
                IsAlive = false;
            }
        }
        
        public void Heal(int healing)
        {
            CurrentHP = Mathf.Min(MaxHP, CurrentHP + healing);
            if (CurrentHP > 0)
            {
                IsAlive = true;
            }
        }
    }
    
    /// <summary>
    /// More complex character component (placeholder for future expansion)
    /// </summary>
    public class CharacterComponent : MonoBehaviour
    {
        [Header("Ability Scores")]
        public int Strength = 10;
        public int Dexterity = 10;
        public int Constitution = 10;
        public int Intelligence = 10;
        public int Wisdom = 10;
        public int Charisma = 10;
        
        public int GetInitiative()
        {
            var dexModifier = (Dexterity - 10) / 2;
            return UnityEngine.Random.Range(1, 21) + dexModifier;
        }
        
        public int GetDexterity()
        {
            return Dexterity;
        }
        
        public int GetAbilityModifier(int abilityScore)
        {
            return (abilityScore - 10) / 2;
        }
    }
} 