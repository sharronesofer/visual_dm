using NUnit.Framework;
using VisualDM.World;
using System;

namespace VisualDM.Tests
{
    [TestFixture]
    public class WorldSystemTests
    {
        [Test]
        public void CalendarSystem_AddsAndRemovesImportantDates()
        {
            var calendar = new CalendarSystem();
            calendar.AddImportantDate("Event1", 2024, 6, 1);
            var dates = calendar.GetImportantDatesForDay(2024, 6, 1);
            Assert.IsNotNull(dates);
            calendar.RemoveImportantDate("Event1");
            Assert.IsEmpty(calendar.GetImportantDatesForDay(2024, 6, 1));
        }

        [Test]
        public void EventSystem_AddsAndRemovesEvents()
        {
            var system = new EventSystem();
            system.AddEvent("E1", DateTime.Now);
            Assert.IsTrue(system.HasEvent("E1"));
            system.RemoveEvent("E1");
            Assert.IsFalse(system.HasEvent("E1"));
        }

        [Test]
        public void WeatherSystem_ChangesWeather()
        {
            var weather = new WeatherSystem();
            weather.SetWeather(WeatherSystem.WeatherType.Rain);
            Assert.AreEqual(WeatherSystem.WeatherType.Rain, weather.CurrentWeather);
            weather.SetWeather(WeatherSystem.WeatherType.Sunny);
            Assert.AreEqual(WeatherSystem.WeatherType.Sunny, weather.CurrentWeather);
        }

        [Test]
        public void WorldManager_InitializesAndManagesState()
        {
            var go = new UnityEngine.GameObject("WorldManager");
            var manager = go.AddComponent<WorldManager>();
            Assert.IsNotNull(manager);
            UnityEngine.Object.DestroyImmediate(go);
        }
    }
} 