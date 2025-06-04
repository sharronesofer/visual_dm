using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;
using VDM.DTOs.Character;

namespace VDM.Core.Services
{
    public class CharacterCreationService : MonoBehaviour, ICharacterCreationService
    {
        [Header("API Configuration")]
        [SerializeField] private string baseApiUrl = "http://localhost:8000/api";
        [SerializeField] private float requestTimeoutSeconds = 30f;
        [SerializeField] private int maxRetryAttempts = 3;
        [SerializeField] private float retryDelaySeconds = 1f;

        [Header("Debug Settings")]
        [SerializeField] private bool enableDebugLogging = true;
        [SerializeField] private bool simulateOfflineMode = false;

        private HttpClient httpClient;

        // Events for UI updates
        public event Action<List<RaceDTO>> OnRacesLoaded;
        public event Action<List<BackgroundDTO>> OnBackgroundsLoaded;
        public event Action<CharacterDTO> OnCharacterCreated;
        public event Action<string> OnError;

        private void Awake()
        {
            InitializeHttpClient();
        }

        private void InitializeHttpClient()
        {
            httpClient = new HttpClient();
            httpClient.Timeout = TimeSpan.FromSeconds(requestTimeoutSeconds);
            httpClient.DefaultRequestHeaders.Add("User-Agent", "VisualDM-Unity-Client/1.0");
        }

        #region ICharacterCreationService Implementation

        public async Task<AvailableRacesResponseDTO> GetAvailableRacesAsync()
        {
            if (simulateOfflineMode)
            {
                return SimulateAvailableRaces();
            }

            return await ExecuteWithRetry(async () =>
            {
                var response = await httpClient.GetAsync($"{baseApiUrl}/character-creation/races");
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<AvailableRacesResponseDTO>(responseJson);
                
                OnRacesLoaded?.Invoke(result.Races);
                return result;
            });
        }

        public async Task<AvailableBackgroundsResponseDTO> GetAvailableBackgroundsAsync()
        {
            if (simulateOfflineMode)
            {
                return SimulateAvailableBackgrounds();
            }

            return await ExecuteWithRetry(async () =>
            {
                var response = await httpClient.GetAsync($"{baseApiUrl}/character-creation/backgrounds");
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<AvailableBackgroundsResponseDTO>(responseJson);
                
                OnBackgroundsLoaded?.Invoke(result.Backgrounds);
                return result;
            });
        }

        public async Task<RaceDTO> GetRaceDetailsAsync(string raceId)
        {
            if (simulateOfflineMode)
            {
                return SimulateRaceDetails(raceId);
            }

            return await ExecuteWithRetry(async () =>
            {
                var response = await httpClient.GetAsync($"{baseApiUrl}/character-creation/races/{raceId}");
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<RaceDTO>(responseJson);
            });
        }

        public async Task<BackgroundDTO> GetBackgroundDetailsAsync(string backgroundId)
        {
            if (simulateOfflineMode)
            {
                return SimulateBackgroundDetails(backgroundId);
            }

            return await ExecuteWithRetry(async () =>
            {
                var response = await httpClient.GetAsync($"{baseApiUrl}/character-creation/backgrounds/{backgroundId}");
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<BackgroundDTO>(responseJson);
            });
        }

        public async Task<CharacterCreationResponseDTO> CreateCharacterAsync(CharacterCreationRequestDTO request)
        {
            if (simulateOfflineMode)
            {
                return SimulateCharacterCreation(request);
            }

            return await ExecuteWithRetry(async () =>
            {
                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/character-creation/create", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<CharacterCreationResponseDTO>(responseJson);
                
                if (result.Success && result.Character != null)
                {
                    OnCharacterCreated?.Invoke(result.Character);
                }
                
                return result;
            });
        }

        public async Task<CharacterValidationResponseDTO> ValidateCharacterAsync(CharacterCreationRequestDTO request)
        {
            if (simulateOfflineMode)
            {
                return SimulateCharacterValidation(request);
            }

            return await ExecuteWithRetry(async () =>
            {
                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/character-creation/validate", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<CharacterValidationResponseDTO>(responseJson);
            });
        }

        public async Task<CharacterStatsDTO> CalculateCharacterStatsAsync(string raceId, string backgroundId, AttributesDTO attributes)
        {
            if (simulateOfflineMode)
            {
                return SimulateCharacterStats(raceId, backgroundId, attributes);
            }

            return await ExecuteWithRetry(async () =>
            {
                var request = new { raceId, backgroundId, attributes };
                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/character-creation/calculate-stats", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<CharacterStatsDTO>(responseJson);
            });
        }

        public async Task<List<CharacterDTO>> GetPlayerCharactersAsync(string playerId)
        {
            if (simulateOfflineMode)
            {
                return SimulatePlayerCharacters(playerId);
            }

            return await ExecuteWithRetry(async () =>
            {
                var response = await httpClient.GetAsync($"{baseApiUrl}/characters/player/{playerId}");
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<List<CharacterDTO>>(responseJson);
            });
        }

        public async Task<CharacterDTO> GetCharacterAsync(string characterId)
        {
            if (simulateOfflineMode)
            {
                return SimulateCharacterDetails(characterId);
            }

            return await ExecuteWithRetry(async () =>
            {
                var response = await httpClient.GetAsync($"{baseApiUrl}/characters/{characterId}");
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<CharacterDTO>(responseJson);
            });
        }

        public async Task<bool> DeleteCharacterAsync(string characterId)
        {
            if (simulateOfflineMode)
            {
                return true; // Simulate successful deletion
            }

            return await ExecuteWithRetry(async () =>
            {
                var response = await httpClient.DeleteAsync($"{baseApiUrl}/characters/{characterId}");
                return response.IsSuccessStatusCode;
            });
        }

        public async Task<CharacterDTO> UpdateCharacterAsync(CharacterDTO character)
        {
            if (simulateOfflineMode)
            {
                return character; // Return unchanged for simulation
            }

            return await ExecuteWithRetry(async () =>
            {
                var json = JsonConvert.SerializeObject(character);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PutAsync($"{baseApiUrl}/characters/{character.Id}", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<CharacterDTO>(responseJson);
            });
        }

        public async Task<PointBuyConfigDTO> GetPointBuyConfigAsync()
        {
            if (simulateOfflineMode)
            {
                return new PointBuyConfigDTO(); // Use default configuration
            }

            return await ExecuteWithRetry(async () =>
            {
                var response = await httpClient.GetAsync($"{baseApiUrl}/character-creation/point-buy-config");
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<PointBuyConfigDTO>(responseJson);
            });
        }

        public async Task<StandardArrayConfigDTO> GetStandardArrayConfigAsync()
        {
            if (simulateOfflineMode)
            {
                return new StandardArrayConfigDTO(); // Use default configuration
            }

            return await ExecuteWithRetry(async () =>
            {
                var response = await httpClient.GetAsync($"{baseApiUrl}/character-creation/standard-array-config");
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<StandardArrayConfigDTO>(responseJson);
            });
        }

        public async Task<List<string>> GetAvailablePortraitsAsync(string raceId = null)
        {
            if (simulateOfflineMode)
            {
                return SimulateAvailablePortraits(raceId);
            }

            return await ExecuteWithRetry(async () =>
            {
                var url = string.IsNullOrEmpty(raceId) 
                    ? $"{baseApiUrl}/character-creation/portraits"
                    : $"{baseApiUrl}/character-creation/portraits?raceId={raceId}";

                var response = await httpClient.GetAsync(url);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<List<string>>(responseJson);
            });
        }

        public async Task<string> UploadPortraitAsync(byte[] imageData, string fileName)
        {
            if (simulateOfflineMode)
            {
                return $"simulated_portrait_{Guid.NewGuid()}.jpg";
            }

            return await ExecuteWithRetry(async () =>
            {
                using (var content = new MultipartFormDataContent())
                {
                    content.Add(new ByteArrayContent(imageData), "portrait", fileName);

                    var response = await httpClient.PostAsync($"{baseApiUrl}/character-creation/upload-portrait", content);
                    response.EnsureSuccessStatusCode();

                    var responseJson = await response.Content.ReadAsStringAsync();
                    var result = JsonConvert.DeserializeObject<dynamic>(responseJson);
                    return result.portraitUrl;
                }
            });
        }

        #endregion

        #region Utility Methods

        private async Task<T> ExecuteWithRetry<T>(Func<Task<T>> operation)
        {
            Exception lastException = null;

            for (int attempt = 0; attempt < maxRetryAttempts; attempt++)
            {
                try
                {
                    return await operation();
                }
                catch (Exception ex)
                {
                    lastException = ex;
                    DebugLog($"Attempt {attempt + 1} failed: {ex.Message}");

                    if (attempt < maxRetryAttempts - 1)
                    {
                        await Task.Delay(TimeSpan.FromSeconds(retryDelaySeconds * (attempt + 1)));
                    }
                }
            }

            var errorMessage = $"Operation failed after {maxRetryAttempts} attempts. Last error: {lastException?.Message}";
            OnError?.Invoke(errorMessage);
            throw new Exception(errorMessage, lastException);
        }

        private void DebugLog(string message)
        {
            if (enableDebugLogging)
            {
                Debug.Log($"[CharacterCreationService] {message}");
            }
        }

        #endregion

        #region Simulation Methods (for offline testing)

        private AvailableRacesResponseDTO SimulateAvailableRaces()
        {
            return new AvailableRacesResponseDTO
            {
                Success = true,
                Races = new List<RaceDTO>
                {
                    new RaceDTO
                    {
                        Id = "human",
                        Name = "Human",
                        Description = "Versatile and ambitious, humans are the most adaptable of the races.",
                        FlavorText = "Humans possess exceptional drive and a great capacity to endure and expand.",
                        AttributeBonuses = new AttributeBonusesDTO { Strength = 1, Dexterity = 1, Constitution = 1, Intelligence = 1, Wisdom = 1, Charisma = 1 },
                        RacialTraits = new List<string> { "Extra Language", "Extra Skill", "Bonus Feat" },
                        SkillProficiencies = new List<string>(),
                        Languages = new List<string> { "Common" },
                        Speed = 30,
                        ImageUrl = "portraits/human_default.jpg"
                    },
                    new RaceDTO
                    {
                        Id = "elf",
                        Name = "Elf",
                        Description = "Graceful and long-lived, elves are skilled in magic and archery.",
                        FlavorText = "Elves are a magical people of otherworldly grace, living in places of ethereal beauty.",
                        AttributeBonuses = new AttributeBonusesDTO { Dexterity = 2 },
                        RacialTraits = new List<string> { "Darkvision", "Fey Ancestry", "Trance", "Keen Senses" },
                        SkillProficiencies = new List<string> { "Perception" },
                        Languages = new List<string> { "Common", "Elvish" },
                        Speed = 30,
                        ImageUrl = "portraits/elf_default.jpg"
                    },
                    new RaceDTO
                    {
                        Id = "dwarf",
                        Name = "Dwarf",
                        Description = "Hardy and resilient, dwarves are known for their craftsmanship and endurance.",
                        FlavorText = "Bold and hardy, dwarves are known as skilled warriors, miners, and workers of stone and metal.",
                        AttributeBonuses = new AttributeBonusesDTO { Constitution = 2 },
                        RacialTraits = new List<string> { "Darkvision", "Dwarven Resilience", "Stonecunning", "Dwarven Combat Training" },
                        SkillProficiencies = new List<string>(),
                        Languages = new List<string> { "Common", "Dwarvish" },
                        Speed = 25,
                        ImageUrl = "portraits/dwarf_default.jpg"
                    }
                }
            };
        }

        private AvailableBackgroundsResponseDTO SimulateAvailableBackgrounds()
        {
            return new AvailableBackgroundsResponseDTO
            {
                Success = true,
                Backgrounds = new List<BackgroundDTO>
                {
                    new BackgroundDTO
                    {
                        Id = "soldier",
                        Name = "Soldier",
                        Description = "You have served in a military organization, learning discipline and combat skills.",
                        FlavorText = "War has been your life for as long as you care to remember.",
                        SkillProficiencies = new List<string> { "Athletics", "Intimidation" },
                        ToolProficiencies = new List<string> { "One type of gaming set", "Vehicles (land)" },
                        Languages = new List<string> { "One of your choice" },
                        Feature = "Military Rank",
                        FeatureDescription = "You have a military rank from your career as a soldier.",
                        PersonalityTraits = new List<string> 
                        { 
                            "I'm always polite and respectful.",
                            "I'm haunted by memories of war.",
                            "I've lost too many friends, and I'm slow to make new ones."
                        },
                        Ideals = new List<string> 
                        { 
                            "Responsibility. I do what I must and obey just authority.",
                            "Independence. When people follow orders blindly, they embrace a kind of tyranny."
                        },
                        Bonds = new List<string> 
                        { 
                            "I would still lay down my life for the people I served with.",
                            "Someone saved my life on the battlefield. To this day, I will never leave a friend behind."
                        },
                        Flaws = new List<string> 
                        { 
                            "The monstrous enemy we faced in battle still leaves me quivering with fear.",
                            "I have little respect for anyone who is not a proven warrior."
                        }
                    },
                    new BackgroundDTO
                    {
                        Id = "scholar",
                        Name = "Scholar",
                        Description = "You spent years learning the lore of the multiverse.",
                        FlavorText = "You are a scholar, devoted to learning and research.",
                        SkillProficiencies = new List<string> { "Arcana", "History" },
                        ToolProficiencies = new List<string>(),
                        Languages = new List<string> { "Two of your choice" },
                        Feature = "Researcher",
                        FeatureDescription = "When you attempt to learn or recall a piece of lore, if you do not know that information, you often know where and from whom you can obtain it.",
                        PersonalityTraits = new List<string> 
                        { 
                            "I use polysyllabic words that convey the impression of great erudition.",
                            "I've read every book in the world's greatest libraries—or I like to boast that I have."
                        },
                        Ideals = new List<string> 
                        { 
                            "Knowledge. The path to power and self-improvement is through knowledge.",
                            "Beauty. What is beautiful points us beyond itself toward what is true."
                        },
                        Bonds = new List<string> 
                        { 
                            "It is my duty to protect my students.",
                            "I have an ancient text that holds terrible secrets that must not fall into the wrong hands."
                        },
                        Flaws = new List<string> 
                        { 
                            "I am easily distracted by the promise of information.",
                            "Most people scream and run when they see a demon. I stop and take notes on its anatomy."
                        }
                    },
                    new BackgroundDTO
                    {
                        Id = "criminal",
                        Name = "Criminal",
                        Description = "You are an experienced criminal with a history of breaking the law.",
                        FlavorText = "You are an experienced criminal with a history of breaking the law.",
                        SkillProficiencies = new List<string> { "Deception", "Stealth" },
                        ToolProficiencies = new List<string> { "One type of gaming set", "Thieves' tools" },
                        Languages = new List<string>(),
                        Feature = "Criminal Contact",
                        FeatureDescription = "You have a reliable and trustworthy contact who acts as your liaison to a network of other criminals.",
                        PersonalityTraits = new List<string> 
                        { 
                            "I always have a plan for what to do when things go wrong.",
                            "I am incredibly slow to trust. Those who seem the fairest often have the most to hide."
                        },
                        Ideals = new List<string> 
                        { 
                            "Honor. I don't steal from others in the trade.",
                            "Freedom. Chains are meant to be broken, as are those who would forge them."
                        },
                        Bonds = new List<string> 
                        { 
                            "I'm trying to pay off an old debt I owe to a generous benefactor.",
                            "My ill-gotten gains go to support my family."
                        },
                        Flaws = new List<string> 
                        { 
                            "When I see something valuable, I can't think about anything but how to steal it.",
                            "When faced with a choice between money and my friends, I usually choose the money."
                        }
                    }
                }
            };
        }

        private RaceDTO SimulateRaceDetails(string raceId)
        {
            var races = SimulateAvailableRaces().Races;
            return races.FirstOrDefault(r => r.Id == raceId) ?? races.First();
        }

        private BackgroundDTO SimulateBackgroundDetails(string backgroundId)
        {
            var backgrounds = SimulateAvailableBackgrounds().Backgrounds;
            return backgrounds.FirstOrDefault(b => b.Id == backgroundId) ?? backgrounds.First();
        }

        private CharacterCreationResponseDTO SimulateCharacterCreation(CharacterCreationRequestDTO request)
        {
            var character = new CharacterDTO
            {
                Id = Guid.NewGuid().ToString(),
                Name = request.Name,
                PlayerId = request.PlayerId,
                Attributes = request.Attributes,
                PortraitUrl = request.PortraitUrl,
                Description = request.Description,
                Backstory = request.Backstory,
                HitPoints = 10 + request.Attributes.GetConstitutionModifier(),
                MaxHitPoints = 10 + request.Attributes.GetConstitutionModifier(),
                ArmorClass = 10 + request.Attributes.GetDexterityModifier()
            };

            // Simulate loading race and background data
            character.Race = SimulateRaceDetails(request.RaceId);
            character.Background = SimulateBackgroundDetails(request.BackgroundId);

            return new CharacterCreationResponseDTO
            {
                Success = true,
                Message = "Character created successfully",
                Character = character
            };
        }

        private CharacterValidationResponseDTO SimulateCharacterValidation(CharacterCreationRequestDTO request)
        {
            var errors = new List<string>();
            var warnings = new List<string>();

            if (string.IsNullOrEmpty(request.Name))
                errors.Add("Character name is required");

            var attributeSum = request.Attributes.Strength + request.Attributes.Dexterity + 
                              request.Attributes.Constitution + request.Attributes.Intelligence + 
                              request.Attributes.Wisdom + request.Attributes.Charisma;

            if (attributeSum != 72) // Standard array sum with racial bonuses
                warnings.Add($"Attribute total ({attributeSum}) may not be optimal");

            return new CharacterValidationResponseDTO
            {
                IsValid = errors.Count == 0,
                Errors = errors,
                Warnings = warnings,
                CalculatedStats = SimulateCharacterStats(request.RaceId, request.BackgroundId, request.Attributes)
            };
        }

        private CharacterStatsDTO SimulateCharacterStats(string raceId, string backgroundId, AttributesDTO attributes)
        {
            return new CharacterStatsDTO
            {
                HitPoints = 10 + attributes.GetConstitutionModifier(),
                ArmorClass = 10 + attributes.GetDexterityModifier(),
                Initiative = attributes.GetDexterityModifier(),
                Speed = raceId == "dwarf" ? 25 : 30,
                SavingThrows = new Dictionary<string, int>
                {
                    { "Strength", attributes.GetStrengthModifier() },
                    { "Dexterity", attributes.GetDexterityModifier() },
                    { "Constitution", attributes.GetConstitutionModifier() },
                    { "Intelligence", attributes.GetIntelligenceModifier() },
                    { "Wisdom", attributes.GetWisdomModifier() },
                    { "Charisma", attributes.GetCharismaModifier() }
                },
                Skills = GenerateSimulatedSkills(attributes, raceId, backgroundId),
                Proficiencies = new List<string> { "Simple weapons", "Light armor" }
            };
        }

        private Dictionary<string, int> GenerateSimulatedSkills(AttributesDTO attributes, string raceId, string backgroundId)
        {
            var skills = new Dictionary<string, int>
            {
                { "Acrobatics", attributes.GetDexterityModifier() },
                { "Animal Handling", attributes.GetWisdomModifier() },
                { "Arcana", attributes.GetIntelligenceModifier() },
                { "Athletics", attributes.GetStrengthModifier() },
                { "Deception", attributes.GetCharismaModifier() },
                { "History", attributes.GetIntelligenceModifier() },
                { "Insight", attributes.GetWisdomModifier() },
                { "Intimidation", attributes.GetCharismaModifier() },
                { "Investigation", attributes.GetIntelligenceModifier() },
                { "Medicine", attributes.GetWisdomModifier() },
                { "Nature", attributes.GetIntelligenceModifier() },
                { "Perception", attributes.GetWisdomModifier() },
                { "Performance", attributes.GetCharismaModifier() },
                { "Persuasion", attributes.GetCharismaModifier() },
                { "Religion", attributes.GetIntelligenceModifier() },
                { "Sleight of Hand", attributes.GetDexterityModifier() },
                { "Stealth", attributes.GetDexterityModifier() },
                { "Survival", attributes.GetWisdomModifier() }
            };

            // Add proficiency bonuses based on race and background
            var proficiencyBonus = 2; // Level 1 proficiency bonus

            if (raceId == "elf")
            {
                skills["Perception"] += proficiencyBonus;
            }

            // Add background skill proficiencies
            var background = SimulateBackgroundDetails(backgroundId);
            foreach (var skill in background.SkillProficiencies)
            {
                if (skills.ContainsKey(skill))
                {
                    skills[skill] += proficiencyBonus;
                }
            }

            return skills;
        }

        private List<CharacterDTO> SimulatePlayerCharacters(string playerId)
        {
            return new List<CharacterDTO>
            {
                new CharacterDTO
                {
                    Id = "char_001",
                    Name = "Aragorn",
                    PlayerId = playerId,
                    Level = 5,
                    Race = SimulateRaceDetails("human"),
                    Background = SimulateBackgroundDetails("soldier")
                }
            };
        }

        private CharacterDTO SimulateCharacterDetails(string characterId)
        {
            return new CharacterDTO
            {
                Id = characterId,
                Name = "Test Character",
                PlayerId = "test_player",
                Level = 1,
                Race = SimulateRaceDetails("human"),
                Background = SimulateBackgroundDetails("soldier"),
                Attributes = new AttributesDTO
                {
                    Strength = 15,
                    Dexterity = 13,
                    Constitution = 14,
                    Intelligence = 12,
                    Wisdom = 10,
                    Charisma = 8
                }
            };
        }

        private List<string> SimulateAvailablePortraits(string raceId)
        {
            var basePortraits = new List<string>
            {
                "portraits/default_01.jpg",
                "portraits/default_02.jpg",
                "portraits/default_03.jpg"
            };

            if (!string.IsNullOrEmpty(raceId))
            {
                basePortraits.AddRange(new List<string>
                {
                    $"portraits/{raceId}_01.jpg",
                    $"portraits/{raceId}_02.jpg",
                    $"portraits/{raceId}_03.jpg"
                });
            }

            return basePortraits;
        }

        #endregion

        #region Cleanup

        private void OnDestroy()
        {
            httpClient?.Dispose();
        }

        #endregion
    }
} 