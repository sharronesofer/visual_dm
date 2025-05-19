using System.Collections.Generic;
using System.Linq;

namespace VDM.Combat
{
    /// <summary>
    /// Manages the turn order queue for all combatants in a battle.
    /// </summary>
    public class TurnQueue
    {
        private readonly List<ICombatant> _queue = new List<ICombatant>();
        private int _currentIndex = 0;

        /// <summary>
        /// Gets the current combatant whose turn it is.
        /// </summary>
        public ICombatant Current => _queue.Count > 0 ? _queue[_currentIndex] : null;

        /// <summary>
        /// Returns a read-only snapshot of the current turn order.
        /// </summary>
        public IReadOnlyList<ICombatant> Order => _queue.AsReadOnly();

        /// <summary>
        /// Adds a combatant to the queue and re-sorts by initiative.
        /// </summary>
        public void AddCombatant(ICombatant combatant)
        {
            if (!_queue.Contains(combatant))
            {
                _queue.Add(combatant);
                SortQueue();
            }
        }

        /// <summary>
        /// Removes a combatant from the queue.
        /// </summary>
        public void RemoveCombatant(ICombatant combatant)
        {
            int idx = _queue.IndexOf(combatant);
            if (idx >= 0)
            {
                _queue.RemoveAt(idx);
                if (_currentIndex >= _queue.Count)
                    _currentIndex = 0;
            }
        }

        /// <summary>
        /// Advances to the next combatant in the queue.
        /// </summary>
        public void NextTurn()
        {
            if (_queue.Count == 0) return;
            _currentIndex = (_currentIndex + 1) % _queue.Count;
        }

        /// <summary>
        /// Re-sorts the queue by initiative (descending).
        /// </summary>
        public void SortQueue()
        {
            _queue.Sort((a, b) => b.Initiative.CompareTo(a.Initiative));
            _currentIndex = 0;
        }

        /// <summary>
        /// Reorders the queue to move a combatant to a new position (for interrupts/delays).
        /// </summary>
        public void MoveCombatant(ICombatant combatant, int newIndex)
        {
            int oldIndex = _queue.IndexOf(combatant);
            if (oldIndex < 0 || newIndex < 0 || newIndex >= _queue.Count) return;
            _queue.RemoveAt(oldIndex);
            _queue.Insert(newIndex, combatant);
            if (_currentIndex >= _queue.Count)
                _currentIndex = 0;
        }
    }
} 