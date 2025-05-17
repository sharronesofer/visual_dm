using System;

namespace Visual_DM.Storage
{
    /// <summary>
    /// Base exception for storage-related errors.
    /// </summary>
    public class StorageException : Exception
    {
        public StorageException(string message) : base(message) { }
        public StorageException(string message, Exception inner) : base(message, inner) { }
    }

    /// <summary>
    /// Exception for not found errors in storage.
    /// </summary>
    public class StorageNotFoundException : StorageException
    {
        public StorageNotFoundException(string message) : base(message) { }
    }

    /// <summary>
    /// Exception for unauthorized access in storage.
    /// </summary>
    public class StorageUnauthorizedException : StorageException
    {
        public StorageUnauthorizedException(string message) : base(message) { }
    }
} 