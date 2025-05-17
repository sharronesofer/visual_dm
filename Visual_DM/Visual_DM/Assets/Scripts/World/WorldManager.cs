using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
{
    public class WorldManager : MonoBehaviour
    {
        public WorldTimeSystem TimeSystem { get; private set; }
        public SeasonSystem SeasonSystem { get; private set; }
        public WeatherSystem WeatherSystem { get; private set; }
        public FactionSystem FactionSystem { get; private set; }
        public EconomySystem EconomySystem { get; private set; }
        public EventSystem EventSystem { get; private set; }
        public CalendarSystem CalendarSystem { get; private set; }

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
    }
} 