using VisualDM.Systems.Economy;
using VisualDM.UI;

public class GameLoader : MonoBehaviour
{
    private EconomySystem _economySystem;

    void Start()
    {
        _economySystem = new EconomySystem();
        // Register resource types
        _economySystem.RegisterResourceType(new ResourceType { Name = "Wheat", Category = ResourceCategory.RawMaterial, IsPerishable = true, DecayRate = 0.01f, Description = "Basic food crop." });
        _economySystem.RegisterResourceType(new ResourceType { Name = "Iron", Category = ResourceCategory.RawMaterial, IsPerishable = false, DecayRate = 0f, Description = "Industrial metal." });
        _economySystem.RegisterResourceType(new ResourceType { Name = "Bread", Category = ResourceCategory.ManufacturedGood, IsPerishable = true, DecayRate = 0.02f, Description = "Processed food." });
        // Register regions
        _economySystem.AddRegion("Northshire");
        _economySystem.AddRegion("Southport");
        // Add resources to regions
        _economySystem.AddResourceToRegion("Northshire", "Wheat", 100, 10, 5);
        _economySystem.AddResourceToRegion("Northshire", "Iron", 50, 2, 1);
        _economySystem.AddResourceToRegion("Southport", "Wheat", 30, 3, 8);
        _economySystem.AddResourceToRegion("Southport", "Iron", 80, 5, 2);
        // Register production chain
        _economySystem.RegisterProductionChain(new ResourceRecipe { OutputResource = "Bread", Inputs = new Dictionary<string, float> { { "Wheat", 5 } }, OutputAmount = 2, ProductionTime = 1 });
        // Add example agents
        _economySystem.RegisterAgent(new EconomySystem.ProducerAgent { Id = "Bakery1", RegionId = "Northshire", OutputResource = "Bread", OutputRate = 2 });
        _economySystem.RegisterAgent(new EconomySystem.ConsumerAgent { Id = "Villager1", RegionId = "Northshire", InputResource = "Bread", ConsumptionRate = 1 });
        // Show economy dashboard
        UIManager.Instance.ShowEconomyDashboard(_economySystem);
    }
} 