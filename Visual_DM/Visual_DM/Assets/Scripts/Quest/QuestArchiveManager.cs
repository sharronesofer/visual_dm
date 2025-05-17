using System;
using System.Collections.Generic;

namespace Visual_DM.Quest
{
    /// <summary>
    /// Manages archiving and restoration of completed quests, with data retention policies.
    /// </summary>
    public class QuestArchiveManager
    {
        private readonly Dictionary<string, Quest> _archivedQuests = new Dictionary<string, Quest>();
        private readonly TimeSpan _retentionPeriod;

        public QuestArchiveManager(TimeSpan? retentionPeriod = null)
        {
            _retentionPeriod = retentionPeriod ?? TimeSpan.FromDays(365);
        }

        public void ArchiveQuest(Quest quest)
        {
            if (!_archivedQuests.ContainsKey(quest.QuestId))
            {
                _archivedQuests[quest.QuestId] = quest;
            }
        }

        public bool RestoreQuest(string questId, out Quest quest)
        {
            if (_archivedQuests.TryGetValue(questId, out quest))
            {
                _archivedQuests.Remove(questId);
                return true;
            }
            quest = null;
            return false;
        }

        public void PurgeExpiredArchives()
        {
            var now = DateTime.UtcNow;
            var toRemove = new List<string>();
            foreach (var kvp in _archivedQuests)
            {
                if (kvp.Value.UpdatedAt + _retentionPeriod < now)
                    toRemove.Add(kvp.Key);
            }
            foreach (var key in toRemove)
                _archivedQuests.Remove(key);
        }

        public bool IsArchived(string questId)
        {
            return _archivedQuests.ContainsKey(questId);
        }
    }
} 