using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections.Generic;

namespace VisualDM.UI
{
    /// <summary>
    /// Main menu controller that sets up and manages the UI components.
    /// This serves as the entry point for the UI system.
    /// </summary>
    public class MainMenuController : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private Canvas mainCanvas;
        [SerializeField] private UIManager uiManager;
        
        [Header("Theme Settings")]
        [SerializeField] private UIThemeManager themeManager;
        [SerializeField] private bool useDarkMode = true;
        
        [Header("Character Model")]
        [SerializeField] private GameObject characterModel;
        [SerializeField] private Animator characterAnimator;
        
        // Character data
        private Dictionary<string, object> characterData = new Dictionary<string, object>();
        
        private void Awake()
        {
            // Set default theme
            if (themeManager != null)
            {
                if (useDarkMode)
                {
                    themeManager.SetDarkMode();
                }
                else
                {
                    themeManager.SetLightMode();
                }
            }
            
            // Create UI manager if not assigned
            if (uiManager == null)
            {
                GameObject uiManagerGO = new GameObject("UIManager");
                uiManager = uiManagerGO.AddComponent<UIManager>();
            }
        }
        
        private void Start()
        {
            // Set up UI
            InitializeUI();
            
            // Subscribe to character change events
            if (uiManager != null)
            {
                uiManager.RegisterCharacterChangeListener(OnCharacterChanged);
            }
            
            // Initialize character
            InitializeCharacter();
        }
        
        /// <summary>
        /// Initialize the UI components
        /// </summary>
        private void InitializeUI()
        {
            if (uiManager != null && mainCanvas != null)
            {
                // Set canvas reference
                uiManager.SetCanvas(mainCanvas);
                
                // Apply theme
                if (themeManager != null)
                {
                    uiManager.SetTheme(themeManager);
                }
            }
        }
        
        /// <summary>
        /// Initialize the character model and data
        /// </summary>
        private void InitializeCharacter()
        {
            // Set default character data
            characterData["race"] = "Human";
            characterData["gender"] = "Male";
            characterData["skinColor"] = new Color(0.9f, 0.8f, 0.7f);
            characterData["hairColor"] = new Color(0.3f, 0.2f, 0.1f);
            characterData["hairStyle"] = 0;
            characterData["faceStyle"] = 0;
            
            // Initialize default armor
            characterData["headArmor"] = "none";
            characterData["chestArmor"] = "leather_chest";
            characterData["legsArmor"] = "leather_legs";
            characterData["bootsArmor"] = "leather_boots";
            
            // Apply initial appearance to character model
            UpdateCharacterAppearance();
        }
        
        /// <summary>
        /// Handle character data changes from UI
        /// </summary>
        private void OnCharacterChanged(object changeData)
        {
            if (changeData == null) return;
            
            // Reflection to get properties from anonymous type
            Type type = changeData.GetType();
            
            // Get change type
            var changeTypeProperty = type.GetProperty("Type");
            if (changeTypeProperty == null) return;
            
            string changeType = (string)changeTypeProperty.GetValue(changeData);
            
            switch (changeType)
            {
                case "appearance":
                    var featureProperty = type.GetProperty("Feature");
                    var valueProperty = type.GetProperty("Value");
                    
                    if (featureProperty != null && valueProperty != null)
                    {
                        string feature = (string)featureProperty.GetValue(changeData);
                        object value = valueProperty.GetValue(changeData);
                        
                        // Update character data
                        characterData[feature] = value;
                        Debug.Log($"Updated character {feature} to {value}");
                    }
                    break;
                
                case "armor":
                    var slotProperty = type.GetProperty("Slot");
                    var itemIdProperty = type.GetProperty("ItemId");
                    
                    if (slotProperty != null && itemIdProperty != null)
                    {
                        Panels.ArmorPanel.EquipmentSlot slot = 
                            (Panels.ArmorPanel.EquipmentSlot)slotProperty.GetValue(changeData);
                        string itemId = (string)itemIdProperty.GetValue(changeData);
                        
                        // Map slot to data key
                        string slotKey = slot.ToString().ToLowerInvariant() + "Armor";
                        
                        // Update character data
                        characterData[slotKey] = itemId;
                        Debug.Log($"Updated armor slot {slot} to {itemId}");
                    }
                    break;
                
                case "preset":
                    var nameProperty = type.GetProperty("Name");
                    
                    if (nameProperty != null)
                    {
                        string presetName = (string)nameProperty.GetValue(changeData);
                        
                        // Load preset data
                        Dictionary<string, object> presetData = LoadPreset(presetName);
                        
                        if (presetData != null)
                        {
                            // Apply preset to character data
                            foreach (var kvp in presetData)
                            {
                                characterData[kvp.Key] = kvp.Value;
                            }
                            
                            Debug.Log($"Applied preset {presetName}");
                        }
                    }
                    break;
                
                case "randomize":
                    var configProperty = type.GetProperty("Config");
                    
                    if (configProperty != null)
                    {
                        Panels.RandomizerPanel.RandomizerConfig config = 
                            (Panels.RandomizerPanel.RandomizerConfig)configProperty.GetValue(changeData);
                        
                        // Randomize character based on config
                        RandomizeCharacter(config);
                        Debug.Log("Randomized character appearance");
                    }
                    break;
            }
            
            // Apply changes to character model
            UpdateCharacterAppearance();
        }
        
        /// <summary>
        /// Update the character appearance based on character data
        /// </summary>
        private void UpdateCharacterAppearance()
        {
            if (characterModel == null) return;
            
            // This would interface with the character customization system
            // For now, we'll just log the changes
            
            Debug.Log("Updating character appearance with:");
            foreach (var kvp in characterData)
            {
                Debug.Log($" - {kvp.Key}: {kvp.Value}");
            }
            
            // Example of how to apply changes to character model components
            CharacterCustomization customization = characterModel.GetComponent<CharacterCustomization>();
            if (customization != null)
            {
                // Apply race
                if (characterData.TryGetValue("race", out object raceObj) && raceObj is string race)
                {
                    customization.SetRace(race);
                }
                
                // Apply gender
                if (characterData.TryGetValue("gender", out object genderObj) && genderObj is string gender)
                {
                    customization.SetGender(gender);
                }
                
                // Apply skin color
                if (characterData.TryGetValue("skinColor", out object skinColorObj) && skinColorObj is Color skinColor)
                {
                    customization.SetSkinColor(skinColor);
                }
                
                // Apply hair
                if (characterData.TryGetValue("hairStyle", out object hairStyleObj) && 
                    characterData.TryGetValue("hairColor", out object hairColorObj))
                {
                    int hairStyle = (int)hairStyleObj;
                    Color hairColor = (Color)hairColorObj;
                    customization.SetHair(hairStyle, hairColor);
                }
                
                // Apply armor
                foreach (Panels.ArmorPanel.EquipmentSlot slot in Enum.GetValues(typeof(Panels.ArmorPanel.EquipmentSlot)))
                {
                    string slotKey = slot.ToString().ToLowerInvariant() + "Armor";
                    
                    if (characterData.TryGetValue(slotKey, out object itemIdObj) && itemIdObj is string itemId)
                    {
                        customization.EquipItem(slot.ToString(), itemId);
                    }
                }
                
                // Apply changes
                customization.ApplyChanges();
            }
        }
        
        /// <summary>
        /// Load a saved character preset
        /// </summary>
        private Dictionary<string, object> LoadPreset(string presetName)
        {
            // In a real implementation, this would load from PlayerPrefs or a file
            // For this example, we'll return a predefined preset
            
            Dictionary<string, object> presetData = new Dictionary<string, object>();
            
            switch (presetName)
            {
                case "Warrior Preset":
                    presetData["race"] = "Human";
                    presetData["gender"] = "Male";
                    presetData["skinColor"] = new Color(0.8f, 0.7f, 0.6f);
                    presetData["hairColor"] = new Color(0.2f, 0.15f, 0.1f);
                    presetData["hairStyle"] = 2;
                    presetData["faceStyle"] = 1;
                    presetData["headArmor"] = "plate_helmet";
                    presetData["chestArmor"] = "plate_chest";
                    presetData["legsArmor"] = "plate_legs";
                    presetData["bootsArmor"] = "plate_boots";
                    break;
                
                case "Mage Preset":
                    presetData["race"] = "Elf";
                    presetData["gender"] = "Female";
                    presetData["skinColor"] = new Color(0.9f, 0.85f, 0.8f);
                    presetData["hairColor"] = new Color(0.9f, 0.9f, 1.0f); // White/silver
                    presetData["hairStyle"] = 5;
                    presetData["faceStyle"] = 0;
                    presetData["headArmor"] = "mage_hood";
                    presetData["chestArmor"] = "mage_robe";
                    presetData["legsArmor"] = "mage_pants";
                    presetData["bootsArmor"] = "mage_boots";
                    break;
                
                case "Rogue Preset":
                    presetData["race"] = "Human";
                    presetData["gender"] = "Female";
                    presetData["skinColor"] = new Color(0.7f, 0.6f, 0.5f);
                    presetData["hairColor"] = new Color(0.1f, 0.1f, 0.1f); // Black
                    presetData["hairStyle"] = 3;
                    presetData["faceStyle"] = 2;
                    presetData["headArmor"] = "leather_hood";
                    presetData["chestArmor"] = "leather_armor";
                    presetData["legsArmor"] = "leather_pants";
                    presetData["bootsArmor"] = "leather_boots";
                    break;
                
                default:
                    return null;
            }
            
            return presetData;
        }
        
        /// <summary>
        /// Randomize character based on randomizer config
        /// </summary>
        private void RandomizeCharacter(Panels.RandomizerPanel.RandomizerConfig config)
        {
            System.Random random = new System.Random();
            
            // Randomize race
            if (config.randomizeRace)
            {
                string[] races = { "Human", "Elf", "Dwarf", "Orc" };
                characterData["race"] = races[random.Next(races.Length)];
            }
            
            // Randomize gender
            if (config.randomizeGender)
            {
                string[] genders = { "Male", "Female" };
                characterData["gender"] = genders[random.Next(genders.Length)];
            }
            
            // Randomize appearance
            if (config.randomizeAppearance)
            {
                // Hair style
                characterData["hairStyle"] = random.Next(8);
                
                // Face style
                characterData["faceStyle"] = random.Next(4);
            }
            
            // Randomize colors
            if (config.randomizeColors)
            {
                // Skin color
                characterData["skinColor"] = new Color(
                    0.6f + (float)random.NextDouble() * 0.4f,
                    0.5f + (float)random.NextDouble() * 0.4f,
                    0.4f + (float)random.NextDouble() * 0.4f
                );
                
                // Hair color
                characterData["hairColor"] = new Color(
                    (float)random.NextDouble() * 0.8f,
                    (float)random.NextDouble() * 0.8f,
                    (float)random.NextDouble() * 0.8f
                );
            }
            
            // Randomize armor
            if (config.randomizeArmor)
            {
                string[] armorSets = { "none", "leather", "chain", "plate", "mage" };
                string armorSet = armorSets[random.Next(armorSets.Length)];
                
                if (armorSet != "none")
                {
                    characterData["headArmor"] = armorSet + "_helmet";
                    characterData["chestArmor"] = armorSet + "_chest";
                    characterData["legsArmor"] = armorSet + "_legs";
                    characterData["bootsArmor"] = armorSet + "_boots";
                }
                else
                {
                    characterData["headArmor"] = "none";
                    characterData["chestArmor"] = "none";
                    characterData["legsArmor"] = "none";
                    characterData["bootsArmor"] = "none";
                }
            }
        }
        
        /// <summary>
        /// Toggle between light and dark theme
        /// </summary>
        public void ToggleTheme()
        {
            if (themeManager != null)
            {
                useDarkMode = !useDarkMode;
                
                if (useDarkMode)
                {
                    themeManager.SetDarkMode();
                }
                else
                {
                    themeManager.SetLightMode();
                }
                
                // Apply theme to UI manager
                if (uiManager != null)
                {
                    uiManager.SetTheme(themeManager);
                }
            }
        }
        
        /// <summary>
        /// Save current character as a preset
        /// </summary>
        public void SaveCurrentPreset(string presetName)
        {
            // In a real implementation, this would save to PlayerPrefs or a file
            Debug.Log($"Saving current character as preset: {presetName}");
            
            // Clone current character data
            Dictionary<string, object> presetData = new Dictionary<string, object>(characterData);
            
            // Save preset
            // Implementation would depend on your save system
        }
    }
} 