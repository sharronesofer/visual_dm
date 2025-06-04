using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
using TMPro;
using VDM.Systems.Npc.Models;

namespace VDM.Systems.NPC.Services
{
    /// <summary>
    /// Handles automatic language selection and communication between player and NPCs.
    /// Implements seamless language resolution to avoid frustrating language barriers.
    /// </summary>
    public class LanguageInteractionService : MonoBehaviour
    {
        [Header("Language Settings")]
        [SerializeField] private bool enableDebugLogging = true;
        [SerializeField] private float minimumComprehension = 0.3f;
        [SerializeField] private bool preferTradeLanguages = true;
        [SerializeField] private bool showLanguageInDialogue = false;
        [SerializeField] private bool allowLanguageOverride = false;
        
        [Header("Language Display")]
        [SerializeField] private string languageDisplayFormat = "({0})";
        [SerializeField] private Color comprehensionGoodColor = Color.green;
        [SerializeField] private Color comprehensionPoorColor = Color.yellow;
        [SerializeField] private Color comprehensionBadColor = Color.red;
        
        // Events for language system
        public static event Action<string, string, float> OnLanguageResolved;
        public static event Action<string, string> OnLanguageBarrierEncountered;
        public static event Action<string, string> OnLanguageLearningOpportunity;
        
        // Cache for language profiles
        private Dictionary<string, NPCLanguageProfile> npcLanguageCache = new();
        private Dictionary<string, float> languageCommonness = new();
        private CharacterLanguageProfile playerLanguageProfile;
        
        #region Public API
        
        /// <summary>
        /// Resolve the best common language between player and NPC for dialogue.
        /// This is the main entry point for automatic language selection.
        /// </summary>
        public async Task<LanguageResolutionResult> ResolveDialogueLanguage(
            string playerId, 
            NPCData npc, 
            string dialogueText = null,
            string forceLanguage = null)
        {
            try
            {
                // Get language profiles
                var playerProfile = await GetPlayerLanguageProfile(playerId);
                var npcProfile = await GetNPCLanguageProfile(npc);
                
                // If forcing a specific language
                if (!string.IsNullOrEmpty(forceLanguage))
                {
                    var forcedResult = CreateForcedLanguageResult(forceLanguage, playerProfile, npcProfile);
                    if (forcedResult != null)
                    {
                        LogLanguageResolution(forcedResult);
                        return forcedResult;
                    }
                }
                
                // Find best common language
                var result = FindBestCommonLanguage(playerProfile, npcProfile, dialogueText);
                
                // Apply comprehension processing if dialogue text provided
                if (!string.IsNullOrEmpty(dialogueText))
                {
                    result = await ProcessDialogueComprehension(result, dialogueText);
                }
                
                LogLanguageResolution(result);
                OnLanguageResolved?.Invoke(result.SelectedLanguage, result.ExplanationText, result.ComprehensionLevel);
                
                return result;
            }
            catch (Exception ex)
            {
                Debug.LogError($"LanguageInteractionService: Failed to resolve dialogue language: {ex.Message}");
                return CreateFallbackResult();
            }
        }
        
        /// <summary>
        /// Check if two characters can communicate effectively.
        /// </summary>
        public async Task<bool> CanCommunicate(string playerId, NPCData npc, float threshold = 0.3f)
        {
            var result = await ResolveDialogueLanguage(playerId, npc);
            return result.ComprehensionLevel >= threshold;
        }
        
        /// <summary>
        /// Get a list of languages the player can use to communicate with this NPC.
        /// </summary>
        public async Task<List<LanguageOption>> GetAvailableLanguageOptions(string playerId, NPCData npc)
        {
            var playerProfile = await GetPlayerLanguageProfile(playerId);
            var npcProfile = await GetNPCLanguageProfile(npc);
            
            var options = new List<LanguageOption>();
            
            foreach (var playerLang in playerProfile.KnownLanguages)
            {
                var comprehension = CalculateLanguageComprehension(playerLang, npcProfile);
                if (comprehension > 0.1f) // Show if there's any possibility of communication
                {
                    options.Add(new LanguageOption
                    {
                        Language = playerLang.Language,
                        ComprehensionLevel = comprehension,
                        PlayerProficiency = playerLang.Proficiency,
                        Description = GetLanguageDescription(playerLang.Language, comprehension)
                    });
                }
            }
            
            return options.OrderByDescending(o => o.ComprehensionLevel).ToList();
        }
        
        #endregion
        
        #region Language Resolution Logic
        
        private LanguageResolutionResult FindBestCommonLanguage(
            CharacterLanguageProfile playerProfile, 
            NPCLanguageProfile npcProfile,
            string dialogueText = null)
        {
            var options = new List<LanguageCandidate>();
            
            // 1. Perfect matches (both know the language well)
            foreach (var playerLang in playerProfile.KnownLanguages)
            {
                var npcLang = npcProfile.KnownLanguages.FirstOrDefault(nl => 
                    nl.Language.Equals(playerLang.Language, StringComparison.OrdinalIgnoreCase));
                
                if (npcLang != null)
                {
                    var avgComprehension = (playerLang.Proficiency + npcLang.Proficiency) / 2.0f;
                    if (avgComprehension >= minimumComprehension)
                    {
                        var bonus = 0.0f;
                        
                        // Bonus for trade languages
                        if (IsTradeLanguage(playerLang.Language))
                        {
                            bonus += preferTradeLanguages ? 0.2f : 0.1f;
                        }
                        
                        options.Add(new LanguageCandidate
                        {
                            Language = playerLang.Language,
                            ComprehensionScore = Math.Min(1.0f, avgComprehension + bonus),
                            Explanation = $"Both characters know {playerLang.Language}",
                            PlayerProficiency = playerLang.Proficiency,
                            NPCProficiency = npcLang.Proficiency
                        });
                    }
                }
            }
            
            // 2. Related languages (family comprehension)
            if (options.Count == 0 || options.Max(o => o.ComprehensionScore) < 0.7f)
            {
                foreach (var playerLang in playerProfile.KnownLanguages)
                {
                    foreach (var npcLang in npcProfile.KnownLanguages)
                    {
                        if (!playerLang.Language.Equals(npcLang.Language, StringComparison.OrdinalIgnoreCase))
                        {
                            var comprehension = CalculateRelatedLanguageComprehension(
                                playerLang.Language, playerLang.Proficiency,
                                npcLang.Language, npcLang.Proficiency);
                            
                            if (comprehension >= minimumComprehension)
                            {
                                var speakerLanguage = playerLang.Proficiency > npcLang.Proficiency 
                                    ? playerLang.Language : npcLang.Language;
                                
                                options.Add(new LanguageCandidate
                                {
                                    Language = speakerLanguage,
                                    ComprehensionScore = comprehension,
                                    Explanation = $"Related languages: {playerLang.Language} ↔ {npcLang.Language}",
                                    PlayerProficiency = playerLang.Proficiency,
                                    NPCProficiency = npcLang.Proficiency
                                });
                            }
                        }
                    }
                }
            }
            
            // 3. Fallback to Common
            if (options.Count == 0)
            {
                options.Add(new LanguageCandidate
                {
                    Language = "Common",
                    ComprehensionScore = 0.6f,
                    Explanation = "Fallback to Common with basic comprehension",
                    PlayerProficiency = 0.8f,
                    NPCProficiency = 0.8f
                });
            }
            
            // 4. Last resort: Trade Common
            if (options.Count == 0)
            {
                options.Add(new LanguageCandidate
                {
                    Language = "Trade Common",
                    ComprehensionScore = 0.4f,
                    Explanation = "Using trade pidgin as last resort",
                    PlayerProficiency = 0.5f,
                    NPCProficiency = 0.5f
                });
            }
            
            // Select the best option
            var bestOption = options.OrderByDescending(o => o.ComprehensionScore).First();
            
            return new LanguageResolutionResult
            {
                SelectedLanguage = bestOption.Language,
                ComprehensionLevel = bestOption.ComprehensionScore,
                ExplanationText = bestOption.Explanation,
                PlayerProficiency = bestOption.PlayerProficiency,
                NPCProficiency = bestOption.NPCProficiency,
                IsAutoResolved = true,
                CanCommunicate = bestOption.ComprehensionScore >= minimumComprehension,
                DisplayText = showLanguageInDialogue ? string.Format(languageDisplayFormat, bestOption.Language) : ""
            };
        }
        
        private float CalculateLanguageComprehension(CharacterLanguage playerLang, NPCLanguageProfile npcProfile)
        {
            var npcLang = npcProfile.KnownLanguages.FirstOrDefault(nl => 
                nl.Language.Equals(playerLang.Language, StringComparison.OrdinalIgnoreCase));
            
            if (npcLang != null)
            {
                return (playerLang.Proficiency + npcLang.Proficiency) / 2.0f;
            }
            
            // Check for related languages
            var bestRelated = 0.0f;
            foreach (var npc_lang in npcProfile.KnownLanguages)
            {
                var related = CalculateRelatedLanguageComprehension(
                    playerLang.Language, playerLang.Proficiency,
                    npc_lang.Language, npc_lang.Proficiency);
                bestRelated = Math.Max(bestRelated, related);
            }
            
            return bestRelated;
        }
        
        private float CalculateRelatedLanguageComprehension(string lang1, float prof1, string lang2, float prof2)
        {
            // Simplified family relationships (this would use backend LanguageEngine in full implementation)
            var familyGroups = new Dictionary<string, string[]>
            {
                ["common_family"] = new[] { "Common", "Elvish", "Halfling", "Gnomish" },
                ["elder_family"] = new[] { "Dwarven", "Orcish", "Giant" },
                ["eastern_family"] = new[] { "Draconic", "Goblin" },
                ["trade_family"] = new[] { "Trade Common", "Sea Cant" }
            };
            
            foreach (var family in familyGroups.Values)
            {
                if (family.Contains(lang1) && family.Contains(lang2))
                {
                    var familyBonus = 0.4f; // Base family comprehension
                    var avgProficiency = (prof1 + prof2) / 2.0f;
                    return familyBonus * avgProficiency;
                }
            }
            
            return 0.0f;
        }
        
        #endregion
        
        #region Profile Management
        
        private async Task<CharacterLanguageProfile> GetPlayerLanguageProfile(string playerId)
        {
            // This would integrate with your character system
            // For now, return a mock profile
            if (playerLanguageProfile == null)
            {
                playerLanguageProfile = new CharacterLanguageProfile
                {
                    CharacterId = playerId,
                    KnownLanguages = new List<CharacterLanguage>
                    {
                        new CharacterLanguage { Language = "Common", Proficiency = 1.0f },
                        new CharacterLanguage { Language = "Trade Common", Proficiency = 0.6f }
                    }
                };
            }
            
            return playerLanguageProfile;
        }
        
        private async Task<NPCLanguageProfile> GetNPCLanguageProfile(NPCData npc)
        {
            if (npcLanguageCache.TryGetValue(npc.id, out var cached))
            {
                return cached;
            }
            
            // Extract languages from NPC dialogue model or generate based on context
            var languages = ExtractNPCLanguages(npc);
            
            var profile = new NPCLanguageProfile
            {
                NPCId = npc.id,
                KnownLanguages = languages,
                PrimaryLanguage = languages.FirstOrDefault()?.Language ?? "Common",
                SettlementId = npc.regionId // Assuming region maps to settlement
            };
            
            npcLanguageCache[npc.id] = profile;
            return profile;
        }
        
        private List<NPCLanguage> ExtractNPCLanguages(NPCData npc)
        {
            var languages = new List<NPCLanguage>();
            
            // Get language from dialogue model if available
            var primaryLang = npc.dialogue?.Language ?? "Common";
            languages.Add(new NPCLanguage { Language = primaryLang, Proficiency = 1.0f });
            
            // Add Common if not already present
            if (!primaryLang.Equals("Common", StringComparison.OrdinalIgnoreCase))
            {
                languages.Add(new NPCLanguage { Language = "Common", Proficiency = 0.8f });
            }
            
            // Add trade language for merchants/in settlements
            if (IsTradeContext(npc))
            {
                languages.Add(new NPCLanguage { Language = "Trade Common", Proficiency = 0.7f });
            }
            
            return languages;
        }
        
        #endregion
        
        #region Helper Methods
        
        private bool IsTradeLanguage(string language)
        {
            return language.Equals("Trade Common", StringComparison.OrdinalIgnoreCase) ||
                   language.Equals("Sea Cant", StringComparison.OrdinalIgnoreCase);
        }
        
        private bool IsTradeContext(NPCData npc)
        {
            return npc.npcType.ToString().Contains("Merchant") ||
                   npc.profession?.Contains("merchant") == true ||
                   npc.profession?.Contains("trader") == true;
        }
        
        private async Task<LanguageResolutionResult> ProcessDialogueComprehension(
            LanguageResolutionResult result, string dialogueText)
        {
            // This would call the backend language engine for full processing
            // For now, just apply basic modification based on comprehension level
            
            if (result.ComprehensionLevel < 0.5f)
            {
                result.ProcessedText = ModifyTextForComprehension(dialogueText, result.ComprehensionLevel, result.SelectedLanguage);
                result.HasComprehensionIssues = true;
            }
            else
            {
                result.ProcessedText = dialogueText;
                result.HasComprehensionIssues = false;
            }
            
            return result;
        }
        
        private string ModifyTextForComprehension(string text, float comprehensionLevel, string speakerLanguage = null)
        {
            if (comprehensionLevel >= 0.8f) return text;
            
            if (comprehensionLevel < 0.3f)
            {
                return "[You can barely understand what they're saying]";
            }
            
            // Enhanced modification for partial comprehension with fictional script
            var words = text.Split(' ');
            var modifiedWords = new List<string>();
            
            for (int i = 0; i < words.Length; i++)
            {
                if (UnityEngine.Random.value < comprehensionLevel || IsImportantWord(words[i]))
                {
                    modifiedWords.Add(words[i]);
                }
                else
                {
                    // Replace with foreign-looking script specific to the language being spoken
                    modifiedWords.Add(GenerateForeignWord(words[i], speakerLanguage));
                }
            }
            
            return string.Join(" ", modifiedWords);
        }
        
        private bool IsImportantWord(string word)
        {
            // Keep proper nouns, numbers, and common words
            if (string.IsNullOrEmpty(word)) return false;
            
            return char.IsUpper(word[0]) || // Proper nouns
                   word.All(char.IsDigit) || // Numbers
                   word.Length <= 3 || // Short words
                   new[] { "the", "and", "or", "but", "in", "on", "at", "to", "from", "a", "an" }
                       .Contains(word.ToLower());
        }
        
        private string GenerateForeignWord(string originalWord, string speakerLanguage = null)
        {
            if (string.IsNullOrEmpty(originalWord)) return originalWord;
            
            // Remove punctuation for processing
            var cleanWord = System.Text.RegularExpressions.Regex.Replace(originalWord, @"[^\w]", "");
            if (string.IsNullOrEmpty(cleanWord)) return originalWord;
            
            // Completely unreadable character sets from various Unicode blocks
            var scriptSets = new Dictionary<string, char[]>
            {
                ["elvish"] = new char[]
                {
                    // Tibetan script - looks mystical and flowing
                    'ཀ', 'ཁ', 'ག', 'ང', 'ཅ', 'ཆ', 'ཇ', 'ཉ', 'ཏ', 'ཐ', 'ད', 'ན', 'པ', 'ཕ', 'བ', 'མ', 'ཙ',
                    'ཚ', 'ཛ', 'ཝ', 'ཞ', 'ཟ', 'འ', 'ཡ', 'ར', 'ལ', 'ཤ', 'ས', 'ཧ', 'ཨ', 'ི', 'ུ', 'ེ', 'ོ'
                },
                ["draconic"] = new char[]
                {
                    // Runic and ancient symbols - looks harsh and angular
                    'ᚠ', 'ᚢ', 'ᚦ', 'ᚨ', 'ᚱ', 'ᚲ', 'ᚷ', 'ᚹ', 'ᚺ', 'ᚾ', 'ᛁ', 'ᛃ', 'ᛈ', 'ᛉ', 'ᛊ', 'ᛏ', 'ᛒ', 'ᛖ', 'ᛗ',
                    'ᛚ', 'ᛜ', 'ᛝ', 'ᛟ', 'ᛞ', 'ᚤ', 'ᚣ', 'ᚧ', 'ᚥ', 'ᚦ', 'ᚩ', 'ᚪ', 'ᚫ', 'ᚬ', 'ᚭ', 'ᚮ', 'ᚯ', 'ᚰ', 'ᚱ', 'ᚲ'
                },
                ["ancient"] = new char[]
                {
                    // Ancient scripts - using simpler alternatives since complex cuneiform may not compile
                    'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ',
                    'Φ', 'Χ', 'Ψ', 'Ω', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע'
                },
                ["mystic"] = new char[]
                {
                    // Geometric and mathematical symbols - looks otherworldly
                    '◊', '◈', '◉', '◎', '○', '◐', '◑', '◒', '◓', '◔', '◕', '◖', '◗', '◘', '◙', '◚', '◛', '◜', '◝', '◞',
                    '◟', '◠', '◡', '◢', '◣', '◤', '◥', '◦', '◧', '◨', '◩', '◪', '◫', '◬', '◭', '◮', '◯', '◰', '◱', '◲'
                }
            };
            
            // Choose script based on the specific language being spoken, or fallback to word length
            string scriptStyle;
            if (!string.IsNullOrEmpty(speakerLanguage))
            {
                scriptStyle = GetScriptStyleForLanguage(speakerLanguage);
            }
            else
            {
                var scriptNames = scriptSets.Keys.ToArray();
                scriptStyle = scriptNames[cleanWord.Length % scriptNames.Length];
            }
            
            var chosenScript = scriptSets.ContainsKey(scriptStyle) ? scriptSets[scriptStyle] : scriptSets["mystic"];
            
            // Generate completely foreign characters - no mapping to English letters
            var foreignChars = new List<char>();
            for (int i = 0; i < cleanWord.Length; i++)
            {
                var c = cleanWord[i];
                if (char.IsLetter(c))
                {
                    // Use character position and word position to select symbols
                    var charIndex = (char.ToLower(c) - 'a' + i) % chosenScript.Length;
                    foreignChars.Add(chosenScript[charIndex]);
                }
                else
                {
                    foreignChars.Add(c); // Keep non-alphabetic characters
                }
            }
            
            var foreignWord = new string(foreignChars.ToArray());
            
            // Occasionally add connector symbols between characters for authenticity
            if (foreignWord.Length > 2 && UnityEngine.Random.value < 0.2f)
            {
                var connectors = new[] { '·', '‧', '⁞', '᭟', '᭞' };
                var connector = connectors[UnityEngine.Random.Range(0, connectors.Length)];
                var insertPos = UnityEngine.Random.Range(1, foreignWord.Length - 1);
                foreignWord = foreignWord.Insert(insertPos, connector.ToString());
            }
            
            // Add back any punctuation from the original word
            var originalPunct = System.Text.RegularExpressions.Regex.Matches(originalWord, @"[^\w]");
            foreach (System.Text.RegularExpressions.Match match in originalPunct)
            {
                foreignWord += match.Value;
            }
            
            return foreignWord;
        }
        
        private string GetScriptStyleForLanguage(string language)
        {
            // Map languages to consistent script styles
            var languageScriptMapping = new Dictionary<string, string>
            {
                ["Elvish"] = "elvish",
                ["Sylvan"] = "elvish",
                ["Gnomish"] = "elvish",
                ["Halfling"] = "elvish",
                ["Draconic"] = "draconic",
                ["Abyssal"] = "draconic",
                ["Infernal"] = "draconic",
                ["Goblin"] = "draconic",
                ["Orcish"] = "draconic",
                ["Ancient Imperial"] = "ancient",
                ["Old Celestial"] = "ancient",
                ["Primordial"] = "ancient",
                ["Giant"] = "ancient",
                ["Dwarven"] = "ancient",
                ["Celestial"] = "mystic",
                ["Druidic"] = "mystic"
            };
            
            return languageScriptMapping.ContainsKey(language) ? languageScriptMapping[language] : "mystic";
        }
        
        private LanguageResolutionResult CreateFallbackResult()
        {
            return new LanguageResolutionResult
            {
                SelectedLanguage = "Common",
                ComprehensionLevel = 0.6f,
                ExplanationText = "Emergency fallback to Common",
                IsAutoResolved = true,
                CanCommunicate = true,
                ProcessedText = "",
                HasComprehensionIssues = false
            };
        }
        
        private LanguageResolutionResult CreateForcedLanguageResult(
            string forcedLanguage, 
            CharacterLanguageProfile playerProfile, 
            NPCLanguageProfile npcProfile)
        {
            var playerLang = playerProfile.KnownLanguages.FirstOrDefault(l => 
                l.Language.Equals(forcedLanguage, StringComparison.OrdinalIgnoreCase));
            var npcLang = npcProfile.KnownLanguages.FirstOrDefault(l => 
                l.Language.Equals(forcedLanguage, StringComparison.OrdinalIgnoreCase));
            
            if (playerLang == null || npcLang == null)
            {
                return null; // Can't force a language neither character knows
            }
            
            var comprehension = (playerLang.Proficiency + npcLang.Proficiency) / 2.0f;
            
            return new LanguageResolutionResult
            {
                SelectedLanguage = forcedLanguage,
                ComprehensionLevel = comprehension,
                ExplanationText = $"Forced to use {forcedLanguage}",
                PlayerProficiency = playerLang.Proficiency,
                NPCProficiency = npcLang.Proficiency,
                IsAutoResolved = false,
                CanCommunicate = comprehension >= minimumComprehension
            };
        }
        
        private string GetLanguageDescription(string language, float comprehension)
        {
            var quality = comprehension switch
            {
                >= 0.8f => "Fluent",
                >= 0.6f => "Good",
                >= 0.4f => "Basic",
                >= 0.2f => "Poor",
                _ => "Barely understands"
            };
            
            return $"{language} ({quality})";
        }
        
        private void LogLanguageResolution(LanguageResolutionResult result)
        {
            if (enableDebugLogging)
            {
                Debug.Log($"Language resolved: {result.SelectedLanguage} " +
                         $"(Comprehension: {result.ComprehensionLevel:P1}) - {result.ExplanationText}");
            }
        }
        
        #endregion
    }
    
    #region Data Classes
    
    [Serializable]
    public class LanguageResolutionResult
    {
        public string SelectedLanguage;
        public float ComprehensionLevel;
        public string ExplanationText;
        public float PlayerProficiency;
        public float NPCProficiency;
        public bool IsAutoResolved;
        public bool CanCommunicate;
        public string ProcessedText;
        public bool HasComprehensionIssues;
        public string DisplayText;
    }
    
    [Serializable]
    public class CharacterLanguageProfile
    {
        public string CharacterId;
        public List<CharacterLanguage> KnownLanguages = new();
        public string PrimaryLanguage;
    }
    
    [Serializable]
    public class NPCLanguageProfile
    {
        public string NPCId;
        public List<NPCLanguage> KnownLanguages = new();
        public string PrimaryLanguage;
        public string SettlementId;
    }
    
    [Serializable]
    public class CharacterLanguage
    {
        public string Language;
        public float Proficiency; // 0.0 to 1.0
    }
    
    [Serializable]
    public class NPCLanguage
    {
        public string Language;
        public float Proficiency; // 0.0 to 1.0
    }
    
    [Serializable]
    public class LanguageOption
    {
        public string Language;
        public float ComprehensionLevel;
        public float PlayerProficiency;
        public string Description;
    }
    
    [Serializable]
    private class LanguageCandidate
    {
        public string Language;
        public float ComprehensionScore;
        public string Explanation;
        public float PlayerProficiency;
        public float NPCProficiency;
    }
    
    #endregion
} 