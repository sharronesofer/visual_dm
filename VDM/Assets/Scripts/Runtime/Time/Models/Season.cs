using Newtonsoft.Json;
using System;


namespace VDM.Runtime.Time.Models
{
    /// <summary>
    /// Represents the four seasons of the year, aligned with backend time system.
    /// </summary>
    [Serializable]
    public enum Season
    {
        /// <summary>
        /// Spring season, typically associated with growth and renewal.
        /// </summary>
        [JsonProperty("spring")]
        Spring = 0,
        
        /// <summary>
        /// Summer season, typically associated with warmth and abundance.
        /// </summary>
        [JsonProperty("summer")]
        Summer = 1,
        
        /// <summary>
        /// Autumn/Fall season, typically associated with harvest and transition.
        /// </summary>
        [JsonProperty("autumn")]
        Autumn = 2,
        
        /// <summary>
        /// Winter season, typically associated with cold and dormancy.
        /// </summary>
        [JsonProperty("winter")]
        Winter = 3
    }
    
    /// <summary>
    /// Extension methods for the Season enum.
    /// </summary>
    public static class SeasonExtensions
    {
        /// <summary>
        /// Gets the next season in the cycle.
        /// </summary>
        /// <param name="season">The current season</param>
        /// <returns>The next season in the cycle</returns>
        public static Season Next(this Season season)
        {
            return (Season)(((int)season + 1) % 4);
        }
        
        /// <summary>
        /// Gets the previous season in the cycle.
        /// </summary>
        /// <param name="season">The current season</param>
        /// <returns>The previous season in the cycle</returns>
        public static Season Previous(this Season season)
        {
            return (Season)(((int)season + 3) % 4);
        }
        
        /// <summary>
        /// Determines which season a given month falls within.
        /// </summary>
        /// <param name="month">The month (1-12)</param>
        /// <param name="monthsPerYear">Total months in the year</param>
        /// <param name="monthsPerSeason">Months per season</param>
        /// <returns>The corresponding season</returns>
        public static Season FromMonth(int month, int monthsPerYear = 12, int monthsPerSeason = 3)
        {
            // Adjust for 1-based month
            int zeroBasedMonth = month - 1;
            
            // Calculate which season the month falls in
            int seasonIndex = (zeroBasedMonth / monthsPerSeason) % 4;
            
            return (Season)seasonIndex;
        }

        /// <summary>
        /// Gets the string representation for backend compatibility.
        /// </summary>
        /// <param name="season">The season</param>
        /// <returns>String representation matching backend</returns>
        public static string ToBackendString(this Season season)
        {
            return season switch
            {
                Season.Spring => "spring",
                Season.Summer => "summer", 
                Season.Autumn => "autumn",
                Season.Winter => "winter",
                _ => "spring"
            };
        }

        /// <summary>
        /// Parse season from backend string representation.
        /// </summary>
        /// <param name="seasonString">Backend season string</param>
        /// <returns>Corresponding Season enum value</returns>
        public static Season FromBackendString(string seasonString)
        {
            return seasonString?.ToLowerInvariant() switch
            {
                "spring" => Season.Spring,
                "summer" => Season.Summer,
                "autumn" or "fall" => Season.Autumn,
                "winter" => Season.Winter,
                _ => Season.Spring
            };
        }
    }
} 