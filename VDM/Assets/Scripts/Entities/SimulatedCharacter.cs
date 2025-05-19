using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.Inventory;

namespace VisualDM.Entities
{
    [Serializable]
    public class SimulatedCharacter
    {
        public string Name { get; set; }
        public CharacterStats Stats;
        public List<VisualDM.Timeline.Models.Feat> ActiveFeats = new List<VisualDM.Timeline.Models.Feat>();
        public Inventory Inventory;

        public SimulatedCharacter(string name, CharacterStats stats, Inventory inventory = null)
        {
            Name = name;
            Stats = stats;
            Inventory = inventory ?? new Inventory();
        }

        public bool CanApplyFeat(VisualDM.Timeline.Models.Feat feat)
        {
            if (ActiveFeats.Contains(feat)) return false;
            // Prerequisite logic should be handled via canonical Feat class
            return true;
        }

        public bool ApplyFeat(VisualDM.Timeline.Models.Feat feat)
        {
            if (!CanApplyFeat(feat)) return false;
            ActiveFeats.Add(feat);
            // Apply logic should be handled via canonical Feat class
            return true;
        }

        public bool RemoveFeat(VisualDM.Timeline.Models.Feat feat)
        {
            if (!ActiveFeats.Contains(feat)) return false;
            // Remove logic should be handled via canonical Feat class
            ActiveFeats.Remove(feat);
            return true;
        }

        public SimulatedCharacter Clone()
        {
            var clone = new SimulatedCharacter(Name, Stats.Clone());
            clone.Inventory = new Inventory(Inventory);
            foreach (var feat in ActiveFeats)
                clone.ActiveFeats.Add(feat); // Shallow copy; feats should be stateless
            return clone;
        }

        /// <summary>
        /// Call this after any inventory change to update encumbrance effects.
        /// </summary>
        public void UpdateEncumbranceEffects()
        {
            float encumbrancePercent = Inventory.GetEncumbrancePercent();
            var (speedMult, staminaMult) = Stats.ApplyEncumbranceEffects(encumbrancePercent);
            // Example: apply speed multiplier to stats (or movement system)
            // Stats.Speed = Mathf.RoundToInt(Stats.Speed * speedMult); // If you want to directly modify
            // Instead, pass multiplier to movement logic as needed
            // Stamina multiplier can be used in stamina drain calculations
        }
    }
} 