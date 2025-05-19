using System;
using System.Collections.Generic;
using System.Linq;
using VisualDM.Systems.Narrative;
using VisualDM.World;
using VisualDM.Systems.EventSystem;
using VisualDM.Systems.MotifSystem;

namespace VisualDM.Systems.Narrative
{
    /// <summary>
    /// Singleton manager for global narrative arcs, cross-region quest state, and world event triggers.
    /// </summary>
    public class GlobalArcManager
    {
        private static GlobalArcManager _instance;
        public static GlobalArcManager Instance => _instance ??= new GlobalArcManager();

        // Registry of all global arcs
        private readonly Dictionary<string, GlobalArc> _globalArcs = new();
        // Mapping: global arc ID -> list of spawned regional arcs
        private readonly Dictionary<string, List<RegionalArc>> _regionalArcsByGlobal = new();
        // Cross-region quest state cache (questId -> state)
        private readonly Dictionary<string, object> _crossRegionQuestState = new();
        // Global narrative context
        public GlobalNarrativeContext NarrativeContext { get; private set; } = new GlobalNarrativeContext();

        private GlobalArcManager() { }

        // --- Registration APIs ---
        public void RegisterGlobalArc(GlobalArc arc)
        {
            if (!_globalArcs.ContainsKey(arc.Id))
                _globalArcs[arc.Id] = arc;
        }

        public void UnregisterGlobalArc(string arcId)
        {
            _globalArcs.Remove(arcId);
            _regionalArcsByGlobal.Remove(arcId);
        }

        public void RegisterRegionalArc(string globalArcId, RegionalArc regionalArc)
        {
            if (!_regionalArcsByGlobal.ContainsKey(globalArcId))
                _regionalArcsByGlobal[globalArcId] = new List<RegionalArc>();
            if (!_regionalArcsByGlobal[globalArcId].Contains(regionalArc))
                _regionalArcsByGlobal[globalArcId].Add(regionalArc);
        }

        public IEnumerable<GlobalArc> GetAllGlobalArcs() => _globalArcs.Values;
        public IEnumerable<RegionalArc> GetRegionalArcsForGlobal(string globalArcId) =>
            _regionalArcsByGlobal.TryGetValue(globalArcId, out var list) ? list : Enumerable.Empty<RegionalArc>();

        // --- Cross-Region Quest State Synchronization ---
        public void SyncQuestState(string questId, object state)
        {
            _crossRegionQuestState[questId] = state;
            // Propagate to all relevant regions (stub: actual propagation logic needed)
            EventBus.Instance.Publish(new CrossRegionQuestStateChangedEvent(questId, state));
        }

        public object GetQuestState(string questId)
        {
            _crossRegionQuestState.TryGetValue(questId, out var state);
            return state;
        }

        // --- World Event Triggers & Cascades ---
        public void TriggerWorldEvent(string eventType, Dictionary<string, object> payload = null)
        {
            // Broadcast world event
            var evt = new WorldEventTriggerEvent(eventType, payload);
            EventBus.Instance.Publish(evt);
            // Cascade to all regional arcs (stub: actual cascade logic needed)
            foreach (var regionalList in _regionalArcsByGlobal.Values)
            {
                foreach (var regionalArc in regionalList)
                {
                    regionalArc.TriggerRegionNarrativeEvent(RegionSystemLocator.Instance.RegionSystem, eventType);
                }
            }
        }

        // --- Conflict Resolution Protocols ---
        public void ResolveStateConflict(string questId, object newState, Func<object, object, object> resolver)
        {
            var current = GetQuestState(questId);
            var resolved = resolver(current, newState);
            SyncQuestState(questId, resolved);
        }

        // --- Motif Integration ---
        public void IntegrateMotif(GlobalArc arc, Motif motif)
        {
            // Example: update arc metadata for motif
            arc.Metadata.Theme = motif?.Theme;
            arc.Metadata.Intensity = motif?.Intensity ?? 0;
        }

        // --- Narrative Context Tracking ---
        public void UpdateNarrativeContext(string playerId, string arcId, int stageIndex)
        {
            NarrativeContext.UpdateProgression(playerId, arcId, stageIndex);
        }
    }

    /// <summary>
    /// Tracks player progression through multi-region/global storylines.
    /// </summary>
    public class GlobalNarrativeContext
    {
        // playerId -> (arcId -> stageIndex)
        private readonly Dictionary<string, Dictionary<string, int>> _progression = new();

        public void UpdateProgression(string playerId, string arcId, int stageIndex)
        {
            if (!_progression.ContainsKey(playerId))
                _progression[playerId] = new Dictionary<string, int>();
            _progression[playerId][arcId] = stageIndex;
        }

        public int? GetProgression(string playerId, string arcId)
        {
            if (_progression.TryGetValue(playerId, out var arcs) && arcs.TryGetValue(arcId, out var idx))
                return idx;
            return null;
        }
    }

    /// <summary>
    /// Event for cross-region quest state changes.
    /// </summary>
    public class CrossRegionQuestStateChangedEvent : GameEvent
    {
        public string QuestId { get; }
        public object State { get; }
        public CrossRegionQuestStateChangedEvent(string questId, object state)
        {
            QuestId = questId;
            State = state;
        }
    }

    /// <summary>
    /// Event for world event triggers.
    /// </summary>
    public class WorldEventTriggerEvent : GameEvent
    {
        public string EventType { get; }
        public Dictionary<string, object> Payload { get; }
        public WorldEventTriggerEvent(string eventType, Dictionary<string, object> payload = null)
        {
            EventType = eventType;
            Payload = payload;
        }
    }

    // Utility for region system access (runtime only)
    public static class RegionSystemLocator
    {
        public static RegionSystem Instance { get; set; }
    }
} 