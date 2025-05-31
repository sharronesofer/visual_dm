using Newtonsoft.Json;
using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.Systems.Economy.Models;


namespace VDM.Systems.Economy.Services
{
    /// <summary>
    /// HTTP service for Economy system API communication
    /// </summary>
    public class EconomyHttpService : BaseHttpService
    {
        private const string ECONOMY_ENDPOINT = "/api/v1/economy";
        private const string MARKETS_ENDPOINT = "/api/v1/economy/markets";
        private const string RESOURCES_ENDPOINT = "/api/v1/economy/resources";
        private const string TRANSACTIONS_ENDPOINT = "/api/v1/economy/transactions";
        private const string TRADE_ROUTES_ENDPOINT = "/api/v1/economy/trade-routes";
        private const string CURRENCIES_ENDPOINT = "/api/v1/economy/currencies";

        public EconomyHttpService() : base() { }

        #region Market Operations

        /// <summary>
        /// Get all markets
        /// </summary>
        public async Task<List<MarketData>> GetMarketsAsync()
        {
            try
            {
                string response = await GetAsync(MARKETS_ENDPOINT);
                return JsonConvert.DeserializeObject<List<MarketData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting markets: {ex.Message}");
                return new List<MarketData>();
            }
        }

        /// <summary>
        /// Get market by ID
        /// </summary>
        public async Task<MarketData> GetMarketAsync(string marketId)
        {
            try
            {
                string response = await GetAsync($"{MARKETS_ENDPOINT}/{marketId}");
                return JsonConvert.DeserializeObject<MarketData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting market {marketId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get markets by region
        /// </summary>
        public async Task<List<MarketData>> GetMarketsByRegionAsync(string regionId)
        {
            try
            {
                string response = await GetAsync($"{MARKETS_ENDPOINT}?region_id={regionId}");
                return JsonConvert.DeserializeObject<List<MarketData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting markets for region {regionId}: {ex.Message}");
                return new List<MarketData>();
            }
        }

        /// <summary>
        /// Create a new market
        /// </summary>
        public async Task<MarketData> CreateMarketAsync(MarketData marketData)
        {
            try
            {
                string json = JsonConvert.SerializeObject(marketData);
                string response = await PostAsync(MARKETS_ENDPOINT, json);
                return JsonConvert.DeserializeObject<MarketData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating market: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update market
        /// </summary>
        public async Task<MarketData> UpdateMarketAsync(string marketId, MarketData marketData)
        {
            try
            {
                string json = JsonConvert.SerializeObject(marketData);
                string response = await PutAsync($"{MARKETS_ENDPOINT}/{marketId}", json);
                return JsonConvert.DeserializeObject<MarketData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error updating market {marketId}: {ex.Message}");
                return null;
            }
        }

        #endregion

        #region Resource Operations

        /// <summary>
        /// Get all resources
        /// </summary>
        public async Task<List<ResourceData>> GetResourcesAsync()
        {
            try
            {
                string response = await GetAsync(RESOURCES_ENDPOINT);
                return JsonConvert.DeserializeObject<List<ResourceData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting resources: {ex.Message}");
                return new List<ResourceData>();
            }
        }

        /// <summary>
        /// Get resource by ID
        /// </summary>
        public async Task<ResourceData> GetResourceAsync(string resourceId)
        {
            try
            {
                string response = await GetAsync($"{RESOURCES_ENDPOINT}/{resourceId}");
                return JsonConvert.DeserializeObject<ResourceData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting resource {resourceId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get current market price for a resource
        /// </summary>
        public async Task<MarketPriceData> GetMarketPriceAsync(string marketId, string resourceId)
        {
            try
            {
                string response = await GetAsync($"{MARKETS_ENDPOINT}/{marketId}/prices/{resourceId}");
                return JsonConvert.DeserializeObject<MarketPriceData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting price for resource {resourceId} in market {marketId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get all prices for a market
        /// </summary>
        public async Task<List<MarketPriceData>> GetMarketPricesAsync(string marketId)
        {
            try
            {
                string response = await GetAsync($"{MARKETS_ENDPOINT}/{marketId}/prices");
                return JsonConvert.DeserializeObject<List<MarketPriceData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting prices for market {marketId}: {ex.Message}");
                return new List<MarketPriceData>();
            }
        }

        #endregion

        #region Transaction Operations

        /// <summary>
        /// Execute a buy transaction
        /// </summary>
        public async Task<TransactionData> BuyResourceAsync(string marketId, string buyerId, string resourceId, int quantity)
        {
            try
            {
                var request = new
                {
                    market_id = marketId,
                    buyer_id = buyerId,
                    resource_id = resourceId,
                    quantity = quantity,
                    transaction_type = "buy"
                };

                string json = JsonConvert.SerializeObject(request);
                string response = await PostAsync($"{TRANSACTIONS_ENDPOINT}/buy", json);
                return JsonConvert.DeserializeObject<TransactionData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error executing buy transaction: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Execute a sell transaction
        /// </summary>
        public async Task<TransactionData> SellResourceAsync(string marketId, string sellerId, string resourceId, int quantity)
        {
            try
            {
                var request = new
                {
                    market_id = marketId,
                    seller_id = sellerId,
                    resource_id = resourceId,
                    quantity = quantity,
                    transaction_type = "sell"
                };

                string json = JsonConvert.SerializeObject(request);
                string response = await PostAsync($"{TRANSACTIONS_ENDPOINT}/sell", json);
                return JsonConvert.DeserializeObject<TransactionData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error executing sell transaction: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get transaction history
        /// </summary>
        public async Task<List<TransactionData>> GetTransactionHistoryAsync(string characterId, int limit = 50)
        {
            try
            {
                string response = await GetAsync($"{TRANSACTIONS_ENDPOINT}?character_id={characterId}&limit={limit}");
                return JsonConvert.DeserializeObject<List<TransactionData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting transaction history for {characterId}: {ex.Message}");
                return new List<TransactionData>();
            }
        }

        #endregion

        #region Trade Route Operations

        /// <summary>
        /// Get all trade routes
        /// </summary>
        public async Task<List<TradeRouteData>> GetTradeRoutesAsync()
        {
            try
            {
                string response = await GetAsync(TRADE_ROUTES_ENDPOINT);
                return JsonConvert.DeserializeObject<List<TradeRouteData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting trade routes: {ex.Message}");
                return new List<TradeRouteData>();
            }
        }

        /// <summary>
        /// Get trade routes by market
        /// </summary>
        public async Task<List<TradeRouteData>> GetTradeRoutesByMarketAsync(string marketId)
        {
            try
            {
                string response = await GetAsync($"{TRADE_ROUTES_ENDPOINT}?market_id={marketId}");
                return JsonConvert.DeserializeObject<List<TradeRouteData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting trade routes for market {marketId}: {ex.Message}");
                return new List<TradeRouteData>();
            }
        }

        #endregion

        #region Currency Operations

        /// <summary>
        /// Get all currencies
        /// </summary>
        public async Task<List<CurrencyData>> GetCurrenciesAsync()
        {
            try
            {
                string response = await GetAsync(CURRENCIES_ENDPOINT);
                return JsonConvert.DeserializeObject<List<CurrencyData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting currencies: {ex.Message}");
                return new List<CurrencyData>();
            }
        }

        /// <summary>
        /// Convert currency
        /// </summary>
        public async Task<float> ConvertCurrencyAsync(string fromCurrencyId, string toCurrencyId, float amount)
        {
            try
            {
                var request = new
                {
                    from_currency_id = fromCurrencyId,
                    to_currency_id = toCurrencyId,
                    amount = amount
                };

                string json = JsonConvert.SerializeObject(request);
                string response = await PostAsync($"{CURRENCIES_ENDPOINT}/convert", json);
                var result = JsonConvert.DeserializeObject<Dictionary<string, object>>(response);
                return Convert.ToSingle(result["converted_amount"]);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error converting currency: {ex.Message}");
                return 0f;
            }
        }

        #endregion

        #region Economic Metrics

        /// <summary>
        /// Get economic metrics for a market
        /// </summary>
        public async Task<List<EconomicMetricData>> GetEconomicMetricsAsync(string marketId, string metricType = null)
        {
            try
            {
                string url = $"{MARKETS_ENDPOINT}/{marketId}/metrics";
                if (!string.IsNullOrEmpty(metricType))
                {
                    url += $"?metric_type={metricType}";
                }

                string response = await GetAsync(url);
                return JsonConvert.DeserializeObject<List<EconomicMetricData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting economic metrics for market {marketId}: {ex.Message}");
                return new List<EconomicMetricData>();
            }
        }

        #endregion
    }
} 