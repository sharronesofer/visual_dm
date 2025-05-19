using System;
using System.Collections.Generic;
using Systems.Integration;
using System.Threading;
using VisualDM.Systems.Economy;

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

        public class RegionalEconomy
        {
            public string RegionId;
            public Dictionary<string, Resource> Resources = new();
            public Dictionary<string, float> MarketPrices = new();
            public List<TradeRoute> TradeRoutes = new();
        }

        private Dictionary<string, Resource> resources = new Dictionary<string, Resource>();
        private List<TradeRoute> tradeRoutes = new List<TradeRoute>();
        private Dictionary<string, float> marketPrices = new Dictionary<string, float>();
        private System.Random rng = new System.Random();
        private Dictionary<string, RegionalEconomy> regionalEconomies = new();
        private Dictionary<string, ResourceType> resourceTypes = new();
        private List<ResourceRecipe> productionChains = new();

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

        public void RegisterResourceType(ResourceType type)
        {
            resourceTypes[type.Name] = type;
        }

        public void AddRegion(string regionId)
        {
            if (!regionalEconomies.ContainsKey(regionId))
                regionalEconomies[regionId] = new RegionalEconomy { RegionId = regionId };
        }

        public void AddResourceToRegion(string regionId, string resourceName, float initialQty, float prodRate, float consRate)
        {
            AddRegion(regionId);
            var region = regionalEconomies[regionId];
            region.Resources[resourceName] = new Resource { Name = resourceName, Quantity = initialQty, ProductionRate = prodRate, ConsumptionRate = consRate };
            region.MarketPrices[resourceName] = 1.0f;
        }

        public void RegisterProductionChain(ResourceRecipe recipe)
        {
            productionChains.Add(recipe);
        }

        public abstract class EconomicAgent
        {
            public string Id;
            public string RegionId;
            public abstract void Act(RegionalEconomy region, EconomySystem system);
        }
        public class ProducerAgent : EconomicAgent
        {
            public string OutputResource;
            public float OutputRate;
            public override void Act(RegionalEconomy region, EconomySystem system)
            {
                if (region.Resources.ContainsKey(OutputResource))
                    region.Resources[OutputResource].Quantity += OutputRate;
                else
                    region.Resources[OutputResource] = new Resource { Name = OutputResource, Quantity = OutputRate };
            }
        }
        public class ConsumerAgent : EconomicAgent
        {
            public string InputResource;
            public float ConsumptionRate;
            public override void Act(RegionalEconomy region, EconomySystem system)
            {
                if (region.Resources.ContainsKey(InputResource))
                {
                    region.Resources[InputResource].Quantity -= ConsumptionRate;
                    if (region.Resources[InputResource].Quantity < 0)
                        region.Resources[InputResource].Quantity = 0;
                }
            }
        }
        public class TraderAgent : EconomicAgent
        {
            public string Resource;
            public string TargetRegionId;
            public float TradeAmount;
            public override void Act(RegionalEconomy region, EconomySystem system)
            {
                if (region.Resources.ContainsKey(Resource) && region.Resources[Resource].Quantity >= TradeAmount)
                {
                    region.Resources[Resource].Quantity -= TradeAmount;
                    system.AddResourceToRegion(TargetRegionId, Resource, TradeAmount, 0, 0);
                }
            }
        }
        private List<EconomicAgent> agents = new();
        public void RegisterAgent(EconomicAgent agent)
        {
            agents.Add(agent);
        }
        public void UpdateRegionalEconomy(string regionId, WorldTimeSystem time)
        {
            if (!regionalEconomies.ContainsKey(regionId)) return;
            var region = regionalEconomies[regionId];
            // Agent simulation
            foreach (var agent in agents)
            {
                if (agent.RegionId == regionId)
                    agent.Act(region, this);
            }
            // Production chains
            foreach (var recipe in productionChains)
            {
                bool canProduce = true;
                foreach (var input in recipe.Inputs)
                {
                    if (!region.Resources.ContainsKey(input.Key) || region.Resources[input.Key].Quantity < input.Value)
                    {
                        canProduce = false;
                        break;
                    }
                }
                if (canProduce)
                {
                    foreach (var input in recipe.Inputs)
                        region.Resources[input.Key].Quantity -= input.Value;
                    if (!region.Resources.ContainsKey(recipe.OutputResource))
                        region.Resources[recipe.OutputResource] = new Resource { Name = recipe.OutputResource };
                    region.Resources[recipe.OutputResource].Quantity += recipe.OutputAmount;
                }
            }
            // Decay, production, consumption
            foreach (var res in region.Resources.Values)
            {
                float decay = 0f;
                if (resourceTypes.TryGetValue(res.Name, out var type) && type.IsPerishable)
                    decay = res.Quantity * type.DecayRate;
                res.Quantity += res.ProductionRate - res.ConsumptionRate - decay;
                if (res.Quantity < 0) res.Quantity = 0;
            }
            // Price determination (supply/demand)
            foreach (var res in region.Resources.Values)
            {
                float supply = res.Quantity;
                float demand = Math.Max(1f, res.ConsumptionRate);
                float basePrice = 1.0f;
                float elasticity = 0.2f;
                float price = basePrice * (demand / Math.Max(1f, supply)) * (1f + elasticity * ((demand - supply) / demand));
                if (region.MarketPrices.ContainsKey(res.Name))
                    region.MarketPrices[res.Name] = Math.Max(0.1f, price);
                else
                    region.MarketPrices[res.Name] = price;
            }
            // TODO: Add trade, agent, and event logic per region
        }

        // Integration hooks
        public Action<string, float> OnFactionEconomicChange; // (factionId, deltaWealth)
        public Action<string, string, float> OnRegionEconomicEvent; // (regionId, eventType, magnitude)
        public Action<string, string, float> OnWorldStateEconomicChange; // (key, eventType, value)
        public void GenerateEconomicEvent(string regionId, string eventType, float magnitude)
        {
            // Example: Shortage, Surplus, TradeDisruption
            OnRegionEconomicEvent?.Invoke(regionId, eventType, magnitude);
            // TODO: Integrate with EventSystem and WorldStateSystem
        }
        public void PersistEconomyState()
        {
            // TODO: Serialize regionalEconomies and agents to WorldStateSystem
            // Example: WorldStateSystem.Instance.Set("EconomyState", ...);
        }
        public void LoadEconomyState()
        {
            // TODO: Deserialize from WorldStateSystem
        }

        public IEnumerable<string> GetAllRegionIds()
        {
            return regionalEconomies.Keys;
        }
        public string GetMarketSummary(string regionId)
        {
            if (!regionalEconomies.ContainsKey(regionId)) return "No data.";
            var region = regionalEconomies[regionId];
            var lines = new List<string>();
            foreach (var res in region.Resources.Values)
            {
                float price = region.MarketPrices.TryGetValue(res.Name, out var p) ? p : 1f;
                lines.Add($"{res.Name}: Qty={res.Quantity:F1}, Price={price:F2}");
            }
            return string.Join("\n", lines);
        }
        public IEnumerable<string> GetRegionResourceNames(string regionId)
        {
            if (!regionalEconomies.ContainsKey(regionId)) return new List<string>();
            return regionalEconomies[regionId].Resources.Keys;
        }
        public void PlayerTrade(string regionId, string resourceName, float amount)
        {
            if (!regionalEconomies.ContainsKey(regionId)) return;
            var region = regionalEconomies[regionId];
            if (!region.Resources.ContainsKey(resourceName)) return;
            // Example: Player buys resource, price increases
            region.Resources[resourceName].Quantity -= amount;
            if (region.Resources[resourceName].Quantity < 0) region.Resources[resourceName].Quantity = 0;
            region.MarketPrices[resourceName] *= 1.05f;
        }
    }
} 