using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Simulation
{
    [Serializable]
    public class SimulatedCharacter
    {
        public string Name;
        public CharacterStats Stats;
        public List<Feat> ActiveFeats = new List<Feat>();
        public List<string> Inventory = new List<string>();

        public SimulatedCharacter(string name, CharacterStats stats)
        {
            Name = name;
            Stats = stats;
        }

        public bool CanApplyFeat(Feat feat)
        {
            if (ActiveFeats.Contains(feat)) return false;
            if (feat.Prerequisites != null)
            {
                foreach (var prereq in feat.Prerequisites)
                {
                    if (!prereq.IsMet(this)) return false;
                }
            }
            return true;
        }

        public bool ApplyFeat(Feat feat)
        {
            if (!CanApplyFeat(feat)) return false;
            ActiveFeats.Add(feat);
            feat.Apply(this);
            return true;
        }

        public bool RemoveFeat(Feat feat)
        {
            if (!ActiveFeats.Contains(feat)) return false;
            feat.Remove(this);
            ActiveFeats.Remove(feat);
            return true;
        }

        public SimulatedCharacter Clone()
        {
            var clone = new SimulatedCharacter(Name, Stats.Clone());
            clone.Inventory = new List<string>(Inventory);
            foreach (var feat in ActiveFeats)
                clone.ActiveFeats.Add(feat); // Shallow copy; feats should be stateless
            return clone;
        }
    }

    [Serializable]
    public class Feat
    {
        public string Name;
        public string Description;
        public List<IFeatPrerequisite> Prerequisites;
        public List<FeatEffect> Effects;

        public void Apply(SimulatedCharacter character)
        {
            if (Effects == null) return;
            foreach (var effect in Effects)
                effect.Apply(character);
        }

        public void Remove(SimulatedCharacter character)
        {
            if (Effects == null) return;
            foreach (var effect in Effects)
                effect.Remove(character);
        }
    }

    public interface IFeatPrerequisite
    {
        bool IsMet(SimulatedCharacter character);
    }

    [Serializable]
    public class FeatEffect
    {
        public string Stat;
        public float Additive;
        public float Multiplicative;

        public void Apply(SimulatedCharacter character)
        {
            if (Math.Abs(Additive) > 0.0001f)
                character.Stats.ApplyAdditiveMod(Stat, Additive);
            if (Math.Abs(Multiplicative - 1f) > 0.0001f)
                character.Stats.ApplyMultiplicativeMod(Stat, Multiplicative);
        }

        public void Remove(SimulatedCharacter character)
        {
            if (Math.Abs(Additive) > 0.0001f)
                character.Stats.RemoveAdditiveMod(Stat, Additive);
            if (Math.Abs(Multiplicative - 1f) > 0.0001f)
                character.Stats.RemoveMultiplicativeMod(Stat, Multiplicative);
        }
    }
} 