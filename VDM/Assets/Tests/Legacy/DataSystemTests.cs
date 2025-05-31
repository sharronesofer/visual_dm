using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using NUnit.Framework;
using VisualDM.Data;

namespace VDM.Tests.Systems.Data
{
    /// <summary>
    /// Comprehensive test suite for the data systems including Entity management,
    /// ModDataManager functionality, and data consistency validation.
    /// </summary>
    [TestFixture]
    public class DataSystemTests
    {
        private ModDataManager _dataManager;
        private string _testModPath;
        
        [SetUp]
        public void Setup()
        {
            // Initialize test environment
            _dataManager = new ModDataManager();
            _testModPath = Path.Combine(Application.temporaryDataPath, "TestMods");
            
            // Clean up any previous test data
            if (Directory.Exists(_testModPath))
                Directory.Delete(_testModPath, true);
                
            Directory.CreateDirectory(_testModPath);
        }
        
        [TearDown]
        public void TearDown()
        {
            // Clean up test data
            _dataManager?.Shutdown();
            
            if (Directory.Exists(_testModPath))
                Directory.Delete(_testModPath, true);
        }
        
        #region Entity Base Class Tests
        
        [Test]
        public void Entity_Creation_ShouldGenerateValidId()
        {
            // Arrange & Act
            var entity = new TestEntity("Test Entity");
            
            // Assert
            Assert.IsNotNull(entity.Id);
            Assert.IsNotEmpty(entity.Id);
            Assert.AreEqual("Test Entity", entity.Name);
            Assert.AreEqual("TestEntity", entity.EntityType);
            Assert.IsTrue(entity.IsActive);
            Assert.LessOrEqual(entity.CreatedAt, DateTime.UtcNow);
            Assert.LessOrEqual(entity.UpdatedAt, DateTime.UtcNow);
        }
        
        [Test]
        public void Entity_Properties_ShouldSupportCRUDOperations()
        {
            // Arrange
            var entity = new TestEntity("Test Entity");
            
            // Act & Assert - Create
            entity.SetProperty("health", 100);
            Assert.IsTrue(entity.HasProperty("health"));
            Assert.AreEqual(100, entity.GetProperty<int>("health"));
            
            // Act & Assert - Read
            Assert.AreEqual(100, entity.GetProperty<int>("health"));
            Assert.AreEqual(0, entity.GetProperty<int>("nonexistent"));
            Assert.AreEqual(50, entity.GetProperty<int>("nonexistent", 50));
            
            // Act & Assert - Update
            entity.SetProperty("health", 80);
            Assert.AreEqual(80, entity.GetProperty<int>("health"));
            
            // Act & Assert - Delete
            Assert.IsTrue(entity.RemoveProperty("health"));
            Assert.IsFalse(entity.HasProperty("health"));
            Assert.IsFalse(entity.RemoveProperty("health")); // Second removal should fail
        }
        
        [Test]
        public void Entity_PropertyTypeCasting_ShouldHandleInvalidCasts()
        {
            // Arrange
            var entity = new TestEntity("Test Entity");
            entity.SetProperty("stringValue", "hello");
            
            // Act & Assert
            Assert.AreEqual("hello", entity.GetProperty<string>("stringValue"));
            Assert.AreEqual(0, entity.GetProperty<int>("stringValue")); // Invalid cast should return default
            Assert.AreEqual(42, entity.GetProperty<int>("stringValue", 42)); // Invalid cast should return default value
        }
        
        [Test]
        public void Entity_ClearProperties_ShouldRemoveAllProperties()
        {
            // Arrange
            var entity = new TestEntity("Test Entity");
            entity.SetProperty("prop1", "value1");
            entity.SetProperty("prop2", 123);
            entity.SetProperty("prop3", true);
            
            // Act
            entity.ClearProperties();
            
            // Assert
            Assert.IsFalse(entity.HasProperty("prop1"));
            Assert.IsFalse(entity.HasProperty("prop2"));
            Assert.IsFalse(entity.HasProperty("prop3"));
            Assert.AreEqual(0, entity.Properties.Count);
        }
        
        [Test]
        public void Entity_Touch_ShouldUpdateTimestamp()
        {
            // Arrange
            var entity = new TestEntity("Test Entity");
            var originalTimestamp = entity.UpdatedAt;
            
            // Wait a tiny bit to ensure timestamp difference
            System.Threading.Thread.Sleep(1);
            
            // Act
            entity.Touch();
            
            // Assert
            Assert.Greater(entity.UpdatedAt, originalTimestamp);
        }
        
        [Test]
        public void Entity_Clone_ShouldCreateDeepCopy()
        {
            // Arrange
            var original = new TestEntity("Original Entity");
            original.SetProperty("health", 100);
            original.SetProperty("level", 5);
            original.SetProperty("equipped", new List<string> { "sword", "shield" });
            
            // Act
            var clone = original.Clone() as TestEntity;
            
            // Assert
            Assert.IsNotNull(clone);
            Assert.AreNotSame(original, clone);
            Assert.AreEqual(original.Id, clone.Id);
            Assert.AreEqual(original.Name, clone.Name);
            Assert.AreEqual(original.GetProperty<int>("health"), clone.GetProperty<int>("health"));
            Assert.AreEqual(original.GetProperty<int>("level"), clone.GetProperty<int>("level"));
            
            // Modify clone and ensure original is unaffected
            clone.SetProperty("health", 50);
            Assert.AreEqual(100, original.GetProperty<int>("health"));
            Assert.AreEqual(50, clone.GetProperty<int>("health"));
        }
        
        #endregion
        
        #region ModDataManager Tests
        
        [Test]
        public void ModDataManager_Initialize_ShouldCreateDirectories()
        {
            // Arrange
            var manager = new ModDataManager();
            
            // Act
            manager.Initialize();
            
            // Assert
            Assert.IsTrue(Directory.Exists(manager.BasePath));
            Assert.IsTrue(Directory.Exists(manager.UserModsPath));
            
            manager.Shutdown();
        }
        
        [Test]
        public void ModDataManager_LoadBaseMod_ShouldCreateDefaultIfMissing()
        {
            // Arrange
            var manager = new ModDataManager();
            
            // Act
            manager.Initialize();
            
            // Assert
            var loadedMods = manager.GetLoadedMods();
            Assert.IsNotEmpty(loadedMods);
            
            var baseMod = loadedMods.Find(m => m.Id == "base");
            Assert.IsNotNull(baseMod);
            Assert.AreEqual("Base Mod", baseMod.Name);
            Assert.IsNotEmpty(baseMod.DataCollections);
            
            manager.Shutdown();
        }
        
        [Test]
        public void ModDataManager_DataCollections_ShouldSupportCRUDOperations()
        {
            // Arrange
            var manager = new ModDataManager();
            manager.Initialize();
            
            // Test getting data from empty collection
            var emptyResult = manager.GetData<string>("Characters", "nonexistent");
            Assert.IsNull(emptyResult);
            
            // Test getting with default value
            var defaultResult = manager.GetData("Characters", "nonexistent", "default");
            Assert.AreEqual("default", defaultResult);
            
            // Test getting IDs from collection
            var ids = manager.GetDataIds("Characters");
            Assert.IsNotNull(ids);
            
            manager.Shutdown();
        }
        
        #endregion
        
        #region Data Consistency Tests
        
        [Test]
        public void DataConsistency_EntityReferences_ShouldBeValid()
        {
            // Arrange
            var entities = new List<TestEntity>
            {
                new TestEntity("1", "Entity1"),
                new TestEntity("2", "Entity2"),
                new TestEntity("3", "Entity3")
            };
            
            // Create references between entities
            entities[0].SetProperty("references", new List<string> { "2", "3" });
            entities[1].SetProperty("references", new List<string> { "3" });
            entities[2].SetProperty("references", new List<string>()); // No references
            
            // Act - Validate references
            var validationResult = ValidateEntityReferences(entities);
            
            // Assert
            Assert.IsTrue(validationResult.IsValid);
            Assert.AreEqual(0, validationResult.InvalidReferences.Count);
            Assert.AreEqual(3, validationResult.TotalEntitiesChecked);
        }
        
        [Test]
        public void DataConsistency_EntityReferences_ShouldDetectInvalidReferences()
        {
            // Arrange
            var entities = new List<TestEntity>
            {
                new TestEntity("1", "Entity1"),
                new TestEntity("2", "Entity2")
            };
            
            // Create invalid references
            entities[0].SetProperty("references", new List<string> { "2", "999" }); // 999 doesn't exist
            entities[1].SetProperty("references", new List<string> { "888", "777" }); // Both don't exist
            
            // Act
            var validationResult = ValidateEntityReferences(entities);
            
            // Assert
            Assert.IsFalse(validationResult.IsValid);
            Assert.AreEqual(3, validationResult.InvalidReferences.Count); // 999, 888, 777
            Assert.Contains("999", validationResult.InvalidReferences);
            Assert.Contains("888", validationResult.InvalidReferences);
            Assert.Contains("777", validationResult.InvalidReferences);
        }
        
        [Test]
        public void DataConsistency_EntityIds_ShouldBeUnique()
        {
            // Arrange
            var entities = new List<TestEntity>
            {
                new TestEntity("1", "Entity1"),
                new TestEntity("2", "Entity2"),
                new TestEntity("1", "DuplicateEntity"), // Duplicate ID
                new TestEntity("3", "Entity3")
            };
            
            // Act
            var duplicateIds = FindDuplicateEntityIds(entities);
            
            // Assert
            Assert.AreEqual(1, duplicateIds.Count);
            Assert.Contains("1", duplicateIds);
        }
        
        [Test]
        public void DataConsistency_EntityProperties_ShouldValidateTypes()
        {
            // Arrange
            var entity = new TestEntity("Test Entity");
            entity.SetProperty("health", 100);
            entity.SetProperty("name", "Test");
            entity.SetProperty("active", true);
            entity.SetProperty("position", new Vector3(1, 2, 3));
            
            // Act & Assert - Valid type access
            Assert.AreEqual(100, entity.GetProperty<int>("health"));
            Assert.AreEqual("Test", entity.GetProperty<string>("name"));
            Assert.AreEqual(true, entity.GetProperty<bool>("active"));
            Assert.AreEqual(new Vector3(1, 2, 3), entity.GetProperty<Vector3>("position"));
            
            // Act & Assert - Invalid type access should return defaults
            Assert.AreEqual("", entity.GetProperty<string>("health")); // int as string
            Assert.AreEqual(0, entity.GetProperty<int>("name")); // string as int
            Assert.AreEqual(false, entity.GetProperty<bool>("health")); // int as bool
        }
        
        #endregion
        
        #region Helper Methods
        
        /// <summary>
        /// Validate entity references for consistency
        /// </summary>
        private ReferenceValidationResult ValidateEntityReferences(List<TestEntity> entities)
        {
            var result = new ReferenceValidationResult();
            var entityIds = new HashSet<string>();
            
            // Collect all entity IDs
            foreach (var entity in entities)
            {
                entityIds.Add(entity.Id);
            }
            
            result.TotalEntitiesChecked = entities.Count;
            
            // Check references in each entity
            foreach (var entity in entities)
            {
                if (entity.HasProperty("references"))
                {
                    var references = entity.GetProperty<List<string>>("references");
                    if (references != null)
                    {
                        foreach (var refId in references)
                        {
                            if (!entityIds.Contains(refId))
                            {
                                result.InvalidReferences.Add(refId);
                            }
                        }
                    }
                }
            }
            
            result.IsValid = result.InvalidReferences.Count == 0;
            return result;
        }
        
        /// <summary>
        /// Find duplicate entity IDs
        /// </summary>
        private List<string> FindDuplicateEntityIds(List<TestEntity> entities)
        {
            var idCounts = new Dictionary<string, int>();
            var duplicates = new List<string>();
            
            foreach (var entity in entities)
            {
                if (idCounts.ContainsKey(entity.Id))
                {
                    idCounts[entity.Id]++;
                    if (idCounts[entity.Id] == 2) // First time we detect a duplicate
                    {
                        duplicates.Add(entity.Id);
                    }
                }
                else
                {
                    idCounts[entity.Id] = 1;
                }
            }
            
            return duplicates;
        }
        
        #endregion
        
        #region Helper Classes
        
        /// <summary>
        /// Test entity implementation for testing
        /// </summary>
        public class TestEntity : Entity
        {
            public TestEntity() : base() { }
            public TestEntity(string name) : base(name) { }
            public TestEntity(string id, string name) : base(id, name) { }
        }
        
        /// <summary>
        /// Result of reference validation
        /// </summary>
        public class ReferenceValidationResult
        {
            public bool IsValid { get; set; }
            public List<string> InvalidReferences { get; set; } = new List<string>();
            public int TotalEntitiesChecked { get; set; }
        }
        
        #endregion
    }
} 