using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;

namespace VDM.Tests.Core
{
    /// <summary>
    /// Mock backend service that simulates API responses for testing
    /// </summary>
    public class MockBackendService : IDisposable
    {
        private readonly Dictionary<string, object> _mockData;
        private readonly Dictionary<string, MockAPIResponse> _apiResponses;
        private MockMode _mode;
        private bool _disposed;

        public enum MockMode
        {
            Offline,    // No network calls, all data from local mocks
            Mock,       // Mock API responses but simulate network behavior
            Live        // Use actual backend (for integration tests)
        }

        public MockBackendService()
        {
            _mockData = new Dictionary<string, object>();
            _apiResponses = new Dictionary<string, MockAPIResponse>();
            _mode = MockMode.Mock;
            InitializeDefaultMocks();
        }

        public void EnableOfflineMode() => _mode = MockMode.Offline;
        public void EnableMockMode() => _mode = MockMode.Mock;
        public void EnableLiveMode() => _mode = MockMode.Live;

        /// <summary>
        /// Initialize default mock data for all systems
        /// </summary>
        private void InitializeDefaultMocks()
        {
            InitializeCharacterMocks();
            InitializeFactionMocks();
            InitializeQuestMocks();
            InitializeCombatMocks();
            InitializeWorldMocks();
            InitializeDialogueMocks();
            InitializeEconomyMocks();
            InitializeInventoryMocks();
            InitializeAnalyticsMocks();
        }

        private void InitializeCharacterMocks()
        {
            SetMockData("characters", new List<object>
            {
                new { id = 1, name = "Test Character", level = 5, health = 100 },
                new { id = 2, name = "Another Character", level = 3, health = 80 }
            });

            SetAPIResponse("GET", "/api/characters", new MockAPIResponse
            {
                StatusCode = 200,
                Data = GetMockData("characters"),
                DelayMs = 100
            });

            SetAPIResponse("POST", "/api/characters", new MockAPIResponse
            {
                StatusCode = 201,
                Data = new { id = 3, name = "New Character", level = 1, health = 100 },
                DelayMs = 200
            });
        }

        private void InitializeFactionMocks()
        {
            SetMockData("factions", new List<object>
            {
                new { id = 1, name = "Test Faction", reputation = 50, territory = "North" },
                new { id = 2, name = "Rival Faction", reputation = -20, territory = "South" }
            });

            SetAPIResponse("GET", "/api/factions", new MockAPIResponse
            {
                StatusCode = 200,
                Data = GetMockData("factions"),
                DelayMs = 150
            });
        }

        private void InitializeQuestMocks()
        {
            SetMockData("quests", new List<object>
            {
                new { id = 1, title = "Test Quest", status = "active", progress = 0.5f },
                new { id = 2, title = "Another Quest", status = "completed", progress = 1.0f }
            });

            SetAPIResponse("GET", "/api/quests", new MockAPIResponse
            {
                StatusCode = 200,
                Data = GetMockData("quests"),
                DelayMs = 120
            });
        }

        private void InitializeCombatMocks()
        {
            SetMockData("combat_stats", new
            {
                damage = 25,
                accuracy = 0.85f,
                defense = 15,
                criticalChance = 0.15f
            });

            SetAPIResponse("POST", "/api/combat/action", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { success = true, damage = 25, critical = false },
                DelayMs = 50
            });
        }

        private void InitializeWorldMocks()
        {
            SetMockData("world_state", new
            {
                time = "Day 15, Hour 14",
                weather = "Clear",
                globalEvents = new List<string> { "Harvest Festival", "Trade Route Disruption" }
            });

            SetAPIResponse("GET", "/api/world/state", new MockAPIResponse
            {
                StatusCode = 200,
                Data = GetMockData("world_state"),
                DelayMs = 80
            });
        }

        private void InitializeDialogueMocks()
        {
            SetMockData("dialogue_options", new List<object>
            {
                new { id = 1, text = "Hello, how are you?", response = "I'm doing well, thank you!" },
                new { id = 2, text = "What brings you here?", response = "I'm looking for adventure." }
            });

            SetAPIResponse("GET", "/api/dialogue", new MockAPIResponse
            {
                StatusCode = 200,
                Data = GetMockData("dialogue_options"),
                DelayMs = 90
            });
        }

        private void InitializeEconomyMocks()
        {
            SetMockData("market_data", new
            {
                gold = 1000,
                items = new List<object>
                {
                    new { id = 1, name = "Iron Sword", price = 100, quantity = 5 },
                    new { id = 2, name = "Health Potion", price = 25, quantity = 20 }
                }
            });

            SetAPIResponse("GET", "/api/economy/market", new MockAPIResponse
            {
                StatusCode = 200,
                Data = GetMockData("market_data"),
                DelayMs = 110
            });
        }

        private void InitializeInventoryMocks()
        {
            SetMockData("inventory", new List<object>
            {
                new { id = 1, name = "Iron Sword", quantity = 1, equipped = true },
                new { id = 2, name = "Health Potion", quantity = 5, equipped = false }
            });

            SetAPIResponse("GET", "/api/inventory", new MockAPIResponse
            {
                StatusCode = 200,
                Data = GetMockData("inventory"),
                DelayMs = 70
            });
        }

        private void InitializeAnalyticsMocks()
        {
            SetMockData("analytics", new
            {
                playerStats = new
                {
                    playtime = 3600,
                    questsCompleted = 15,
                    battlesWon = 8,
                    itemsCollected = 42
                }
            });

            SetAPIResponse("GET", "/api/analytics", new MockAPIResponse
            {
                StatusCode = 200,
                Data = GetMockData("analytics"),
                DelayMs = 200
            });
        }

        /// <summary>
        /// Set mock data for a specific key
        /// </summary>
        public void SetMockData(string key, object data)
        {
            _mockData[key] = data;
        }

        /// <summary>
        /// Get mock data for a specific key
        /// </summary>
        public T GetMockData<T>(string key, T defaultValue = default(T))
        {
            if (_mockData.TryGetValue(key, out var data))
            {
                return JsonConvert.DeserializeObject<T>(JsonConvert.SerializeObject(data));
            }
            return defaultValue;
        }

        /// <summary>
        /// Get mock data as object
        /// </summary>
        public object GetMockData(string key)
        {
            return _mockData.TryGetValue(key, out var data) ? data : null;
        }

        /// <summary>
        /// Set API response for a specific endpoint
        /// </summary>
        public void SetAPIResponse(string method, string endpoint, MockAPIResponse response)
        {
            var key = $"{method.ToUpper()} {endpoint}";
            _apiResponses[key] = response;
        }

        /// <summary>
        /// Simulate API call and return mock response
        /// </summary>
        public async Task<MockAPIResponse> CallAPI(string method, string endpoint, object data = null)
        {
            if (_mode == MockMode.Live)
            {
                // In live mode, would make actual API calls
                throw new NotImplementedException("Live mode not implemented in mock service");
            }

            var key = $"{method.ToUpper()} {endpoint}";
            if (!_apiResponses.TryGetValue(key, out var response))
            {
                return new MockAPIResponse
                {
                    StatusCode = 404,
                    Error = $"No mock response defined for {key}",
                    DelayMs = 0
                };
            }

            // Simulate network delay
            if (_mode == MockMode.Mock && response.DelayMs > 0)
            {
                await Task.Delay(response.DelayMs);
            }

            // Simulate occasional network failures in mock mode
            if (_mode == MockMode.Mock && UnityEngine.Random.Range(0f, 1f) < 0.01f) // 1% failure rate
            {
                return new MockAPIResponse
                {
                    StatusCode = 500,
                    Error = "Simulated network error",
                    DelayMs = response.DelayMs
                };
            }

            return response;
        }

        /// <summary>
        /// Reset all mock data to defaults
        /// </summary>
        public void Reset()
        {
            _mockData.Clear();
            _apiResponses.Clear();
            InitializeDefaultMocks();
        }

        /// <summary>
        /// Simulate WebSocket message
        /// </summary>
        public void SimulateWebSocketMessage(string channel, object data)
        {
            // In a real implementation, this would trigger WebSocket event handlers
            UnityEngine.Debug.Log($"[MOCK WebSocket] Channel: {channel}, Data: {JsonConvert.SerializeObject(data)}");
        }

        /// <summary>
        /// Generate test data for stress testing
        /// </summary>
        public void GenerateStressTestData(string dataType, int count)
        {
            var testData = new List<object>();
            
            for (int i = 0; i < count; i++)
            {
                testData.Add(GenerateTestItem(dataType, i));
            }
            
            SetMockData($"stress_test_{dataType}", testData);
        }

        private object GenerateTestItem(string dataType, int index)
        {
            return dataType.ToLower() switch
            {
                "characters" => new { id = index, name = $"Character {index}", level = index % 10 + 1, health = 100 },
                "quests" => new { id = index, title = $"Quest {index}", status = index % 2 == 0 ? "active" : "completed" },
                "items" => new { id = index, name = $"Item {index}", price = index * 10, quantity = index % 5 + 1 },
                _ => new { id = index, data = $"Test data {index}" }
            };
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _mockData?.Clear();
                _apiResponses?.Clear();
                _disposed = true;
            }
        }
    }

    /// <summary>
    /// Mock API response structure
    /// </summary>
    public class MockAPIResponse
    {
        public int StatusCode { get; set; } = 200;
        public object Data { get; set; }
        public string Error { get; set; }
        public int DelayMs { get; set; } = 0;
        public Dictionary<string, string> Headers { get; set; } = new Dictionary<string, string>();
        
        public bool IsSuccess => StatusCode >= 200 && StatusCode < 300;
    }
} 