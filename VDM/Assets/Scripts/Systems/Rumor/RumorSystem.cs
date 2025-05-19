using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Systems.Events;

namespace VDM.Systems.Rumor
{
    public enum RumorType
    {
        Scandal,
        Secret,
        Prophecy,
        Discovery,
        Catastrophe,
        Miracle,
        Betrayal,
        Romance,
        Treasure,
        Monster,
        Political,
        Economic,
        Invention,
        Disappearance,
        Uprising
    }

    // Canonical rumor types:
    // Scandal, Secret, Prophecy, Discovery, Catastrophe, Miracle, Betrayal, Romance, Treasure, Monster, Political, Economic, Invention, Disappearance, Uprising
    [Serializable]
    public class Rumor
    {
        public RumorType Type;
        public string Content;
        public float TruthValue; // 0.0 (false) to 1.0 (true)
        public int Severity; // 1-5
        public string Category;
        public int SpreadCount;
        public float Believability; // 0.0-1.0, per entity
        public DateTime CreatedAt;
        public DateTime LastSpreadAt;
        // Extend with additional fields as needed
    }

    public class RumorSystem : MonoBehaviour
    {
        public List<Rumor> ActiveRumors { get; private set; } = new List<Rumor>();
        private System.Random rng = new System.Random();
        private const float MutationRate = 0.2f;
        private const float DecayRate = 0.05f; // per day

        private static readonly Dictionary<RumorType, string> RumorTypeDescriptions = new Dictionary<RumorType, string>
        {
            { RumorType.Scandal, "Gossip about personal or political misdeeds" },
            { RumorType.Secret, "Hidden information, often with high stakes" },
            { RumorType.Prophecy, "Predictions about future events" },
            { RumorType.Discovery, "News of new lands, resources, or inventions" },
            { RumorType.Catastrophe, "Warnings of disaster, war, or plague" },
            { RumorType.Miracle, "Reports of supernatural or miraculous events" },
            { RumorType.Betrayal, "Accusations of treachery or broken trust" },
            { RumorType.Romance, "Tales of love affairs or forbidden relationships" },
            { RumorType.Treasure, "Hints of hidden wealth or valuable items" },
            { RumorType.Monster, "Sightings or rumors of dangerous creatures" },
            { RumorType.Political, "Shifts in power, alliances, or intrigue" },
            { RumorType.Economic, "Market crashes, booms, or trade opportunities" },
            { RumorType.Invention, "New technologies or magical discoveries" },
            { RumorType.Disappearance, "Missing persons or unexplained vanishings" },
            { RumorType.Uprising, "Rebellions, revolts, or civil unrest" }
        };

        public void SpreadRumor(Rumor rumor, List<int> recipientIds)
        {
            foreach (var recipientId in recipientIds)
            {
                var mutatedRumor = rng.NextDouble() < MutationRate ? MutateRumor(rumor) : rumor;
                // Simulate believability update (stub: could be per-entity)
                mutatedRumor.Believability = Mathf.Clamp01(mutatedRumor.Believability + (float)rng.NextDouble() * 0.1f);
                mutatedRumor.SpreadCount++;
                mutatedRumor.LastSpreadAt = DateTime.UtcNow;
                // In a real system, deliver to recipient's memory/rumor log here
                var evt = new RumorSpreadEvent { Content = mutatedRumor.Content };
                EventDispatcher.Instance.Dispatch(evt);
            }
        }

        public Rumor MutateRumor(Rumor original)
        {
            var mutated = new Rumor
            {
                Type = original.Type,
                Content = MutateContent(original.Content),
                TruthValue = Mathf.Clamp01(original.TruthValue + ((float)rng.NextDouble() - 0.5f) * 0.2f),
                Severity = Mathf.Clamp(original.Severity + rng.Next(-1, 2), 1, 5),
                Category = original.Category,
                SpreadCount = original.SpreadCount,
                Believability = original.Believability,
                CreatedAt = original.CreatedAt,
                LastSpreadAt = DateTime.UtcNow
            };
            return mutated;
        }

        private string MutateContent(string content)
        {
            // Simple mutation: add a random adjective (stub)
            string[] adjectives = { "shocking", "unconfirmed", "ancient", "mysterious", "urgent", "secret" };
            if (rng.NextDouble() < 0.5)
                return content + " (" + adjectives[rng.Next(adjectives.Length)] + ")";
            return content;
        }

        public void DecayRumors()
        {
            for (int i = ActiveRumors.Count - 1; i >= 0; i--)
            {
                var rumor = ActiveRumors[i];
                rumor.Believability = Mathf.Max(0f, rumor.Believability - DecayRate);
                if (rumor.Believability <= 0.01f && rumor.SpreadCount > 0)
                {
                    ActiveRumors.RemoveAt(i);
                }
            }
        }

        // Narrative hook: get current rumor context for GPT or narrative systems
        public string GetRumorContext()
        {
            if (ActiveRumors.Count == 0) return "No active rumors.";
            var rumor = ActiveRumors[rng.Next(ActiveRumors.Count)];
            return $"Rumor: {rumor.Type} - {rumor.Content} (Believability: {rumor.Believability:F2})";
        }
    }
} 