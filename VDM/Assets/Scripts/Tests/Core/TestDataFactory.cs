using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace VDM.Tests.Core
{
    /// <summary>
    /// Factory for creating test data objects for various VDM systems
    /// </summary>
    public static class TestDataFactory
    {
        private static readonly System.Random _random = new System.Random();

        /// <summary>
        /// Create test data for a specific type
        /// </summary>
        public static T Create<T>() where T : class, new()
        {
            return Create<T>(new Dictionary<string, object>());
        }

        /// <summary>
        /// Create test data with specific property overrides
        /// </summary>
        public static T Create<T>(Dictionary<string, object> propertyOverrides) where T : class, new()
        {
            var instance = new T();
            var type = typeof(T);

            // Apply default test values based on type
            SetDefaultValues(instance, type);

            // Apply property overrides
            foreach (var kvp in propertyOverrides)
            {
                var property = type.GetProperty(kvp.Key);
                if (property != null && property.CanWrite)
                {
                    property.SetValue(instance, kvp.Value);
                }
            }

            return instance;
        }

        private static void SetDefaultValues(object instance, Type type)
        {
            var properties = type.GetProperties().Where(p => p.CanWrite);

            foreach (var property in properties)
            {
                var value = GenerateDefaultValue(property.PropertyType, property.Name);
                if (value != null)
                {
                    property.SetValue(instance, value);
                }
            }
        }

        private static object GenerateDefaultValue(Type propertyType, string propertyName)
        {
            var name = propertyName.ToLower();

            // Handle nullable types
            if (propertyType.IsGenericType && propertyType.GetGenericTypeDefinition() == typeof(Nullable<>))
            {
                propertyType = Nullable.GetUnderlyingType(propertyType);
            }

            // String properties
            if (propertyType == typeof(string))
            {
                return GenerateStringValue(name);
            }

            // Numeric properties
            if (propertyType == typeof(int))
            {
                return GenerateIntValue(name);
            }

            if (propertyType == typeof(float))
            {
                return GenerateFloatValue(name);
            }

            if (propertyType == typeof(double))
            {
                return GenerateDoubleValue(name);
            }

            // Boolean properties
            if (propertyType == typeof(bool))
            {
                return GenerateBoolValue(name);
            }

            // DateTime properties
            if (propertyType == typeof(DateTime))
            {
                return GenerateDateTimeValue(name);
            }

            // Enum properties
            if (propertyType.IsEnum)
            {
                var enumValues = Enum.GetValues(propertyType);
                return enumValues.GetValue(_random.Next(enumValues.Length));
            }

            // Vector properties
            if (propertyType == typeof(Vector2))
            {
                return new Vector2(_random.Next(-100, 100), _random.Next(-100, 100));
            }

            if (propertyType == typeof(Vector3))
            {
                return new Vector3(_random.Next(-100, 100), _random.Next(-100, 100), _random.Next(-100, 100));
            }

            // Color properties
            if (propertyType == typeof(Color))
            {
                return new Color(_random.NextSingle(), _random.NextSingle(), _random.NextSingle(), 1f);
            }

            // List properties
            if (propertyType.IsGenericType && propertyType.GetGenericTypeDefinition() == typeof(List<>))
            {
                var elementType = propertyType.GetGenericArguments()[0];
                var listType = typeof(List<>).MakeGenericType(elementType);
                var list = Activator.CreateInstance(listType);
                
                // Add a few test items
                for (int i = 0; i < _random.Next(1, 4); i++)
                {
                    var item = GenerateDefaultValue(elementType, $"item{i}");
                    if (item != null)
                    {
                        listType.GetMethod("Add").Invoke(list, new[] { item });
                    }
                }
                
                return list;
            }

            return null;
        }

        private static string GenerateStringValue(string propertyName)
        {
            return propertyName switch
            {
                "id" or "identifier" => Guid.NewGuid().ToString(),
                "name" or "title" => $"Test {propertyName} {_random.Next(1000)}",
                "description" => $"Test description for {propertyName}",
                "email" => $"test{_random.Next(1000)}@example.com",
                "username" => $"testuser{_random.Next(1000)}",
                "password" => "TestPassword123!",
                "status" => _random.Next(2) == 0 ? "active" : "inactive",
                "type" or "category" => $"TestType{_random.Next(10)}",
                "url" or "link" => $"https://example.com/test{_random.Next(1000)}",
                "path" => $"/test/path/{_random.Next(1000)}",
                "address" => $"{_random.Next(999)} Test Street",
                "city" => "Test City",
                "state" => "TS",
                "country" => "Test Country",
                "phone" => $"555-{_random.Next(100, 999):D3}-{_random.Next(1000, 9999):D4}",
                _ => $"Test {propertyName} Value"
            };
        }

        private static int GenerateIntValue(string propertyName)
        {
            return propertyName switch
            {
                "id" => _random.Next(1, 10000),
                "level" => _random.Next(1, 100),
                "health" or "hp" => _random.Next(1, 1000),
                "mana" or "mp" => _random.Next(1, 500),
                "experience" or "exp" or "xp" => _random.Next(0, 100000),
                "damage" => _random.Next(1, 100),
                "defense" => _random.Next(1, 50),
                "speed" => _random.Next(1, 20),
                "age" => _random.Next(18, 80),
                "quantity" or "count" => _random.Next(1, 100),
                "price" or "cost" => _random.Next(1, 10000),
                "weight" => _random.Next(1, 1000),
                "size" => _random.Next(1, 100),
                "rank" => _random.Next(1, 10),
                "score" => _random.Next(0, 1000),
                _ => _random.Next(1, 100)
            };
        }

        private static float GenerateFloatValue(string propertyName)
        {
            return propertyName switch
            {
                "progress" => _random.NextSingle(),
                "percentage" or "percent" => _random.NextSingle() * 100f,
                "accuracy" => _random.NextSingle(),
                "criticalchance" or "critchance" => _random.NextSingle() * 0.5f,
                "multiplier" => _random.NextSingle() * 2f + 0.5f,
                "scale" => _random.NextSingle() * 2f + 0.5f,
                "opacity" or "alpha" => _random.NextSingle(),
                "volume" => _random.NextSingle(),
                "duration" => _random.NextSingle() * 60f,
                "distance" => _random.NextSingle() * 1000f,
                "radius" => _random.NextSingle() * 100f,
                _ => _random.NextSingle() * 100f
            };
        }

        private static double GenerateDoubleValue(string propertyName)
        {
            return GenerateFloatValue(propertyName);
        }

        private static bool GenerateBoolValue(string propertyName)
        {
            return propertyName switch
            {
                "enabled" or "active" => true,
                "disabled" or "inactive" => false,
                "visible" => true,
                "hidden" => false,
                "completed" or "finished" => _random.Next(2) == 0,
                "started" or "begun" => true,
                "locked" => false,
                "unlocked" => true,
                _ => _random.Next(2) == 0
            };
        }

        private static DateTime GenerateDateTimeValue(string propertyName)
        {
            var baseDate = DateTime.UtcNow;
            return propertyName switch
            {
                "created" or "createdat" or "createddate" => baseDate.AddDays(-_random.Next(1, 365)),
                "updated" or "updatedat" or "modifieddate" => baseDate.AddDays(-_random.Next(1, 30)),
                "deleted" or "deletedat" => DateTime.MinValue,
                "started" or "startat" or "startdate" => baseDate.AddDays(-_random.Next(1, 100)),
                "ended" or "endat" or "enddate" => baseDate.AddDays(_random.Next(1, 100)),
                "due" or "duedate" => baseDate.AddDays(_random.Next(1, 30)),
                "birth" or "birthdate" or "birthday" => baseDate.AddYears(-_random.Next(18, 80)),
                _ => baseDate.AddDays(_random.Next(-365, 365))
            };
        }

        /// <summary>
        /// Create a list of test data objects
        /// </summary>
        public static List<T> CreateList<T>(int count, Func<int, Dictionary<string, object>> propertyOverrideGenerator = null) where T : class, new()
        {
            var list = new List<T>();
            for (int i = 0; i < count; i++)
            {
                var overrides = propertyOverrideGenerator?.Invoke(i) ?? new Dictionary<string, object>();
                list.Add(Create<T>(overrides));
            }
            return list;
        }

        /// <summary>
        /// Create test data for specific VDM systems
        /// </summary>
        public static class Systems
        {
            public static object CreateCharacterData()
            {
                return new
                {
                    Id = _random.Next(1, 10000),
                    Name = $"Test Character {_random.Next(1000)}",
                    Level = _random.Next(1, 100),
                    Health = _random.Next(50, 1000),
                    Mana = _random.Next(0, 500),
                    Experience = _random.Next(0, 100000),
                    Attributes = new
                    {
                        Strength = _random.Next(1, 20),
                        Dexterity = _random.Next(1, 20),
                        Intelligence = _random.Next(1, 20),
                        Constitution = _random.Next(1, 20)
                    },
                    Status = _random.Next(2) == 0 ? "alive" : "dead",
                    Class = new[] { "Warrior", "Mage", "Rogue", "Cleric" }[_random.Next(4)]
                };
            }

            public static object CreateQuestData()
            {
                return new
                {
                    Id = _random.Next(1, 10000),
                    Title = $"Test Quest {_random.Next(1000)}",
                    Description = "A test quest for validation purposes",
                    Status = new[] { "available", "active", "completed", "failed" }[_random.Next(4)],
                    Progress = _random.NextSingle(),
                    Difficulty = new[] { "easy", "medium", "hard", "legendary" }[_random.Next(4)],
                    Rewards = new
                    {
                        Experience = _random.Next(100, 5000),
                        Gold = _random.Next(10, 1000),
                        Items = new[] { "Test Sword", "Test Potion", "Test Armor" }
                    }
                };
            }

            public static object CreateFactionData()
            {
                return new
                {
                    Id = _random.Next(1, 1000),
                    Name = $"Test Faction {_random.Next(100)}",
                    Reputation = _random.Next(-100, 100),
                    Territory = $"Test Territory {_random.Next(10)}",
                    Leader = $"Leader {_random.Next(100)}",
                    Members = _random.Next(10, 1000),
                    Relations = new Dictionary<string, int>
                    {
                        { "Allied Faction", _random.Next(50, 100) },
                        { "Enemy Faction", _random.Next(-100, -50) }
                    }
                };
            }

            public static object CreateCombatData()
            {
                return new
                {
                    Id = _random.Next(1, 10000),
                    AttackerId = _random.Next(1, 1000),
                    DefenderId = _random.Next(1, 1000),
                    Action = new[] { "attack", "defend", "cast_spell", "use_item" }[_random.Next(4)],
                    Damage = _random.Next(1, 100),
                    IsCritical = _random.Next(10) == 0,
                    HitChance = _random.NextSingle(),
                    Result = new[] { "hit", "miss", "critical", "blocked" }[_random.Next(4)]
                };
            }

            public static object CreateInventoryData()
            {
                return new
                {
                    Id = _random.Next(1, 10000),
                    OwnerId = _random.Next(1, 1000),
                    Items = CreateList<object>(5, i => new Dictionary<string, object>
                    {
                        { "ItemId", i + 1 },
                        { "Name", $"Test Item {i}" },
                        { "Quantity", _random.Next(1, 10) },
                        { "Type", new[] { "weapon", "armor", "consumable", "misc" }[_random.Next(4)] }
                    }),
                    Capacity = _random.Next(20, 100),
                    Weight = _random.Next(1, 500)
                };
            }
        }
    }
} 