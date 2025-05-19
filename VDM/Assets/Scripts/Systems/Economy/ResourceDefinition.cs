using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Economy
{
    public enum ResourceCategory
    {
        RawMaterial,
        ManufacturedGood,
        Service,
        Currency
    }

    [Serializable]
    public class ResourceType
    {
        public string Name;
        public ResourceCategory Category;
        public bool IsPerishable;
        public float DecayRate; // 0 = non-perishable, >0 = % lost per tick
        public string Description;
    }

    [Serializable]
    public class ResourceRecipe
    {
        public string OutputResource;
        public Dictionary<string, float> Inputs = new(); // Resource name -> amount
        public float OutputAmount;
        public float ProductionTime; // in ticks
    }
} 