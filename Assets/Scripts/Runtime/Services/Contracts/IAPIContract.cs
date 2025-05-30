using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace VDM.Runtime.Services.Contracts
{
    /// <summary>
    /// Base interface for all API service contracts.
    /// Defines common patterns for API operations and error handling.
    /// </summary>
    public interface IAPIContract
    {
        /// <summary>
        /// Service name for identification and logging
        /// </summary>
        string ServiceName { get; }
        
        /// <summary>
        /// API version this contract supports
        /// </summary>
        string ApiVersion { get; }
        
        /// <summary>
        /// Base URL for this API service
        /// </summary>
        string BaseUrl { get; set; }
        
        /// <summary>
        /// Whether the service is currently available
        /// </summary>
        bool IsServiceAvailable { get; }
        
        /// <summary>
        /// Test connectivity to the API service
        /// </summary>
        /// <returns>True if service is reachable and responding</returns>
        Task<bool> TestConnectionAsync();
        
        /// <summary>
        /// Get health status of the API service
        /// </summary>
        /// <returns>Health status information</returns>
        Task<ServiceHealthResponse> GetHealthStatusAsync();
        
        /// <summary>
        /// Initialize the API contract with configuration
        /// </summary>
        /// <param name="config">Service configuration</param>
        Task InitializeAsync(APIServiceConfig config);
        
        /// <summary>
        /// Clean up resources when service is no longer needed
        /// </summary>
        Task DisposeAsync();
    }
    
    /// <summary>
    /// Configuration for API services
    /// </summary>
    [Serializable]
    public class APIServiceConfig
    {
        public string BaseUrl { get; set; } = "";
        public string ApiKey { get; set; } = "";
        public int TimeoutSeconds { get; set; } = 30;
        public int RetryAttempts { get; set; } = 3;
        public bool EnableLogging { get; set; } = true;
        public bool UseMockData { get; set; } = false;
        public Dictionary<string, string> Headers { get; set; } = new Dictionary<string, string>();
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Health status response for API services
    /// </summary>
    [Serializable]
    public class ServiceHealthResponse
    {
        public bool IsHealthy { get; set; }
        public string Status { get; set; } = "";
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public long ResponseTimeMs { get; set; }
        public string Version { get; set; } = "";
        public Dictionary<string, object> Details { get; set; } = new Dictionary<string, object>();
        public List<string> Issues { get; set; } = new List<string>();
    }
    
    /// <summary>
    /// Standard API response wrapper
    /// </summary>
    /// <typeparam name="T">Response data type</typeparam>
    [Serializable]
    public class APIResponse<T>
    {
        public bool IsSuccess { get; set; }
        public T Data { get; set; }
        public string Error { get; set; } = "";
        public string ErrorCode { get; set; } = "";
        public List<string> ValidationErrors { get; set; } = new List<string>();
        public APIResponseMetadata Metadata { get; set; } = new APIResponseMetadata();
    }
    
    /// <summary>
    /// Metadata for API responses
    /// </summary>
    [Serializable]
    public class APIResponseMetadata
    {
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public long ResponseTimeMs { get; set; }
        public string RequestId { get; set; } = "";
        public string ApiVersion { get; set; } = "";
        public Dictionary<string, object> Headers { get; set; } = new Dictionary<string, object>();
        public PaginationInfo Pagination { get; set; }
    }
    
    /// <summary>
    /// Pagination information for list responses
    /// </summary>
    [Serializable]
    public class PaginationInfo
    {
        public int Page { get; set; } = 1;
        public int PageSize { get; set; } = 10;
        public int TotalItems { get; set; }
        public int TotalPages { get; set; }
        public bool HasNextPage { get; set; }
        public bool HasPreviousPage { get; set; }
    }
    
    /// <summary>
    /// Standard query parameters for API requests
    /// </summary>
    [Serializable]
    public class APIQueryParams
    {
        public int Page { get; set; } = 1;
        public int PageSize { get; set; } = 10;
        public string SortBy { get; set; } = "";
        public string SortOrder { get; set; } = "asc"; // asc or desc
        public string Search { get; set; } = "";
        public Dictionary<string, string> Filters { get; set; } = new Dictionary<string, string>();
        public List<string> IncludeFields { get; set; } = new List<string>();
        public List<string> ExcludeFields { get; set; } = new List<string>();
    }
} 