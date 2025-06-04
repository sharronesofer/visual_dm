using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.DTOs.Character;
using VDM.Systems.Character.UI;
using VDM.Systems.Dialogue.Models;
using VDM.Systems.Character.Models;

namespace VDM.Systems.Dialogue.Integration
{
    /// <summary>
    /// Integrates skill checks with the dialogue system.
    /// Allows dialogue options to trigger skill checks and respond to results.
    /// </summary>
    public class DialogueSkillCheckIntegration : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private bool enableAutoSkillChecks = true;
        [SerializeField] private bool showSkillDCInOptions = true;
        [SerializeField] private float skillCheckResultDelay = 1.0f;
        
        // Events for dialogue-skill integration
        public static event Action<DialogueNodeDTO, SkillCheckResultDTO> OnDialogueSkillCheckCompleted;
        public static event Action<DialogueNodeDTO> OnDialogueSkillCheckStarted;
        
        // Current dialogue context
        private DialogueNodeDTO currentDialogueNode;
        private string currentCharacterId;
        private List<string> currentEnvironmentalConditions = new List<string>();
        
        private void OnEnable()
        {
            // Subscribe to skill check completion
            SkillCheckManager.OnSkillCheckCompleted += HandleSkillCheckCompleted;
            SkillCheckManager.OnSkillCheckCancelled += HandleSkillCheckCancelled;
        }
        
        private void OnDisable()
        {
            // Unsubscribe from events
            SkillCheckManager.OnSkillCheckCompleted -= HandleSkillCheckCompleted;
            SkillCheckManager.OnSkillCheckCancelled -= HandleSkillCheckCancelled;
        }
        
        /// <summary>
        /// Process a dialogue node to check for skill check requirements.
        /// This is called when dialogue options are being displayed.
        /// </summary>
        /// <param name="dialogueNode">Current dialogue node</param>
        /// <param name="characterId">Character in dialogue</param>
        /// <param name="environmentalConditions">Current environmental conditions</param>
        /// <returns>Modified dialogue node with skill check options</returns>
        public async Task<DialogueNodeDTO> ProcessDialogueNodeForSkillChecks(
            DialogueNodeDTO dialogueNode,
            string characterId,
            List<string> environmentalConditions = null)
        {
            currentDialogueNode = dialogueNode;
            currentCharacterId = characterId;
            currentEnvironmentalConditions = environmentalConditions ?? new List<string>();
            
            var processedNode = new DialogueNodeDTO
            {
                Id = dialogueNode.Id,
                Text = dialogueNode.Text,
                SpeakerId = dialogueNode.SpeakerId,
                Options = new List<DialogueOptionDTO>()
            };
            
            // Process each dialogue option
            foreach (var option in dialogueNode.Options)
            {
                var processedOption = await ProcessDialogueOption(option, characterId, environmentalConditions);
                processedNode.Options.Add(processedOption);
            }
            
            return processedNode;
        }
        
        private async Task<DialogueOptionDTO> ProcessDialogueOption(
            DialogueOptionDTO option,
            string characterId,
            List<string> environmentalConditions)
        {
            var processedOption = new DialogueOptionDTO
            {
                Id = option.Id,
                Text = option.Text,
                NextNodeId = option.NextNodeId,
                Conditions = option.Conditions,
                SkillCheck = option.SkillCheck
            };
            
            // Check if this option has skill check requirements
            if (option.SkillCheck != null)
            {
                processedOption = await EnhanceSkillCheckOption(processedOption, characterId, environmentalConditions);
            }
            
            return processedOption;
        }
        
        private async Task<DialogueOptionDTO> EnhanceSkillCheckOption(
            DialogueOptionDTO option,
            string characterId,
            List<string> environmentalConditions)
        {
            var skillCheck = option.SkillCheck;
            
            // Calculate environmental modifiers for this skill
            var totalModifier = CalculateEnvironmentalModifier(skillCheck.SkillName, environmentalConditions);
            
            // Get character's skill modifier (would need character service)
            var characterSkillModifier = await GetCharacterSkillModifier(characterId, skillCheck.SkillName);
            
            // Enhance option text with skill information
            if (showSkillDCInOptions)
            {
                var enhancedText = $"{option.Text} [{skillCheck.SkillName.Replace("_", " ")} DC {skillCheck.DC}";
                
                if (totalModifier != 0)
                {
                    enhancedText += $" {(totalModifier >= 0 ? "+" : "")}{totalModifier}";
                }
                
                enhancedText += "]";
                option.Text = enhancedText;
            }
            
            // Add environmental conditions to skill check
            if (skillCheck.EnvironmentalConditions == null)
            {
                skillCheck.EnvironmentalConditions = new List<string>();
            }
            
            skillCheck.EnvironmentalConditions.AddRange(environmentalConditions);
            
            return option;
        }
        
        /// <summary>
        /// Execute a skill check from a dialogue option.
        /// Called when player selects a dialogue option that requires a skill check.
        /// </summary>
        /// <param name="dialogueOption">Selected dialogue option</param>
        /// <param name="characterId">Character making the check</param>
        /// <returns>True if skill check was initiated successfully</returns>
        public async Task<bool> ExecuteDialogueSkillCheck(DialogueOptionDTO dialogueOption, string characterId)
        {
            if (dialogueOption.SkillCheck == null)
            {
                Debug.LogWarning("ExecuteDialogueSkillCheck called on option without skill check");
                return false;
            }
            
            try
            {
                OnDialogueSkillCheckStarted?.Invoke(currentDialogueNode);
                
                // Create skill check request
                var skillCheckRequest = new SkillCheckRequestDTO
                {
                    CharacterId = characterId,
                    Context = $"Dialogue: {currentDialogueNode.Text}",
                    EnvironmentalConditions = currentEnvironmentalConditions,
                    SkillOptions = new List<SkillCheckOptionDTO>
                    {
                        new SkillCheckOptionDTO
                        {
                            SkillName = dialogueOption.SkillCheck.SkillName,
                            OptionText = dialogueOption.Text,
                            DC = dialogueOption.SkillCheck.DC,
                            Description = dialogueOption.SkillCheck.Description ?? dialogueOption.Text,
                            EnvironmentalConditions = dialogueOption.SkillCheck.EnvironmentalConditions ?? new List<string>()
                        }
                    }
                };
                
                // Request skill check through the manager
                SkillCheckManager.RequestSkillCheck(skillCheckRequest);
                
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error executing dialogue skill check: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Create skill check options for exploration or investigation scenarios.
        /// </summary>
        /// <param name="context">Exploration context</param>
        /// <param name="characterId">Character exploring</param>
        /// <param name="availableSkills">Skills that can be used</param>
        /// <param name="environmentalConditions">Current conditions</param>
        /// <returns>Skill check request</returns>
        public SkillCheckRequestDTO CreateExplorationSkillChecks(
            string context,
            string characterId,
            List<string> availableSkills,
            List<string> environmentalConditions = null)
        {
            var skillOptions = new List<SkillCheckOptionDTO>();
            
            foreach (var skillName in availableSkills)
            {
                var dc = CalculateSkillDC(skillName, context, environmentalConditions);
                var description = GetSkillDescription(skillName, context);
                
                skillOptions.Add(new SkillCheckOptionDTO
                {
                    SkillName = skillName,
                    OptionText = $"Use {skillName.Replace("_", " ")}",
                    DC = dc,
                    Description = description,
                    EnvironmentalConditions = environmentalConditions ?? new List<string>()
                });
            }
            
            return new SkillCheckRequestDTO
            {
                CharacterId = characterId,
                Context = context,
                EnvironmentalConditions = environmentalConditions ?? new List<string>(),
                SkillOptions = skillOptions
            };
        }
        
        private void HandleSkillCheckCompleted(SkillCheckResultDTO result)
        {
            if (currentDialogueNode != null)
            {
                OnDialogueSkillCheckCompleted?.Invoke(currentDialogueNode, result);
            }
        }
        
        private void HandleSkillCheckCancelled(string characterId)
        {
            // Handle cancellation if needed
            Debug.Log($"Skill check cancelled for character {characterId}");
        }
        
        private int CalculateEnvironmentalModifier(string skillName, List<string> conditions)
        {
            // This would integrate with your configuration system
            int totalModifier = 0;
            
            foreach (var condition in conditions)
            {
                // Look up modifier from configuration
                totalModifier += GetEnvironmentalModifierFromConfig(skillName, condition);
            }
            
            return totalModifier;
        }
        
        private int GetEnvironmentalModifierFromConfig(string skillName, string condition)
        {
            // This would call your backend configuration system
            // For now, return some example modifiers
            var modifiers = new Dictionary<string, Dictionary<string, int>>
            {
                ["darkness"] = new Dictionary<string, int>
                {
                    ["perception"] = -5,
                    ["investigation"] = -3,
                    ["stealth"] = 2
                },
                ["bright_light"] = new Dictionary<string, int>
                {
                    ["perception"] = 2,
                    ["stealth"] = -2
                },
                ["noisy"] = new Dictionary<string, int>
                {
                    ["perception"] = -3,
                    ["stealth"] = -2
                },
                ["crowded"] = new Dictionary<string, int>
                {
                    ["stealth"] = 2,
                    ["perception"] = -1
                }
            };
            
            if (modifiers.ContainsKey(condition) && modifiers[condition].ContainsKey(skillName))
            {
                return modifiers[condition][skillName];
            }
            
            return 0;
        }
        
        private async Task<int> GetCharacterSkillModifier(string characterId, string skillName)
        {
            // This would call the character service to get skill modifier
            // For now, return a placeholder
            await Task.Delay(1); // Simulate async call
            return 5; // Placeholder value
        }
        
        private int CalculateSkillDC(string skillName, string context, List<string> environmentalConditions)
        {
            // Base DC calculation based on context
            int baseDC = 15; // Medium difficulty
            
            // Adjust based on context
            if (context.Contains("complex") || context.Contains("difficult"))
                baseDC += 5;
            else if (context.Contains("simple") || context.Contains("easy"))
                baseDC -= 5;
            
            // Adjust based on environmental conditions
            foreach (var condition in environmentalConditions ?? new List<string>())
            {
                if (condition.Contains("favorable"))
                    baseDC -= 2;
                else if (condition.Contains("adverse"))
                    baseDC += 2;
            }
            
            return Math.Max(5, Math.Min(30, baseDC)); // Clamp between 5 and 30
        }
        
        private string GetSkillDescription(string skillName, string context)
        {
            var descriptions = new Dictionary<string, string>
            {
                ["perception"] = "Carefully observe your surroundings for details",
                ["investigation"] = "Thoroughly examine and analyze the area",
                ["stealth"] = "Move quietly and avoid detection",
                ["persuasion"] = "Use charm and logic to convince",
                ["deception"] = "Mislead with cunning words",
                ["intimidation"] = "Use fear and threats to your advantage",
                ["insight"] = "Read the true intentions and emotions",
                ["athletics"] = "Use physical strength and coordination",
                ["acrobatics"] = "Perform agile and dexterous movements"
            };
            
            return descriptions.GetValueOrDefault(skillName, $"Use your {skillName.Replace("_", " ")} skill");
        }
        
        // Public API for other systems
        public bool IsProcessingSkillCheck => SkillCheckManager.Instance != null && SkillCheckManager.Instance.IsSkillCheckActive;
        public DialogueNodeDTO CurrentDialogueNode => currentDialogueNode;
    }
} 