using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using Newtonsoft.Json;

namespace VisualDM.Systems.FeatHistory
{
    public class FeatHistoryDatabase
    {
        private readonly string dbFilePath;
        private List<FeatAchievementEvent> events;
        private Dictionary<string, List<FeatAchievementEvent>> eventsByCharacter;
        private readonly int retentionDays = 365; // Example retention policy

        public FeatHistoryDatabase(string filePath)
        {
            dbFilePath = filePath;
            Load();
        }

        private void Load()
        {
            if (File.Exists(dbFilePath))
            {
                var json = File.ReadAllText(dbFilePath);
                events = JsonConvert.DeserializeObject<List<FeatAchievementEvent>>(json) ?? new List<FeatAchievementEvent>();
            }
            else
            {
                events = new List<FeatAchievementEvent>();
            }
            IndexEvents();
        }

        private void Save()
        {
            var json = JsonConvert.SerializeObject(events, Formatting.Indented);
            File.WriteAllText(dbFilePath, json);
        }

        private void IndexEvents()
        {
            eventsByCharacter = events
                .GroupBy(e => e.CharacterId)
                .ToDictionary(g => g.Key, g => g.OrderBy(ev => ev.Timestamp).ToList());
        }

        public void AddEvent(FeatAchievementEvent featEvent)
        {
            events.Add(featEvent);
            if (!eventsByCharacter.ContainsKey(featEvent.CharacterId))
                eventsByCharacter[featEvent.CharacterId] = new List<FeatAchievementEvent>();
            eventsByCharacter[featEvent.CharacterId].Add(featEvent);
            eventsByCharacter[featEvent.CharacterId] = eventsByCharacter[featEvent.CharacterId].OrderBy(e => e.Timestamp).ToList();
            Save();
        }

        public List<FeatAchievementEvent> GetEventsForCharacter(string characterId)
        {
            return eventsByCharacter.ContainsKey(characterId)
                ? new List<FeatAchievementEvent>(eventsByCharacter[characterId])
                : new List<FeatAchievementEvent>();
        }

        public List<FeatAchievementEvent> QueryEvents(DateTime? from = null, DateTime? to = null)
        {
            return events.Where(e => (!from.HasValue || e.Timestamp >= from.Value) && (!to.HasValue || e.Timestamp <= to.Value)).ToList();
        }

        public void PruneOldEvents()
        {
            var cutoff = DateTime.UtcNow.AddDays(-retentionDays);
            events = events.Where(e => e.Timestamp >= cutoff).ToList();
            IndexEvents();
            Save();
        }
    }
} 