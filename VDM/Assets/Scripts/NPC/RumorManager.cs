using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using UnityEngine;

namespace VDM.NPC
{
    /// <summary>
    /// Singleton manager for all active rumors in the game world.
    /// </summary>
    public class RumorManager : MonoBehaviour
    {
        public static RumorManager Instance { get; private set; }
        public List<RumorData> ActiveRumors { get; private set; } = new List<RumorData>();

        private string SavePath => Path.Combine(Application.persistentDataPath, "rumors.json");

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(this);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        /// <summary>
        /// Add a new rumor to the system.
        /// </summary>
        public void AddRumor(RumorData rumor)
        {
            ActiveRumors.Add(rumor);
        }

        /// <summary>
        /// Remove a rumor from the system.
        /// </summary>
        public void RemoveRumor(RumorData rumor)
        {
            ActiveRumors.Remove(rumor);
        }

        /// <summary>
        /// Find all rumors from a specific NPC.
        /// </summary>
        public List<RumorData> FindRumorsBySource(int npcId)
        {
            return ActiveRumors.Where(r => r.SourceNpcId == npcId).ToList();
        }

        /// <summary>
        /// Find all rumors of a specific category.
        /// </summary>
        public List<RumorData> FindRumorsByCategory(RumorCategory category)
        {
            return ActiveRumors.Where(r => r.Category == category).ToList();
        }

        /// <summary>
        /// Save all rumors to a JSON file.
        /// </summary>
        public void SaveRumors()
        {
            var json = JsonSerializer.Serialize(ActiveRumors);
            File.WriteAllText(SavePath, json);
        }

        /// <summary>
        /// Load rumors from a JSON file.
        /// </summary>
        public void LoadRumors()
        {
            if (!File.Exists(SavePath)) return;
            var json = File.ReadAllText(SavePath);
            ActiveRumors = JsonSerializer.Deserialize<List<RumorData>>(json) ?? new List<RumorData>();
        }
    }
} 