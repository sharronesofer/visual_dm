using NUnit.Framework;
using VisualDM.UI;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

namespace VisualDM.Tests
{
    [TestFixture]
    public class UITests
    {
        [Test]
        public void FileValidationService_ValidatesFileTypeAndSize()
        {
            var service = new FileValidationService();
            var valid = service.ValidateFile("test.png", "image/png", 1024 * 100, out string error);
            Assert.IsTrue(valid);
            var invalid = service.ValidateFile("test.exe", "application/octet-stream", 1024 * 100, out error);
            Assert.IsFalse(invalid);
        }

        [Test]
        public async Task FileUploadService_UploadsFileSuccessfully()
        {
            var service = new FileUploadService();
            byte[] data = Encoding.UTF8.GetBytes("test data");
            string tempPath = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
            bool result = await service.UploadFileAsync(tempPath, data, (progress) => { });
            Assert.IsTrue(result);
            if (File.Exists(tempPath)) File.Delete(tempPath);
        }

        [Test]
        public void ItemManagementPanel_InitializesWithoutError()
        {
            var go = new GameObject("ItemPanel");
            var panel = go.AddComponent<ItemManagementPanel>();
            Assert.DoesNotThrow(() => panel.Initialize());
            Object.DestroyImmediate(go);
        }
    }
} 