using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Simulation
{
    [Serializable]
    public class CharacterStats
    {
        // Core attributes
        public int Strength;
        public int Dexterity;
        public int Constitution;
        public int Intelligence;
        public int Wisdom;
        public int Charisma;

        // Derived stats
        public int MaxHP;
        public int ArmorClass;
        public int Initiative;
        public int Speed;

        // Modifiers (additive/multiplicative)
        private Dictionary<string, float> additiveMods = new Dictionary<string, float>();
        private Dictionary<string, float> multiplicativeMods = new Dictionary<string, float>();

        public CharacterStats(int str = 10, int dex = 10, int con = 10, int intel = 10, int wis = 10, int cha = 10)
        {
            Strength = str;
            Dexterity = dex;
            Constitution = con;
            Intelligence = intel;
            Wisdom = wis;
            Charisma = cha;
            RecalculateDerivedStats();
        }

        public void ApplyAdditiveMod(string stat, float value)
        {
            if (!additiveMods.ContainsKey(stat)) additiveMods[stat] = 0f;
            additiveMods[stat] += value;
            RecalculateDerivedStats();
        }

        public void ApplyMultiplicativeMod(string stat, float value)
        {
            if (!multiplicativeMods.ContainsKey(stat)) multiplicativeMods[stat] = 1f;
            multiplicativeMods[stat] *= value;
            RecalculateDerivedStats();
        }

        public void RemoveAdditiveMod(string stat, float value)
        {
            if (additiveMods.ContainsKey(stat))
            {
                additiveMods[stat] -= value;
                if (Mathf.Abs(additiveMods[stat]) < 0.0001f) additiveMods.Remove(stat);
                RecalculateDerivedStats();
            }
        }

        public void RemoveMultiplicativeMod(string stat, float value)
        {
            if (multiplicativeMods.ContainsKey(stat))
            {
                multiplicativeMods[stat] /= value;
                if (Mathf.Abs(multiplicativeMods[stat] - 1f) < 0.0001f) multiplicativeMods.Remove(stat);
                RecalculateDerivedStats();
            }
        }

        public int GetStat(string stat)
        {
            int baseValue = stat switch
            {
                "Strength" => Strength,
                "Dexterity" => Dexterity,
                "Constitution" => Constitution,
                "Intelligence" => Intelligence,
                "Wisdom" => Wisdom,
                "Charisma" => Charisma,
                _ => 0
            };
            float add = additiveMods.ContainsKey(stat) ? additiveMods[stat] : 0f;
            float mult = multiplicativeMods.ContainsKey(stat) ? multiplicativeMods[stat] : 1f;
            return Mathf.RoundToInt((baseValue + add) * mult);
        }

        public void RecalculateDerivedStats()
        {
            MaxHP = 10 + GetStat("Constitution") * 2;
            ArmorClass = 10 + Mathf.FloorToInt(GetStat("Dexterity") / 2f);
            Initiative = GetStat("Dexterity");
            Speed = 30 + Mathf.FloorToInt(GetStat("Dexterity") / 2f);
        }

        public CharacterStats Clone()
        {
            var clone = new CharacterStats(Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma);
            foreach (var kv in additiveMods) clone.additiveMods[kv.Key] = kv.Value;
            foreach (var kv in multiplicativeMods) clone.multiplicativeMods[kv.Key] = kv.Value;
            clone.RecalculateDerivedStats();
            return clone;
        }
    }
} 