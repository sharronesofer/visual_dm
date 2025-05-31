using System.Collections.Generic;
using System;


namespace VDM.Infrastructure.Data.Models
{
    /// <summary>
    /// Core interface for all data models in the system.
    /// Provides common functionality for data validation, serialization, and metadata.
    /// </summary>
    public interface IDataModel
    {
        /// <summary>
        /// Unique identifier for this data model instance
        /// </summary>
        string Id { get; }
        
        /// <summary>
        /// Version of the data model format
        /// </summary>
        string Version { get; }
        
        /// <summary>
        /// Timestamp when the data was last updated
        /// </summary>
        DateTime LastUpdated { get; }
        
        /// <summary>
        /// Description of the data model contents
        /// </summary>
        string Description { get; }
        
        /// <summary>
        /// Validate the data model
        /// </summary>
        /// <returns>True if valid, false otherwise</returns>
        bool IsValid();
        
        /// <summary>
        /// Get validation errors if any
        /// </summary>
        /// <returns>List of validation error messages</returns>
        List<string> GetValidationErrors();
        
        /// <summary>
        /// Convert the model to a dictionary for serialization
        /// </summary>
        /// <returns>Dictionary representation of the model</returns>
        Dictionary<string, object> ToDictionary();
        
        /// <summary>
        /// Update the model from a dictionary
        /// </summary>
        /// <param name="data">Dictionary containing model data</param>
        void FromDictionary(Dictionary<string, object> data);
    }
} 