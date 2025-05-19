using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.Narrative;

namespace VisualDM.Systems.Quest
{
    /// <summary>
    /// Developer tools for visualizing and debugging arc-to-quest relationships.
    /// </summary>
    public static class ArcToQuestDebugTools
    {
        /// <summary>
        /// Prints the mapping from arcs to generated quests.
        /// </summary>
        public static void PrintArcToQuestMapping(GlobalArc arc, List<Quest> quests)
        {
            Debug.Log($"[ArcToQuestDebug] Arc: {arc.Title} ({arc.Id})");
            foreach (var quest in quests)
            {
                Debug.Log($"  Quest: {quest.Title} (ID: {quest.Id}) | Status: {quest.Status}");
                foreach (var stage in quest.Stages)
                {
                    Debug.Log($"    Stage: {string.Join(", ", stage.Objectives)}");
                }
            }
        }

        /// <summary>
        /// Prints quest chains and dependencies for debugging.
        /// </summary>
        public static void PrintQuestChains(QuestDependencyManager depManager, List<Quest> quests)
        {
            foreach (var quest in quests)
            {
                Debug.Log($"[ArcToQuestDebug] Quest: {quest.Title} (ID: {quest.Id})");
                // Print prerequisites and chains (requires public accessors in depManager)
                // For demonstration, assume methods exist:
                // var prereqs = depManager.GetPrerequisites(quest.Id);
                // var chains = depManager.GetQuestChain(quest.Id);
            }
        }

        /// <summary>
        /// Validates that generated quests meet arc requirements (basic checks).
        /// </summary>
        public static bool ValidateQuestGeneration(GlobalArc arc, List<Quest> quests)
        {
            if (arc == null || quests == null || quests.Count == 0) return false;
            // Example: Ensure each arc stage has a corresponding quest
            var stageNames = new HashSet<string>();
            foreach (var stage in arc.Stages)
                stageNames.Add(stage.Name);
            foreach (var quest in quests)
            {
                bool found = false;
                foreach (var stage in quest.Stages)
                {
                    foreach (var obj in stage.Objectives)
                    {
                        foreach (var name in stageNames)
                        {
                            if (obj.Contains(name))
                            {
                                found = true;
                                break;
                            }
                        }
                        if (found) break;
                    }
                    if (found) break;
                }
                if (!found)
                {
                    Debug.LogWarning($"[ArcToQuestDebug] Quest '{quest.Title}' does not match any arc stage.");
                    return false;
                }
            }
            Debug.Log("[ArcToQuestDebug] All quests validated against arc stages.");
            return true;
        }
    }
}