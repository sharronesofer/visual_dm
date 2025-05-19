using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.NPC.MotifSystem
{
    public class MotifDialogueProvider
    {
        [Serializable]
        public class DialogueOption
        {
            public string Text;
            public List<string> RequiredMotifs;
            public float Weight;
            public DialogueOption(string text, List<string> requiredMotifs = null, float weight = 1f)
            {
                Text = text;
                RequiredMotifs = requiredMotifs ?? new List<string>();
                Weight = weight;
            }
        }

        private Dictionary<string, List<DialogueOption>> motifDialogueTemplates = new Dictionary<string, List<DialogueOption>>();
        private Dictionary<string, List<DialogueOption>> dialogueCache = new Dictionary<string, List<DialogueOption>>();

        public void RegisterMotifDialogue(string motifName, DialogueOption option)
        {
            if (!motifDialogueTemplates.ContainsKey(motifName))
                motifDialogueTemplates[motifName] = new List<DialogueOption>();
            motifDialogueTemplates[motifName].Add(option);
        }

        public List<DialogueOption> GetDialogueOptions(Vector2 npcLocation)
        {
            var activeMotifs = MotifManager.Instance.GetMotifsAffectingLocation(npcLocation);
            string cacheKey = string.Join("|", activeMotifs.ConvertAll(m => m.Name));
            if (dialogueCache.TryGetValue(cacheKey, out var cached))
                return cached;

            var options = new List<DialogueOption>();
            foreach (var motif in activeMotifs)
            {
                if (motifDialogueTemplates.TryGetValue(motif.Name, out var motifOptions))
                {
                    foreach (var opt in motifOptions)
                    {
                        // Check motif requirements
                        bool valid = true;
                        foreach (var req in opt.RequiredMotifs)
                        {
                            if (!activeMotifs.Exists(m => m.Name == req))
                            {
                                valid = false;
                                break;
                            }
                        }
                        if (valid)
                        {
                            // Template substitution (e.g., {MOTIF_NAME})
                            string text = opt.Text.Replace("{MOTIF_NAME}", motif.Name);
                            options.Add(new DialogueOption(text, opt.RequiredMotifs, opt.Weight));
                        }
                    }
                }
            }
            // Fallback: generic dialogue if no motif-specific
            if (options.Count == 0 && motifDialogueTemplates.TryGetValue("default", out var defaultOptions))
                options.AddRange(defaultOptions);

            dialogueCache[cacheKey] = options;
            return options;
        }

        public DialogueOption GetWeightedDialogueOption(Vector2 npcLocation)
        {
            var options = GetDialogueOptions(npcLocation);
            if (options.Count == 0) return null;
            float totalWeight = 0f;
            foreach (var opt in options) totalWeight += opt.Weight;
            float r = UnityEngine.Random.value * totalWeight;
            float acc = 0f;
            foreach (var opt in options)
            {
                acc += opt.Weight;
                if (r <= acc) return opt;
            }
            return options[0];
        }
    }
} 