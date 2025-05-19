using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
using VisualDM.Data;
using TMPro;
using Newtonsoft.Json.Linq;

namespace VisualDM.Debug
{
    /// <summary>
    /// Debug tool for testing the mod data loading system and displaying loaded data.
    /// Attach this to a UI GameObject to visualize loaded mod data.
    /// </summary>
    public class ModDataTester : MonoBehaviour
    {
        [SerializeField]
        private TMP_Dropdown _categoryDropdown;
        
        [SerializeField]
        private TMP_Dropdown _itemDropdown;
        
        [SerializeField]
        private TMP_Text _dataDisplay;
        
        [SerializeField]
        private Button _refreshButton;
        
        [SerializeField] 
        private Button _syncButton;
        
        [SerializeField]
        private TMP_Text _statusText;
        
        private ModDataManager _modDataManager;
        private Dictionary<string, Dictionary<string, JObject>> _loadedData = new Dictionary<string, Dictionary<string, JObject>>();
        
        private void Start()
        {
            _modDataManager = ModDataManager.Instance;
            
            // Initialize UI elements if they're assigned
            if (_refreshButton != null)
            {
                _refreshButton.onClick.AddListener(RefreshData);
            }
            
            if (_syncButton != null)
            {
                _syncButton.onClick.AddListener(TriggerSync);
            }
            
            if (_categoryDropdown != null)
            {
                _categoryDropdown.onValueChanged.AddListener(OnCategorySelected);
            }
            
            if (_itemDropdown != null)
            {
                _itemDropdown.onValueChanged.AddListener(OnItemSelected);
            }
            
            // Initial load after a short delay to ensure ModDataManager is ready
            Invoke("RefreshData", 1.0f);
        }
        
        /// <summary>
        /// Refresh the displayed data by reloading categories and items.
        /// </summary>
        public void RefreshData()
        {
            if (_modDataManager == null)
            {
                SetStatus("Error: ModDataManager not available.");
                return;
            }
            
            _loadedData.Clear();
            
            if (_statusText != null)
            {
                SetStatus("Loading mod data...");
            }
            
            // Get all available categories
            List<string> categories = _modDataManager.GetAllCategories();
            
            if (categories.Count == 0)
            {
                SetStatus("No mod categories found.");
                return;
            }
            
            // Load data for each category
            foreach (string category in categories)
            {
                Dictionary<string, JObject> items = _modDataManager.GetAllItems(category);
                _loadedData[category] = items;
            }
            
            // Update the categories dropdown
            if (_categoryDropdown != null)
            {
                _categoryDropdown.ClearOptions();
                _categoryDropdown.AddOptions(categories);
                _categoryDropdown.value = 0;
            }
            
            // Update the status
            SetStatus($"Loaded {categories.Count} categories with {_loadedData.Values.Sum(d => d.Count)} total items.");
            
            // Trigger the category selection to update items dropdown
            OnCategorySelected(0);
        }
        
        /// <summary>
        /// Handle category selection change.
        /// </summary>
        private void OnCategorySelected(int index)
        {
            if (_categoryDropdown == null || _itemDropdown == null || index < 0 || index >= _categoryDropdown.options.Count)
            {
                return;
            }
            
            string selectedCategory = _categoryDropdown.options[index].text;
            
            if (!_loadedData.TryGetValue(selectedCategory, out var items) || items.Count == 0)
            {
                _itemDropdown.ClearOptions();
                _itemDropdown.AddOptions(new List<string> { "No items" });
                _dataDisplay.text = "No items available in this category.";
                return;
            }
            
            // Update the items dropdown
            _itemDropdown.ClearOptions();
            List<string> itemOptions = items.Keys.ToList();
            _itemDropdown.AddOptions(itemOptions);
            _itemDropdown.value = 0;
            
            // Trigger the item selection to update the data display
            OnItemSelected(0);
        }
        
        /// <summary>
        /// Handle item selection change.
        /// </summary>
        private void OnItemSelected(int index)
        {
            if (_categoryDropdown == null || _itemDropdown == null || 
                _categoryDropdown.value < 0 || _categoryDropdown.value >= _categoryDropdown.options.Count ||
                index < 0 || index >= _itemDropdown.options.Count)
            {
                return;
            }
            
            string selectedCategory = _categoryDropdown.options[_categoryDropdown.value].text;
            string selectedItem = _itemDropdown.options[index].text;
            
            if (_loadedData.TryGetValue(selectedCategory, out var items) && 
                items.TryGetValue(selectedItem, out var itemData))
            {
                // Display the item data as formatted JSON
                _dataDisplay.text = itemData.ToString(Newtonsoft.Json.Formatting.Indented);
            }
            else
            {
                _dataDisplay.text = "Item data not available.";
            }
        }
        
        /// <summary>
        /// Trigger synchronization with the backend server.
        /// </summary>
        private void TriggerSync()
        {
            // Find the ModSynchronizer component
            ModSynchronizer synchronizer = FindObjectOfType<ModSynchronizer>();
            
            if (synchronizer != null)
            {
                SetStatus("Synchronizing with server...");
                synchronizer.TriggerSync();
            }
            else
            {
                SetStatus("Error: ModSynchronizer not available.");
            }
        }
        
        /// <summary>
        /// Set the status text if available.
        /// </summary>
        private void SetStatus(string status)
        {
            if (_statusText != null)
            {
                _statusText.text = status;
                Debug.Log(status);
            }
        }
    }
} 