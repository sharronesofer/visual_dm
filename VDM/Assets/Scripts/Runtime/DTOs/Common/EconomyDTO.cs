using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Economic.Economy
{
    /// <summary>
    /// Base DTO for economy system with common fields
    /// </summary>
    [Serializable]
    public abstract class EconomyBaseDTO : MetadataDTO
    {
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Primary DTO for economy system
    /// </summary>
    [Serializable]
    public class EconomyDTO : EconomyBaseDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public string Status { get; set; } = "active";
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request DTO for creating economy
    /// </summary>
    [Serializable]
    public class CreateEconomyDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request DTO for updating economy
    /// </summary>
    [Serializable]
    public class UpdateEconomyDTO
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public string Status { get; set; }
        public Dictionary<string, object> Properties { get; set; }
    }

    /// <summary>
    /// Response DTO for economy
    /// </summary>
    [Serializable]
    public class EconomyResponseDTO : SuccessResponseDTO
    {
        public EconomyDTO Economy { get; set; } = new EconomyDTO();
    }

    /// <summary>
    /// Response DTO for economy lists
    /// </summary>
    [Serializable]
    public class EconomyListResponseDTO : SuccessResponseDTO
    {
        public List<EconomyDTO> Economies { get; set; } = new List<EconomyDTO>();
        public int Total { get; set; }
        public int Page { get; set; }
        public int Size { get; set; }
        public bool HasNext { get; set; }
        public bool HasPrev { get; set; }
    }

    /// <summary>
    /// Market data DTO for economic information
    /// </summary>
    [Serializable]
    public class MarketDataDTO : EconomyBaseDTO
    {
        public string MarketId { get; set; } = string.Empty;
        public string CommodityId { get; set; } = string.Empty;
        public string CommodityName { get; set; } = string.Empty;
        public decimal CurrentPrice { get; set; }
        public decimal BasePrice { get; set; }
        public int Supply { get; set; }
        public int Demand { get; set; }
        public string PriceTrend { get; set; } = "stable";
        public Dictionary<string, object> MarketConditions { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Transaction DTO for economic transactions
    /// </summary>
    [Serializable]
    public class TransactionDTO : EconomyBaseDTO
    {
        public string TransactionId { get; set; } = string.Empty;
        public string BuyerId { get; set; } = string.Empty;
        public string SellerId { get; set; } = string.Empty;
        public string CommodityId { get; set; } = string.Empty;
        public int Quantity { get; set; }
        public decimal UnitPrice { get; set; }
        public decimal TotalPrice { get; set; }
        public string TransactionType { get; set; } = "trade";
        public string Status { get; set; } = "pending";
        public DateTime TransactionDate { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Commodity future DTO for economic forecasting
    /// </summary>
    [Serializable]
    public class CommodityFutureDTO : EconomyBaseDTO
    {
        public string CommodityId { get; set; } = string.Empty;
        public string CommodityName { get; set; } = string.Empty;
        public decimal PredictedPrice { get; set; }
        public DateTime PredictionDate { get; set; }
        public float Confidence { get; set; }
        public List<string> Factors { get; set; } = new List<string>();
        public Dictionary<string, object> MarketAnalysis { get; set; } = new Dictionary<string, object>();
    }
} 