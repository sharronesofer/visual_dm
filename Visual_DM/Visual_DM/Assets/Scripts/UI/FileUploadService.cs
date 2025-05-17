using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Visual_DM.Storage;

namespace VisualDM.UI
{
    /// <summary>
    /// Service for uploading files with chunking, progress, cancellation, and retry.
    /// </summary>
    public class FileUploadService
    {
        private readonly IStorageProvider _storageProvider;
        private const int ChunkSize = 2 * 1024 * 1024; // 2 MB
        public FileUploadService(IStorageProvider storageProvider)
        {
            _storageProvider = storageProvider;
        }

        public class UploadProgress
        {
            public long BytesSent;
            public long TotalBytes;
            public float Progress => TotalBytes > 0 ? (float)BytesSent / TotalBytes : 0f;
            public float SpeedBytesPerSec;
            public TimeSpan? EstimatedRemaining;
        }

        public class UploadResult
        {
            public bool Success;
            public string ErrorMessage;
            public string StoragePath;
        }

        /// <summary>
        /// Uploads a file in chunks with progress and cancellation support.
        /// </summary>
        public async Task<UploadResult> UploadFileAsync(string filePath, string storagePath, Action<UploadProgress> onProgress = null, CancellationToken cancellationToken = default, int maxRetries = 3)
        {
            if (!File.Exists(filePath))
                return new UploadResult { Success = false, ErrorMessage = "File does not exist." };

            var fileInfo = new FileInfo(filePath);
            long totalBytes = fileInfo.Length;
            long bytesSent = 0;
            int retries = 0;
            var progress = new UploadProgress { BytesSent = 0, TotalBytes = totalBytes };
            DateTime startTime = DateTime.UtcNow;
            try
            {
                using (var fs = new FileStream(filePath, FileMode.Open, FileAccess.Read))
                {
                    // For small files, upload in one go
                    if (totalBytes <= ChunkSize)
                    {
                        var data = new byte[totalBytes];
                        await fs.ReadAsync(data, 0, (int)totalBytes, cancellationToken);
                        await _storageProvider.Save(storagePath, data);
                        progress.BytesSent = totalBytes;
                        onProgress?.Invoke(progress);
                        return new UploadResult { Success = true, StoragePath = storagePath };
                    }

                    // For large files, upload in chunks
                    int chunkIndex = 0;
                    while (bytesSent < totalBytes)
                    {
                        int chunkSize = (int)Math.Min(ChunkSize, totalBytes - bytesSent);
                        var buffer = new byte[chunkSize];
                        int read = await fs.ReadAsync(buffer, 0, chunkSize, cancellationToken);
                        if (read == 0) break;
                        bool chunkUploaded = false;
                        retries = 0;
                        while (!chunkUploaded && retries < maxRetries)
                        {
                            try
                            {
                                // For chunked upload, append chunk index to path
                                string chunkPath = $"{storagePath}.chunk{chunkIndex}";
                                await _storageProvider.Save(chunkPath, buffer);
                                chunkUploaded = true;
                            }
                            catch
                            {
                                retries++;
                                if (retries >= maxRetries)
                                    throw;
                                await Task.Delay(500 * retries, cancellationToken); // Exponential backoff
                            }
                        }
                        bytesSent += read;
                        chunkIndex++;
                        progress.BytesSent = bytesSent;
                        var elapsed = DateTime.UtcNow - startTime;
                        progress.SpeedBytesPerSec = bytesSent / (float)Math.Max(1, elapsed.TotalSeconds);
                        if (progress.SpeedBytesPerSec > 0)
                        {
                            var remaining = (totalBytes - bytesSent) / progress.SpeedBytesPerSec;
                            progress.EstimatedRemaining = TimeSpan.FromSeconds(remaining);
                        }
                        onProgress?.Invoke(progress);
                        cancellationToken.ThrowIfCancellationRequested();
                    }
                    // After all chunks uploaded, merge them (implementation depends on storage backend)
                    // For local file system, merge chunks into final file
                    await MergeChunksAsync(storagePath, chunkIndex);
                    return new UploadResult { Success = true, StoragePath = storagePath };
                }
            }
            catch (OperationCanceledException)
            {
                return new UploadResult { Success = false, ErrorMessage = "Upload cancelled." };
            }
            catch (Exception ex)
            {
                return new UploadResult { Success = false, ErrorMessage = ex.Message };
            }
        }

        private async Task MergeChunksAsync(string storagePath, int chunkCount)
        {
            // Only for local file system provider
            var dir = Path.GetDirectoryName(storagePath);
            var tempPath = storagePath + ".tmp";
            using (var outStream = new FileStream(tempPath, FileMode.Create, FileAccess.Write))
            {
                for (int i = 0; i < chunkCount; i++)
                {
                    string chunkPath = $"{storagePath}.chunk{i}";
                    var chunkData = await _storageProvider.Load(chunkPath);
                    await outStream.WriteAsync(chunkData, 0, chunkData.Length);
                    await _storageProvider.Delete(chunkPath);
                }
            }
            // Move temp file to final destination
            if (File.Exists(storagePath))
                File.Delete(storagePath);
            File.Move(tempPath, storagePath);
        }
    }
} 