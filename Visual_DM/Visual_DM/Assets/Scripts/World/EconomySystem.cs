using System;
using System.Collections.Generic;

namespace VisualDM.World
{
    public class EconomySystem
    {
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
            resources[name] = new Resource { Name = name, Quantity = initialQty, ProductionRate = prodRate, ConsumptionRate = consRate };
            marketPrices[name] = 1.0f;
        }

        public void AddTradeRoute(string from, string to, float volume)
        {
            tradeRoutes.Add(new TradeRoute { From = from, To = to, Volume = volume });
        }

        public void UpdateEconomy(WorldTimeSystem time)
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
                // Simple trade simulation: move volume between resources if both exist
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
        }

        public float GetResourceQuantity(string name) => resources.TryGetValue(name, out var r) ? r.Quantity : 0f;
        public float GetMarketPrice(string name) => marketPrices.TryGetValue(name, out var p) ? p : 1f;
    }
} 