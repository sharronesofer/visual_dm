using System;

namespace VisualDM.Storage
{
    /// <summary>
    /// Interface for objects that can be persisted by the PersistenceManager.
    /// </summary>
    public interface IStorable
    {
        /// <summary>
        /// Returns a unique identifier for the storable object (used as a key in storage).
        /// </summary>
        string GetStorageKey();

        /// <summary>
        /// Serializes the object to a byte array (JSON or binary).
        /// </summary>
        byte[] Serialize();

        /// <summary>
        /// Populates the object from a byte array (JSON or binary).
        /// </summary>
        void Deserialize(byte[] data);

        /// <summary>
        /// Returns the version of the data schema for migration support.
        /// </summary>
        int DataVersion { get; }
    }
} 