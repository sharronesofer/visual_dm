using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.Economy.Models
{
    /// <summary>
    /// Market data model representing a regional market with dynamic pricing
    /// </summary>
    [Serializable]
    public class MarketData
    {
        public string id;
        public string name;
        public string regionId;
        public string marketType; // general, specialized, black_market
        public Dictionary<string, float> priceModifiers; // resource_id -> modifier
        public Dictionary<string, SupplyDemandData> supplyDemand; // resource_id -> supply/demand data
        public Dictionary<string, float> tradingVolume; // resource_id -> volume
        public float taxRate;
        public DateTime createdAt;
        public DateTime updatedAt;
        public Dictionary<string, object> metadata;

        public MarketData()
        {
            id = Guid.NewGuid().ToString();
            priceModifiers = new Dictionary<string, float>();
            supplyDemand = new Dictionary<string, SupplyDemandData>();
            tradingVolume = new Dictionary<string, float>();
            metadata = new Dictionary<string, object>();
            taxRate = 0.05f;
            createdAt = DateTime.UtcNow;
            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Supply and demand data for a specific resource
    /// </summary>
    [Serializable]
    public class SupplyDemandData
    {
        public float supply;
        public float demand;
        
        public SupplyDemandData() { }
        
        public SupplyDemandData(float supply, float demand)
        {
            this.supply = supply;
            this.demand = demand;
        }
    }

    /// <summary>
    /// Resource model for economic calculations
    /// </summary>
    [Serializable]
    public class ResourceData
    {
        public string id;
        public string name;
        public string description;
        public float baseValue;
        public string category;
        public bool isTradeGood;
        public float weight;
        public Dictionary<string, object> properties;
        public DateTime createdAt;
        public DateTime updatedAt;

        public ResourceData()
        {
            id = Guid.NewGuid().ToString();
            properties = new Dictionary<string, object>();
            createdAt = DateTime.UtcNow;
            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Trade route data model
    /// </summary>
    [Serializable]
    public class TradeRouteData
    {
        public string id;
        public string name;
        public string originMarketId;
        public string destinationMarketId;
        public List<string> intermediateMarketIds;
        public Dictionary<string, float> transportCosts; // resource_id -> cost
        public float distance;
        public float dangerLevel;
        public bool isActive;
        public DateTime createdAt;
        public DateTime updatedAt;

        public TradeRouteData()
        {
            id = Guid.NewGuid().ToString();
            intermediateMarketIds = new List<string>();
            transportCosts = new Dictionary<string, float>();
            createdAt = DateTime.UtcNow;
            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Economic metric for tracking market performance
    /// </summary>
    [Serializable]
    public class EconomicMetricData
    {
        public string id;
        public string marketId;
        public string metricType; // price_index, inflation_rate, trade_volume, etc.
        public float value;
        public DateTime timestamp;
        public Dictionary<string, object> metadata;

        public EconomicMetricData()
        {
            id = Guid.NewGuid().ToString();
            metadata = new Dictionary<string, object>();
            timestamp = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Transaction record model
    /// </summary>
    [Serializable]
    public class TransactionData
    {
        public string id;
        public string buyerId;
        public string sellerId;
        public string marketId;
        public string resourceId;
        public int quantity;
        public float unitPrice;
        public float totalValue;
        public float taxAmount;
        public DateTime timestamp;
        public string transactionType; // buy, sell, transfer
        public Dictionary<string, object> metadata;

        public TransactionData()
        {
            id = Guid.NewGuid().ToString();
            metadata = new Dictionary<string, object>();
            timestamp = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Currency data model
    /// </summary>
    [Serializable]
    public class CurrencyData
    {
        public string id;
        public string name;
        public string symbol;
        public float exchangeRate; // relative to base currency
        public bool isBaseCurrency;
        public string regionId;
        public DateTime createdAt;
        public DateTime updatedAt;

        public CurrencyData()
        {
            id = Guid.NewGuid().ToString();
            createdAt = DateTime.UtcNow;
            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Market price calculation result
    /// </summary>
    [Serializable]
    public class MarketPriceData
    {
        public string resourceId;
        public string marketId;
        public float currentPrice;
        public float basePrice;
        public float modifier;
        public float supplyFactor;
        public float demandFactor;
        public DateTime calculatedAt;

        public MarketPriceData()
        {
            calculatedAt = DateTime.UtcNow;
        }
    }
} 