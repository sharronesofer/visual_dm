using System.Collections.Generic;
using UnityEngine;
using VDM.DTOs.Character;
using VDM.Systems.Character.UI;
using VDM.Systems.Dialogue.Integration;

namespace VDM.Core.Examples
{
    /// <summary>
    /// Example script demonstrating how to use the noncombat skills system.
    /// Shows various skill check scenarios: exploration, dialogue, stealth, investigation.
    /// </summary>
    public class SkillCheckExample : MonoBehaviour
    {
        [Header("Example Configuration")]
        [SerializeField] private string exampleCharacterId = "player-character-1";
        [SerializeField] private bool enableDebugMode = true;
        
        [Header("Example Scenarios")]
        [SerializeField] private KeyCode triggerPerceptionKey = KeyCode.P;
        [SerializeField] private KeyCode triggerStealthKey = KeyCode.S;
        [SerializeField] private KeyCode triggerSocialKey = KeyCode.T;
        [SerializeField] private KeyCode triggerInvestigationKey = KeyCode.I;
        [SerializeField] private KeyCode triggerExplorationKey = KeyCode.E;
        
        private DialogueSkillCheckIntegration dialogueIntegration;
        
        private void Start()
        {
            // Get dialogue integration component
            dialogueIntegration = FindObjectOfType<DialogueSkillCheckIntegration>();
            
            // Subscribe to skill check events
            SkillCheckManager.OnSkillCheckCompleted += HandleSkillCheckCompleted;
            SkillCheckManager.OnSkillCheckCancelled += HandleSkillCheckCancelled;
            
            LogDebug("Skill Check Example initialized. Press keys to trigger examples:");
            LogDebug($"P = Perception, S = Stealth, T = Social, I = Investigation, E = Exploration");
        }
        
        private void OnDestroy()
        {
            // Unsubscribe from events
            SkillCheckManager.OnSkillCheckCompleted -= HandleSkillCheckCompleted;
            SkillCheckManager.OnSkillCheckCancelled -= HandleSkillCheckCancelled;
        }
        
        private void Update()
        {
            // Check for example key presses
            if (Input.GetKeyDown(triggerPerceptionKey))
            {
                TriggerPerceptionExample();
            }
            else if (Input.GetKeyDown(triggerStealthKey))
            {
                TriggerStealthExample();
            }
            else if (Input.GetKeyDown(triggerSocialKey))
            {
                TriggerSocialExample();
            }
            else if (Input.GetKeyDown(triggerInvestigationKey))
            {
                TriggerInvestigationExample();
            }
            else if (Input.GetKeyDown(triggerExplorationKey))
            {
                TriggerExplorationExample();
            }
        }
        
        #region Example Scenarios
        
        private void TriggerPerceptionExample()
        {
            LogDebug("Triggering Perception Example - Looking for hidden details");
            
            var environmentalConditions = new List<string> { "dim_light", "cluttered" };
            
            var skillCheckRequest = new SkillCheckRequestDTO
            {
                CharacterId = exampleCharacterId,
                Context = "You scan the room carefully, looking for anything out of place.",
                EnvironmentalConditions = environmentalConditions,
                SkillOptions = new List<SkillCheckOptionDTO>
                {
                    new SkillCheckOptionDTO
                    {
                        SkillName = "perception",
                        OptionText = "Search for hidden objects",
                        DC = 15,
                        Description = "Use your keen senses to spot anything unusual",
                        EnvironmentalConditions = environmentalConditions
                    },
                    new SkillCheckOptionDTO
                    {
                        SkillName = "investigation",
                        OptionText = "Methodically examine the area",
                        DC = 18,
                        Description = "Take time to carefully analyze every detail",
                        EnvironmentalConditions = environmentalConditions
                    }
                }
            };
            
            SkillCheckManager.RequestSkillCheck(skillCheckRequest);
        }
        
        private void TriggerStealthExample()
        {
            LogDebug("Triggering Stealth Example - Sneaking past guards");
            
            var environmentalConditions = new List<string> { "shadows", "soft_ground" };
            
            var skillCheckRequest = new SkillCheckRequestDTO
            {
                CharacterId = exampleCharacterId,
                Context = "Guards patrol ahead. You need to get past without being seen.",
                EnvironmentalConditions = environmentalConditions,
                SkillOptions = new List<SkillCheckOptionDTO>
                {
                    new SkillCheckOptionDTO
                    {
                        SkillName = "stealth",
                        OptionText = "Sneak through the shadows",
                        DC = 16,
                        Description = "Use the darkness to your advantage",
                        EnvironmentalConditions = environmentalConditions
                    },
                    new SkillCheckOptionDTO
                    {
                        SkillName = "acrobatics",
                        OptionText = "Climb over obstacles quietly",
                        DC = 20,
                        Description = "Take a more athletic but risky approach",
                        EnvironmentalConditions = environmentalConditions
                    }
                }
            };
            
            SkillCheckManager.RequestSkillCheck(skillCheckRequest);
        }
        
        private void TriggerSocialExample()
        {
            LogDebug("Triggering Social Example - Negotiating with an NPC");
            
            var environmentalConditions = new List<string> { "public_setting", "friendly_atmosphere" };
            
            var skillCheckRequest = new SkillCheckRequestDTO
            {
                CharacterId = exampleCharacterId,
                Context = "The merchant seems hesitant to give you information about the stolen goods.",
                EnvironmentalConditions = environmentalConditions,
                SkillOptions = new List<SkillCheckOptionDTO>
                {
                    new SkillCheckOptionDTO
                    {
                        SkillName = "persuasion",
                        OptionText = "Appeal to their sense of justice",
                        DC = 14,
                        Description = "Use logical arguments and charm",
                        EnvironmentalConditions = environmentalConditions
                    },
                    new SkillCheckOptionDTO
                    {
                        SkillName = "intimidation",
                        OptionText = "Pressure them for answers",
                        DC = 16,
                        Description = "Use fear to get what you want",
                        EnvironmentalConditions = environmentalConditions
                    },
                    new SkillCheckOptionDTO
                    {
                        SkillName = "deception",
                        OptionText = "Pretend to be a city official",
                        DC = 18,
                        Description = "Lie convincingly to gain their cooperation",
                        EnvironmentalConditions = environmentalConditions
                    }
                }
            };
            
            SkillCheckManager.RequestSkillCheck(skillCheckRequest);
        }
        
        private void TriggerInvestigationExample()
        {
            LogDebug("Triggering Investigation Example - Examining a crime scene");
            
            var environmentalConditions = new List<string> { "good_lighting", "undisturbed_scene" };
            
            var skillCheckRequest = new SkillCheckRequestDTO
            {
                CharacterId = exampleCharacterId,
                Context = "The crime scene holds many secrets. What evidence can you uncover?",
                EnvironmentalConditions = environmentalConditions,
                SkillOptions = new List<SkillCheckOptionDTO>
                {
                    new SkillCheckOptionDTO
                    {
                        SkillName = "investigation",
                        OptionText = "Examine physical evidence",
                        DC = 15,
                        Description = "Look for fingerprints, footprints, and other clues",
                        EnvironmentalConditions = environmentalConditions
                    },
                    new SkillCheckOptionDTO
                    {
                        SkillName = "insight",
                        OptionText = "Reconstruct what happened",
                        DC = 17,
                        Description = "Use intuition to understand the sequence of events",
                        EnvironmentalConditions = environmentalConditions
                    },
                    new SkillCheckOptionDTO
                    {
                        SkillName = "perception",
                        OptionText = "Search for hidden evidence",
                        DC = 19,
                        Description = "Look for things that might have been missed",
                        EnvironmentalConditions = environmentalConditions
                    }
                }
            };
            
            SkillCheckManager.RequestSkillCheck(skillCheckRequest);
        }
        
        private void TriggerExplorationExample()
        {
            LogDebug("Triggering Exploration Example - Multiple skill options");
            
            if (dialogueIntegration != null)
            {
                var availableSkills = new List<string> 
                { 
                    "perception", "investigation", "athletics", "acrobatics", "survival" 
                };
                
                var environmentalConditions = new List<string> { "wilderness", "dense_forest", "twilight" };
                
                var skillCheckRequest = dialogueIntegration.CreateExplorationSkillChecks(
                    "You come across an ancient ruin in the forest. How do you approach it?",
                    exampleCharacterId,
                    availableSkills,
                    environmentalConditions
                );
                
                SkillCheckManager.RequestSkillCheck(skillCheckRequest);
            }
            else
            {
                LogDebug("DialogueSkillCheckIntegration not found - cannot create exploration example");
            }
        }
        
        #endregion
        
        #region Event Handlers
        
        private void HandleSkillCheckCompleted(SkillCheckResultDTO result)
        {
            LogDebug($"Skill Check Completed: {result.SkillName}");
            LogDebug($"Result: {result.TotalRoll} vs DC {result.DC} = {(result.Success ? "SUCCESS" : "FAILURE")}");
            
            if (result.CriticalSuccess)
            {
                LogDebug("CRITICAL SUCCESS! Exceptional outcome!");
            }
            else if (result.CriticalFailure)
            {
                LogDebug("CRITICAL FAILURE! Significant complications!");
            }
            
            // Handle specific outcomes based on skill type
            HandleSkillCheckOutcome(result);
        }
        
        private void HandleSkillCheckCancelled(string characterId)
        {
            LogDebug($"Skill check cancelled for character: {characterId}");
        }
        
        private void HandleSkillCheckOutcome(SkillCheckResultDTO result)
        {
            // This is where you would trigger different game outcomes based on the skill check result
            switch (result.SkillName)
            {
                case "perception":
                    if (result.Success)
                    {
                        LogDebug("You notice several interesting details about your surroundings.");
                        if (result.DegreeOfSuccess >= 10)
                        {
                            LogDebug("You also spot a hidden passage behind a loose stone!");
                        }
                    }
                    else
                    {
                        LogDebug("Nothing seems out of the ordinary to you.");
                    }
                    break;
                    
                case "stealth":
                    if (result.Success)
                    {
                        LogDebug("You successfully move without being detected.");
                        if (result.CriticalSuccess)
                        {
                            LogDebug("You're so stealthy that you gain advantage on your next action!");
                        }
                    }
                    else
                    {
                        LogDebug("Your movement attracts unwanted attention!");
                        if (result.CriticalFailure)
                        {
                            LogDebug("You've triggered an alarm! Combat may be imminent.");
                        }
                    }
                    break;
                    
                case "persuasion":
                case "intimidation":
                case "deception":
                    if (result.Success)
                    {
                        LogDebug("Your social approach was effective. The NPC is cooperating.");
                        LogDebug("You gain valuable information about your quest.");
                    }
                    else
                    {
                        LogDebug("Your social attempt failed. The NPC seems resistant.");
                        if (result.SkillName == "intimidation" && result.CriticalFailure)
                        {
                            LogDebug("Your intimidation backfired! The NPC is now hostile.");
                        }
                    }
                    break;
                    
                case "investigation":
                    if (result.Success)
                    {
                        LogDebug("Your careful examination reveals important clues.");
                        if (result.DegreeOfSuccess >= 5)
                        {
                            LogDebug("You also discover a valuable piece of evidence!");
                        }
                    }
                    else
                    {
                        LogDebug("Despite your efforts, you don't find anything useful.");
                    }
                    break;
                    
                default:
                    if (result.Success)
                    {
                        LogDebug($"Your {result.SkillName} check was successful!");
                    }
                    else
                    {
                        LogDebug($"Your {result.SkillName} check failed.");
                    }
                    break;
            }
        }
        
        #endregion
        
        private void LogDebug(string message)
        {
            if (enableDebugMode)
            {
                Debug.Log($"[SkillCheckExample] {message}");
            }
        }
    }
} 