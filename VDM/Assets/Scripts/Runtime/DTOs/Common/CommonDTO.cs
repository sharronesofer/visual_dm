using System;
using System.Collections.Generic;

namespace VDM.DTOs.Core.Shared
{
    /// <summary>
    /// Standard API error response
    /// </summary>
    [Serializable]
    public class ErrorDTO
    {
        public string Detail { get; set; } = string.Empty;
        public string Code { get; set; }
    }

    /// <summary>
    /// Standard API success response
    /// </summary>
    [Serializable]
    public class SuccessResponseDTO
    {
        public string Status { get; set; } = "success";
        public string Message { get; set; }
    }

    /// <summary>
    /// Validation error details
    /// </summary>
    [Serializable]
    public class ValidationErrorDetailDTO
    {
        public List<string> Location { get; set; } = new List<string>();
        public string Message { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
    }

    /// <summary>
    /// Validation error response
    /// </summary>
    [Serializable]
    public class ValidationErrorDTO
    {
        public List<ValidationErrorDetailDTO> Detail { get; set; } = new List<ValidationErrorDetailDTO>();
    }

    /// <summary>
    /// Generic coordinate structure
    /// </summary>
    [Serializable]
    public class CoordinateDTO
    {
        public float X { get; set; }
        public float Y { get; set; }
        public float? Z { get; set; }
    }

    /// <summary>
    /// Hexagonal coordinate system
    /// </summary>
    [Serializable]
    public class HexCoordinateDTO
    {
        public int Q { get; set; }
        public int R { get; set; }
        public int S { get; set; }
    }

    /// <summary>
    /// Generic properties container
    /// </summary>
    [Serializable]
    public class PropertiesDTO
    {
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Generic metadata container
    /// </summary>
    [Serializable]
    public class MetadataDTO
    {
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }
        public string CreatedBy { get; set; }
        public int? Version { get; set; }
    }

    /// <summary>
    /// Range/boundary definition
    /// </summary>
    [Serializable]
    public class RangeDTO
    {
        public float Min { get; set; }
        public float Max { get; set; }
    }

    /// <summary>
    /// Generic ID reference
    /// </summary>
    [Serializable]
    public class IdReferenceDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Type { get; set; }
    }

    /// <summary>
    /// Pagination request parameters
    /// </summary>
    [Serializable]
    public class PaginationRequestDTO
    {
        public int Page { get; set; } = 1;
        public int PageSize { get; set; } = 20;
        public string SortBy { get; set; }
        public string SortOrder { get; set; } = "asc";
    }

    /// <summary>
    /// Pagination response metadata
    /// </summary>
    [Serializable]
    public class PaginationResponseDTO
    {
        public int Page { get; set; }
        public int PageSize { get; set; }
        public int TotalItems { get; set; }
        public int TotalPages { get; set; }
        public bool HasNext { get; set; }
        public bool HasPrevious { get; set; }
    }

    /// <summary>
    /// Generic paginated response wrapper
    /// </summary>
    [Serializable]
    public class PaginatedResponseDTO<T>
    {
        public List<T> Items { get; set; } = new List<T>();
        public PaginationResponseDTO Pagination { get; set; } = new PaginationResponseDTO();
    }
} 