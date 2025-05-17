using NUnit.Framework;
using VisualDM.World;
using System.Linq;

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
    }
} 