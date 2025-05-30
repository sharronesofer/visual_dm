using System;
using UnityEngine;

namespace VisualDM.DTOs.Core
{
    /// <summary>
    /// Base DTO for all VisualDM data transfer objects
    /// </summary>
    [Serializable]
    public class BaseDTO
    {
        public string Id { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Generic response wrapper
    /// </summary>
    [Serializable]
    public class ResponseDTO<T>
    {
        public bool Success { get; set; } = true;
        public string Message { get; set; } = string.Empty;
        public T Data { get; set; }
        public string[] Errors { get; set; } = new string[0];
    }

    /// <summary>
    /// API response for data operations
    /// </summary>
    [Serializable]
    public class ApiResponseDTO : BaseDTO
    {
        public int StatusCode { get; set; } = 200;
        public string Status { get; set; } = "Success";
    }

    namespace Auth
    {
        /// <summary>
        /// Authentication related DTOs
        /// </summary>
        [Serializable]
        public class AuthTokenDTO
        {
            public string Token { get; set; } = string.Empty;
            public string RefreshToken { get; set; } = string.Empty;
            public DateTime ExpiresAt { get; set; } = DateTime.UtcNow.AddHours(1);
        }

        [Serializable]
        public class LoginRequestDTO
        {
            public string Username { get; set; } = string.Empty;
            public string Password { get; set; } = string.Empty;
        }
    }

    namespace Shared
    {
        /// <summary>
        /// Shared DTOs across the application
        /// </summary>
        [Serializable]
        public class PaginationDTO
        {
            public int Page { get; set; } = 1;
            public int PageSize { get; set; } = 20;
            public int Total { get; set; } = 0;
        }

        [Serializable]
        public class MetadataDTO
        {
            public string Version { get; set; } = "1.0.0";
            public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        }
    }
} 