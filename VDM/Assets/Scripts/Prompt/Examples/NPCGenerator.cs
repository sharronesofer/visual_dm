using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.Prompt;

namespace VDM.Examples
{
    /// <summary>
    /// Example component that demonstrates using the prompt system to generate NPCs.
    /// This provides a simple UI for generating NPCs with different parameters.
    /// </summary>
    public class NPCGenerator : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TMP_InputField _roleInput;
        [SerializeField] private TMP_Dropdown _importanceDropdown;
        [SerializeField] private TMP_InputField _settingInput;
        [SerializeField] private TMP_InputField _raceInput;
        [SerializeField] private TMP_InputField _specificRequirementsInput;
        [SerializeField] private Button _generateButton;
        [SerializeField] private TextMeshProUGUI _resultText;
        [SerializeField] private GameObject _loadingIndicator;
        
        [Header("Generation Settings")]
        [SerializeField] private bool _enableRandomGeneration = false;
        [SerializeField] private float _randomGenerationInterval = 30f;
        
        // Sample roles for random generation
        private readonly string[] _sampleRoles = new string[]
        {
            "tavern keeper", "blacksmith", "city guard", "noble", "merchant",
            "wizard", "priest", "farmer", "sailor", "captain", "thief",
            "guild master", "minstrel", "bounty hunter", "sage", "healer"
        };
        
        // Sample settings for random generation
        private readonly string[] _sampleSettings = new string[]
        {
            "medieval fantasy", "coastal town", "mountain village",
            "bustling city", "frontier outpost", "elven forest",
            "dwarven stronghold", "desert oasis", "frozen tundra"
        };
        
        // Sample races for random generation
        private readonly string[] _sampleRaces = new string[]
        {
            "human", "elf", "dwarf", "halfling", "gnome", "half-orc",
            "half-elf", "tiefling", "dragonborn", "genasi"
        };
        
        private float _lastGenerationTime;
        private bool _isGenerating = false;
        
        private void Awake()
        {
            // Ensure prompt manager is available
            var instance = PromptManager.Instance;
            
            // Set up UI if available
            if (_generateButton != null)
            {
                _generateButton.onClick.AddListener(OnGenerateButtonClicked);
            }
            
            // Set up dropdown options if available
            if (_importanceDropdown != null)
            {
                _importanceDropdown.options.Clear();
                _importanceDropdown.options.Add(new TMP_Dropdown.OptionData("Minor"));
                _importanceDropdown.options.Add(new TMP_Dropdown.OptionData("Supporting"));
                _importanceDropdown.options.Add(new TMP_Dropdown.OptionData("Major"));
                _importanceDropdown.value = 1; // Default to "Supporting"
            }
            
            // Default values
            if (_roleInput != null && string.IsNullOrEmpty(_roleInput.text))
            {
                _roleInput.text = "shopkeeper";
            }
            
            if (_settingInput != null && string.IsNullOrEmpty(_settingInput.text))
            {
                _settingInput.text = "medieval fantasy";
            }
            
            // Hide loading indicator initially
            if (_loadingIndicator != null)
            {
                _loadingIndicator.SetActive(false);
            }
        }
        
        private void Update()
        {
            // Handle random generation if enabled
            if (_enableRandomGeneration && !_isGenerating)
            {
                if (Time.time - _lastGenerationTime > _randomGenerationInterval)
                {
                    _lastGenerationTime = Time.time;
                    GenerateRandomNPC();
                }
            }
        }
        
        private async void OnGenerateButtonClicked()
        {
            if (_isGenerating) return;
            
            try
            {
                _isGenerating = true;
                SetUIInteractable(false);
                
                // Get values from UI
                string role = _roleInput?.text ?? "guard";
                string importance = GetSelectedImportance();
                string setting = _settingInput?.text ?? "medieval fantasy";
                
                // Build additional params
                Dictionary<string, object> additionalParams = new Dictionary<string, object>();
                
                if (_raceInput != null && !string.IsNullOrEmpty(_raceInput.text))
                {
                    additionalParams["race"] = _raceInput.text;
                }
                
                if (_specificRequirementsInput != null && !string.IsNullOrEmpty(_specificRequirementsInput.text))
                {
                    additionalParams["specific_requirements"] = _specificRequirementsInput.text;
                }
                
                // Generate NPC
                string npcDescription = await PromptService.GenerateNPC(
                    role,
                    importance,
                    setting,
                    additionalParams
                );
                
                // Display result
                if (_resultText != null)
                {
                    _resultText.text = npcDescription;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating NPC: {ex.Message}");
                if (_resultText != null)
                {
                    _resultText.text = $"Error generating NPC: {ex.Message}";
                }
            }
            finally
            {
                _isGenerating = false;
                SetUIInteractable(true);
            }
        }
        
        private async void GenerateRandomNPC()
        {
            if (_isGenerating) return;
            
            try
            {
                _isGenerating = true;
                SetUIInteractable(false);
                
                // Generate random parameters
                string role = _sampleRoles[UnityEngine.Random.Range(0, _sampleRoles.Length)];
                string importance = UnityEngine.Random.Range(0, 3) == 2 ? "major" : 
                                   (UnityEngine.Random.Range(0, 2) == 1 ? "supporting" : "minor");
                string setting = _sampleSettings[UnityEngine.Random.Range(0, _sampleSettings.Length)];
                
                // Update UI if available
                if (_roleInput != null) _roleInput.text = role;
                if (_importanceDropdown != null)
                {
                    _importanceDropdown.value = importance == "major" ? 2 : 
                                               (importance == "supporting" ? 1 : 0);
                }
                if (_settingInput != null) _settingInput.text = setting;
                
                // Build additional params
                Dictionary<string, object> additionalParams = new Dictionary<string, object>();
                string race = _sampleRaces[UnityEngine.Random.Range(0, _sampleRaces.Length)];
                additionalParams["race"] = race;
                
                if (_raceInput != null) _raceInput.text = race;
                
                // Generate NPC
                string npcDescription = await PromptService.GenerateNPC(
                    role,
                    importance,
                    setting,
                    additionalParams
                );
                
                // Display result
                if (_resultText != null)
                {
                    _resultText.text = npcDescription;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating random NPC: {ex.Message}");
                if (_resultText != null)
                {
                    _resultText.text = $"Error generating random NPC: {ex.Message}";
                }
            }
            finally
            {
                _isGenerating = false;
                SetUIInteractable(true);
            }
        }
        
        private string GetSelectedImportance()
        {
            if (_importanceDropdown == null) return "supporting";
            
            switch (_importanceDropdown.value)
            {
                case 0: return "minor";
                case 2: return "major";
                case 1:
                default: return "supporting";
            }
        }
        
        private void SetUIInteractable(bool interactable)
        {
            if (_generateButton != null) _generateButton.interactable = interactable;
            if (_roleInput != null) _roleInput.interactable = interactable;
            if (_importanceDropdown != null) _importanceDropdown.interactable = interactable;
            if (_settingInput != null) _settingInput.interactable = interactable;
            if (_raceInput != null) _raceInput.interactable = interactable;
            if (_specificRequirementsInput != null) _specificRequirementsInput.interactable = interactable;
            
            if (_loadingIndicator != null)
            {
                _loadingIndicator.SetActive(!interactable);
            }
        }
    }
} 