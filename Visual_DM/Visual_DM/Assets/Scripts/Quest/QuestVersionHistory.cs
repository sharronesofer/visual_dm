using System;
using System.Collections.Generic;

namespace Visual_DM.Quest
{
    /// <summary>
    /// Tracks the version history of a quest, supports diffs and rollback.
    /// </summary>
    public class QuestVersionHistory
    {
        private readonly List<QuestVersionEntry> _history = new List<QuestVersionEntry>();
        public IReadOnlyList<QuestVersionEntry> History => _history.AsReadOnly();

        public void AddVersion(Quest quest)
        {
            var entry = new QuestVersionEntry
            {
                Version = quest.Version,
                Title = quest.Title,
                Description = quest.Description,
                Timestamp = quest.UpdatedAt,
                State = quest.StateMachine.CurrentState
            };
            _history.Add(entry);
        }

        public QuestVersionEntry GetVersion(int version)
        {
            return _history.FindLast(e => e.Version == version);
        }

        public QuestVersionEntry GetLatestVersion()
        {
            return _history.Count > 0 ? _history[_history.Count - 1] : null;
        }

        public bool Rollback(Quest quest, int version)
        {
            var entry = GetVersion(version);
            if (entry == null) return false;
            quest.Title = entry.Title;
            quest.Description = entry.Description;
            quest.StateMachine.TryTransition(entry.State);
            quest.Version = entry.Version;
            quest.UpdatedAt = DateTime.UtcNow;
            return true;
        }
    }

    public class QuestVersionEntry
    {
        public int Version { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public DateTime Timestamp { get; set; }
        public QuestState State { get; set; }
    }
} 