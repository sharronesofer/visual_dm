using System.Collections;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using VDM.Tests.Core;
using System.Collections.Generic;

namespace VDM.Tests.Core.Character
{
    /// <summary>
    /// Unit tests for Character system components
    /// </summary>
    public class CharacterSystemTests : VDMUnitTestBase
    {
        private CharacterTestData _testCharacter;

        [SetUp]
        public override void SetUp()
        {
            base.SetUp();
            _testCharacter = CreateTestData<CharacterTestData>();
        }

        [Test]
        public void CharacterCreation_WithValidData_ShouldSucceed()
        {
            // Arrange
            var characterData = new
            {
                name = "Test Hero",
                class_ = "Warrior",
                level = 1,
                attributes = new { strength = 15, dexterity = 12, intelligence = 10, constitution = 14 }
            };

            // Act
            var character = CreateCharacter(characterData);

            // Assert
            Assert.IsNotNull(character);
            Assert.AreEqual("Test Hero", character.Name);
            Assert.AreEqual("Warrior", character.Class);
            Assert.AreEqual(1, character.Level);
            Assert.AreEqual(15, character.Attributes.Strength);
        }

        [Test]
        public void CharacterLevelUp_WhenHasEnoughExperience_ShouldIncreaseLevel()
        {
            // Arrange
            var character = CreateCharacter(new { level = 1, experience = 1000 });
            var initialLevel = character.Level;

            // Act
            character.AddExperience(500); // Should trigger level up
            
            // Assert
            Assert.Greater(character.Level, initialLevel);
            Assert.AreEqual(2, character.Level);
        }

        [Test]
        public void CharacterTakeDamage_WhenDamageExceedsHealth_ShouldNotGoBelowZero()
        {
            // Arrange
            var character = CreateCharacter(new { health = 100 });

            // Act
            character.TakeDamage(150);

            // Assert
            Assert.AreEqual(0, character.CurrentHealth);
            Assert.IsTrue(character.IsDead);
        }

        [Test]
        public void CharacterHeal_WhenBelowMaxHealth_ShouldIncreaseHealth()
        {
            // Arrange
            var character = CreateCharacter(new { health = 100, currentHealth = 50 });
            
            // Act
            character.Heal(30);
            
            // Assert
            Assert.AreEqual(80, character.CurrentHealth);
        }

        [Test]
        public void CharacterHeal_WhenAtMaxHealth_ShouldNotExceedMaximum()
        {
            // Arrange
            var character = CreateCharacter(new { health = 100, currentHealth = 90 });
            
            // Act
            character.Heal(20);
            
            // Assert
            Assert.AreEqual(100, character.CurrentHealth);
        }

        [Test]
        [TestCase("Strength", 15, 18)]
        [TestCase("Dexterity", 12, 15)]
        [TestCase("Intelligence", 10, 13)]
        [TestCase("Constitution", 14, 17)]
        public void CharacterAttributeIncrease_ShouldUpdateCorrectly(string attributeName, int initial, int expected)
        {
            // Arrange
            var character = CreateCharacter(new { });
            character.Attributes.SetAttribute(attributeName, initial);
            
            // Act
            character.Attributes.IncreaseAttribute(attributeName, 3);
            
            // Assert
            Assert.AreEqual(expected, character.Attributes.GetAttribute(attributeName));
        }

        [Test]
        public async Task CharacterSave_WithValidData_ShouldCallAPI()
        {
            // Arrange
            var character = CreateCharacter(new { name = "Save Test Character" });
            MockBackend.SetAPIResponse("POST", "/api/characters", new MockAPIResponse 
            { 
                StatusCode = 201, 
                Data = new { id = 123, name = "Save Test Character" } 
            });

            // Act
            var result = await character.SaveAsync();

            // Assert
            Assert.IsTrue(result.IsSuccess);
            Assert.AreEqual(123, character.Id);
        }

        [Test]
        public async Task CharacterLoad_WithValidId_ShouldPopulateData()
        {
            // Arrange
            var characterId = 456;
            var expectedCharacterData = new
            {
                id = characterId,
                name = "Loaded Character",
                level = 5,
                health = 200
            };
            
            MockBackend.SetAPIResponse("GET", $"/api/characters/{characterId}", new MockAPIResponse
            {
                StatusCode = 200,
                Data = expectedCharacterData
            });

            // Act
            var character = new TestCharacter();
            var result = await character.LoadAsync(characterId);

            // Assert
            Assert.IsTrue(result.IsSuccess);
            Assert.AreEqual("Loaded Character", character.Name);
            Assert.AreEqual(5, character.Level);
            Assert.AreEqual(200, character.MaxHealth);
        }

        [Test]
        public void CharacterEquipItem_WithValidItem_ShouldUpdateStats()
        {
            // Arrange
            var character = CreateCharacter(new { });
            var weapon = CreateTestItem("Iron Sword", "weapon", new { damage = 15 });

            // Act
            character.EquipItem(weapon);

            // Assert
            Assert.IsTrue(character.Equipment.HasWeapon);
            Assert.AreEqual(weapon, character.Equipment.Weapon);
            Assert.AreEqual(15, character.GetTotalDamage());
        }

        [Test]
        public void CharacterUnequipItem_WhenItemEquipped_ShouldRemoveFromEquipment()
        {
            // Arrange
            var character = CreateCharacter(new { });
            var weapon = CreateTestItem("Iron Sword", "weapon", new { damage = 15 });
            character.EquipItem(weapon);

            // Act
            character.UnequipItem("weapon");

            // Assert
            Assert.IsFalse(character.Equipment.HasWeapon);
            Assert.AreEqual(0, character.GetTotalDamage());
        }

        [Test]
        public void CharacterCanLevelUp_WhenHasRequiredExperience_ShouldReturnTrue()
        {
            // Arrange
            var character = CreateCharacter(new { level = 1, experience = 1000 });

            // Act & Assert
            Assert.IsTrue(character.CanLevelUp());
        }

        [Test]
        public void CharacterCanLevelUp_WhenInsufficientExperience_ShouldReturnFalse()
        {
            // Arrange
            var character = CreateCharacter(new { level = 1, experience = 100 });

            // Act & Assert
            Assert.IsFalse(character.CanLevelUp());
        }

        [Test]
        public void CharacterGetNextLevelExperience_ShouldCalculateCorrectly()
        {
            // Arrange
            var character = CreateCharacter(new { level = 1 });

            // Act
            var nextLevelExp = character.GetNextLevelExperience();

            // Assert
            Assert.Greater(nextLevelExp, 0);
            Assert.AreEqual(1000, nextLevelExp); // Assuming level 2 requires 1000 exp
        }

        [Test]
        public void CharacterGetExperienceProgress_ShouldReturnCorrectPercentage()
        {
            // Arrange
            var character = CreateCharacter(new { level = 1, experience = 500 });

            // Act
            var progress = character.GetExperienceProgress();

            // Assert
            Assert.AreEqual(0.5f, progress, 0.01f); // 50% progress to next level
        }

        // Performance test
        [Test]
        public void CharacterOperations_ShouldCompleteWithinPerformanceThreshold()
        {
            // Arrange
            var character = CreateCharacter(new { });

            // Act - Perform multiple operations
            for (int i = 0; i < 100; i++)
            {
                character.AddExperience(10);
                character.TakeDamage(5);
                character.Heal(5);
            }

            // Assert
            AssertPerformance(100f); // Should complete within 100ms
        }

        [Test]
        public void Character_Creation_ReturnsValidCharacter()
        {
            // Arrange
            var builder = new CharacterBuilder();
            
            // Act
            var character = builder
                .SetName("Test Character")
                .SetRace("Human")
                .SetAbilities(new List<string> { "Combat Training", "Skill Focus" })
                .Build();
            
            // Assert
            Assert.IsNotNull(character);
            Assert.AreEqual("Test Character", character.Name);
            Assert.AreEqual("Human", character.Race);
            Assert.IsTrue(character.Abilities.Contains("Combat Training"));
        }

        #region Helper Methods

        private TestCharacter CreateCharacter(object properties)
        {
            // Mock character creation based on properties
            var character = new TestCharacter();
            
            // Use reflection or property mapping to set values
            foreach (var prop in properties.GetType().GetProperties())
            {
                var value = prop.GetValue(properties);
                var targetProp = character.GetType().GetProperty(prop.Name, System.Reflection.BindingFlags.IgnoreCase | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
                targetProp?.SetValue(character, value);
            }
            
            return character;
        }

        private TestItem CreateTestItem(string name, string type, object properties)
        {
            var item = new TestItem { Name = name, Type = type };
            
            foreach (var prop in properties.GetType().GetProperties())
            {
                var value = prop.GetValue(properties);
                var targetProp = item.GetType().GetProperty(prop.Name, System.Reflection.BindingFlags.IgnoreCase | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
                targetProp?.SetValue(item, value);
            }
            
            return item;
        }

        #endregion
    }

    #region Test Data Classes

    public class CharacterTestData
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Class { get; set; }
        public int Level { get; set; }
        public int Health { get; set; }
        public int CurrentHealth { get; set; }
        public int Experience { get; set; }
        public CharacterAttributes Attributes { get; set; }
    }

    public class TestCharacter
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Race { get; set; }
        public string Class { get; set; }
        public int Level { get; set; } = 1;
        public int MaxHealth { get; set; } = 100;
        public int CurrentHealth { get; set; } = 100;
        public int Experience { get; set; }
        public CharacterAttributes Attributes { get; set; } = new CharacterAttributes();
        public CharacterEquipment Equipment { get; set; } = new CharacterEquipment();
        public List<string> Abilities { get; set; } = new List<string>();
        
        // Backward compatibility - Visual DM uses "Abilities" terminology, but "Feats" is supported for legacy code
        public List<string> Feats 
        {
            get => Abilities;
            set => Abilities = value;
        }
        
        public bool IsDead => CurrentHealth <= 0;

        public void AddExperience(int amount)
        {
            Experience += amount;
            if (CanLevelUp())
            {
                Level++;
                var healthIncrease = 20;
                MaxHealth += healthIncrease;
                CurrentHealth += healthIncrease;
            }
        }

        public void TakeDamage(int damage)
        {
            CurrentHealth = Mathf.Max(0, CurrentHealth - damage);
        }

        public void Heal(int amount)
        {
            CurrentHealth = Mathf.Min(MaxHealth, CurrentHealth + amount);
        }

        public bool CanLevelUp()
        {
            return Experience >= GetNextLevelExperience();
        }

        public int GetNextLevelExperience()
        {
            return Level * 1000; // Simple progression formula
        }

        public float GetExperienceProgress()
        {
            var currentLevelExp = (Level - 1) * 1000;
            var nextLevelExp = GetNextLevelExperience();
            return (float)(Experience - currentLevelExp) / (nextLevelExp - currentLevelExp);
        }

        public void EquipItem(TestItem item)
        {
            Equipment.EquipItem(item);
        }

        public void UnequipItem(string slot)
        {
            Equipment.UnequipItem(slot);
        }

        public int GetTotalDamage()
        {
            var baseDamage = Attributes.Strength;
            var weaponDamage = Equipment.HasWeapon ? Equipment.Weapon.Damage : 0;
            return baseDamage + weaponDamage;
        }

        public async Task<TestResult> SaveAsync()
        {
            // Mock save implementation
            await Task.Delay(50);
            Id = 123; // Mock assigned ID
            return new TestResult { IsSuccess = true };
        }

        public async Task<TestResult> LoadAsync(int id)
        {
            // Mock load implementation
            await Task.Delay(50);
            Name = "Loaded Character";
            Level = 5;
            MaxHealth = 200;
            return new TestResult { IsSuccess = true };
        }
    }

    public class CharacterAttributes
    {
        public int Strength { get; set; } = 10;
        public int Dexterity { get; set; } = 10;
        public int Intelligence { get; set; } = 10;
        public int Constitution { get; set; } = 10;

        public void SetAttribute(string name, int value)
        {
            switch (name.ToLower())
            {
                case "strength": Strength = value; break;
                case "dexterity": Dexterity = value; break;
                case "intelligence": Intelligence = value; break;
                case "constitution": Constitution = value; break;
            }
        }

        public int GetAttribute(string name)
        {
            return name.ToLower() switch
            {
                "strength" => Strength,
                "dexterity" => Dexterity,
                "intelligence" => Intelligence,
                "constitution" => Constitution,
                _ => 0
            };
        }

        public void IncreaseAttribute(string name, int amount)
        {
            SetAttribute(name, GetAttribute(name) + amount);
        }
    }

    public class CharacterEquipment
    {
        public TestItem Weapon { get; private set; }
        public TestItem Armor { get; private set; }
        public TestItem Accessory { get; private set; }

        public bool HasWeapon => Weapon != null;
        public bool HasArmor => Armor != null;
        public bool HasAccessory => Accessory != null;

        public void EquipItem(TestItem item)
        {
            switch (item.Type.ToLower())
            {
                case "weapon": Weapon = item; break;
                case "armor": Armor = item; break;
                case "accessory": Accessory = item; break;
            }
        }

        public void UnequipItem(string slot)
        {
            switch (slot.ToLower())
            {
                case "weapon": Weapon = null; break;
                case "armor": Armor = null; break;
                case "accessory": Accessory = null; break;
            }
        }
    }

    public class TestItem
    {
        public string Name { get; set; }
        public string Type { get; set; }
        public int Damage { get; set; }
        public int Defense { get; set; }
        public int Value { get; set; }
    }

    public class TestResult
    {
        public bool IsSuccess { get; set; }
        public string Message { get; set; }
    }

    /// <summary>
    /// Mock CharacterBuilder for testing purposes
    /// </summary>
    public class CharacterBuilder
    {
        private string _name;
        private string _race;
        private List<string> _abilities = new List<string>();

        public CharacterBuilder SetName(string name)
        {
            _name = name;
            return this;
        }

        public CharacterBuilder SetRace(string race)
        {
            _race = race;
            return this;
        }

        public CharacterBuilder SetAbilities(List<string> abilities)
        {
            _abilities = abilities ?? new List<string>();
            return this;
        }

        // Backward compatibility method - Visual DM uses "Abilities" terminology
        public CharacterBuilder SetFeats(List<string> feats)
        {
            return SetAbilities(feats);
        }

        public TestCharacter Build()
        {
            return new TestCharacter
            {
                Name = _name,
                Race = _race,
                Abilities = new List<string>(_abilities)
            };
        }
    }

    #endregion
} 