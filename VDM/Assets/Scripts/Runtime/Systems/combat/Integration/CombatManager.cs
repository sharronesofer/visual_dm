using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Systems.Combat.Models;


namespace VDM.Systems.Combat.Integration
{
    /// <summary>
    /// High-level combat manager that orchestrates combat encounters
    /// Legacy combat manager - being replaced by CombatSystemManager
    /// </summary>
    [System.Obsolete("Use CombatSystemManager instead")]
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
                
                // Check if combat should end
                CheckCombatEnd();
            }
        }
        
        /// <summary>
        /// Start the combat encounter
        /// </summary>
        public void StartCombat()
        {
            if (_combatActive || _participants.Count < 2)
            {
                Debug.LogWarning("Cannot start combat: already active or insufficient participants");
                return;
            }
            
            _combatActive = true;
            CalculateInitiativeOrder();
            _currentTurnIndex = 0;
            
            OnCombatStarted?.Invoke();
            EmitCombatEvent(new CombatEvent
            {
                Type = CombatEventType.CombatStarted,
                Message = "Combat has begun!"
            });
            
            StartNextTurn();
        }
        
        /// <summary>
        /// End the combat encounter
        /// </summary>
        public void EndCombat()
        {
            if (!_combatActive)
            {
                return;
            }
            
            _combatActive = false;
            _currentTurnIndex = 0;
            
            OnCombatEnded?.Invoke();
            EmitCombatEvent(new CombatEvent
            {
                Type = CombatEventType.CombatEnded,
                Message = "Combat has ended!"
            });
        }
        
        /// <summary>
        /// Execute a combat action
        /// </summary>
        public CombatResult ExecuteAction(Combatant actor, VDM.DTOs.Combat.CombatActionDTO action, Combatant target = null)
        {
            if (!_combatActive || actor == null || action == null)
            {
                return new CombatResult
                {
                    Success = false,
                    Message = "Invalid action parameters"
                };
            }
            
            // Execute the action
            var result = action.Execute(actor, target);
            
            // Emit combat event
            EmitCombatEvent(new CombatEvent
            {
                Type = CombatEventType.ActionTaken,
                Participant = actor,
                Action = action,
                Message = result.Message ?? $"{actor.Name} used {action.Name}"
            });
            
            // Check for combat end conditions
            CheckCombatEnd();
            
            return result;
        }
        
        /// <summary>
        /// Advance to the next turn
        /// </summary>
        public void NextTurn()
        {
            if (!_combatActive || _turnOrder.Count == 0)
            {
                return;
            }
            
            // End current turn
            var currentCombatant = GetCurrentTurnCombatant();
            if (currentCombatant != null)
            {
                OnTurnEnded?.Invoke(currentCombatant);
            }
            
            // Advance to next turn
            _currentTurnIndex = (_currentTurnIndex + 1) % _turnOrder.Count;
            
            StartNextTurn();
        }
        
        /// <summary>
        /// Get the combatant whose turn it currently is
        /// </summary>
        public Combatant GetCurrentTurnCombatant()
        {
            if (!_combatActive || _turnOrder.Count == 0 || _currentTurnIndex >= _turnOrder.Count)
            {
                return null;
            }
            
            return _turnOrder[_currentTurnIndex];
        }
        
        /// <summary>
        /// Get all participants in the combat
        /// </summary>
        public List<Combatant> GetParticipants()
        {
            return new List<Combatant>(_participants);
        }
        
        /// <summary>
        /// Get the current turn order
        /// </summary>
        public List<Combatant> GetTurnOrder()
        {
            return new List<Combatant>(_turnOrder);
        }
        
        /// <summary>
        /// Check if combat is currently active
        /// </summary>
        public bool IsCombatActive()
        {
            return _combatActive;
        }
        
        private void CalculateInitiativeOrder()
        {
            _turnOrder.Clear();
            _turnOrder.AddRange(_participants);
            
            // Sort by initiative (highest first)
            _turnOrder.Sort((a, b) => b.CalculateInitiative().CompareTo(a.CalculateInitiative()));
        }
        
        private void StartNextTurn()
        {
            var currentCombatant = GetCurrentTurnCombatant();
            if (currentCombatant != null)
            {
                OnTurnStarted?.Invoke(currentCombatant);
                EmitCombatEvent(new CombatEvent
                {
                    Type = CombatEventType.TurnStarted,
                    Participant = currentCombatant,
                    Message = $"It's {currentCombatant.Name}'s turn"
                });
            }
        }
        
        private void CheckCombatEnd()
        {
            if (!_combatActive)
            {
                return;
            }
            
            // Check if only one faction remains
            var aliveCombatants = _participants.FindAll(c => c.IsAlive);
            
            if (aliveCombatants.Count <= 1)
            {
                EndCombat();
            }
        }
        
        private void EmitCombatEvent(CombatEvent combatEvent)
        {
            OnCombatEvent?.Invoke(combatEvent);
        }
    }
} 