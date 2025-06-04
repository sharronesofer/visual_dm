using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;
using System.Net.Http;
using System.Text;
using NativeWebSocket;
using VDM.DTOs.Character;
using VDM.Infrastructure.Services;

namespace VDM.Core.Services
{
    public class SkillCheckService : MonoBehaviour, ISkillCheckService
    {
        [Header("API Configuration")]
        [SerializeField] private string baseApiUrl = "http://localhost:8000/api";
        [SerializeField] private string webSocketUrl = "ws://localhost:8000/ws";
        [SerializeField] private float requestTimeoutSeconds = 30f;
        [SerializeField] private int maxRetryAttempts = 3;
        [SerializeField] private float retryDelaySeconds = 1f;

        [Header("Debug Settings")]
        [SerializeField] private bool enableDebugLogging = true;
        [SerializeField] private bool simulateOfflineMode = false;

        private HttpClient httpClient;
        private WebSocket webSocket;
        private bool isWebSocketConnected = false;

        // Events for real-time updates
        public event Action<SkillCheckResultDTO> OnSkillCheckCompleted;
        public event Action<string> OnSkillCheckError;
        public event Action<bool> OnConnectionStatusChanged;

        private void Awake()
        {
            InitializeHttpClient();
            InitializeWebSocket();
        }

        private void InitializeHttpClient()
        {
            httpClient = new HttpClient();
            httpClient.Timeout = TimeSpan.FromSeconds(requestTimeoutSeconds);
            httpClient.DefaultRequestHeaders.Add("User-Agent", "VisualDM-Unity-Client/1.0");
        }

        private async void InitializeWebSocket()
        {
            if (simulateOfflineMode) return;

            try
            {
                webSocket = new WebSocket(webSocketUrl);

                webSocket.OnOpen += () =>
                {
                    DebugLog("WebSocket connection opened");
                    isWebSocketConnected = true;
                    OnConnectionStatusChanged?.Invoke(true);
                };

                webSocket.OnMessage += (bytes) =>
                {
                    var message = System.Text.Encoding.UTF8.GetString(bytes);
                    HandleWebSocketMessage(message);
                };

                webSocket.OnError += (e) =>
                {
                    DebugLog($"WebSocket error: {e}");
                    OnSkillCheckError?.Invoke($"WebSocket error: {e}");
                };

                webSocket.OnClose += (e) =>
                {
                    DebugLog($"WebSocket connection closed: {e}");
                    isWebSocketConnected = false;
                    OnConnectionStatusChanged?.Invoke(false);
                };

                await webSocket.Connect();
            }
            catch (Exception ex)
            {
                DebugLog($"Failed to initialize WebSocket: {ex.Message}");
                OnSkillCheckError?.Invoke($"WebSocket initialization failed: {ex.Message}");
            }
        }

        private void HandleWebSocketMessage(string message)
        {
            try
            {
                var wsMessage = JsonConvert.DeserializeObject<WebSocketMessage>(message);
                
                switch (wsMessage.type)
                {
                    case "skill_check_result":
                        var result = JsonConvert.DeserializeObject<SkillCheckResultDTO>(wsMessage.data.ToString());
                        OnSkillCheckCompleted?.Invoke(result);
                        break;
                    case "skill_check_error":
                        OnSkillCheckError?.Invoke(wsMessage.data.ToString());
                        break;
                    default:
                        DebugLog($"Unknown WebSocket message type: {wsMessage.type}");
                        break;
                }
            }
            catch (Exception ex)
            {
                DebugLog($"Error parsing WebSocket message: {ex.Message}");
            }
        }

        #region ISkillCheckService Implementation

        public async Task<SkillCheckResultDTO> ExecuteSkillCheckAsync(SkillCheckRequestDTO request)
        {
            if (simulateOfflineMode)
            {
                return SimulateSkillCheckResult(request);
            }

            return await ExecuteWithRetry(async () =>
            {
                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/skill-checks/execute", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<SkillCheckResultDTO>(responseJson);
            });
        }

        public async Task<PassiveSkillResultDTO> GetPassiveSkillScoreAsync(string characterId, string skillName, List<string> environmentalConditions = null)
        {
            if (simulateOfflineMode)
            {
                return SimulatePassiveSkillResult(skillName);
            }

            return await ExecuteWithRetry(async () =>
            {
                var request = new
                {
                    characterId,
                    skillName,
                    environmentalConditions = environmentalConditions ?? new List<string>()
                };

                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/skill-checks/passive", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<PassiveSkillResultDTO>(responseJson);
            });
        }

        public async Task<OpposedSkillCheckResultDTO> ExecuteOpposedSkillCheckAsync(string character1Id, string character2Id, string skill1, string skill2, List<string> environmentalConditions = null)
        {
            if (simulateOfflineMode)
            {
                return SimulateOpposedSkillResult(skill1, skill2);
            }

            return await ExecuteWithRetry(async () =>
            {
                var request = new
                {
                    character1Id,
                    character2Id,
                    skill1,
                    skill2,
                    environmentalConditions = environmentalConditions ?? new List<string>()
                };

                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/skill-checks/opposed", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<OpposedSkillCheckResultDTO>(responseJson);
            });
        }

        public async Task<GroupSkillCheckResultDTO> ExecuteGroupSkillCheckAsync(List<string> characterIds, string skillName, int difficultyClass, List<string> environmentalConditions = null)
        {
            if (simulateOfflineMode)
            {
                return SimulateGroupSkillResult(characterIds, skillName);
            }

            return await ExecuteWithRetry(async () =>
            {
                var request = new
                {
                    characterIds,
                    skillName,
                    difficultyClass,
                    environmentalConditions = environmentalConditions ?? new List<string>()
                };

                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/skill-checks/group", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<GroupSkillCheckResultDTO>(responseJson);
            });
        }

        public async Task<PerceptionResultDTO> ExecutePerceptionCheckAsync(string characterId, List<string> environmentalConditions = null, string targetType = null)
        {
            if (simulateOfflineMode)
            {
                return SimulatePerceptionResult();
            }

            return await ExecuteWithRetry(async () =>
            {
                var request = new
                {
                    characterId,
                    environmentalConditions = environmentalConditions ?? new List<string>(),
                    targetType
                };

                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/skill-checks/perception", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<PerceptionResultDTO>(responseJson);
            });
        }

        public async Task<StealthResultDTO> ExecuteStealthCheckAsync(string characterId, List<string> environmentalConditions = null, List<string> targetIds = null)
        {
            if (simulateOfflineMode)
            {
                return SimulateStealthResult();
            }

            return await ExecuteWithRetry(async () =>
            {
                var request = new
                {
                    characterId,
                    environmentalConditions = environmentalConditions ?? new List<string>(),
                    targetIds = targetIds ?? new List<string>()
                };

                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/skill-checks/stealth", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<StealthResultDTO>(responseJson);
            });
        }

        public async Task<SocialResultDTO> ExecuteSocialCheckAsync(string characterId, string interactionType, string targetId = null, List<string> environmentalConditions = null)
        {
            if (simulateOfflineMode)
            {
                return SimulateSocialResult(interactionType);
            }

            return await ExecuteWithRetry(async () =>
            {
                var request = new
                {
                    characterId,
                    interactionType,
                    targetId,
                    environmentalConditions = environmentalConditions ?? new List<string>()
                };

                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/skill-checks/social", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<SocialResultDTO>(responseJson);
            });
        }

        public async Task<InvestigationResultDTO> ExecuteInvestigationCheckAsync(string characterId, string investigationType, List<string> environmentalConditions = null)
        {
            if (simulateOfflineMode)
            {
                return SimulateInvestigationResult(investigationType);
            }

            return await ExecuteWithRetry(async () =>
            {
                var request = new
                {
                    characterId,
                    investigationType,
                    environmentalConditions = environmentalConditions ?? new List<string>()
                };

                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{baseApiUrl}/skill-checks/investigation", content);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<InvestigationResultDTO>(responseJson);
            });
        }

        public async Task RecordSkillCheckAnalyticsAsync(SkillCheckAnalyticsDTO analytics)
        {
            if (simulateOfflineMode) return;

            try
            {
                var json = JsonConvert.SerializeObject(analytics);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                await httpClient.PostAsync($"{baseApiUrl}/analytics/skill-checks", content);
            }
            catch (Exception ex)
            {
                DebugLog($"Failed to record analytics: {ex.Message}");
                // Don't throw - analytics failures shouldn't break gameplay
            }
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

            throw new Exception($"Operation failed after {maxRetryAttempts} attempts. Last error: {lastException?.Message}", lastException);
        }

        private void DebugLog(string message)
        {
            if (enableDebugLogging)
            {
                Debug.Log($"[SkillCheckService] {message}");
            }
        }

        #endregion

        #region Simulation Methods (for offline testing)

        private SkillCheckResultDTO SimulateSkillCheckResult(SkillCheckRequestDTO request)
        {
            var diceRoll = UnityEngine.Random.Range(1, 21);
            var totalRoll = diceRoll + request.SkillModifier;
            
            return new SkillCheckResultDTO
            {
                Success = totalRoll >= request.DifficultyClass,
                DiceRoll = diceRoll,
                TotalRoll = totalRoll,
                DifficultyClass = request.DifficultyClass,
                SkillModifier = request.SkillModifier,
                SkillName = request.SkillName,
                CharacterId = request.CharacterId,
                ResultDescription = totalRoll >= request.DifficultyClass ? "Success!" : "Failure",
                AppliedModifiers = request.EnvironmentalConditions,
                IsCriticalSuccess = diceRoll == 20,
                IsCriticalFailure = diceRoll == 1,
                Timestamp = DateTime.UtcNow
            };
        }

        private PassiveSkillResultDTO SimulatePassiveSkillResult(string skillName)
        {
            return new PassiveSkillResultDTO
            {
                SkillName = skillName,
                PassiveScore = UnityEngine.Random.Range(10, 25),
                SkillModifier = UnityEngine.Random.Range(0, 8),
                Success = true,
                ResultDescription = $"Passive {skillName} check simulated"
            };
        }

        private OpposedSkillCheckResultDTO SimulateOpposedSkillResult(string skill1, string skill2)
        {
            var roll1 = UnityEngine.Random.Range(1, 21) + UnityEngine.Random.Range(0, 8);
            var roll2 = UnityEngine.Random.Range(1, 21) + UnityEngine.Random.Range(0, 8);

            return new OpposedSkillCheckResultDTO
            {
                Winner = roll1 > roll2 ? "character1" : "character2",
                Character1Result = new SkillCheckResultDTO
                {
                    Success = roll1 > roll2,
                    TotalRoll = roll1,
                    SkillName = skill1,
                    ResultDescription = "Simulated opposed check"
                },
                Character2Result = new SkillCheckResultDTO
                {
                    Success = roll2 > roll1,
                    TotalRoll = roll2,
                    SkillName = skill2,
                    ResultDescription = "Simulated opposed check"
                }
            };
        }

        private GroupSkillCheckResultDTO SimulateGroupSkillResult(List<string> characterIds, string skillName)
        {
            var results = new List<SkillCheckResultDTO>();
            var successCount = 0;

            foreach (var id in characterIds)
            {
                var roll = UnityEngine.Random.Range(1, 21) + UnityEngine.Random.Range(0, 8);
                var success = roll >= 15; // Arbitrary DC for simulation
                if (success) successCount++;

                results.Add(new SkillCheckResultDTO
                {
                    Success = success,
                    TotalRoll = roll,
                    SkillName = skillName,
                    CharacterId = id,
                    ResultDescription = "Simulated group check"
                });
            }

            return new GroupSkillCheckResultDTO
            {
                OverallSuccess = successCount >= (characterIds.Count / 2 + 1), // Majority must succeed
                SuccessCount = successCount,
                TotalParticipants = characterIds.Count,
                IndividualResults = results
            };
        }

        private PerceptionResultDTO SimulatePerceptionResult()
        {
            return new PerceptionResultDTO
            {
                Success = UnityEngine.Random.value > 0.3f,
                TotalRoll = UnityEngine.Random.Range(8, 25),
                SkillName = "Perception",
                ResultDescription = "Simulated perception check",
                DetectedTargets = new List<string> { "hidden_door", "secret_passage" },
                PerceptionType = "visual",
                Range = UnityEngine.Random.Range(30, 120)
            };
        }

        private StealthResultDTO SimulateStealthResult()
        {
            return new StealthResultDTO
            {
                Success = UnityEngine.Random.value > 0.4f,
                TotalRoll = UnityEngine.Random.Range(8, 25),
                SkillName = "Stealth",
                ResultDescription = "Simulated stealth check",
                StealthLevel = UnityEngine.Random.Range(1, 4),
                DetectedBy = new List<string>(),
                ConcealmentType = "shadow"
            };
        }

        private SocialResultDTO SimulateSocialResult(string interactionType)
        {
            return new SocialResultDTO
            {
                Success = UnityEngine.Random.value > 0.35f,
                TotalRoll = UnityEngine.Random.Range(8, 25),
                SkillName = "Persuasion",
                ResultDescription = "Simulated social interaction",
                InteractionType = interactionType,
                ReputationChange = UnityEngine.Random.Range(-2, 3),
                UnlockedOptions = new List<string> { "additional_dialogue", "quest_shortcut" }
            };
        }

        private InvestigationResultDTO SimulateInvestigationResult(string investigationType)
        {
            return new InvestigationResultDTO
            {
                Success = UnityEngine.Random.value > 0.25f,
                TotalRoll = UnityEngine.Random.Range(8, 25),
                SkillName = "Investigation",
                ResultDescription = "Simulated investigation",
                InvestigationType = investigationType,
                CluesFound = new List<string> { "bloody_fingerprint", "torn_cloth", "mysterious_letter" },
                InvestigationTime = UnityEngine.Random.Range(300, 1200)
            };
        }

        #endregion

        #region Cleanup

        private void OnDestroy()
        {
            httpClient?.Dispose();
            webSocket?.Close();
        }

        private void OnApplicationPause(bool pauseStatus)
        {
            if (pauseStatus && isWebSocketConnected)
            {
                webSocket?.Close();
            }
            else if (!pauseStatus && !isWebSocketConnected)
            {
                _ = InitializeWebSocket();
            }
        }

        #endregion
    }
} 