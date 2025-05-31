using NativeWebSocket;
using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Infrastructure.Services.Websocket;
using VDM.Systems.Economy.Models;


namespace VDM.Systems.Economy.Services
{
    /// <summary>
    /// WebSocket handler for Economy system real-time updates
    /// </summary>
    public class EconomyWebSocketHandler : BaseWebSocketHandler
    {
        #region Events

        public event Action<MarketData> OnMarketUpdated;
        public event Action<MarketPriceData> OnPriceUpdated;
        public event Action<TransactionData> OnTransactionCompleted;
        public event Action<TradeRouteData> OnTradeRouteUpdated;
        public event Action<EconomicMetricData> OnEconomicMetricUpdated;
        public event Action<CurrencyData> OnCurrencyUpdated;
        public event Action<string, Dictionary<string, object>> OnMarketEvent;

        #endregion

        private const string ECONOMY_CHANNEL = "economy";
        private const string MARKET_CHANNEL = "market";
        private const string PRICES_CHANNEL = "prices";
        private const string TRANSACTIONS_CHANNEL = "transactions";
        private const string TRADE_ROUTES_CHANNEL = "trade_routes";
        private const string CURRENCIES_CHANNEL = "currencies";
        private const string METRICS_CHANNEL = "metrics";

        public EconomyWebSocketHandler() : base() { }

        public void Initialize(string serverUrl)
        {
            // Initialize WebSocket connection
            Connect(serverUrl);
            
            // Subscribe to economy channels
            SubscribeToChannels();
        }

        private void SubscribeToChannels()
        {
            Subscribe(ECONOMY_CHANNEL);
            Subscribe(MARKET_CHANNEL);
            Subscribe(PRICES_CHANNEL);
            Subscribe(TRANSACTIONS_CHANNEL);
            Subscribe(TRADE_ROUTES_CHANNEL);
            Subscribe(CURRENCIES_CHANNEL);
            Subscribe(METRICS_CHANNEL);
        }

        protected override void HandleMessage(string message)
        {
            try
            {
                var messageData = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
                
                if (!messageData.ContainsKey("type") || !messageData.ContainsKey("channel"))
                {
                    Debug.LogWarning($"Economy WebSocket message missing type or channel field: {message}");
                    return;
                }

                string messageType = messageData["type"].ToString();
                string channel = messageData["channel"].ToString();

                switch (channel)
                {
                    case MARKET_CHANNEL:
                        HandleMarketMessage(messageType, messageData);
                        break;
                    case PRICES_CHANNEL:
                        HandlePriceMessage(messageType, messageData);
                        break;
                    case TRANSACTIONS_CHANNEL:
                        HandleTransactionMessage(messageType, messageData);
                        break;
                    case TRADE_ROUTES_CHANNEL:
                        HandleTradeRouteMessage(messageType, messageData);
                        break;
                    case CURRENCIES_CHANNEL:
                        HandleCurrencyMessage(messageType, messageData);
                        break;
                    case METRICS_CHANNEL:
                        HandleMetricMessage(messageType, messageData);
                        break;
                    case ECONOMY_CHANNEL:
                        HandleEconomyMessage(messageType, messageData);
                        break;
                    default:
                        Debug.LogWarning($"Unknown economy channel: {channel}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling economy WebSocket message: {ex.Message}\nMessage: {message}");
            }
        }

        #region Message Handlers

        private void HandleMarketMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "market_created":
                case "market_updated":
                    if (messageData.ContainsKey("market"))
                    {
                        var marketJson = JsonConvert.SerializeObject(messageData["market"]);
                        var market = JsonConvert.DeserializeObject<MarketData>(marketJson);
                        OnMarketUpdated?.Invoke(market);
                    }
                    break;

                case "market_event":
                    if (messageData.ContainsKey("market_id") && messageData.ContainsKey("event_data"))
                    {
                        string marketId = messageData["market_id"].ToString();
                        var eventData = messageData["event_data"] as Dictionary<string, object>;
                        OnMarketEvent?.Invoke(marketId, eventData);
                    }
                    break;
            }
        }

        private void HandlePriceMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "price_updated":
                    if (messageData.ContainsKey("price_data"))
                    {
                        var priceJson = JsonConvert.SerializeObject(messageData["price_data"]);
                        var priceData = JsonConvert.DeserializeObject<MarketPriceData>(priceJson);
                        OnPriceUpdated?.Invoke(priceData);
                    }
                    break;

                case "price_bulk_update":
                    if (messageData.ContainsKey("prices"))
                    {
                        var pricesJson = JsonConvert.SerializeObject(messageData["prices"]);
                        var prices = JsonConvert.DeserializeObject<List<MarketPriceData>>(pricesJson);
                        foreach (var price in prices)
                        {
                            OnPriceUpdated?.Invoke(price);
                        }
                    }
                    break;
            }
        }

        private void HandleTransactionMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "transaction_completed":
                    if (messageData.ContainsKey("transaction"))
                    {
                        var transactionJson = JsonConvert.SerializeObject(messageData["transaction"]);
                        var transaction = JsonConvert.DeserializeObject<TransactionData>(transactionJson);
                        OnTransactionCompleted?.Invoke(transaction);
                    }
                    break;
            }
        }

        private void HandleTradeRouteMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "trade_route_created":
                case "trade_route_updated":
                    if (messageData.ContainsKey("trade_route"))
                    {
                        var routeJson = JsonConvert.SerializeObject(messageData["trade_route"]);
                        var route = JsonConvert.DeserializeObject<TradeRouteData>(routeJson);
                        OnTradeRouteUpdated?.Invoke(route);
                    }
                    break;
            }
        }

        private void HandleCurrencyMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "currency_updated":
                case "exchange_rate_updated":
                    if (messageData.ContainsKey("currency"))
                    {
                        var currencyJson = JsonConvert.SerializeObject(messageData["currency"]);
                        var currency = JsonConvert.DeserializeObject<CurrencyData>(currencyJson);
                        OnCurrencyUpdated?.Invoke(currency);
                    }
                    break;
            }
        }

        private void HandleMetricMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "metric_updated":
                    if (messageData.ContainsKey("metric"))
                    {
                        var metricJson = JsonConvert.SerializeObject(messageData["metric"]);
                        var metric = JsonConvert.DeserializeObject<EconomicMetricData>(metricJson);
                        OnEconomicMetricUpdated?.Invoke(metric);
                    }
                    break;
            }
        }

        private void HandleEconomyMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "economy_status_update":
                    // Handle general economy status updates
                    Debug.Log($"Economy status update: {JsonConvert.SerializeObject(messageData)}");
                    break;

                case "system_maintenance":
                    // Handle system maintenance notifications
                    Debug.Log($"Economy system maintenance: {JsonConvert.SerializeObject(messageData)}");
                    break;
            }
        }

        #endregion

        #region Subscription Management

        /// <summary>
        /// Subscribe to market updates for a specific market
        /// </summary>
        public void SubscribeToMarket(string marketId)
        {
            Subscribe($"{MARKET_CHANNEL}:{marketId}");
        }

        /// <summary>
        /// Unsubscribe from market updates for a specific market
        /// </summary>
        public void UnsubscribeFromMarket(string marketId)
        {
            Unsubscribe($"{MARKET_CHANNEL}:{marketId}");
        }

        /// <summary>
        /// Subscribe to price updates for a specific resource in a market
        /// </summary>
        public void SubscribeToPrice(string marketId, string resourceId)
        {
            Subscribe($"{PRICES_CHANNEL}:{marketId}:{resourceId}");
        }

        /// <summary>
        /// Subscribe to all price updates for a market
        /// </summary>
        public void SubscribeToMarketPrices(string marketId)
        {
            Subscribe($"{PRICES_CHANNEL}:{marketId}");
        }

        /// <summary>
        /// Subscribe to transaction updates for a character
        /// </summary>
        public void SubscribeToCharacterTransactions(string characterId)
        {
            Subscribe($"{TRANSACTIONS_CHANNEL}:{characterId}");
        }

        /// <summary>
        /// Subscribe to trade route updates
        /// </summary>
        public void SubscribeToTradeRoutes(string regionId = null)
        {
            if (string.IsNullOrEmpty(regionId))
            {
                Subscribe(TRADE_ROUTES_CHANNEL);
            }
            else
            {
                Subscribe($"{TRADE_ROUTES_CHANNEL}:{regionId}");
            }
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Send a request to track a specific market
        /// </summary>
        public void RequestMarketTracking(string marketId)
        {
            var request = new
            {
                type = "track_market",
                market_id = marketId
            };

            SendMessage(MARKET_CHANNEL, JsonConvert.SerializeObject(request));
        }

        /// <summary>
        /// Send a request to get current market status
        /// </summary>
        public void RequestMarketStatus(string marketId)
        {
            var request = new
            {
                type = "get_market_status",
                market_id = marketId
            };

            SendMessage(MARKET_CHANNEL, JsonConvert.SerializeObject(request));
        }

        /// <summary>
        /// Send a request to get real-time price updates
        /// </summary>
        public void RequestPriceUpdates(string marketId, List<string> resourceIds = null)
        {
            var request = new
            {
                type = "request_price_updates",
                market_id = marketId,
                resource_ids = resourceIds
            };

            SendMessage(PRICES_CHANNEL, JsonConvert.SerializeObject(request));
        }

        #endregion
    }
} 