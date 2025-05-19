using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Systems.Events;

namespace VDM.Systems.Population
{
    public enum POIType
    {
        City,
        Town,
        Village,
        Ruins,
        Dungeon,
        Religious,
        Embassy,
        Outpost,
        Market,
        Custom
    }

    [Serializable]
    public class POIPopulation
    {
        public POIType Type;
        public int CurrentPopulation;
        public int TargetPopulation;
        public int MinPopulation;
        public float BaseRate;
        public string POIId;
        // Extend with additional fields as needed
    }

    public class PopulationManager : MonoBehaviour
    {
        public List<POIPopulation> AllPOIs { get; private set; } = new List<POIPopulation>();
        public float GlobalMultiplier { get; set; } = 1.0f;
        public event Action<POIPopulation> OnPopulationChanged;

        public void MonthlyUpdate()
        {
            foreach (var poi in AllPOIs)
            {
                int oldPop = poi.CurrentPopulation;
                if (poi.CurrentPopulation < poi.TargetPopulation)
                {
                    float rate = poi.BaseRate * ((float)poi.CurrentPopulation / poi.TargetPopulation) * GlobalMultiplier;
                    if (poi.CurrentPopulation >= 0.9f * poi.TargetPopulation)
                        rate *= 0.5f; // Soft cap
                    int add = Mathf.FloorToInt(rate);
                    poi.CurrentPopulation += add;
                    if (poi.CurrentPopulation > poi.TargetPopulation)
                        poi.CurrentPopulation = poi.TargetPopulation; // Hard cap
                }
                if (poi.CurrentPopulation < poi.MinPopulation)
                    poi.CurrentPopulation = poi.MinPopulation; // Prevent ghost towns
                // Emit event for all population changes
                OnPopulationChanged?.Invoke(poi);
                if (oldPop != poi.CurrentPopulation)
                {
                    var evt = new PopulationChangedEvent
                    {
                        POIId = poi.POIId,
                        OldPopulation = oldPop,
                        NewPopulation = poi.CurrentPopulation,
                        Timestamp = DateTime.UtcNow
                    };
                    EventDispatcher.Instance.Dispatch(evt);
                }
            }
        }

        public void SetGlobalMultiplier(float multiplier)
        {
            GlobalMultiplier = multiplier;
        }

        public void SetBaseRate(POIType type, float baseRate)
        {
            foreach (var poi in AllPOIs)
                if (poi.Type == type)
                    poi.BaseRate = baseRate;
        }
    }
} 