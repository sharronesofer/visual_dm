using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems
{
    /// <summary>
    /// Manages advanced unit selection modes: single, multi, area, path, and formation.
    /// Integrates with coordinate/grid systems via public interfaces. Runtime-only, modular, and extensible.
    /// </summary>
    public class UnitSelectionManager : MonoBehaviour
    {
        public enum SelectionMode
        {
            Single,
            Multi,
            Area,
            Path,
            Formation
        }

        public SelectionMode CurrentMode { get; set; } = SelectionMode.Single;

        // Selected units
        private readonly HashSet<ISelectableUnit> selectedUnits = new HashSet<ISelectableUnit>();

        // For area selection
        private Vector2 areaStart;
        private Vector2 areaEnd;
        private bool isAreaSelecting = false;

        // For path selection
        private List<Vector2> pathPoints = new List<Vector2>();
        private bool isPathSelecting = false;

        // For formation selection
        private List<ISelectableUnit> formationUnits = new List<ISelectableUnit>();
        private FormationType currentFormation = FormationType.Line;
        public enum FormationType { Line, Circle }

        // Reference to coordinate/grid system (set via inspector or code)
        public IGridSystem GridSystem { get; set; }

        // Selection events
        public event Action<HashSet<ISelectableUnit>> OnSelectionChanged;
        // Event for when a selection is about to change (before)
        public event Action<HashSet<ISelectableUnit>> OnSelectionChanging;
        // Event for when a group is assigned or recalled
        public event Action<int, HashSet<ISelectableUnit>> OnGroupChanged;
        // Event for accessibility (e.g., screen reader, haptic feedback)
        public event Action<string> OnAccessibilityEvent;

        // Selection filters
        private readonly List<ISelectionFilter> activeFilters = new List<ISelectionFilter>();

        // Selection history
        private readonly List<SelectionHistoryEntry> selectionHistory = new List<SelectionHistoryEntry>();
        private int historyIndex = -1;
        public int MaxHistoryDepth { get; set; } = 10;

        // Selection groups (1-9, with support for nested/hierarchical groups)
        private readonly Dictionary<int, SelectionGroup> selectionGroups = new Dictionary<int, SelectionGroup>();

        /// <summary>
        /// Register a new filter to be applied to selection.
        /// </summary>
        public void AddFilter(ISelectionFilter filter)
        {
            if (!activeFilters.Contains(filter))
                activeFilters.Add(filter);
        }

        /// <summary>
        /// Remove a filter from the active filter list.
        /// </summary>
        public void RemoveFilter(ISelectionFilter filter)
        {
            activeFilters.Remove(filter);
        }

        /// <summary>
        /// Apply all active filters to a set of units.
        /// </summary>
        private HashSet<ISelectableUnit> ApplyFilters(IEnumerable<ISelectableUnit> units)
        {
            var filtered = new HashSet<ISelectableUnit>(units);
            foreach (var filter in activeFilters)
            {
                filtered = filter.Apply(filtered);
            }
            return filtered;
        }

        /// <summary>
        /// Assigns the current selection to a group (1-9). Overwrites previous group.
        /// </summary>
        public void AssignGroup(int groupNumber)
        {
            if (groupNumber < 1 || groupNumber > 9) return;
            selectionGroups[groupNumber] = new SelectionGroup(new HashSet<ISelectableUnit>(selectedUnits));
            OnGroupChanged?.Invoke(groupNumber, new HashSet<ISelectableUnit>(selectedUnits));
            OnAccessibilityEvent?.Invoke($"Assigned {selectedUnits.Count} unit(s) to group {groupNumber}");
        }

        /// <summary>
        /// Recalls a group (1-9) and selects its units.
        /// </summary>
        public void RecallGroup(int groupNumber)
        {
            if (selectionGroups.TryGetValue(groupNumber, out var group))
            {
                ChangeSelection(new HashSet<ISelectableUnit>(group.Units), $"Recalled group {groupNumber} with {group.Units.Count} unit(s)");
                OnGroupChanged?.Invoke(groupNumber, new HashSet<ISelectableUnit>(group.Units));
            }
        }

        /// <summary>
        /// Adds units to an existing group (1-9).
        /// </summary>
        public void AddToGroup(int groupNumber, IEnumerable<ISelectableUnit> units)
        {
            if (groupNumber < 1 || groupNumber > 9) return;
            if (!selectionGroups.ContainsKey(groupNumber))
                selectionGroups[groupNumber] = new SelectionGroup();
            foreach (var unit in units)
                selectionGroups[groupNumber].Units.Add(unit);
        }

        /// <summary>
        /// Removes units from a group (1-9).
        /// </summary>
        public void RemoveFromGroup(int groupNumber, IEnumerable<ISelectableUnit> units)
        {
            if (groupNumber < 1 || groupNumber > 9) return;
            if (!selectionGroups.ContainsKey(groupNumber)) return;
            foreach (var unit in units)
                selectionGroups[groupNumber].Units.Remove(unit);
        }

        /// <summary>
        /// Supports nested/hierarchical grouping by allowing groups to reference other groups.
        /// </summary>
        public void AddGroupToGroup(int parentGroup, int childGroup)
        {
            if (parentGroup < 1 || parentGroup > 9 || childGroup < 1 || childGroup > 9) return;
            if (!selectionGroups.ContainsKey(parentGroup))
                selectionGroups[parentGroup] = new SelectionGroup();
            if (selectionGroups.TryGetValue(childGroup, out var child))
                selectionGroups[parentGroup].NestedGroups.Add(childGroup);
        }

        /// <summary>
        /// Gets all units in a group, including nested groups.
        /// </summary>
        public HashSet<ISelectableUnit> GetAllUnitsInGroup(int groupNumber)
        {
            var result = new HashSet<ISelectableUnit>();
            var visited = new HashSet<int>();
            CollectUnitsRecursive(groupNumber, result, visited);
            return result;
        }

        private void CollectUnitsRecursive(int groupNumber, HashSet<ISelectableUnit> result, HashSet<int> visited)
        {
            if (visited.Contains(groupNumber)) return;
            visited.Add(groupNumber);
            if (!selectionGroups.TryGetValue(groupNumber, out var group)) return;
            foreach (var unit in group.Units)
                result.Add(unit);
            foreach (var nested in group.NestedGroups)
                CollectUnitsRecursive(nested, result, visited);
        }

        // Hotkey support (call from Update or input system)
        private void HandleGroupHotkeys()
        {
            for (int i = 1; i <= 9; i++)
            {
                if (Core.GetKeyDown(KeyCode.Alpha0 + i))
                {
                    if (Core.GetKey(KeyCode.LeftControl) || Core.GetKey(KeyCode.RightControl))
                        AssignGroup(i); // Ctrl+Number assigns
                    else
                        RecallGroup(i); // Number recalls
                }
            }
        }

        void Update()
        {
            HandleGroupHotkeys();
            switch (CurrentMode)
            {
                case SelectionMode.Single:
                    HandleSingleSelection();
                    break;
                case SelectionMode.Multi:
                    HandleMultiSelection();
                    break;
                case SelectionMode.Area:
                    HandleAreaSelection();
                    break;
                case SelectionMode.Path:
                    HandlePathSelection();
                    break;
                case SelectionMode.Formation:
                    HandleFormationSelection();
                    break;
            }
        }

        private void HandleSingleSelection()
        {
            if (Core.GetMouseButtonDown(0))
            {
                var unit = RaycastUnitAtMouse();
                if (unit != null)
                {
                    var filtered = ApplyFilters(new HashSet<ISelectableUnit> { unit });
                    ChangeSelection(filtered, $"Selected {filtered.Count} unit(s)");
                }
            }
        }

        private void HandleMultiSelection()
        {
            if (Core.GetMouseButtonDown(0))
            {
                var unit = RaycastUnitAtMouse();
                if (unit != null)
                {
                    var temp = new HashSet<ISelectableUnit>(selectedUnits);
                    if (Core.GetKey(KeyCode.LeftShift) || Core.GetKey(KeyCode.RightShift))
                        temp.Add(unit);
                    else
                    {
                        temp.Clear();
                        temp.Add(unit);
                    }
                    var filtered = ApplyFilters(temp);
                    ChangeSelection(filtered, $"Selected {filtered.Count} unit(s)");
                }
            }
        }

        private void HandleAreaSelection()
        {
            if (Core.GetMouseButtonDown(0))
            {
                isAreaSelecting = true;
                areaStart = GetMouseWorldPosition();
            }
            if (Core.GetMouseButton(0) && isAreaSelecting)
            {
                areaEnd = GetMouseWorldPosition();
                // Optionally: Draw selection rectangle for feedback
            }
            if (Core.GetMouseButtonUp(0) && isAreaSelecting)
            {
                isAreaSelecting = false;
                var units = GetUnitsInArea(areaStart, areaEnd);
                var filtered = ApplyFilters(units);
                ChangeSelection(filtered, $"Selected {filtered.Count} unit(s) in area");
            }
        }

        private void HandlePathSelection()
        {
            if (Core.GetMouseButtonDown(0))
            {
                isPathSelecting = true;
                pathPoints.Clear();
                pathPoints.Add(GetMouseWorldPosition());
            }
            if (Core.GetMouseButton(0) && isPathSelecting)
            {
                pathPoints.Add(GetMouseWorldPosition());
                // Optionally: Draw path for feedback
            }
            if (Core.GetMouseButtonUp(0) && isPathSelecting)
            {
                isPathSelecting = false;
                var units = GetUnitsAlongPath(pathPoints);
                var filtered = ApplyFilters(units);
                ChangeSelection(filtered, $"Selected {filtered.Count} unit(s) along path");
            }
        }

        private void HandleFormationSelection()
        {
            // Example: Select units and arrange them in a formation
            // This is a placeholder for formation logic
            // Could be triggered by a hotkey or UI
        }

        private ISelectableUnit RaycastUnitAtMouse()
        {
            Vector2 mousePos = GetMouseWorldPosition();
            var hit = Physics2D.Raycast(mousePos, Vector2.zero);
            if (hit.collider != null)
            {
                return hit.collider.GetComponent<ISelectableUnit>();
            }
            return null;
        }

        private Vector2 GetMouseWorldPosition()
        {
            return Camera.main.ScreenToWorldPoint(Core.mousePosition);
        }

        private IEnumerable<ISelectableUnit> GetUnitsInArea(Vector2 start, Vector2 end)
        {
            // Use grid system or Physics2D.OverlapArea for performance
            var min = Vector2.Min(start, end);
            var max = Vector2.Max(start, end);
            var colliders = Physics2D.OverlapAreaAll(min, max);
            foreach (var col in colliders)
            {
                var unit = col.GetComponent<ISelectableUnit>();
                if (unit != null)
                    yield return unit;
            }
        }

        private IEnumerable<ISelectableUnit> GetUnitsAlongPath(List<Vector2> path)
        {
            // Placeholder: select units near the path
            float pathRadius = 0.5f;
            var units = new HashSet<ISelectableUnit>();
            foreach (var point in path)
            {
                var colliders = Physics2D.OverlapCircleAll(point, pathRadius);
                foreach (var col in colliders)
                {
                    var unit = col.GetComponent<ISelectableUnit>();
                    if (unit != null)
                        units.Add(unit);
                }
            }
            return units;
        }

        private void LogSelectionHistory(HashSet<ISelectableUnit> selection)
        {
            // Remove any redo history
            if (historyIndex < selectionHistory.Count - 1)
                selectionHistory.RemoveRange(historyIndex + 1, selectionHistory.Count - historyIndex - 1);
            // Add new entry
            selectionHistory.Add(new SelectionHistoryEntry(selection, DateTime.UtcNow));
            // Enforce max depth
            if (selectionHistory.Count > MaxHistoryDepth)
                selectionHistory.RemoveAt(0);
            historyIndex = selectionHistory.Count - 1;
        }

        public bool CanUndo => historyIndex > 0;
        public bool CanRedo => historyIndex < selectionHistory.Count - 1;

        public HashSet<ISelectableUnit> UndoSelection()
        {
            if (CanUndo)
            {
                historyIndex--;
                var entry = selectionHistory[historyIndex];
                selectedUnits.Clear();
                foreach (var unit in entry.Selection)
                    selectedUnits.Add(unit);
                OnSelectionChanged?.Invoke(new HashSet<ISelectableUnit>(selectedUnits));
                return new HashSet<ISelectableUnit>(selectedUnits);
            }
            return null;
        }

        public HashSet<ISelectableUnit> RedoSelection()
        {
            if (CanRedo)
            {
                historyIndex++;
                var entry = selectionHistory[historyIndex];
                selectedUnits.Clear();
                foreach (var unit in entry.Selection)
                    selectedUnits.Add(unit);
                OnSelectionChanged?.Invoke(new HashSet<ISelectableUnit>(selectedUnits));
                return new HashSet<ISelectableUnit>(selectedUnits);
            }
            return null;
        }

        public IReadOnlyList<SelectionHistoryEntry> GetSelectionHistory() => selectionHistory.AsReadOnly();

        // Optimized selection change invocation
        private void InvokeSelectionChanged(HashSet<ISelectableUnit> newSelection)
        {
            OnSelectionChanging?.Invoke(new HashSet<ISelectableUnit>(selectedUnits));
            selectedUnits.Clear();
            foreach (var unit in newSelection)
                selectedUnits.Add(unit);
            OnSelectionChanged?.Invoke(new HashSet<ISelectableUnit>(selectedUnits));
            LogSelectionHistory(selectedUnits);
        }

        // Use this method for all selection changes
        private void ChangeSelection(HashSet<ISelectableUnit> newSelection, string accessibilityMessage = null)
        {
            InvokeSelectionChanged(newSelection);
            if (!string.IsNullOrEmpty(accessibilityMessage))
                OnAccessibilityEvent?.Invoke(accessibilityMessage);
        }
    }

    // Interface for selectable units
    public interface ISelectableUnit
    {
        GameObject gameObject { get; }
        string UnitType { get; } // e.g., "NPC", "Building"
        float HealthPercent { get; } // 0-1
        string Mood { get; } // e.g., "Happy", "Angry"
        float AttackRange { get; }
        float MovementSpeed { get; }
        float GetTrait(string traitName); // e.g., "Aggression", "Curiosity"
    }

    // Selection filter interface
    public interface ISelectionFilter
    {
        HashSet<ISelectableUnit> Apply(HashSet<ISelectableUnit> units);
    }

    /// <summary>
    /// Filters units by type (e.g., unit type, building type).
    /// </summary>
    public class TypeFilter : ISelectionFilter
    {
        private readonly string requiredType;
        public TypeFilter(string type) { requiredType = type; }
        public HashSet<ISelectableUnit> Apply(HashSet<ISelectableUnit> units)
        {
            var filtered = new HashSet<ISelectableUnit>();
            foreach (var unit in units)
            {
                if (unit.UnitType == requiredType)
                    filtered.Add(unit);
            }
            return filtered;
        }
    }

    /// <summary>
    /// Filters units by state (e.g., health percentage, status effects, mood).
    /// </summary>
    public class StateFilter : ISelectionFilter
    {
        public enum StateType { HealthAbove, HealthBelow, MoodEquals }
        private readonly StateType stateType;
        private readonly float threshold;
        private readonly string mood;
        public StateFilter(StateType type, float value = 0, string moodName = null)
        {
            stateType = type;
            threshold = value;
            mood = moodName;
        }
        public HashSet<ISelectableUnit> Apply(HashSet<ISelectableUnit> units)
        {
            var filtered = new HashSet<ISelectableUnit>();
            foreach (var unit in units)
            {
                switch (stateType)
                {
                    case StateType.HealthAbove:
                        if (unit.HealthPercent > threshold) filtered.Add(unit);
                        break;
                    case StateType.HealthBelow:
                        if (unit.HealthPercent < threshold) filtered.Add(unit);
                        break;
                    case StateType.MoodEquals:
                        if (unit.Mood == mood) filtered.Add(unit);
                        break;
                }
            }
            return filtered;
        }
    }

    /// <summary>
    /// Filters units by attribute (e.g., attack range, movement speed, personality traits).
    /// </summary>
    public class AttributeFilter : ISelectionFilter
    {
        public enum AttributeType { AttackRange, MovementSpeed, TraitAbove, TraitBelow }
        private readonly AttributeType attributeType;
        private readonly string traitName;
        private readonly float threshold;
        public AttributeFilter(AttributeType type, float value = 0, string trait = null)
        {
            attributeType = type;
            threshold = value;
            traitName = trait;
        }
        public HashSet<ISelectableUnit> Apply(HashSet<ISelectableUnit> units)
        {
            var filtered = new HashSet<ISelectableUnit>();
            foreach (var unit in units)
            {
                switch (attributeType)
                {
                    case AttributeType.AttackRange:
                        if (unit.AttackRange >= threshold) filtered.Add(unit);
                        break;
                    case AttributeType.MovementSpeed:
                        if (unit.MovementSpeed >= threshold) filtered.Add(unit);
                        break;
                    case AttributeType.TraitAbove:
                        if (unit.GetTrait(traitName) > threshold) filtered.Add(unit);
                        break;
                    case AttributeType.TraitBelow:
                        if (unit.GetTrait(traitName) < threshold) filtered.Add(unit);
                        break;
                }
            }
            return filtered;
        }
    }

    public class SelectionHistoryEntry
    {
        public HashSet<ISelectableUnit> Selection { get; }
        public DateTime Timestamp { get; }
        public SelectionHistoryEntry(IEnumerable<ISelectableUnit> selection, DateTime timestamp)
        {
            Selection = new HashSet<ISelectableUnit>(selection);
            Timestamp = timestamp;
        }
    }

    public class SelectionGroup
    {
        public HashSet<ISelectableUnit> Units { get; } = new HashSet<ISelectableUnit>();
        public List<int> NestedGroups { get; } = new List<int>();
        public SelectionGroup() { }
        public SelectionGroup(HashSet<ISelectableUnit> units)
        {
            Units = new HashSet<ISelectableUnit>(units);
        }
    }
} 