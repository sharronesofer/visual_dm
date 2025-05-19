using System;
using System.Collections.Generic;

namespace VisualDM.World
{
    public class SeasonSystem
    {
        public enum Season { Spring, Summer, Autumn, Winter }
        public Season CurrentSeason { get; private set; }
        public Dictionary<Season, int> SeasonStartDays { get; private set; }
        private WorldTimeSystem timeSystem;

        public SeasonSystem(WorldTimeSystem timeSystem)
        {
            this.timeSystem = timeSystem;
            // Default: Spring starts day 1, Summer 91, Autumn 181, Winter 271 (for 360-day year)
            SeasonStartDays = new Dictionary<Season, int>
            {
                { Season.Spring, 1 },
                { Season.Summer, 91 },
                { Season.Autumn, 181 },
                { Season.Winter, 271 }
            };
            UpdateSeason(timeSystem);
        }

        public void UpdateSeason(WorldTimeSystem time)
        {
            int dayOfYear = (time.Month - 1) * time.DaysPerMonth + time.Day;
            if (dayOfYear >= SeasonStartDays[Season.Winter])
                CurrentSeason = Season.Winter;
            else if (dayOfYear >= SeasonStartDays[Season.Autumn])
                CurrentSeason = Season.Autumn;
            else if (dayOfYear >= SeasonStartDays[Season.Summer])
                CurrentSeason = Season.Summer;
            else
                CurrentSeason = Season.Spring;
        }

        public void SetSeasonStartDays(Dictionary<Season, int> startDays)
        {
            SeasonStartDays = startDays;
        }
    }
} 