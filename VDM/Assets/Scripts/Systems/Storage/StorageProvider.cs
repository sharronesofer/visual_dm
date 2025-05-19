using System.Threading.Tasks;

namespace VisualDM.Storage
{
    /// <summary>
    /// Interface for a flexible storage backend supporting multiple providers.
    /// See README.md in this directory for usage and implementation details.
    /// </summary>
    public interface IStorageProvider
    {
        /// <summary>
        /// Saves data to the specified path, with optional versioning.
        /// </summary>
        /// <param name="path">The storage path (relative or absolute, normalized).</param>
        /// <param name="data">The data to save.</param>
        /// <param name="version">Optional version number for versioned saves.</param>
        /// <returns>The normalized path where the data was saved.</returns>
        Task<string> Save(string path, byte[] data, int version = 0);

        /// <summary>
        /// Loads data from the specified path, with optional versioning.
        /// </summary>
        /// <param name="path">The storage path.</param>
        /// <param name="version">Optional version number for versioned loads.</param>
        /// <returns>The loaded data as a byte array.</returns>
        Task<byte[]> Load(string path, int version = 0);

        /// <summary>
        /// Deletes the file at the specified path.
        /// </summary>
        /// <param name="path">The storage path.</param>
        /// <returns>True if the file was deleted, false otherwise.</returns>
        Task<bool> Delete(string path);

        /// <summary>
        /// Checks if a file exists at the specified path.
        /// </summary>
        /// <param name="path">The storage path.</param>
        /// <returns>True if the file exists, false otherwise.</returns>
        Task<bool> Exists(string path);

        /// <summary>
        /// Lists all files in the specified directory.
        /// </summary>
        /// <param name="directory">The directory path.</param>
        /// <returns>Array of file paths.</returns>
        Task<string[]> List(string directory);

        /// <summary>
        /// Saves data from a stream to the specified path (for large files).
        /// </summary>
        /// <param name="path">The storage path.</param>
        /// <param name="inputStream">The input stream to save.</param>
        /// <returns>The normalized path where the data was saved.</returns>
        Task<string> SaveStream(string path, System.IO.Stream inputStream);

        /// <summary>
        /// Loads data as a stream from the specified path (for large files).
        /// <b>Caller MUST dispose the returned stream to prevent file handle/resource leaks.</b>
        /// Failure to do so will result in resource leaks and potential instability.
        /// </summary>
        /// <param name="path">The storage path.</param>
        /// <returns>A stream for reading the file data. <b>Caller must dispose.</b></returns>
        Task<System.IO.Stream> LoadStream(string path);
    }
}