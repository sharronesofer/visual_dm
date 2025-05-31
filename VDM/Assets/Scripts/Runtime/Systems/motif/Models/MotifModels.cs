using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Systems.Motifs.Models
{
    /// <summary>
    /// Categorizes motifs by their narrative impact
    /// </summary>
    public enum MotifCategory
    {
        Ascension,
        Betrayal,
        Chaos,
        Collapse,
        Compulsion,
        Control,
        Death,
        Deception,
        Defiance,
        Desire,
        Destiny,
        Echo,
        Expansion,
        Faith,
        Fear,
        Futility,
        Grief,
        Guilt,
        Hope,
        Hunger,
        Innocence,
        Invention,
        Isolation,
        Justice,
        Loyalty,
        Madness,
        Obsession,
        Paranoia,
        Peace,
        Power,
        Pride,
        Protection,
        Rebirth,
        Redemption,
        Regret,
        Revelation,
        Ruin,
        Sacrifice,
        Silence,
        Shadow,
        Stagnation,
        Temptation,
        Time,
        Transformation,
        Truth,
        Unity,
        Vengeance,
        Worship
    }

    /// <summary>
    /// Defines the scope of a motif's influence
    /// </summary>
    public enum MotifScope
    {
        Global,    // Affects the entire world
        Regional,  // Affects a specific region
        Local      // Affects a specific location
    }

    /// <summary>
    /// Represents the lifecycle stage of a motif
    /// </summary>
    public enum MotifLifecycle
    {
        Dormant,   // Not active, waiting to emerge
        Emerging,  // Beginning to take effect
        Stable,    // At full strength
        Waning,    // Declining in power
        Fading     // Nearly gone
    }

    /// <summary>
    /// Targets for motif effects
    /// </summary>
    public enum MotifEffectTarget
    {
        NPC,         // Affects NPC behavior, dialogue, etc.
        Event,       // Influences event generation and frequency
        Quest,       // Modifies quest/arc generation and outcomes
        Faction,     // Adjusts faction relationships and tension
        Environment, // Alters weather patterns, ambient effects
        Economy,     // Impacts economic factors like prices, resource availability
        Narrative,   // Provides context for narrative generation
        Custom       // Custom effect type
    }

    /// <summary>
    /// Location information for a motif
    /// </summary>
    [Serializable]
    public class LocationInfo
    {
        public string regionId;
        public Vector2 position;
        public float radius;

        public LocationInfo()
        {
            regionId = null;
            position = Vector2.zero;
            radius = 0f;
        }

        public LocationInfo(string regionId, Vector2 position, float radius)
        {
            this.regionId = regionId;
            this.position = position;
            this.radius = radius;
        }
    }

    /// <summary>
    /// Represents a specific effect a motif has on game systems
    /// </summary>
    [Serializable]
    public class MotifEffect
    {
        public MotifEffectTarget target;
        public int intensity = 1; // 1-10 scale
        public string description;
        public Dictionary<string, object> parameters;

        public MotifEffect()
        {
            parameters = new Dictionary<string, object>();
        }

        public MotifEffect(MotifEffectTarget target, int intensity, string description)
        {
            this.target = target;
            this.intensity = Mathf.Clamp(intensity, 1, 10);
            this.description = description;
            this.parameters = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Represents a narrative motif in the game world
    /// </summary>
    [Serializable]
    public class Motif
    {
        public string id;
        public string name;
        public string description;
        public MotifCategory category;
        public MotifScope scope;
        public string theme = "general";
        public MotifLifecycle lifecycle = MotifLifecycle.Emerging;
        public int intensity = 5; // 1-10 scale
        
        // Duration and timing
        public DateTime startTime;
        public DateTime endTime;
        public int durationDays = 14;
        
        // Location data for regional/local motifs
        public LocationInfo location;
        
        // Effects
        public List<MotifEffect> effects;
        
        // Metadata
        public DateTime createdAt;
        public DateTime updatedAt;
        public Dictionary<string, object> metadata;
        
        // Enhanced narrative integration
        public string tone = "neutral";
        public string narrativeDirection = "steady";
        public List<string> descriptors;
        
        // Optional fields for advanced synthesis
        public List<string> associatedElements;
        public List<string> opposingThemes;
        
        // Context for narrative generation
        public string narrativeGuidance;
        
        // Tags for categorization and filtering
        public List<string> tags;

        public Motif()
        {
            id = Guid.NewGuid().ToString();
            effects = new List<MotifEffect>();
            metadata = new Dictionary<string, object>();
            descriptors = new List<string>();
            associatedElements = new List<string>();
            opposingThemes = new List<string>();
            tags = new List<string>();
            createdAt = DateTime.UtcNow;
            updatedAt = DateTime.UtcNow;
        }

        /// <summary>
        /// Update the lifecycle of the motif
        /// </summary>
        public void UpdateLifecycle(MotifLifecycle newLifecycle)
        {
            lifecycle = newLifecycle;
            updatedAt = DateTime.UtcNow;
        }

        /// <summary>
        /// Check if the motif is currently active
        /// </summary>
        public bool IsActive()
        {
            return lifecycle != MotifLifecycle.Dormant && lifecycle != MotifLifecycle.Fading;
        }

        /// <summary>
        /// Get the motif's influence strength based on lifecycle and intensity
        /// </summary>
        public float GetInfluenceStrength()
        {
            float baseStrength = intensity / 10f;
            
            return lifecycle switch
            {
                MotifLifecycle.Dormant => 0f,
                MotifLifecycle.Emerging => baseStrength * 0.3f,
                MotifLifecycle.Stable => baseStrength,
                MotifLifecycle.Waning => baseStrength * 0.6f,
                MotifLifecycle.Fading => baseStrength * 0.1f,
                _ => baseStrength
            };
        }
    }

    /// <summary>
    /// Data for creating a new motif
    /// </summary>
    [Serializable]
    public class MotifCreateData
    {
        public string name;
        public string description;
        public MotifCategory category;
        public MotifScope scope;
        public string theme = "general";
        public MotifLifecycle lifecycle = MotifLifecycle.Emerging;
        public int intensity = 5;
        public int durationDays = 14;
        public LocationInfo location;
        public List<MotifEffect> effects;
        public Dictionary<string, object> metadata;

        public MotifCreateData()
        {
            effects = new List<MotifEffect>();
            metadata = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Data for updating an existing motif
    /// </summary>
    [Serializable]
    public class MotifUpdateData
    {
        public string name;
        public string description;
        public MotifCategory? category;
        public MotifScope? scope;
        public string theme;
        public MotifLifecycle? lifecycle;
        public int? intensity;
        public int? durationDays;
        public LocationInfo location;
        public List<MotifEffect> effects;
        public Dictionary<string, object> metadata;
    }

    /// <summary>
    /// Filter criteria for querying motifs
    /// </summary>
    [Serializable]
    public class MotifFilter
    {
        public List<MotifCategory> categories;
        public List<MotifScope> scopes;
        public List<MotifLifecycle> lifecycles;
        public int? minIntensity;
        public int? maxIntensity;
        public string regionId;
        public string effectType;
        public bool activeOnly = true;
        public List<string> ids;
        public List<string> themes;
        public List<string> regionIds;
        public bool? isGlobal;
        public Dictionary<string, object> metadata;
        public List<string> tags;
        public DateTime? createdAfter;
        public DateTime? createdBefore;
        public DateTime? updatedAfter;
        public DateTime? updatedBefore;

        public MotifFilter()
        {
            categories = new List<MotifCategory>();
            scopes = new List<MotifScope>();
            lifecycles = new List<MotifLifecycle>();
            ids = new List<string>();
            themes = new List<string>();
            regionIds = new List<string>();
            metadata = new Dictionary<string, object>();
            tags = new List<string>();
        }
    }

    /// <summary>
    /// Response wrapper for API calls
    /// </summary>
    [Serializable]
    public class MotifResponse<T>
    {
        public bool success;
        public string message;
        public T data;
        public List<string> errors;

        public MotifResponse()
        {
            errors = new List<string>();
        }
    }

    /// <summary>
    /// Narrative context information for GPT integration
    /// </summary>
    [Serializable]
    public class MotifNarrativeContext
    {
        public List<Motif> activeMotifs;
        public string dominantMotif;
        public List<string> narrativeThemes;
        public int motifCount;
        public string locationType;
        public string locationName;
        public bool hasMotifs;
        public string promptText;
        public List<string> themes;

        public MotifNarrativeContext()
        {
            activeMotifs = new List<Motif>();
            narrativeThemes = new List<string>();
            themes = new List<string>();
        }
    }
} 