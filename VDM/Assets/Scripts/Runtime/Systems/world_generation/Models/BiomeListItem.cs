using UnityEngine;
using VDM.DTOs.Common;
using VDM.Systems.Worldgeneration.Models;

namespace VDM.Systems.Worldgeneration.Ui
{
    /// <summary>
    /// UI component for displaying biome items in a list
    /// </summary>
    public class BiomeListItem : MonoBehaviour
    {
        private BiomeConfigDTO _biome;

        /// <summary>
        /// Initialize the list item with biome data
        /// </summary>
        public void Initialize(BiomeConfigDTO biome)
        {
            _biome = biome;
            UpdateDisplay();
        }

        /// <summary>
        /// Update the display with current biome data
        /// </summary>
        private void UpdateDisplay()
        {
            if (_biome == null) return;
            
            // TODO: Set biome name, description, etc. on UI elements
            Debug.Log($"Displaying biome: {_biome.Name}");
        }

        /// <summary>
        /// Called when biome is selected
        /// </summary>
        public void OnSelect()
        {
            Debug.Log($"Selected biome: {_biome?.Name}");
        }
    }
} 