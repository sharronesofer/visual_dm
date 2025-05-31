using System;
using UnityEngine;
using VDM.DTOs.Common;

namespace VDM.Systems.Worldgeneration.Ui
{
    /// <summary>
    /// UI component for displaying continent items in a list
    /// </summary>
    public class ContinentListItem : MonoBehaviour
    {
        private ContinentModel _continent;
        private Action<ContinentModel> _onSelected;
        private Action<ContinentModel> _onDeleted;

        /// <summary>
        /// Initialize the list item with continent data and callbacks
        /// </summary>
        public void Initialize(ContinentModel continent, Action<ContinentModel> onSelected, Action<ContinentModel> onDeleted)
        {
            _continent = continent;
            _onSelected = onSelected;
            _onDeleted = onDeleted;
            
            // TODO: Update UI elements with continent data
            UpdateDisplay();
        }

        /// <summary>
        /// Update the display with current continent data
        /// </summary>
        private void UpdateDisplay()
        {
            if (_continent == null) return;
            
            // TODO: Set continent name, description, etc. on UI elements
            Debug.Log($"Displaying continent: {_continent.Name}");
        }

        /// <summary>
        /// Called when continent is selected
        /// </summary>
        public void OnSelect()
        {
            _onSelected?.Invoke(_continent);
        }

        /// <summary>
        /// Called when continent should be deleted
        /// </summary>
        public void OnDelete()
        {
            _onDeleted?.Invoke(_continent);
        }
    }
} 