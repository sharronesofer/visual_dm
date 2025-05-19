using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.EventSystem;

namespace VisualDM.Systems.FeatHistory
{
    public class FeatEventTracker : MonoBehaviour
    {
        public static FeatEventTracker Instance { get; private set; }

        private Queue<FeatAchievementEvent> eventBuffer = new Queue<FeatAchievementEvent>();
        private FeatHistoryDatabase database;
        private float flushInterval = 1.0f; // seconds
        private float flushTimer = 0f;
        private bool initialized = false;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(this);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Initialize();
        }

        private void Initialize()
        {
            if (initialized) return;
            string dbPath = Application.persistentDataPath + "/feat_history.json";
            database = new FeatHistoryDatabase(dbPath);
            initialized = true;
        }

        private void Update()
        {
            flushTimer += Time.deltaTime;
            if (flushTimer >= flushInterval)
            {
                FlushBuffer();
                flushTimer = 0f;
            }
        }

        public void RecordFeatAcquisition(string characterId, string featId, CharacterSnapshot snapshot, string context = "")
        {
            try
            {
                var featEvent = new FeatAchievementEvent
                {
                    Id = Guid.NewGuid().ToString(),
                    CharacterId = characterId,
                    FeatId = featId,
                    Timestamp = DateTime.UtcNow,
                    CharacterLevel = snapshot.Level,
                    StatsSnapshot = snapshot,
                    Context = context
                };
                eventBuffer.Enqueue(featEvent);
                var progressionEvent = new FeatProgressionEvent(
                    characterId,
                    featId,
                    snapshot.Level,
                    featEvent.Timestamp
                );
                EventBus.Instance.Publish(progressionEvent);
                Debug.Log($"[FeatEventTracker] Queued feat acquisition: {featId} for character {characterId} (event-driven)");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[FeatEventTracker] Error recording feat acquisition: {ex.Message}");
            }
        }

        public void FlushBuffer()
        {
            while (eventBuffer.Count > 0)
            {
                var featEvent = eventBuffer.Dequeue();
                try
                {
                    database.AddEvent(featEvent);
                    Debug.Log($"[FeatEventTracker] Flushed feat event: {featEvent.Id}");
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[FeatEventTracker] Error saving feat event: {ex.Message}");
                    // Optionally re-enqueue or handle failed writes
                }
            }
        }

        public List<FeatAchievementEvent> GetHistoryForCharacter(string characterId)
        {
            return database.GetEventsForCharacter(characterId);
        }

        public void PruneOldEvents()
        {
            database.PruneOldEvents();
        }
    }
} 