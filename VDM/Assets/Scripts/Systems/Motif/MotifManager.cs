using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Systems.Events;

namespace VDM.Systems.Motif
{
    public enum MotifType
    {
        War,
        Famine,
        Plague,
        Prosperity,
        Festival,
        Migration,
        Discovery,
        Catastrophe,
        Peace,
        Revolution,
        TradeBoom,
        ReligiousAwakening,
        ArcaneSurge,
        PoliticalIntrigue,
        Exploration,
        CulturalRenaissance
    }

    public enum MotifEffect
    {
        NPCBehavior,
        EventFrequency,
        ResourceYield,
        RelationshipChange,
        ArcDevelopment,
        FactionTension,
        WeatherPattern,
        EconomicShift,
        NarrativeFlavor,
        Custom
    }

    [Serializable]
    public class Motif
    {
        public MotifType Type;
        public string Description;
        public int Intensity; // 1-7
        public int DurationDays;
        public List<MotifEffect> Effects = new List<MotifEffect>();
        public DateTime StartDate;
        public DateTime EndDate;
        public bool IsGlobal;
    }

    public class MotifManager : MonoBehaviour
    {
        public Motif GlobalMotif { get; private set; }
        public List<Motif> RegionalMotifs { get; private set; } = new List<Motif>();
        private System.Random rng = new System.Random();

        private static readonly Dictionary<MotifType, string> MotifDescriptions = new Dictionary<MotifType, string>
        {
            { MotifType.War, "A period of widespread conflict and strife." },
            { MotifType.Famine, "Scarcity of food and resources affects the land." },
            { MotifType.Plague, "Disease spreads rapidly among the population." },
            { MotifType.Prosperity, "Economic growth and abundance flourish." },
            { MotifType.Festival, "Celebrations and festivities uplift spirits." },
            { MotifType.Migration, "Large groups move across regions seeking new opportunities." },
            { MotifType.Discovery, "New lands, resources, or knowledge are uncovered." },
            { MotifType.Catastrophe, "Natural or magical disasters cause widespread upheaval." },
            { MotifType.Peace, "A rare time of harmony and stability." },
            { MotifType.Revolution, "Societal or political upheaval reshapes the world." },
            { MotifType.TradeBoom, "Trade routes thrive, bringing wealth and goods." },
            { MotifType.ReligiousAwakening, "Spiritual fervor and new beliefs spread." },
            { MotifType.ArcaneSurge, "Magical energies intensify, affecting all systems." },
            { MotifType.PoliticalIntrigue, "Schemes and secrets dominate the political landscape." },
            { MotifType.Exploration, "Adventurers and settlers push the boundaries of the known world." },
            { MotifType.CulturalRenaissance, "Art, science, and culture experience a golden age." }
        };

        public void InitializeGlobalMotif()
        {
            var motifType = (MotifType)rng.Next(Enum.GetValues(typeof(MotifType)).Length);
            GlobalMotif = new Motif
            {
                Type = motifType,
                Description = MotifDescriptions[motifType],
                Intensity = 7,
                DurationDays = rng.Next(18, 39), // 28 ± 10 days
                StartDate = DateTime.UtcNow,
                IsGlobal = true
            };
            var evt = new MotifChangedEvent { Motif = GlobalMotif.Type.ToString() };
            EventDispatcher.Instance.Dispatch(evt);
        }

        public void RotateRegionalMotifs(int regionCount)
        {
            RegionalMotifs.Clear();
            for (int i = 0; i < regionCount; i++)
            {
                var motifType = (MotifType)rng.Next(Enum.GetValues(typeof(MotifType)).Length);
                int intensity = rng.Next(1, 7);
                int duration = intensity * rng.Next(3, 7); // Duration proportional to intensity
                RegionalMotifs.Add(new Motif
                {
                    Type = motifType,
                    Description = MotifDescriptions[motifType],
                    Intensity = intensity,
                    DurationDays = duration,
                    StartDate = DateTime.UtcNow,
                    IsGlobal = false
                });
                var evt = new MotifChangedEvent { Motif = motifType.ToString() };
                EventDispatcher.Instance.Dispatch(evt);
            }
        }

        public void AdvanceDay()
        {
            if (GlobalMotif != null && (DateTime.UtcNow - GlobalMotif.StartDate).TotalDays >= GlobalMotif.DurationDays)
            {
                InitializeGlobalMotif();
            }
            for (int i = 0; i < RegionalMotifs.Count; i++)
            {
                var motif = RegionalMotifs[i];
                if ((DateTime.UtcNow - motif.StartDate).TotalDays >= motif.DurationDays)
                {
                    // Replace with new motif
                    var motifType = (MotifType)rng.Next(Enum.GetValues(typeof(MotifType)).Length);
                    int intensity = rng.Next(1, 7);
                    int duration = intensity * rng.Next(3, 7);
                    RegionalMotifs[i] = new Motif
                    {
                        Type = motifType,
                        Description = MotifDescriptions[motifType],
                        Intensity = intensity,
                        DurationDays = duration,
                        StartDate = DateTime.UtcNow,
                        IsGlobal = false
                    };
                }
            }
        }

        public void ApplyMotifEffects(Motif motif)
        {
            foreach (var effect in motif.Effects)
            {
                // Pseudocode: integrate with world state, NPCs, narrative
                switch (effect)
                {
                    case MotifEffect.NPCBehavior:
                        // Apply NPC behavior changes
                        break;
                    case MotifEffect.EventFrequency:
                        // Adjust event spawn rates
                        break;
                    case MotifEffect.ResourceYield:
                        // Modify resource production
                        break;
                    case MotifEffect.RelationshipChange:
                        // Affect relationship gain/loss
                        break;
                    case MotifEffect.ArcDevelopment:
                        // Influence arc/quest progression
                        break;
                    case MotifEffect.FactionTension:
                        // Modify faction tension
                        break;
                    case MotifEffect.WeatherPattern:
                        // Alter weather
                        break;
                    case MotifEffect.EconomicShift:
                        // Impact economy
                        break;
                    case MotifEffect.NarrativeFlavor:
                        // Add context for GPT/narrative
                        break;
                    case MotifEffect.Custom:
                        // Custom effect
                        break;
                }
            }
        }

        // Narrative hook: get current motif context for GPT or narrative systems
        public string GetMotifContext(bool global = true, int regionIndex = -1)
        {
            if (global && GlobalMotif != null)
                return $"Global Motif: {GlobalMotif.Type} - {GlobalMotif.Description} (Intensity: {GlobalMotif.Intensity})";
            if (!global && regionIndex >= 0 && regionIndex < RegionalMotifs.Count)
            {
                var motif = RegionalMotifs[regionIndex];
                return $"Regional Motif: {motif.Type} - {motif.Description} (Intensity: {motif.Intensity})";
            }
            return "No motif context available.";
        }
    }
} 