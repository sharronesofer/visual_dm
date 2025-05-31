using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Infrastructure.Core
{
    /// <summary>
    /// High-level combat manager that orchestrates combat encounters
    /// </summary>
    public class CombatManager
    {
        private List<Combatant> _participants = new List<Combatant>();
        private List<Combatant> _turnOrder = new List<Combatant>();
        private int _currentTurnIndex = 0;
        private bool _combatActive = false;
        
        // Events
        public event Action<CombatEvent> OnCombatEvent;
        public event Action<Combatant> OnTurnStarted;
        public event Action<Combatant> OnTurnEnded;
        public event Action OnCombatStarted;
        public event Action OnCombatEnded;
        
        /// <summary>
        /// Add a participant to the combat
        /// </summary>
        public void AddParticipant(Combatant combatant)
        {
            if (combatant != null && !_participants.Contains(combatant))
            {
                _participants.Add(combatant);
                EmitCombatEvent(new CombatEvent
                {
                    Type = CombatEventType.ParticipantAdded,
                    Participant = combatant,
                    Message = $"{combatant.Name} joined the combat"
                });
            }
        }
        
        /// <summary>
        /// Remove a participant from the combat
        /// </summary>
        public void RemoveParticipant(Combatant combatant)
        {
            if (combatant != null && _participants.Contains(combatant))
            {
                _participants.Remove(combatant);
                _turnOrder.Remove(combatant);
                
                EmitCombatEvent(new CombatEvent
                {
                    Type = CombatEventType.ParticipantRemoved,
                    Participant = combatant,
                    Message = $"{combatant.Name} left the combat"
                });
                
                // Adjust turn index if necessary
                if (_currentTurnIndex >= _turnOrder.Count && _turnOrder.Count > 0)
                {
                    _currentTurnIndex = 0;
                }
            }
        }
        
        /// <summary>
        /// Initialize combat with current participants
        /// </summary>
        public void InitializeCombat()
        {
            if (_participants.Count == 0)
            {
                Debug.LogWarning("Cannot initialize combat with no participants");
                return;
            }
            
            // Sort participants by initiative
            _turnOrder.Clear();
            _turnOrder.AddRange(_participants);
            _turnOrder.Sort((a, b) => b.Initiative.CompareTo(a.Initiative));
            
            _currentTurnIndex = 0;
            _combatActive = true;
            
            OnCombatStarted?.Invoke();
            EmitCombatEvent(new CombatEvent
            {
                Type = CombatEventType.CombatStarted,
                Message = "Combat has begun!"
            });
            
            // Start first turn
            if (_turnOrder.Count > 0)
            {
                OnTurnStarted?.Invoke(_turnOrder[_currentTurnIndex]);
            }
        }
        
        /// <summary>
        /// Execute a combat action
        /// </summary>
        public void ExecuteAction(LocalCombatAction action)
        {
            if (action == null || !_combatActive)
                return;
                
            // Validate action
            if (!ValidateAction(action))
            {
                EmitCombatEvent(new CombatEvent
                {
                    Type = CombatEventType.ActionFailed,
                    Participant = action.Actor,
                    Message = $"Invalid action by {action.Actor.Name}"
                });
                return;
            }
            
            // Process the action
            var result = ProcessAction(action);
            
            // Emit action event
            EmitCombatEvent(new CombatEvent
            {
                Type = CombatEventType.ActionExecuted,
                Participant = action.Actor,
                Target = action.Target,
                Message = result.Message,
                Damage = result.Damage
            });
            
            // Apply results
            if (result.Damage > 0 && action.Target != null)
            {
                action.Target.TakeDamage(result.Damage);
                
                if (action.Target.CurrentHP <= 0)
                {
                    EmitCombatEvent(new CombatEvent
                    {
                        Type = CombatEventType.ParticipantDefeated,
                        Participant = action.Target,
                        Message = $"{action.Target.Name} has been defeated!"
                    });
                }
            }
            
            // Check if combat should end
            CheckCombatEndConditions();
        }
        
        /// <summary>
        /// Advance to the next turn
        /// </summary>
        public void NextTurn()
        {
            if (!_combatActive || _turnOrder.Count == 0)
                return;
                
            // End current turn
            var currentParticipant = _turnOrder[_currentTurnIndex];
            OnTurnEnded?.Invoke(currentParticipant);
            
            // Advance to next participant
            _currentTurnIndex = (_currentTurnIndex + 1) % _turnOrder.Count;
            
            // Start next turn
            var nextParticipant = _turnOrder[_currentTurnIndex];
            OnTurnStarted?.Invoke(nextParticipant);
            
            EmitCombatEvent(new CombatEvent
            {
                Type = CombatEventType.TurnChanged,
                Participant = nextParticipant,
                Message = $"It's {nextParticipant.Name}'s turn"
            });
        }
        
        /// <summary>
        /// Get the current turn order
        /// </summary>
        public List<Combatant> GetTurnOrder()
        {
            return new List<Combatant>(_turnOrder);
        }
        
        /// <summary>
        /// Get the current active participant
        /// </summary>
        public Combatant GetCurrentParticipant()
        {
            if (_turnOrder.Count > 0 && _currentTurnIndex < _turnOrder.Count)
                return _turnOrder[_currentTurnIndex];
            return null;
        }
        
        /// <summary>
        /// End combat
        /// </summary>
        public void EndCombat()
        {
            if (!_combatActive)
                return;
                
            _combatActive = false;
            OnCombatEnded?.Invoke();
            
            EmitCombatEvent(new CombatEvent
            {
                Type = CombatEventType.CombatEnded,
                Message = "Combat has ended!"
            });
        }
        
        /// <summary>
        /// Validate if an action can be performed
        /// </summary>
        private bool ValidateAction(LocalCombatAction action)
        {
            // Check if actor is in turn order
            if (!_turnOrder.Contains(action.Actor))
                return false;
                
            // Check if it's the actor's turn (simplified)
            var currentParticipant = GetCurrentParticipant();
            if (currentParticipant != action.Actor)
                return false;
                
            // Check if actor is alive
            if (action.Actor.CurrentHP <= 0)
                return false;
                
            return true;
        }
        
        /// <summary>
        /// Process a combat action and return results
        /// </summary>
        private ActionResult ProcessAction(LocalCombatAction action)
        {
            var result = new ActionResult();
            
            switch (action.Type)
            {
                case CombatActionType.Attack:
                    result = ProcessAttack(action);
                    break;
                    
                case CombatActionType.Defend:
                    result = ProcessDefend(action);
                    break;
                    
                case CombatActionType.Cast:
                    result = ProcessCast(action);
                    break;
                    
                case CombatActionType.Move:
                    result = ProcessMove(action);
                    break;
                    
                default:
                    result.Success = false;
                    result.Message = "Unknown action type";
                    break;
            }
            
            return result;
        }
        
        /// <summary>
        /// Process an attack action
        /// </summary>
        private ActionResult ProcessAttack(LocalCombatAction action)
        {
            var result = new ActionResult();
            
            if (action.Target == null)
            {
                result.Success = false;
                result.Message = "No target for attack";
                return result;
            }
            
            // Simple attack calculation
            var attackRoll = UnityEngine.Random.Range(1, 21);
            var attackBonus = action.Actor.AttackBonus;
            var totalAttack = attackRoll + attackBonus;
            
            if (totalAttack >= action.Target.ArmorClass)
            {
                var damage = UnityEngine.Random.Range(1, action.Actor.DamageRoll + 1) + action.Actor.DamageBonus;
                result.Success = true;
                result.Damage = damage;
                result.Message = $"{action.Actor.Name} hits {action.Target.Name} for {damage} damage!";
            }
            else
            {
                result.Success = true; // Action succeeded but missed
                result.Damage = 0;
                result.Message = $"{action.Actor.Name} misses {action.Target.Name}";
            }
            
            return result;
        }
        
        /// <summary>
        /// Process a defend action
        /// </summary>
        private ActionResult ProcessDefend(LocalCombatAction action)
        {
            var result = new ActionResult
            {
                Success = true,
                Message = $"{action.Actor.Name} takes a defensive stance"
            };
            
            // Could add defensive bonuses here
            return result;
        }
        
        /// <summary>
        /// Process a cast action
        /// </summary>
        private ActionResult ProcessCast(LocalCombatAction action)
        {
            var result = new ActionResult
            {
                Success = true,
                Message = $"{action.Actor.Name} casts a spell"
            };
            
            // Placeholder for spell effects
            return result;
        }
        
        /// <summary>
        /// Process a move action
        /// </summary>
        private ActionResult ProcessMove(LocalCombatAction action)
        {
            var result = new ActionResult
            {
                Success = true,
                Message = $"{action.Actor.Name} moves"
            };
            
            return result;
        }
        
        /// <summary>
        /// Check if combat should end
        /// </summary>
        private void CheckCombatEndConditions()
        {
            // Count alive participants by faction (simplified)
            var aliveParticipants = _participants.FindAll(p => p.CurrentHP > 0);
            
            if (aliveParticipants.Count <= 1)
            {
                EndCombat();
            }
        }
        
        /// <summary>
        /// Emit a combat event
        /// </summary>
        private void EmitCombatEvent(CombatEvent combatEvent)
        {
            OnCombatEvent?.Invoke(combatEvent);
        }
    }
    
    /// <summary>
    /// Represents a combatant in the combat system
    /// </summary>
    [System.Serializable]
    public class Combatant
    {
        public string Name { get; set; }
        public int MaxHP { get; set; }
        public int CurrentHP { get; set; }
        public int ArmorClass { get; set; }
        public int Initiative { get; set; }
        public int AttackBonus { get; set; }
        public int DamageRoll { get; set; } = 6; // d6
        public int DamageBonus { get; set; }
        
        public Combatant(string name, int maxHP, int armorClass)
        {
            Name = name;
            MaxHP = maxHP;
            CurrentHP = maxHP;
            ArmorClass = armorClass;
            Initiative = UnityEngine.Random.Range(1, 21);
            AttackBonus = 2;
            DamageBonus = 1;
        }
        
        public void TakeDamage(int damage)
        {
            CurrentHP = Mathf.Max(0, CurrentHP - damage);
        }
        
        public void Heal(int healing)
        {
            CurrentHP = Mathf.Min(MaxHP, CurrentHP + healing);
        }
        
        public bool IsAlive => CurrentHP > 0;
    }
    
    /// <summary>
    /// Represents a combat action
    /// </summary>
    public class LocalCombatAction
    {
        public string Name { get; set; } = "Unknown Action";
        public string Description { get; set; } = "No description available";
        public int Range { get; set; } = 1;
        public int Damage { get; set; } = 0;
        public string DamageType { get; set; } = "Physical";
        public int ManaCost { get; set; } = 0;
        public CombatActionType Type { get; set; }
        public Combatant Actor { get; set; }
        public Combatant Target { get; set; }
        public Vector3 Position { get; set; }
        public Dictionary<string, object> Parameters { get; set; }
        
        public LocalCombatAction(CombatActionType type, Combatant actor, Combatant target = null)
        {
            Type = type;
            Actor = actor;
            Target = target;
            Parameters = new Dictionary<string, object>();
            
            // Set default name based on type
            Name = type.ToString();
            Description = $"Performs a {type.ToString().ToLower()} action";
        }
    }
    
    /// <summary>
    /// Types of combat actions
    /// </summary>
    public enum CombatActionType
    {
        Attack,
        Defend,
        Cast,
        Move,
        Item,
        Wait
    }
    
    /// <summary>
    /// Result of a combat action
    /// </summary>
    public class ActionResult
    {
        public bool Success { get; set; }
        public int Damage { get; set; }
        public int Healing { get; set; }
        public string Message { get; set; }
        public GameObject TargetEntity { get; set; }
        public List<string> Effects { get; set; }
        
        public ActionResult()
        {
            Effects = new List<string>();
        }
    }
    
    /// <summary>
    /// Combat event for notification system
    /// </summary>
    public class CombatEvent
    {
        public CombatEventType Type { get; set; }
        public Combatant Participant { get; set; }
        public Combatant Target { get; set; }
        public string Message { get; set; }
        public int Damage { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.Now;
    }
    
    /// <summary>
    /// Types of combat events
    /// </summary>
    public enum CombatEventType
    {
        CombatStarted,
        CombatEnded,
        TurnChanged,
        ActionExecuted,
        ActionFailed,
        ParticipantAdded,
        ParticipantRemoved,
        ParticipantDefeated
    }
} 