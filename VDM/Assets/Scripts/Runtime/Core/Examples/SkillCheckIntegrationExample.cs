using System.Collections.Generic;
using UnityEngine;
using VDM.Systems.Character.UI;
using VDM.Systems.Dialogue.Integration;
using VDM.UI.SkillCheck;
using VDM.DTOs.Character;
using VDM.Core.Services;

namespace VDM.Core.Examples
{
    /// <summary>
    /// Comprehensive example demonstrating the complete noncombat skills integration system.
    /// This script shows how SkillCheckManager, SkillCheckService, SkillCheckUIComponent, 
    /// and DialogueSkillCheckIntegration work together to provide rich skill check gameplay.
    /// </summary>
    public class SkillCheckIntegrationExample : MonoBehaviour
    {
        [Header("Component References")]
        [SerializeField] private SkillCheckUIComponent skillCheckUI;
        [SerializeField] private SkillCheckService skillCheckService;
        [SerializeField] private DialogueSkillCheckIntegration dialogueIntegration;

        [Header("Test Character Data")]
        [SerializeField] private string testCharacterId = "player_character_001";
        [SerializeField] private bool useOfflineMode = true;

        [Header("Example Scenarios")]
        [SerializeField] private bool enableKeyboardTesting = true;

        private Dictionary<string, int> characterSkillModifiers;
        private List<string> currentEnvironmentalConditions;

        private void Awake()
        {
            InitializeTestData();
            SetupComponents();
        }

        private void InitializeTestData()
        {
            // Initialize test character skill modifiers
            characterSkillModifiers = new Dictionary<string, int>
            {
                { "Perception", 5 },
                { "Stealth", 3 },
                { "Persuasion", 7 },
                { "Deception", 4 },
                { "Intimidation", 2 },
                { "Investigation", 6 },
                { "Insight", 4 },
                { "Athletics", 2 },
                { "Acrobatics", 3 },
                { "Sleight of Hand", 1 },
                { "Arcana", 8 },
                { "History", 6 },
                { "Nature", 2 },
                { "Religion", 3 }
            };

            // Set up environmental conditions for testing
            currentEnvironmentalConditions = new List<string>
            {
                "dim_lighting",
                "indoor_environment",
                "quiet_atmosphere"
            };
        }

        private void SetupComponents()
        {
            // Configure SkillCheckService for testing
            if (skillCheckService != null && useOfflineMode)
            {
                // Enable offline simulation mode for testing without backend
                var simulateField = typeof(SkillCheckService).GetField("simulateOfflineMode", 
                    System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                if (simulateField != null)
                {
                    simulateField.SetValue(skillCheckService, true);
                }
            }

            // Subscribe to skill check completion events
            if (skillCheckUI != null)
            {
                skillCheckUI.OnSkillCheckCompleted += HandleSkillCheckCompleted;
                skillCheckUI.OnSkillCheckCancelled += HandleSkillCheckCancelled;
            }

            Debug.Log("SkillCheckIntegrationExample initialized. Use keyboard keys to test different scenarios:");
            Debug.Log("P = Perception Check | S = Stealth Check | T = Social Interaction");
            Debug.Log("I = Investigation Check | E = Exploration Scenario | D = Dialogue Integration");
            Debug.Log("G = Group Skill Check | O = Opposed Skill Check | Q = Quick Skill Check");
        }

        private void Update()
        {
            if (!enableKeyboardTesting) return;

            if (Input.GetKeyDown(KeyCode.P))
                TriggerPerceptionScenario();
            
            if (Input.GetKeyDown(KeyCode.S))
                TriggerStealthScenario();
            
            if (Input.GetKeyDown(KeyCode.T))
                TriggerSocialInteractionScenario();
            
            if (Input.GetKeyDown(KeyCode.I))
                TriggerInvestigationScenario();
            
            if (Input.GetKeyDown(KeyCode.E))
                TriggerExplorationScenario();
            
            if (Input.GetKeyDown(KeyCode.D))
                TriggerDialogueIntegrationScenario();
            
            if (Input.GetKeyDown(KeyCode.G))
                TriggerGroupSkillCheckScenario();
            
            if (Input.GetKeyDown(KeyCode.O))
                TriggerOpposedSkillCheckScenario();
            
            if (Input.GetKeyDown(KeyCode.Q))
                TriggerQuickSkillCheckScenario();
        }

        #region Scenario Implementations

        private void TriggerPerceptionScenario()
        {
            Debug.Log("=== PERCEPTION SCENARIO ===");
            Debug.Log("You enter a dimly lit ancient library. Something seems off about the room...");

            var perceptionOptions = new List<SkillCheckOptionDTO>
            {
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Perception",
                    DifficultyClass = 15,
                    SkillModifier = characterSkillModifiers["Perception"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "dim_lighting", "dusty_environment" },
                    Description = "Search for hidden passages or unusual details"
                },
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Investigation",
                    DifficultyClass = 18,
                    SkillModifier = characterSkillModifiers["Investigation"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "dim_lighting", "dusty_environment" },
                    Description = "Carefully examine the bookshelves and furniture for clues"
                }
            };

            ShowSkillCheckOptions(perceptionOptions, "You notice something suspicious about the library. How do you investigate?");
        }

        private void TriggerStealthScenario()
        {
            Debug.Log("=== STEALTH SCENARIO ===");
            Debug.Log("Guards patrol the corridor ahead. You need to sneak past them...");

            var stealthOptions = new List<SkillCheckOptionDTO>
            {
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Stealth",
                    DifficultyClass = 14,
                    SkillModifier = characterSkillModifiers["Stealth"],
                    HasAdvantage = true, // Shadows provide advantage
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "shadowy_corners", "stone_floor" },
                    Description = "Use the shadows to sneak past the guards"
                },
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Sleight of Hand",
                    DifficultyClass = 16,
                    SkillModifier = characterSkillModifiers["Sleight of Hand"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "close_quarters" },
                    Description = "Create a distraction with thrown objects"
                }
            };

            ShowSkillCheckOptions(stealthOptions, "Two guards block your path. How do you proceed?");
        }

        private void TriggerSocialInteractionScenario()
        {
            Debug.Log("=== SOCIAL INTERACTION SCENARIO ===");
            Debug.Log("The tavern keeper eyes you suspiciously. Getting information won't be easy...");

            var socialOptions = new List<SkillCheckOptionDTO>
            {
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Persuasion",
                    DifficultyClass = 12,
                    SkillModifier = characterSkillModifiers["Persuasion"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "crowded_tavern", "friendly_atmosphere" },
                    Description = "Appeal to their better nature and offer coin"
                },
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Intimidation",
                    DifficultyClass = 10,
                    SkillModifier = characterSkillModifiers["Intimidation"],
                    HasAdvantage = false,
                    HasDisadvantage = true, // Public setting makes intimidation harder
                    EnvironmentalConditions = new List<string> { "crowded_tavern", "witnesses_present" },
                    Description = "Make veiled threats to get them to talk"
                },
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Deception",
                    DifficultyClass = 14,
                    SkillModifier = characterSkillModifiers["Deception"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "crowded_tavern" },
                    Description = "Spin a convincing lie about why you need the information"
                }
            };

            ShowSkillCheckOptions(socialOptions, "The tavern keeper seems reluctant to share information. What's your approach?");
        }

        private void TriggerInvestigationScenario()
        {
            Debug.Log("=== INVESTIGATION SCENARIO ===");
            Debug.Log("A crime scene lies before you. Multiple clues await discovery...");

            var investigationOptions = new List<SkillCheckOptionDTO>
            {
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Investigation",
                    DifficultyClass = 13,
                    SkillModifier = characterSkillModifiers["Investigation"],
                    HasAdvantage = true, // Good lighting helps
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "good_lighting", "undisturbed_scene" },
                    Description = "Systematically examine the physical evidence"
                },
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Insight",
                    DifficultyClass = 15,
                    SkillModifier = characterSkillModifiers["Insight"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "emotional_scene" },
                    Description = "Try to understand the motivation behind the crime"
                },
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Arcana",
                    DifficultyClass = 18,
                    SkillModifier = characterSkillModifiers["Arcana"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "magical_residue" },
                    Description = "Examine the scene for magical traces or components"
                }
            };

            ShowSkillCheckOptions(investigationOptions, "The crime scene holds many secrets. How do you begin your investigation?");
        }

        private void TriggerExplorationScenario()
        {
            Debug.Log("=== EXPLORATION SCENARIO ===");
            Debug.Log("You discover an ancient chamber with multiple points of interest...");

            var explorationOptions = new List<SkillCheckOptionDTO>
            {
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "History",
                    DifficultyClass = 16,
                    SkillModifier = characterSkillModifiers["History"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "ancient_carvings", "well_preserved" },
                    Description = "Decipher the historical significance of the chamber"
                },
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Religion",
                    DifficultyClass = 14,
                    SkillModifier = characterSkillModifiers["Religion"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "religious_symbols", "altar_present" },
                    Description = "Interpret the religious symbols and their meaning"
                },
                new SkillCheckOptionDTO
                {
                    CharacterId = testCharacterId,
                    SkillName = "Athletics",
                    DifficultyClass = 12,
                    SkillModifier = characterSkillModifiers["Athletics"],
                    HasAdvantage = false,
                    HasDisadvantage = false,
                    EnvironmentalConditions = new List<string> { "climbing_required", "stable_handholds" },
                    Description = "Climb to reach the elevated alcove"
                }
            };

            ShowSkillCheckOptions(explorationOptions, "The ancient chamber presents multiple opportunities for discovery. What catches your attention first?");
        }

        private void TriggerDialogueIntegrationScenario()
        {
            Debug.Log("=== DIALOGUE INTEGRATION SCENARIO ===");
            Debug.Log("Testing dialogue system integration with skill checks...");

            if (dialogueIntegration != null)
            {
                // Simulate a dialogue node that requires skill checks
                var mockDialogueNode = new
                {
                    id = "tavern_keeper_suspicious",
                    text = "The tavern keeper looks at you with suspicion.",
                    options = new[]
                    {
                        new { text = "[Persuasion DC 15] Offer to buy information", skill = "Persuasion", dc = 15 },
                        new { text = "[Intimidation DC 12] Demand answers", skill = "Intimidation", dc = 12 },
                        new { text = "[Insight DC 14] Read their true intentions", skill = "Insight", dc = 14 }
                    }
                };

                Debug.Log($"Dialogue Node: {mockDialogueNode.text}");
                foreach (var option in mockDialogueNode.options)
                {
                    Debug.Log($"Option: {option.text}");
                }

                Debug.Log("Dialogue integration would automatically generate skill check options based on the dialogue choices.");
            }
            else
            {
                Debug.LogWarning("DialogueSkillCheckIntegration component not found!");
            }
        }

        private void TriggerGroupSkillCheckScenario()
        {
            Debug.Log("=== GROUP SKILL CHECK SCENARIO ===");
            Debug.Log("Your party must work together to overcome a challenge...");

            // Simulate a group skill check using SkillCheckManager
            var groupCharacterIds = new List<string> { testCharacterId, "companion_001", "companion_002" };
            
            SkillCheckManager.RequestGroupSkillCheck(
                groupCharacterIds,
                "Athletics",
                15,
                currentEnvironmentalConditions,
                "Your party attempts to climb the treacherous cliff face together."
            );
        }

        private void TriggerOpposedSkillCheckScenario()
        {
            Debug.Log("=== OPPOSED SKILL CHECK SCENARIO ===");
            Debug.Log("You engage in a contest of wits with a rival...");

            SkillCheckManager.RequestOpposedSkillCheck(
                testCharacterId,
                "rival_npc_001",
                "Deception",
                "Insight",
                currentEnvironmentalConditions,
                "You attempt to bluff the rival merchant while they try to see through your deception."
            );
        }

        private void TriggerQuickSkillCheckScenario()
        {
            Debug.Log("=== QUICK SKILL CHECK SCENARIO ===");
            Debug.Log("A simple, immediate skill check...");

            SkillCheckManager.RequestQuickSkillCheck(
                testCharacterId,
                "Perception",
                12,
                characterSkillModifiers["Perception"],
                currentEnvironmentalConditions,
                "You quickly scan the area for immediate threats."
            );
        }

        #endregion

        #region UI Integration

        private void ShowSkillCheckOptions(List<SkillCheckOptionDTO> options, string context)
        {
            if (skillCheckUI != null)
            {
                skillCheckUI.ShowSkillCheckOptions(options, context);
                skillCheckUI.ShowEnvironmentalConditions(currentEnvironmentalConditions);
            }
            else
            {
                Debug.LogWarning("SkillCheckUIComponent not found! Cannot display skill check interface.");
                // Fallback: execute first option automatically
                if (options.Count > 0)
                {
                    var request = CreateSkillCheckRequest(options[0], context);
                    SkillCheckManager.ExecuteSkillCheck(request);
                }
            }
        }

        private SkillCheckRequestDTO CreateSkillCheckRequest(SkillCheckOptionDTO option, string context)
        {
            return new SkillCheckRequestDTO
            {
                CharacterId = option.CharacterId,
                SkillName = option.SkillName,
                DifficultyClass = option.DifficultyClass,
                SkillModifier = option.SkillModifier,
                HasAdvantage = option.HasAdvantage,
                HasDisadvantage = option.HasDisadvantage,
                EnvironmentalConditions = option.EnvironmentalConditions ?? new List<string>(),
                Context = context
            };
        }

        #endregion

        #region Event Handlers

        private void HandleSkillCheckCompleted(SkillCheckResultDTO result)
        {
            Debug.Log("=== SKILL CHECK COMPLETED ===");
            Debug.Log($"Skill: {result.SkillName}");
            Debug.Log($"Result: {(result.Success ? "SUCCESS" : "FAILURE")}");
            Debug.Log($"Dice Roll: {result.DiceRoll} | Total: {result.TotalRoll} | DC: {result.DifficultyClass}");
            
            if (result.IsCriticalSuccess)
                Debug.Log("🌟 CRITICAL SUCCESS! Exceptional outcome achieved!");
            else if (result.IsCriticalFailure)
                Debug.Log("💥 CRITICAL FAILURE! Consequences may follow...");

            Debug.Log($"Description: {result.ResultDescription}");

            // Simulate consequences based on skill check results
            SimulateSkillCheckConsequences(result);
        }

        private void HandleSkillCheckCancelled()
        {
            Debug.Log("Skill check cancelled by player.");
        }

        private void SimulateSkillCheckConsequences(SkillCheckResultDTO result)
        {
            // Demonstrate how skill check results might affect the game world
            switch (result.SkillName.ToLower())
            {
                case "perception":
                    if (result.Success)
                        Debug.Log("🔍 You notice a hidden switch behind the bookshelf!");
                    else
                        Debug.Log("👁️ Nothing seems out of the ordinary...");
                    break;

                case "stealth":
                    if (result.Success)
                        Debug.Log("🤫 You slip past the guards unnoticed!");
                    else
                        Debug.Log("🚨 A guard spots you! 'Hey, you there!'");
                    break;

                case "persuasion":
                    if (result.Success)
                        Debug.Log("😊 The NPC's expression softens and they share valuable information.");
                    else
                        Debug.Log("😐 The NPC remains unmoved by your arguments.");
                    break;

                case "investigation":
                    if (result.Success)
                        Debug.Log("🔎 You discover crucial evidence that advances the mystery!");
                    else
                        Debug.Log("❓ The clues remain just out of reach of your understanding.");
                    break;
            }

            // Record analytics (simulated)
            RecordSkillCheckAnalytics(result);
        }

        private void RecordSkillCheckAnalytics(SkillCheckResultDTO result)
        {
            var analytics = new SkillCheckAnalyticsDTO
            {
                CharacterId = result.CharacterId,
                SkillName = result.SkillName,
                DifficultyClass = result.DifficultyClass,
                Success = result.Success,
                DiceRoll = result.DiceRoll,
                TotalRoll = result.TotalRoll,
                EnvironmentalConditions = result.AppliedModifiers,
                Timestamp = result.Timestamp
            };

            // In a real implementation, this would be sent to the backend
            Debug.Log($"📊 Analytics recorded for {result.SkillName} skill check");
        }

        #endregion

        #region Public Testing Methods

        /// <summary>
        /// Public method for testing specific skill checks programmatically
        /// </summary>
        public void TestSkillCheck(string skillName, int difficultyClass, bool hasAdvantage = false, bool hasDisadvantage = false)
        {
            if (!characterSkillModifiers.ContainsKey(skillName))
            {
                Debug.LogError($"Skill '{skillName}' not found in character skill modifiers!");
                return;
            }

            var option = new SkillCheckOptionDTO
            {
                CharacterId = testCharacterId,
                SkillName = skillName,
                DifficultyClass = difficultyClass,
                SkillModifier = characterSkillModifiers[skillName],
                HasAdvantage = hasAdvantage,
                HasDisadvantage = hasDisadvantage,
                EnvironmentalConditions = currentEnvironmentalConditions,
                Description = $"Manual test of {skillName} skill"
            };

            ShowSkillCheckOptions(new List<SkillCheckOptionDTO> { option }, $"Testing {skillName} skill check (DC {difficultyClass})");
        }

        /// <summary>
        /// Update environmental conditions for testing
        /// </summary>
        public void SetEnvironmentalConditions(List<string> conditions)
        {
            currentEnvironmentalConditions = conditions ?? new List<string>();
            Debug.Log($"Environmental conditions updated: {string.Join(", ", currentEnvironmentalConditions)}");
        }

        #endregion

        private void OnDestroy()
        {
            if (skillCheckUI != null)
            {
                skillCheckUI.OnSkillCheckCompleted -= HandleSkillCheckCompleted;
                skillCheckUI.OnSkillCheckCancelled -= HandleSkillCheckCancelled;
            }
        }
    }
} 