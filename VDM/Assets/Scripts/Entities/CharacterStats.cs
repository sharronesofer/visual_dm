using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Entities
{
    // Forward declare CharacterEncumbrance if not already defined
    public class CharacterEncumbrance; // Forward declaration

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

        public CharacterEncumbrance Encumbrance = new CharacterEncumbrance();

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

        /// <summary>
        /// Applies encumbrance effects to movement speed and stamina drain based on encumbrance percent (0-1).
        /// </summary>
        /// <param name="encumbrancePercent">Current encumbrance as a percent of max weight (0-1).</param>
        /// <returns>Tuple of (speedMultiplier, staminaMultiplier)</returns>
        public (float speedMultiplier, float staminaMultiplier) ApplyEncumbranceEffects(float encumbrancePercent)
        {
            float speedMult = Encumbrance.GetSpeedMultiplier(encumbrancePercent);
            float staminaMult = Encumbrance.GetStaminaMultiplier(encumbrancePercent);
            return (speedMult, staminaMult);
        }
    }

    public enum EncumbranceLevel
    {
        Unencumbered,
        Encumbered,
        HeavilyEncumbered
    }

    public class CharacterEncumbrance
    {
        // Thresholds as percent of MaxWeight
        public float EncumberedThreshold = 0.5f; // 50%
        public float HeavilyEncumberedThreshold = 0.8f; // 80%

        // Movement speed multipliers
        public float UnencumberedSpeedMult = 1.0f;
        public float EncumberedSpeedMult = 0.75f;
        public float HeavilyEncumberedSpeedMult = 0.5f;

        // Stamina drain multipliers
        public float UnencumberedStaminaMult = 1.0f;
        public float EncumberedStaminaMult = 1.5f;
        public float HeavilyEncumberedStaminaMult = 2.0f;

        public EncumbranceLevel GetLevel(float encumbrancePercent)
        {
            if (encumbrancePercent >= HeavilyEncumberedThreshold) return EncumbranceLevel.HeavilyEncumbered;
            if (encumbrancePercent >= EncumberedThreshold) return EncumbranceLevel.Encumbered;
            return EncumbranceLevel.Unencumbered;
        }

        public float GetSpeedMultiplier(float encumbrancePercent)
        {
            var level = GetLevel(encumbrancePercent);
            return level switch
            {
                EncumbranceLevel.Unencumbered => UnencumberedSpeedMult,
                EncumbranceLevel.Encumbered => EncumberedSpeedMult,
                EncumbranceLevel.HeavilyEncumbered => HeavilyEncumberedSpeedMult,
                _ => 1.0f
            };
        }

        public float GetStaminaMultiplier(float encumbrancePercent)
        {
            var level = GetLevel(encumbrancePercent);
            return level switch
            {
                EncumbranceLevel.Unencumbered => UnencumberedStaminaMult,
                EncumbranceLevel.Encumbered => EncumberedStaminaMult,
                EncumbranceLevel.HeavilyEncumbered => HeavilyEncumberedStaminaMult,
                _ => 1.0f
            };
        }
    }
} 