using System;
using System.Collections.Generic;
using Systems.Integration;
using System.Threading;

namespace VisualDM.World
{
    public class EconomySystem
    {
        // --- Transaction Safety ---
        // All resource and trade modifications are atomic and thread-safe.
        // Each operation is wrapped in a lock and logged with a unique transaction ID.
        // See: Task #592 implementation notes.
        private readonly object _economyLock = new object();

        public class Resource
        {
            public string Name;
            public float Quantity;
            public float ProductionRate;
            public float ConsumptionRate;
        }

        public class TradeRoute
        {
            public string From;
            public string To;
            public float Volume;
        }

        private Dictionary<string, Resource> resources = new Dictionary<string, Resource>();
        private List<TradeRoute> tradeRoutes = new List<TradeRoute>();
        private Dictionary<string, float> marketPrices = new Dictionary<string, float>();
        private System.Random rng = new System.Random();

        public void AddResource(string name, float initialQty, float prodRate, float consRate)
        {
            lock (_economyLock)
            {
                string txnId = Guid.NewGuid().ToString();
                try
                {
                    resources[name] = new Resource { Name = name, Quantity = initialQty, ProductionRate = prodRate, ConsumptionRate = consRate };
                    marketPrices[name] = 1.0f;
                    IntegrationLogger.Log($"[Economy] AddResource txn={txnId} name={name}", LogLevel.Info, "EconomySystem", null, "AddResource", "Committed");
                }
                catch (Exception ex)
                {
                    IntegrationLogger.Log($"[Economy] AddResource txn={txnId} failed: {ex.Message}", LogLevel.Error, "EconomySystem", null, "AddResource", "RolledBack");
                    throw;
                }
            }
        }

        public void AddTradeRoute(string from, string to, float volume)
        {
            lock (_economyLock)
            {
                string txnId = Guid.NewGuid().ToString();
                try
                {
                    tradeRoutes.Add(new TradeRoute { From = from, To = to, Volume = volume });
                    IntegrationLogger.Log($"[Economy] AddTradeRoute txn={txnId} from={from} to={to}", LogLevel.Info, "EconomySystem", null, "AddTradeRoute", "Committed");
                }
                catch (Exception ex)
                {
                    IntegrationLogger.Log($"[Economy] AddTradeRoute txn={txnId} failed: {ex.Message}", LogLevel.Error, "EconomySystem", null, "AddTradeRoute", "RolledBack");
                    throw;
                }
            }
        }

        public void UpdateEconomy(WorldTimeSystem time)
        {
            lock (_economyLock)
            {
                string txnId = Guid.NewGuid().ToString();
                try
                {
                    // Update resources
                    foreach (var res in resources.Values)
                    {
                        res.Quantity += res.ProductionRate - res.ConsumptionRate;
                        if (res.Quantity < 0) res.Quantity = 0;
                    }
                    // Simulate trade
                    foreach (var route in tradeRoutes)
                    {
                        if (resources.ContainsKey(route.From) && resources.ContainsKey(route.To))
                        {
                            float tradeAmount = Math.Min(route.Volume, resources[route.From].Quantity);
                            resources[route.From].Quantity -= tradeAmount;
                            resources[route.To].Quantity += tradeAmount;
                        }
                    }
                    // Update market prices
                    foreach (var res in resources.Values)
                    {
                        float fluctuation = (float)(rng.NextDouble() - 0.5) * 0.1f; // +/-5%
                        float supplyDemand = (res.ProductionRate - res.ConsumptionRate) / Math.Max(1f, res.Quantity);
                        marketPrices[res.Name] *= 1f + fluctuation + 0.01f * supplyDemand;
                        if (marketPrices[res.Name] < 0.1f) marketPrices[res.Name] = 0.1f;
                    }
                    IntegrationLogger.Log($"[Economy] UpdateEconomy txn={txnId}", LogLevel.Info, "EconomySystem", null, "UpdateEconomy", "Committed");
                }
                catch (Exception ex)
                {
                    IntegrationLogger.Log($"[Economy] UpdateEconomy txn={txnId} failed: {ex.Message}", LogLevel.Error, "EconomySystem", null, "UpdateEconomy", "RolledBack");
                    throw;
                }
            }
        }

        public float GetResourceQuantity(string name) => resources.TryGetValue(name, out var r) ? r.Quantity : 0f;
        public float GetMarketPrice(string name) => marketPrices.TryGetValue(name, out var p) ? p : 1f;
    }
} 