using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using VDM.DTOs.Common;
using VDM.Infrastructure.Data.Models;


namespace VDM.Infrastructure.Data.Services
{
    /// <summary>
    /// Interface for data service operations.
    /// Provides CRUD operations and data management functionality.
    /// </summary>
    public interface IDataService<T> where T : class, IDataModel, new()
    {
        /// <summary>
        /// Get a data model by ID
        /// </summary>
        /// <param name="id">Unique identifier</param>
        /// <returns>Data model or null if not found</returns>
        Task<T> GetByIdAsync(string id);

        /// <summary>
        /// Get all data models
        /// </summary>
        /// <returns>List of all data models</returns>
        Task<List<T>> GetAllAsync();

        /// <summary>
        /// Create a new data model
        /// </summary>
        /// <param name="model">Data model to create</param>
        /// <returns>Created data model</returns>
        Task<T> CreateAsync(T model);

        /// <summary>
        /// Update an existing data model
        /// </summary>
        /// <param name="model">Data model to update</param>
        /// <returns>Updated data model</returns>
        Task<T> UpdateAsync(T model);

        /// <summary>
        /// Delete a data model by ID
        /// </summary>
        /// <param name="id">Unique identifier</param>
        /// <returns>True if deleted, false if not found</returns>
        Task<bool> DeleteAsync(string id);

        /// <summary>
        /// Check if a data model exists
        /// </summary>
        /// <param name="id">Unique identifier</param>
        /// <returns>True if exists, false otherwise</returns>
        Task<bool> ExistsAsync(string id);

        /// <summary>
        /// Validate a data model
        /// </summary>
        /// <param name="model">Data model to validate</param>
        /// <returns>True if valid, false otherwise</returns>
        bool ValidateModel(T model);

        /// <summary>
        /// Get validation errors for a data model
        /// </summary>
        /// <param name="model">Data model to validate</param>
        /// <returns>List of validation errors</returns>
        List<string> GetValidationErrors(T model);

        /// <summary>
        /// Save data to persistent storage
        /// </summary>
        /// <returns>True if successful, false otherwise</returns>
        Task<bool> SaveAsync();

        /// <summary>
        /// Load data from persistent storage
        /// </summary>
        /// <returns>True if successful, false otherwise</returns>
        Task<bool> LoadAsync();

        /// <summary>
        /// Clear all data
        /// </summary>
        void Clear();

        /// <summary>
        /// Get the count of data models
        /// </summary>
        /// <returns>Number of data models</returns>
        int Count { get; }
    }
} 