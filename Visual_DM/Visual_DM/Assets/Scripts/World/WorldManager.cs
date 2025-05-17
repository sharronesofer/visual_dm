using System;
using System.Collections.Generic;
using UnityEngine;
using Systems.Integration;

namespace VisualDM.World
{
    // Integrated with ServiceLocator and IntegrationEventBus for cross-system quest/world state operations.
    // Implements IWorldSystem for standardized integration.
    public class WorldManager : MonoBehaviour, IWorldSystem
    {
        public WorldTimeSystem TimeSystem { get; private set; }
        public SeasonSystem SeasonSystem { get; private set; }
        public WeatherSystem WeatherSystem { get; private set; }
        public FactionSystem FactionSystem { get; private set; }
        public EconomySystem EconomySystem { get; private set; }
        public EventSystem EventSystem { get; private set; }
        public CalendarSystem CalendarSystem { get; private set; }
        public RegionSystem RegionSystem { get; private set; }

        void Awake()
        {
            // Initialize all world subsystems
            TimeSystem = new WorldTimeSystem();
            SeasonSystem = new SeasonSystem(TimeSystem);
            WeatherSystem = new WeatherSystem(TimeSystem, SeasonSystem);
            FactionSystem = new FactionSystem();
            EconomySystem = new EconomySystem();
            EventSystem = new EventSystem();
            CalendarSystem = new CalendarSystem();
            RegionSystem = new RegionSystem();
            // Example: Create a region and associate with an arc (runtime only)
            var region = new Region("Central Plains", "Biome", new UnityEngine.Rect(0, 0, 100, 100));
            region.DominantFactions.Add("KingdomA");
            region.ResourceDistribution["Wheat"] = 500f;
            region.CulturalAttributes["Dialect"] = "Plainspeak";
            RegionSystem.AddRegion(region);
            // Example arc association (arcId would come from narrative system)
            string exampleArcId = "arc-001";
            RegionSystem.AssociateArcWithRegion(exampleArcId, region.Id);
            // Example: Lookup region at a position
            var found = RegionSystem.GetRegionAtPosition(new UnityEngine.Vector2(10, 10));
            Debug.Log($"Region at (10,10): {found?.Name}");

            // Subscribe to integration event bus
            Systems.Integration.IntegrationEventBus.Instance.Subscribe<Systems.Integration.IntegrationMessage>(OnIntegrationMessage);
        }

        private void OnIntegrationMessage(Systems.Integration.IntegrationMessage message)
        {
            // TODO: Handle integration messages as needed
            Debug.Log($"[WorldManager] Received integration message: {message.MessageType} from {message.SourceSystem} to {message.TargetSystem}");
        }

        void Update()
        {
            // Advance world time and update all systems
            TimeSystem.Tick(Time.deltaTime);
            SeasonSystem.UpdateSeason(TimeSystem);
            WeatherSystem.UpdateWeather(TimeSystem, SeasonSystem);
            EconomySystem.UpdateEconomy(TimeSystem);
            EventSystem.UpdateEvents(TimeSystem);
        }

        // IWorldSystem implementation
        public void OnQuestEvent(QuestEventData eventData)
        {
            // TODO: Handle quest event integration logic
            Debug.Log($"[WorldManager] Received quest event: {eventData.EventType} for Quest {eventData.QuestId}");
        }

        public WorldState GetWorldStateForQuest(string questId)
        {
            // TODO: Return world state relevant to the quest
            Debug.Log($"[WorldManager] GetWorldStateForQuest called for Quest {questId}");
            return new WorldState { StateId = questId, Description = "Stub world state" };
        }

        public void SyncWorldState(WorldState state)
        {
            // TODO: Sync world state from external system
            Debug.Log($"[WorldManager] SyncWorldState called for StateId {state.StateId}");
        }

        void OnDestroy()
        {
            // Unsubscribe from integration event bus to prevent memory leaks
            Systems.Integration.IntegrationEventBus.Instance.Unsubscribe<Systems.Integration.IntegrationMessage>(OnIntegrationMessage);
        }
    }
}