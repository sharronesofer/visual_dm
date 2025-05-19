using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Quest
{
    /// <summary>
    /// Manages quest relationships, prerequisites, and dependency tracking.
    /// </summary>
    public class QuestDependencyGraph
    {
        private readonly Dictionary<string, HashSet<string>> _dependencies = new Dictionary<string, HashSet<string>>();
        private readonly Dictionary<string, HashSet<string>> _dependents = new Dictionary<string, HashSet<string>>();

        /// <summary>
        /// Adds a dependency: questId depends on prerequisiteId.
        /// </summary>
        public bool AddDependency(string questId, string prerequisiteId)
        {
            if (questId == prerequisiteId) return false;
            if (!_dependencies.ContainsKey(questId)) _dependencies[questId] = new HashSet<string>();
            if (!_dependents.ContainsKey(prerequisiteId)) _dependents[prerequisiteId] = new HashSet<string>();
            _dependencies[questId].Add(prerequisiteId);
            _dependents[prerequisiteId].Add(questId);
            return !HasCircularDependency(questId);
        }

        /// <summary>
        /// Removes a dependency.
        /// </summary>
        public void RemoveDependency(string questId, string prerequisiteId)
        {
            _dependencies.TryGetValue(questId, out var prereqs);
            prereqs?.Remove(prerequisiteId);
            _dependents.TryGetValue(prerequisiteId, out var dependents);
            dependents?.Remove(questId);
        }

        /// <summary>
        /// Returns true if questId has a circular dependency.
        /// </summary>
        public bool HasCircularDependency(string questId)
        {
            var visited = new HashSet<string>();
            return HasCircularDependencyHelper(questId, visited);
        }

        private bool HasCircularDependencyHelper(string questId, HashSet<string> visited)
        {
            if (!visited.Add(questId)) return true;
            if (!_dependencies.TryGetValue(questId, out var prereqs)) return false;
            foreach (var prereq in prereqs)
            {
                if (HasCircularDependencyHelper(prereq, visited)) return true;
            }
            visited.Remove(questId);
            return false;
        }

        /// <summary>
        /// Returns all prerequisites for a quest.
        /// </summary>
        public IEnumerable<string> GetPrerequisites(string questId)
        {
            return _dependencies.TryGetValue(questId, out var prereqs) ? prereqs : Array.Empty<string>();
        }

        /// <summary>
        /// Returns all dependents for a quest.
        /// </summary>
        public IEnumerable<string> GetDependents(string questId)
        {
            return _dependents.TryGetValue(questId, out var dependents) ? dependents : Array.Empty<string>();
        }

        /// <summary>
        /// Updates quest dependencies when a prerequisite is completed.
        /// </summary>
        public void OnPrerequisiteCompleted(string prerequisiteId)
        {
            foreach (var dependent in GetDependents(prerequisiteId))
            {
                // Custom logic to update dependent quests can be added here
            }
        }
    }
} 