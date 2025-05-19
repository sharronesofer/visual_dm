using NUnit.Framework;
using VisualDM.Storage;
using System.IO;
using System.Text;
using System.Threading.Tasks;

namespace VisualDM.Tests
{
    [TestFixture]
    public class StorageTests
    {
        private string tempDir;
        private FileSystemStorageProvider provider;

        [SetUp]
        public void Setup()
        {
            tempDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
            Directory.CreateDirectory(tempDir);
            provider = new FileSystemStorageProvider(tempDir);
        }

        [TearDown]
        public void Teardown()
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, true);
        }

        [Test]
        public async Task SaveAndLoad_WritesAndReadsFile()
        {
            string path = "testfile.txt";
            byte[] data = Encoding.UTF8.GetBytes("Hello World");
            await provider.Save(path, data);
            var loaded = await provider.Load(path);
            Assert.AreEqual("Hello World", Encoding.UTF8.GetString(loaded));
        }

        [Test]
        public async Task ExistsAndDelete_WorksCorrectly()
        {
            string path = "deletefile.txt";
            await provider.Save(path, Encoding.UTF8.GetBytes("data"));
            Assert.IsTrue(await provider.Exists(path));
            await provider.Delete(path);
            Assert.IsFalse(await provider.Exists(path));
        }

        [Test]
        public void StorageFactory_ReturnsFileSystemProvider()
        {
            var p = StorageFactory.GetProvider("filesystem", tempDir);
            Assert.IsInstanceOf<FileSystemStorageProvider>(p);
        }

        private class MockStorable : IStorable
        {
            public string Key { get; set; }
            public string Value { get; set; }
            public int DataVersion { get; set; } = 1;

            public string GetStorageKey() => Key;
            public byte[] Serialize() => System.Text.Encoding.UTF8.GetBytes(Value);
            public void Deserialize(byte[] data) => Value = System.Text.Encoding.UTF8.GetString(data);
        }

        [Test]
        public async Task PersistenceManager_SaveAndLoad_WorksCorrectly()
        {
            var config = new PersistenceConfig
            {
                StorageProviderType = "filesystem",
                StorageProviderConfig = tempDir,
                EnableEncryption = false
            };
            PersistenceManager.Instance.Initialize(config);

            var storable = new MockStorable { Key = "testkey", Value = "TestValue", DataVersion = 2 };
            await PersistenceManager.Instance.SaveAsync(storable);

            var loaded = new MockStorable { Key = "testkey", DataVersion = 2 };
            var result = await PersistenceManager.Instance.LoadAsync(loaded);
            Assert.IsTrue(result);
            Assert.AreEqual(storable.Value, loaded.Value);
        }

        [Test]
        public async Task PersistenceManager_Delete_WorksCorrectly()
        {
            var config = new PersistenceConfig
            {
                StorageProviderType = "filesystem",
                StorageProviderConfig = tempDir,
                EnableEncryption = false
            };
            PersistenceManager.Instance.Initialize(config);

            var storable = new MockStorable { Key = "deletekey", Value = "DeleteMe", DataVersion = 1 };
            await PersistenceManager.Instance.SaveAsync(storable);
            var deleted = await PersistenceManager.Instance.DeleteAsync(storable);
            Assert.IsTrue(deleted);
            var loaded = new MockStorable { Key = "deletekey", DataVersion = 1 };
            var result = await PersistenceManager.Instance.LoadAsync(loaded);
            Assert.IsFalse(result);
        }

        private class TestStorable : IStorable
        {
            public string Key { get; set; }
            public string Value { get; set; }
            public int DataVersion { get; set; } = 1;
            public string GetStorageKey() => Key;
            public byte[] Serialize() => SerializationHelper.ToJsonBytes(this);
            public void Deserialize(byte[] data)
            {
                var obj = SerializationHelper.FromJsonBytes<TestStorable>(data);
                Key = obj.Key;
                Value = obj.Value;
                DataVersion = obj.DataVersion;
            }
        }

        [Test]
        public void SerializationHelper_Json_SerializeDeserialize_Works()
        {
            var obj = new TestStorable { Key = "jsonkey", Value = "jsonvalue", DataVersion = 3 };
            var bytes = SerializationHelper.ToJsonBytes(obj);
            var deserialized = SerializationHelper.FromJsonBytes<TestStorable>(bytes);
            Assert.AreEqual(obj.Key, deserialized.Key);
            Assert.AreEqual(obj.Value, deserialized.Value);
            Assert.AreEqual(obj.DataVersion, deserialized.DataVersion);
        }

        [Test]
        public void SerializationHelper_Binary_SerializeDeserialize_Works()
        {
            var obj = new TestStorable { Key = "binkey", Value = "binvalue", DataVersion = 2 };
            var bytes = SerializationHelper.ToBinary(obj);
            var deserialized = SerializationHelper.FromBinary<TestStorable>(bytes);
            Assert.AreEqual(obj.Key, deserialized.Key);
            Assert.AreEqual(obj.Value, deserialized.Value);
            Assert.AreEqual(obj.DataVersion, deserialized.DataVersion);
        }

        [Test]
        public void SerializationHelper_ValidateVersioned_Works()
        {
            var obj = new TestStorable { DataVersion = 5 };
            Assert.IsTrue(SerializationHelper.ValidateVersioned(obj, 5));
            Assert.IsFalse(SerializationHelper.ValidateVersioned(obj, 4));
        }

        [Test]
        public void SerializationHelper_Migrate_Works()
        {
            var oldObj = new TestStorable { Key = "migrate", Value = "old", DataVersion = 1 };
            TestStorable MigrationFunc(TestStorable o, int from, int to)
            {
                return new TestStorable { Key = o.Key, Value = o.Value + "_migrated", DataVersion = to };
            }
            var migrated = SerializationHelper.Migrate(oldObj, 1, 2, MigrationFunc);
            Assert.AreEqual("migrate", migrated.Key);
            Assert.AreEqual("old_migrated", migrated.Value);
            Assert.AreEqual(2, migrated.DataVersion);
        }
    }
} 