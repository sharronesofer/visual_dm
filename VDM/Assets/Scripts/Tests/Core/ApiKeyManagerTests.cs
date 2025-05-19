using NUnit.Framework;
using VDM.Core;

namespace VDM.Tests.Core
{
    [TestFixture]
    public class ApiKeyManagerTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var manager = new ApiKeyManager();
            Assert.IsNotNull(manager);
        }

        [Test]
        public void SetAndGetApiKey_Works()
        {
            var manager = new ApiKeyManager();
            manager.SetApiKey("service", "key123");
            Assert.AreEqual("key123", manager.GetApiKey("service"));
        }

        [Test]
        public void GetApiKey_UnknownService_ReturnsNull()
        {
            var manager = new ApiKeyManager();
            Assert.IsNull(manager.GetApiKey("unknown"));
        }

        [Test]
        public void RemoveApiKey_RemovesKey()
        {
            var manager = new ApiKeyManager();
            manager.SetApiKey("service", "key123");
            manager.RemoveApiKey("service");
            Assert.IsNull(manager.GetApiKey("service"));
        }
    }
} 