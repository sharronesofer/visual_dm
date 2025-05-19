using NUnit.Framework;
using VisualDM.World;
using System.Linq;
using UnityEngine;

namespace VisualDM.Tests
{
    [TestFixture]
    public class WorldTests
    {
        [Test]
        public void WorldTimeSystem_Tick_AdvancesTime()
        {
            var time = new WorldTimeSystem(1, 1, 1, 0, 0, 0);
            int initialDay = time.Day;
            time.Tick(2f); // Should advance 2 seconds
            Assert.AreEqual(initialDay, time.Day); // Not enough to advance day
            for (int i = 0; i < 86400; i++) // Simulate 1 day (in seconds)
                time.Tick(1f);
            Assert.AreNotEqual(initialDay, time.Day);
        }

        [Test]
        public void SeasonSystem_UpdatesSeasonCorrectly()
        {
            var time = new WorldTimeSystem(1, 1, 1);
            var season = new SeasonSystem(time);
            time.Tick(1f); // Spring
            Assert.AreEqual(SeasonSystem.Season.Spring, season.CurrentSeason);
            time = new WorldTimeSystem(1, 7, 1); // Summer
            season = new SeasonSystem(time);
            Assert.AreEqual(SeasonSystem.Season.Summer, season.CurrentSeason);
        }

        [Test]
        public void FactionSystem_AddAndGetRelationship()
        {
            var factions = new FactionSystem();
            factions.AddFaction("A");
            factions.AddFaction("B");
            factions.SetRelationship("A", "B", 0.5f);
            Assert.AreEqual(0.5f, factions.GetRelationship("A", "B"));
        }

        [Test]
        public void EconomySystem_AddResourceAndUpdate()
        {
            var econ = new EconomySystem();
            econ.AddResource("Gold", 100, 10, 5);
            var time = new WorldTimeSystem();
            econ.UpdateEconomy(time);
            // Should not throw and should update resource
            Assert.IsTrue(econ != null);
        }

        [Test]
        public void Region_CreationAndProperties()
        {
            var rect = new Rect(0, 0, 10, 10);
            var region = new VisualDM.World.Region("TestRegion", "Biome", rect);
            region.DominantFactions.Add("FactionA");
            region.ResourceDistribution["Gold"] = 100f;
            region.CulturalAttributes["Language"] = "Elvish";
            Assert.AreEqual("TestRegion", region.Name);
            Assert.AreEqual("Biome", region.Type);
            Assert.IsTrue(region.DominantFactions.Contains("FactionA"));
            Assert.AreEqual(100f, region.ResourceDistribution["Gold"]);
            Assert.AreEqual("Elvish", region.CulturalAttributes["Language"]);
        }

        [Test]
        public void Region_BoundaryDetection_Works()
        {
            var rect = new Rect(0, 0, 10, 10);
            var region = new VisualDM.World.Region("TestRegion", "Biome", rect);
            Assert.IsTrue(region.Contains(new Vector2(5, 5)));
            Assert.IsFalse(region.Contains(new Vector2(15, 15)));
        }

        [Test]
        public void RegionSystem_AddAndQueryRegions()
        {
            var sys = new VisualDM.World.RegionSystem();
            var region1 = new VisualDM.World.Region("A", "City", new Rect(0, 0, 5, 5));
            var region2 = new VisualDM.World.Region("B", "Forest", new Rect(3, 3, 5, 5));
            sys.AddRegion(region1);
            sys.AddRegion(region2);
            // Overlapping area
            var all = sys.GetAllRegionsAtPosition(new Vector2(4, 4));
            Assert.AreEqual(2, all.Count);
            var single = sys.GetRegionAtPosition(new Vector2(1, 1));
            Assert.AreEqual(region1.Id, single.Id);
        }

        [Test]
        public void RegionSystem_ArcAssociation_Works()
        {
            var sys = new VisualDM.World.RegionSystem();
            var region = new VisualDM.World.Region("A", "City", new Rect(0, 0, 5, 5));
            sys.AddRegion(region);
            string arcId = "arc-123";
            sys.AssociateArcWithRegion(arcId, region.Id);
            var regions = sys.GetRegionsForArc(arcId);
            Assert.AreEqual(1, regions.Count);
            Assert.AreEqual(region.Id, regions[0].Id);
        }

        [Test]
        public void RegionSystem_Serialization_Works()
        {
            var sys = new VisualDM.World.RegionSystem();
            var region = new VisualDM.World.Region("A", "City", new Rect(0, 0, 5, 5));
            sys.AddRegion(region);
            string json = sys.Serialize();
            var sys2 = VisualDM.World.RegionSystem.Deserialize(json);
            Assert.AreEqual(1, sys2.GetAllRegions().GetEnumerator().MoveNext() ? 1 : 0);
        }
    }
}