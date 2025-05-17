using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems;
using VisualDM.UI.Components;

namespace VisualDM.UI
{
    /// <summary>
    /// Runtime UI panel for managing selection filters and groups.
    /// Integrates with UnitSelectionManager. Accessible and extensible.
    /// </summary>
    public class SelectionPanel : MonoBehaviour
    {
        public UnitSelectionManager SelectionManager;

        // UI elements (assume these are created at runtime, not via inspector)
        private List<Checkbox> filterCheckboxes = new List<Checkbox>();
        private List<Button> groupAssignButtons = new List<Button>();
        private List<Button> groupRecallButtons = new List<Button>();
        private InputField filterValueInput;
        private RuntimeTextLabel statusLabel;

        void Start()
        {
            // Create filter checkboxes for type, state, attribute filters
            CreateFilterCheckbox("Type: NPC", () => ToggleTypeFilter("NPC"));
            CreateFilterCheckbox("Type: Building", () => ToggleTypeFilter("Building"));
            CreateFilterCheckbox("State: Health > 50%", () => ToggleStateFilter(StateFilter.StateType.HealthAbove, 0.5f));
            CreateFilterCheckbox("State: Mood = Happy", () => ToggleStateFilter(StateFilter.StateType.MoodEquals, 0, "Happy"));
            CreateFilterCheckbox("Attribute: Aggression > 0.7", () => ToggleAttributeFilter(AttributeFilter.AttributeType.TraitAbove, 0.7f, "Aggression"));
            // ... add more as needed

            // Create group assign/recall buttons
            for (int i = 1; i <= 9; i++)
            {
                int groupNum = i;
                groupAssignButtons.Add(CreateButton($"Assign Group {i}", () => SelectionManager.AssignGroup(groupNum)));
                groupRecallButtons.Add(CreateButton($"Recall Group {i}", () => SelectionManager.RecallGroup(groupNum)));
            }

            // Create status label
            statusLabel = CreateStatusLabel();

            // Subscribe to selection events for feedback
            SelectionManager.OnSelectionChanged += selection => statusLabel.Text = $"Selected: {selection.Count} unit(s)";
            SelectionManager.OnGroupChanged += (group, units) => statusLabel.Text = $"Group {group}: {units.Count} unit(s)";
            SelectionManager.OnAccessibilityEvent += msg => statusLabel.Text = msg;
        }

        private void CreateFilterCheckbox(string label, Action onToggle)
        {
            var checkbox = InstantiateCheckbox(label);
            checkbox.OnValueChanged += _ => onToggle();
            filterCheckboxes.Add(checkbox);
        }

        private Button CreateButton(string label, Action onClick)
        {
            var button = InstantiateButton(label);
            button.OnClick += onClick;
            return button;
        }

        private RuntimeTextLabel CreateStatusLabel()
        {
            var label = InstantiateStatusLabel();
            label.Text = "Selection Panel Ready";
            return label;
        }

        // Example filter toggles (add/remove filters)
        private void ToggleTypeFilter(string type)
        {
            var filter = new TypeFilter(type);
            if (!HasFilter(filter))
                SelectionManager.AddFilter(filter);
            else
                SelectionManager.RemoveFilter(filter);
        }
        private void ToggleStateFilter(StateFilter.StateType type, float value, string mood = null)
        {
            var filter = new StateFilter(type, value, mood);
            if (!HasFilter(filter))
                SelectionManager.AddFilter(filter);
            else
                SelectionManager.RemoveFilter(filter);
        }
        private void ToggleAttributeFilter(AttributeFilter.AttributeType type, float value, string trait = null)
        {
            var filter = new AttributeFilter(type, value, trait);
            if (!HasFilter(filter))
                SelectionManager.AddFilter(filter);
            else
                SelectionManager.RemoveFilter(filter);
        }
        private bool HasFilter(ISelectionFilter filter)
        {
            // Simple reference check; for production, implement proper filter equality
            return false;
        }

        // Placeholder instantiation methods (replace with runtime UI creation logic)
        private Checkbox InstantiateCheckbox(string label) => new GameObject(label).AddComponent<Checkbox>();
        private Button InstantiateButton(string label) => new GameObject(label).AddComponent<Button>();
        private RuntimeTextLabel InstantiateStatusLabel() => new GameObject("StatusLabel").AddComponent<RuntimeTextLabel>();
    }
} 