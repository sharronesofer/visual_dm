using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Infrastructure.Data.Models
{
    /// <summary>
    /// Base implementation for all data models in the system.
    /// Provides common functionality for validation, serialization, and metadata management.
    /// </summary>
    [Serializable]
    public abstract class BaseDataModel : IDataModel
    {
        [SerializeField] protected string _id;
        [SerializeField] protected string _version;
        [SerializeField] protected DateTime _lastUpdated;
        [SerializeField] protected string _description;
        [SerializeField] protected Dictionary<string, object> _data;

        /// <summary>
        /// Unique identifier for this data model instance
        /// </summary>
        public string Id => _id;

        /// <summary>
        /// Version of the data model format
        /// </summary>
        public string Version => _version;

        /// <summary>
        /// Timestamp when the data was last updated
        /// </summary>
        public DateTime LastUpdated => _lastUpdated;

        /// <summary>
        /// Description of the data model contents
        /// </summary>
        public string Description => _description;

        /// <summary>
        /// Raw data dictionary
        /// </summary>
        protected Dictionary<string, object> Data => _data ?? (_data = new Dictionary<string, object>());

        /// <summary>
        /// Initialize base data model
        /// </summary>
        /// <param name="id">Unique identifier</param>
        /// <param name="version">Data model version</param>
        /// <param name="description">Description of the data</param>
        protected BaseDataModel(string id = null, string version = "1.0.0", string description = "")
        {
            _id = id ?? Guid.NewGuid().ToString();
            _version = version;
            _description = description;
            _lastUpdated = DateTime.UtcNow;
            _data = new Dictionary<string, object>();
        }

        /// <summary>
        /// Constructor for deserialization
        /// </summary>
        protected BaseDataModel()
        {
            // For Unity serialization
        }

        /// <summary>
        /// Validate the data model
        /// </summary>
        /// <returns>True if valid, false otherwise</returns>
        public virtual bool IsValid()
        {
            var errors = GetValidationErrors();
            return errors.Count == 0;
        }

        /// <summary>
        /// Get validation errors if any
        /// </summary>
        /// <returns>List of validation error messages</returns>
        public virtual List<string> GetValidationErrors()
        {
            var errors = new List<string>();

            if (string.IsNullOrEmpty(_id))
            {
                errors.Add("Id cannot be null or empty");
            }

            if (string.IsNullOrEmpty(_version))
            {
                errors.Add("Version cannot be null or empty");
            }

            return errors;
        }

        /// <summary>
        /// Convert the model to a dictionary for serialization
        /// </summary>
        /// <returns>Dictionary representation of the model</returns>
        public virtual Dictionary<string, object> ToDictionary()
        {
            var result = new Dictionary<string, object>
            {
                ["metadata"] = new Dictionary<string, object>
                {
                    ["id"] = _id,
                    ["version"] = _version,
                    ["last_updated"] = _lastUpdated.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                    ["description"] = _description
                },
                ["data"] = new Dictionary<string, object>(Data)
            };

            return result;
        }

        /// <summary>
        /// Update the model from a dictionary
        /// </summary>
        /// <param name="data">Dictionary containing model data</param>
        public virtual void FromDictionary(Dictionary<string, object> data)
        {
            if (data.TryGetValue("metadata", out var metadataObj) && metadataObj is Dictionary<string, object> metadata)
            {
                if (metadata.TryGetValue("id", out var id))
                    _id = id?.ToString();

                if (metadata.TryGetValue("version", out var version))
                    _version = version?.ToString();

                if (metadata.TryGetValue("description", out var description))
                    _description = description?.ToString();

                if (metadata.TryGetValue("last_updated", out var lastUpdated))
                {
                    if (DateTime.TryParse(lastUpdated?.ToString(), out var parsedDate))
                        _lastUpdated = parsedDate;
                }
            }

            if (data.TryGetValue("data", out var dataObj) && dataObj is Dictionary<string, object> dataDict)
            {
                _data = new Dictionary<string, object>(dataDict);
            }
        }

        /// <summary>
        /// Convert to JSON string
        /// </summary>
        /// <returns>JSON representation</returns>
        public string ToJson()
        {
            return JsonConvert.SerializeObject(ToDictionary(), Formatting.Indented);
        }

        /// <summary>
        /// Update metadata
        /// </summary>
        /// <param name="version">New version</param>
        /// <param name="description">New description</param>
        public void UpdateMetadata(string version = null, string description = null)
        {
            if (!string.IsNullOrEmpty(version))
                _version = version;

            if (!string.IsNullOrEmpty(description))
                _description = description;

            _lastUpdated = DateTime.UtcNow;
        }

        public override string ToString()
        {
            return $"[{GetType().Name}] {_id} v{_version} - {_description}";
        }
    }
} 