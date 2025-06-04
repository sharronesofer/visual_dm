using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using VDM.Systems.Motifs.Models;

namespace VDM.Systems.Motifs.Utils
{
    /// <summary>
    /// Utility class for common motif operations and helper functions.
    /// Provides static methods for motif validation, filtering, and calculations.
    /// </summary>
    public static class MotifUtils
    {
        #region Validation

        /// <summary>
        /// Validate motif data for creation
        /// </summary>
        public static List<string> ValidateMotifCreateData(MotifCreateData data)
        {
            var errors = new List<string>();

            if (string.IsNullOrWhiteSpace(data.name))
                errors.Add("Motif name is required");

            if (string.IsNullOrWhiteSpace(data.description))
                errors.Add("Motif description is required");

            if (data.intensity < 1 || data.intensity > 10)
                errors.Add("Motif intensity must be between 1 and 10");

            if (data.durationDays < 1)
                errors.Add("Motif duration must be at least 1 day");

            if (string.IsNullOrWhiteSpace(data.theme))
                errors.Add("Motif theme is required");

            return errors;
        }

        /// <summary>
        /// Validate motif update data
        /// </summary>
        public static List<string> ValidateMotifUpdateData(MotifUpdateData data)
        {
            var errors = new List<string>();

            if (data.intensity.HasValue && (data.intensity < 1 || data.intensity > 10))
                errors.Add("Motif intensity must be between 1 and 10");

            if (data.durationDays.HasValue && data.durationDays < 1)
                errors.Add("Motif duration must be at least 1 day");

            return errors;
        }

        /// <summary>
        /// Check if a motif is currently active
        /// </summary>
        public static bool IsMotifActive(Motif motif)
        {
            return motif.lifecycle != MotifLifecycle.Dormant && 
                   motif.lifecycle != MotifLifecycle.Fading;
        }

        #endregion

        #region Filtering and Sorting

        /// <summary>
        /// Filter motifs by multiple criteria
        /// </summary>
        public static List<Motif> FilterMotifs(List<Motif> motifs, MotifFilter filter)
        {
            if (filter == null) return motifs;

            return motifs.Where(motif =>
            {
                // Category filter
                if (filter.categories != null && filter.categories.Count > 0 && 
                    !filter.categories.Contains(motif.category))
                    return false;

                // Scope filter
                if (filter.scopes != null && filter.scopes.Count > 0 && 
                    !filter.scopes.Contains(motif.scope))
                    return false;

                // Lifecycle filter
                if (filter.lifecycles != null && filter.lifecycles.Count > 0 && 
                    !filter.lifecycles.Contains(motif.lifecycle))
                    return false;

                // Intensity filter
                if (filter.minIntensity.HasValue && motif.intensity < filter.minIntensity.Value)
                    return false;
                if (filter.maxIntensity.HasValue && motif.intensity > filter.maxIntensity.Value)
                    return false;

                // Active only filter
                if (filter.activeOnly && !IsMotifActive(motif))
                    return false;

                // Region filter
                if (!string.IsNullOrEmpty(filter.regionId) && 
                    motif.location?.regionId != filter.regionId)
                    return false;

                // Theme filter
                if (filter.themes != null && filter.themes.Count > 0 && 
                    !filter.themes.Contains(motif.theme))
                    return false;

                // Tag filter
                if (filter.tags != null && filter.tags.Count > 0 && 
                    (motif.tags == null || !filter.tags.Any(tag => motif.tags.Contains(tag))))
                    return false;

                return true;
            }).ToList();
        }

        /// <summary>
        /// Sort motifs by various criteria
        /// </summary>
        public static List<Motif> SortMotifs(List<Motif> motifs, MotifSortCriteria criteria, bool ascending = true)
        {
            IOrderedEnumerable<Motif> sorted = criteria switch
            {
                MotifSortCriteria.Name => ascending ? 
                    motifs.OrderBy(m => m.name) : 
                    motifs.OrderByDescending(m => m.name),
                MotifSortCriteria.Category => ascending ? 
                    motifs.OrderBy(m => m.category) : 
                    motifs.OrderByDescending(m => m.category),
                MotifSortCriteria.Intensity => ascending ? 
                    motifs.OrderBy(m => m.intensity) : 
                    motifs.OrderByDescending(m => m.intensity),
                MotifSortCriteria.Lifecycle => ascending ? 
                    motifs.OrderBy(m => m.lifecycle) : 
                    motifs.OrderByDescending(m => m.lifecycle),
                MotifSortCriteria.CreatedDate => ascending ? 
                    motifs.OrderBy(m => m.createdAt) : 
                    motifs.OrderByDescending(m => m.createdAt),
                MotifSortCriteria.Duration => ascending ? 
                    motifs.OrderBy(m => m.durationDays) : 
                    motifs.OrderByDescending(m => m.durationDays),
                _ => ascending ? 
                    motifs.OrderBy(m => m.name) : 
                    motifs.OrderByDescending(m => m.name)
            };

            return sorted.ToList();
        }

        #endregion

        #region Distance and Position Calculations

        /// <summary>
        /// Calculate distance between two motifs
        /// </summary>
        public static float CalculateDistance(Motif motif1, Motif motif2)
        {
            if (motif1.location == null || motif2.location == null)
                return float.MaxValue;

            Vector2 pos1 = motif1.location.position;
            Vector2 pos2 = motif2.location.position;
            return Vector2.Distance(pos1, pos2);
        }

        /// <summary>
        /// Calculate distance from a position to a motif
        /// </summary>
        public static float CalculateDistanceToPosition(Motif motif, Vector2 position)
        {
            if (motif.location == null)
                return float.MaxValue;

            return Vector2.Distance(motif.location.position, position);
        }

        /// <summary>
        /// Check if a position is within a motif's area of influence
        /// </summary>
        public static bool IsPositionInMotifRange(Motif motif, Vector2 position)
        {
            if (motif.scope == MotifScope.Global)
                return true;

            if (motif.location == null)
                return false;

            float distance = CalculateDistanceToPosition(motif, position);
            return distance <= motif.location.radius;
        }

        /// <summary>
        /// Get all motifs affecting a specific position
        /// </summary>
        public static List<Motif> GetMotifsAtPosition(List<Motif> motifs, Vector2 position, bool includeGlobal = true)
        {
            return motifs.Where(motif =>
            {
                if (motif.scope == MotifScope.Global)
                    return includeGlobal;

                return IsPositionInMotifRange(motif, position);
            }).ToList();
        }

        #endregion

        #region Influence and Strength Calculations

        /// <summary>
        /// Calculate a motif's influence strength at a specific position
        /// </summary>
        public static float CalculateInfluenceStrength(Motif motif, Vector2 position)
        {
            float baseStrength = motif.GetInfluenceStrength();

            if (motif.scope == MotifScope.Global)
                return baseStrength;

            if (motif.location == null)
                return 0f;

            float distance = CalculateDistanceToPosition(motif, position);
            float radius = motif.location.radius;

            if (distance > radius)
                return 0f;

            // Linear falloff from center to edge
            float falloff = 1f - (distance / radius);
            return baseStrength * falloff;
        }

        /// <summary>
        /// Calculate combined influence of multiple motifs at a position
        /// </summary>
        public static MotifInfluence CalculateCombinedInfluence(List<Motif> motifs, Vector2 position)
        {
            var influence = new MotifInfluence();
            var categoryInfluences = new Dictionary<MotifCategory, float>();

            foreach (var motif in motifs)
            {
                float strength = CalculateInfluenceStrength(motif, position);
                if (strength > 0)
                {
                    influence.TotalStrength += strength;
                    influence.MotifCount++;

                    if (!categoryInfluences.ContainsKey(motif.category))
                        categoryInfluences[motif.category] = 0f;
                    
                    categoryInfluences[motif.category] += strength;
                }
            }

            // Find dominant category
            if (categoryInfluences.Count > 0)
            {
                var dominant = categoryInfluences.OrderByDescending(kvp => kvp.Value).First();
                influence.DominantCategory = dominant.Key;
                influence.DominantStrength = dominant.Value;
            }

            influence.CategoryInfluences = categoryInfluences;
            return influence;
        }

        #endregion

        #region Color and Visual Utilities

        /// <summary>
        /// Get the standard color for a motif category
        /// </summary>
        public static Color GetCategoryColor(MotifCategory category)
        {
            return category switch
            {
                MotifCategory.Ascension => new Color(1f, 0.8f, 0.2f), // Gold
                MotifCategory.Betrayal => new Color(0.8f, 0.2f, 0.2f), // Dark Red
                MotifCategory.Chaos => new Color(0.6f, 0.2f, 0.8f), // Purple
                MotifCategory.Collapse => new Color(0.5f, 0.3f, 0.2f), // Brown
                MotifCategory.Control => new Color(0.8f, 0.4f, 0.2f), // Orange
                MotifCategory.Death => new Color(0.1f, 0.1f, 0.1f), // Black
                MotifCategory.Deception => new Color(0.7f, 0.3f, 0.7f), // Magenta
                MotifCategory.Desire => new Color(1f, 0.4f, 0.6f), // Pink
                MotifCategory.Fear => new Color(0.4f, 0.1f, 0.1f), // Dark Red
                MotifCategory.Hope => new Color(0.2f, 0.8f, 0.4f), // Green
                MotifCategory.Justice => new Color(0.2f, 0.4f, 0.8f), // Blue
                MotifCategory.Madness => new Color(0.8f, 0.2f, 0.8f), // Bright Purple
                MotifCategory.Peace => new Color(0.6f, 0.8f, 0.9f), // Light Blue
                MotifCategory.Power => new Color(0.8f, 0.4f, 0.2f), // Orange-Red
                MotifCategory.Shadow => new Color(0.2f, 0.2f, 0.3f), // Dark Gray
                MotifCategory.Truth => new Color(0.9f, 0.9f, 0.2f), // Bright Yellow
                MotifCategory.Vengeance => new Color(0.9f, 0.1f, 0.1f), // Bright Red
                _ => new Color(0.5f, 0.5f, 0.5f) // Default Gray
            };
        }

        /// <summary>
        /// Get a blended color representing multiple motif categories
        /// </summary>
        public static Color GetBlendedCategoryColor(Dictionary<MotifCategory, float> categoryInfluences)
        {
            if (categoryInfluences.Count == 0)
                return Color.gray;

            Color blendedColor = Color.black;
            float totalWeight = categoryInfluences.Values.Sum();

            foreach (var kvp in categoryInfluences)
            {
                Color categoryColor = GetCategoryColor(kvp.Key);
                float weight = kvp.Value / totalWeight;
                blendedColor += categoryColor * weight;
            }

            return blendedColor;
        }

        #endregion

        #region String and Display Utilities

        /// <summary>
        /// Get a formatted display string for a motif
        /// </summary>
        public static string GetMotifDisplayString(Motif motif)
        {
            return $"{motif.name} ({motif.category}, {motif.scope}, Intensity: {motif.intensity})";
        }

        /// <summary>
        /// Get a short summary of a motif
        /// </summary>
        public static string GetMotifSummary(Motif motif)
        {
            string summary = $"{motif.name}: {motif.description}";
            if (summary.Length > 100)
            {
                summary = summary.Substring(0, 97) + "...";
            }
            return summary;
        }

        /// <summary>
        /// Format motif duration as human-readable text
        /// </summary>
        public static string FormatDuration(int durationDays)
        {
            if (durationDays == 1)
                return "1 day";
            else if (durationDays < 7)
                return $"{durationDays} days";
            else if (durationDays < 30)
            {
                int weeks = durationDays / 7;
                int remainingDays = durationDays % 7;
                string result = $"{weeks} week{(weeks > 1 ? "s" : "")}";
                if (remainingDays > 0)
                    result += $" {remainingDays} day{(remainingDays > 1 ? "s" : "")}";
                return result;
            }
            else
            {
                int months = durationDays / 30;
                int remainingDays = durationDays % 30;
                string result = $"{months} month{(months > 1 ? "s" : "")}";
                if (remainingDays > 0)
                    result += $" {remainingDays} day{(remainingDays > 1 ? "s" : "")}";
                return result;
            }
        }

        #endregion

        #region Data Conversion

        /// <summary>
        /// Create a location info object from position and radius
        /// </summary>
        public static VDM.Systems.Motifs.Models.LocationInfo CreateLocationInfo(Vector2 position, float radius = 10f, string regionId = "default")
        {
            return new VDM.Systems.Motifs.Models.LocationInfo
            {
                position = position,
                radius = radius,
                regionId = regionId
            };
        }

        /// <summary>
        /// Get position from location info
        /// </summary>
        public static Vector2 GetPosition(VDM.Systems.Motifs.Models.LocationInfo location)
        {
            return location?.position ?? Vector2.zero;
        }

        /// <summary>
        /// Convert Unity Vector3 to Vector2 (ignoring Y)
        /// </summary>
        public static Vector2 Vector3ToVector2(Vector3 vector3)
        {
            return new Vector2(vector3.x, vector3.z);
        }

        /// <summary>
        /// Convert Vector2 to Unity Vector3 (with Y = 0)
        /// </summary>
        public static Vector3 Vector2ToVector3(Vector2 vector2, float y = 0f)
        {
            return new Vector3(vector2.x, y, vector2.y);
        }

        #endregion
    }

    #region Supporting Data Structures

    /// <summary>
    /// Represents combined motif influence at a position
    /// </summary>
    public class MotifInfluence
    {
        public float TotalStrength { get; set; }
        public int MotifCount { get; set; }
        public MotifCategory? DominantCategory { get; set; }
        public float DominantStrength { get; set; }
        public Dictionary<MotifCategory, float> CategoryInfluences { get; set; } = new Dictionary<MotifCategory, float>();
    }

    /// <summary>
    /// Criteria for sorting motifs
    /// </summary>
    public enum MotifSortCriteria
    {
        Name,
        Category,
        Intensity,
        Lifecycle,
        CreatedDate,
        Duration
    }

    #endregion
} 