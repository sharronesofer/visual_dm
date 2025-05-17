using NUnit.Framework;
using Visual_DM.Storage;
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
    }
} 