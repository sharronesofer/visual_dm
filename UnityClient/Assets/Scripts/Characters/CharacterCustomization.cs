using UnityEngine;
using System;
using System.Collections.Generic;

namespace VisualDM
{
    /// <summary>
    /// Handles character customization and appearance changes
    /// This component manages the visual aspects of the character model
    /// </summary>
    public class CharacterCustomization : MonoBehaviour
    {
        [Header("Character Model")]
        [SerializeField] private SkinnedMeshRenderer bodyRenderer;
        [SerializeField] private SkinnedMeshRenderer headRenderer;
        [SerializeField] private SkinnedMeshRenderer hairRenderer;
        
        [Header("Equipment Renderers")]
        [SerializeField] private SkinnedMeshRenderer[] equipmentRenderers;
        
        [Header("Color Properties")]
        [SerializeField] private string skinColorProperty = "_SkinColor";
        [SerializeField] private string hairColorProperty = "_HairColor";
        
        // Race data
        [Serializable]
        public class RaceData
        {
            public string raceName;
            public Mesh bodyMesh;
            public Mesh headMesh;
            public Vector2 heightRange = new Vector2(1f, 1.2f);
            public Vector2 buildRange = new Vector2(0.9f, 1.1f);
        }
        
        [Header("Race Settings")]
        [SerializeField] private RaceData[] races;
        
        // Current character data
        private string currentRace = "Human";
        private string currentGender = "Male";
        private Color currentSkinColor = Color.white;
        private Color currentHairColor = Color.black;
        private int currentHairStyle = 0;
        private int currentFaceStyle = 0;
        
        // Equipment data
        private Dictionary<string, string> equippedItems = new Dictionary<string, string>();
        
        // Materials
        private Material bodyMaterial;
        private Material hairMaterial;
        
        // Flag to track if updates are needed
        private bool needsUpdate = false;
        
        private void Awake()
        {
            // Create instance materials
            if (bodyRenderer != null && bodyRenderer.sharedMaterial != null)
            {
                bodyMaterial = new Material(bodyRenderer.sharedMaterial);
                bodyRenderer.material = bodyMaterial;
            }
            
            if (hairRenderer != null && hairRenderer.sharedMaterial != null)
            {
                hairMaterial = new Material(hairRenderer.sharedMaterial);
                hairRenderer.material = hairMaterial;
            }
            
            // Initialize equipment slots
            equippedItems["Head"] = "none";
            equippedItems["Shoulders"] = "none";
            equippedItems["Chest"] = "none";
            equippedItems["Arms"] = "none";
            equippedItems["Hands"] = "none";
            equippedItems["Waist"] = "none";
            equippedItems["Legs"] = "none";
            equippedItems["Feet"] = "none";
            equippedItems["Accessory1"] = "none";
            equippedItems["Accessory2"] = "none";
        }
        
        private void Update()
        {
            // Apply changes if needed
            if (needsUpdate)
            {
                ApplyChanges();
                needsUpdate = false;
            }
        }
        
        /// <summary>
        /// Set the character race
        /// </summary>
        public void SetRace(string race)
        {
            if (currentRace != race)
            {
                currentRace = race;
                needsUpdate = true;
                Debug.Log($"Set race to {race}");
            }
        }
        
        /// <summary>
        /// Set the character gender
        /// </summary>
        public void SetGender(string gender)
        {
            if (currentGender != gender)
            {
                currentGender = gender;
                needsUpdate = true;
                Debug.Log($"Set gender to {gender}");
            }
        }
        
        /// <summary>
        /// Set the character skin color
        /// </summary>
        public void SetSkinColor(Color color)
        {
            if (currentSkinColor != color)
            {
                currentSkinColor = color;
                needsUpdate = true;
                Debug.Log($"Set skin color to {color}");
            }
        }
        
        /// <summary>
        /// Set the character hair style and color
        /// </summary>
        public void SetHair(int hairStyle, Color hairColor)
        {
            bool changed = false;
            
            if (currentHairStyle != hairStyle)
            {
                currentHairStyle = hairStyle;
                changed = true;
            }
            
            if (currentHairColor != hairColor)
            {
                currentHairColor = hairColor;
                changed = true;
            }
            
            if (changed)
            {
                needsUpdate = true;
                Debug.Log($"Set hair to style {hairStyle}, color {hairColor}");
            }
        }
        
        /// <summary>
        /// Set the character face style
        /// </summary>
        public void SetFace(int faceStyle)
        {
            if (currentFaceStyle != faceStyle)
            {
                currentFaceStyle = faceStyle;
                needsUpdate = true;
                Debug.Log($"Set face style to {faceStyle}");
            }
        }
        
        /// <summary>
        /// Equip an item to a specific slot
        /// </summary>
        public void EquipItem(string slot, string itemId)
        {
            if (equippedItems.ContainsKey(slot) && equippedItems[slot] != itemId)
            {
                equippedItems[slot] = itemId;
                needsUpdate = true;
                Debug.Log($"Equipped {itemId} to {slot}");
            }
        }
        
        /// <summary>
        /// Apply all changes to the character model
        /// </summary>
        public void ApplyChanges()
        {
            // Apply race and gender (would change mesh)
            ApplyRaceAndGender();
            
            // Apply colors
            ApplyColors();
            
            // Apply equipment
            ApplyEquipment();
            
            // Apply face and hair style (would blend shapes)
            ApplyFaceAndHair();
            
            Debug.Log("Applied all character customization changes");
        }
        
        /// <summary>
        /// Apply race and gender changes to the character model
        /// </summary>
        private void ApplyRaceAndGender()
        {
            // In a real implementation, this would:
            // 1. Find the appropriate mesh for the race/gender
            // 2. Apply the mesh to the renderers
            // 3. Update bone scales according to race
            
            // For this example, we'll just log
            Debug.Log($"Applied race: {currentRace}, gender: {currentGender}");
            
            RaceData raceData = null;
            foreach (var race in races)
            {
                if (race.raceName == currentRace)
                {
                    raceData = race;
                    break;
                }
            }
            
            if (raceData != null && bodyRenderer != null && headRenderer != null)
            {
                // Apply race meshes
                if (raceData.bodyMesh != null)
                {
                    bodyRenderer.sharedMesh = raceData.bodyMesh;
                }
                
                if (raceData.headMesh != null)
                {
                    headRenderer.sharedMesh = raceData.headMesh;
                }
                
                // Apply gender-specific scaling
                float heightScale = raceData.heightRange.x;
                float buildScale = raceData.buildRange.x;
                
                if (currentGender == "Male")
                {
                    heightScale = Mathf.Lerp(raceData.heightRange.x, raceData.heightRange.y, 0.7f);
                    buildScale = Mathf.Lerp(raceData.buildRange.x, raceData.buildRange.y, 0.7f);
                }
                else if (currentGender == "Female")
                {
                    heightScale = Mathf.Lerp(raceData.heightRange.x, raceData.heightRange.y, 0.4f);
                    buildScale = Mathf.Lerp(raceData.buildRange.x, raceData.buildRange.y, 0.3f);
                }
                
                // Apply scaling to character
                transform.localScale = new Vector3(buildScale, heightScale, buildScale);
            }
        }
        
        /// <summary>
        /// Apply color changes to the character model
        /// </summary>
        private void ApplyColors()
        {
            // Apply skin color
            if (bodyMaterial != null && !string.IsNullOrEmpty(skinColorProperty))
            {
                bodyMaterial.SetColor(skinColorProperty, currentSkinColor);
            }
            
            // Apply hair color
            if (hairMaterial != null && !string.IsNullOrEmpty(hairColorProperty))
            {
                hairMaterial.SetColor(hairColorProperty, currentHairColor);
            }
            
            Debug.Log($"Applied skin color: {currentSkinColor}, hair color: {currentHairColor}");
        }
        
        /// <summary>
        /// Apply equipment changes to the character model
        /// </summary>
        private void ApplyEquipment()
        {
            // In a real implementation, this would:
            // 1. Load the appropriate mesh for each equipped item
            // 2. Update the equipment renderers
            // 3. Handle equipment visibility based on slots
            
            // For this example, we'll just log
            Debug.Log("Applied equipment:");
            foreach (var kvp in equippedItems)
            {
                if (kvp.Value != "none")
                {
                    Debug.Log($" - {kvp.Key}: {kvp.Value}");
                }
            }
        }
        
        /// <summary>
        /// Apply face and hair style changes to the character model
        /// </summary>
        private void ApplyFaceAndHair()
        {
            // In a real implementation, this would:
            // 1. Set blend shape values based on face style
            // 2. Change hair mesh based on hair style
            
            // For this example, we'll just log
            Debug.Log($"Applied face style: {currentFaceStyle}, hair style: {currentHairStyle}");
            
            // Apply hair style (would change mesh or blend shapes)
            if (hairRenderer != null && hairRenderer.sharedMesh != null)
            {
                // In a real implementation, this would change the hair mesh or blend shapes
                // Example: hairRenderer.sharedMesh = hairStyles[currentHairStyle];
            }
        }
        
        /// <summary>
        /// Get current character customization data
        /// </summary>
        public Dictionary<string, object> GetCharacterData()
        {
            Dictionary<string, object> data = new Dictionary<string, object>();
            
            // Add appearance data
            data["race"] = currentRace;
            data["gender"] = currentGender;
            data["skinColor"] = currentSkinColor;
            data["hairColor"] = currentHairColor;
            data["hairStyle"] = currentHairStyle;
            data["faceStyle"] = currentFaceStyle;
            
            // Add equipment data
            foreach (var kvp in equippedItems)
            {
                data[kvp.Key.ToLowerInvariant() + "Armor"] = kvp.Value;
            }
            
            return data;
        }
    }
} 