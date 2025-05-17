using System;
using System.IO;
using System.Threading.Tasks;
using UnityEngine;
using Visual_DM.Storage;

namespace VisualDM.UI
{
    /// <summary>
    /// Handles post-upload processing: notifications, metadata extraction, thumbnail generation, and storage integration.
    /// </summary>
    public class PostUploadProcessor
    {
        private readonly IStorageProvider _storageProvider;
        public PostUploadProcessor(IStorageProvider storageProvider)
        {
            _storageProvider = storageProvider;
        }

        public class PostUploadResult
        {
            public bool Success;
            public string ErrorMessage;
            public string StoragePath;
            public object Metadata;
            public string ThumbnailPath;
        }

        public async Task<PostUploadResult> ProcessAsync(string filePath, string storagePath)
        {
            try
            {
                // Extract metadata
                object metadata = ExtractMetadata(filePath);
                await _storageProvider.SaveMetadata(storagePath, metadata);

                // Generate thumbnail if image or video
                string ext = Path.GetExtension(filePath).ToLowerInvariant();
                string thumbnailPath = null;
                if (ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".gif")
                {
                    thumbnailPath = await GenerateImageThumbnailAsync(filePath, storagePath);
                }
                // TODO: Add video thumbnail support

                // Store file reference (could be a DB or file index, here just metadata)
                // Custom hooks can be added here

                // Notify success (could be via event, callback, or UI)
                return new PostUploadResult
                {
                    Success = true,
                    StoragePath = storagePath,
                    Metadata = metadata,
                    ThumbnailPath = thumbnailPath
                };
            }
            catch (Exception ex)
            {
                // Notify failure
                return new PostUploadResult { Success = false, ErrorMessage = ex.Message };
            }
        }

        private object ExtractMetadata(string filePath)
        {
            var ext = Path.GetExtension(filePath).ToLowerInvariant();
            if (ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".gif")
            {
                var bytes = File.ReadAllBytes(filePath);
                Texture2D tex = new Texture2D(2, 2);
                tex.LoadImage(bytes);
                return new { Width = tex.width, Height = tex.height, Format = tex.format.ToString() };
            }
            // Add more metadata extraction as needed
            return null;
        }

        private async Task<string> GenerateImageThumbnailAsync(string filePath, string storagePath)
        {
            var bytes = File.ReadAllBytes(filePath);
            Texture2D tex = new Texture2D(2, 2);
            tex.LoadImage(bytes);
            int thumbWidth = 128;
            int thumbHeight = Mathf.RoundToInt((float)tex.height / tex.width * thumbWidth);
            Texture2D thumb = new Texture2D(thumbWidth, thumbHeight);
            Color[] pixels = tex.GetPixels(0, 0, tex.width, tex.height);
            // Simple nearest-neighbor resize (for demo)
            for (int y = 0; y < thumbHeight; y++)
            {
                for (int x = 0; x < thumbWidth; x++)
                {
                    int srcX = Mathf.FloorToInt((float)x / thumbWidth * tex.width);
                    int srcY = Mathf.FloorToInt((float)y / thumbHeight * tex.height);
                    thumb.SetPixel(x, y, tex.GetPixel(srcX, srcY));
                }
            }
            thumb.Apply();
            byte[] thumbBytes = thumb.EncodeToPNG();
            string thumbPath = storagePath + ".thumb.png";
            await _storageProvider.Save(thumbPath, thumbBytes);
            return thumbPath;
        }
    }
} 