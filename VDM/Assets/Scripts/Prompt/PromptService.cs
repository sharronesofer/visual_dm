using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

namespace VDM.Prompt
{
    /// <summary>
    /// Utility service that provides easy access to the most common prompt generation
    /// scenarios in the game. This wraps the PromptManager with domain-specific
    /// convenience methods for game systems.
    /// </summary>
    public static class PromptService
    {
        /// <summary>
        /// Generate an NPC with the specified parameters.
        /// </summary>
        /// <param name="role">The NPC's role in the world</param>
        /// <param name="importance">Importance level (minor, supporting, major)</param>
        /// <param name="settingType">Type of setting (e.g., "medieval fantasy")</param>
        /// <param name="additionalParams">Additional template parameters</param>
        /// <returns>The generated NPC description</returns>
        public static async Task<string> GenerateNPC(
            string role,
            string importance = "supporting",
            string settingType = "medieval fantasy",
            Dictionary<string, object> additionalParams = null)
        {
            var context = new Dictionary<string, object>
            {
                { "npc_role", role },
                { "importance", importance },
                { "setting_type", settingType }
            };
            
            if (additionalParams != null)
            {
                foreach (var param in additionalParams)
                {
                    context[param.Key] = param.Value;
                }
            }
            
            var response = await PromptManager.Instance.GenerateAsync("npc_generation", context);
            return response.Success ? response.Content : $"Failed to generate NPC: {response.Error}";
        }
        
        /// <summary>
        /// Generate an encounter for the specified parameters.
        /// </summary>
        /// <param name="partyLevel">Average party level</param>
        /// <param name="partySize">Number of party members</param>
        /// <param name="encounterType">Type of encounter (combat, social, puzzle, etc.)</param>
        /// <param name="difficulty">Encounter difficulty (easy, medium, hard, etc.)</param>
        /// <param name="settingType">Setting type (e.g., "dungeon", "forest")</param>
        /// <returns>The generated encounter description</returns>
        public static async Task<string> GenerateEncounter(
            int partyLevel,
            int partySize,
            string encounterType,
            string difficulty = "medium",
            string settingType = "dungeon")
        {
            string templateName = encounterType.ToLower() == "combat" ? "combat_encounter" : "encounter_generation";
            
            var context = new Dictionary<string, object>
            {
                { "party_level", partyLevel },
                { "party_size", partySize },
                { "encounter_type", encounterType },
                { "difficulty", difficulty },
                { "setting_type", settingType }
            };
            
            var response = await PromptManager.Instance.GenerateAsync(templateName, context);
            return response.Success ? response.Content : $"Failed to generate encounter: {response.Error}";
        }
        
        /// <summary>
        /// Generate dialogue for an NPC in response to a player action or dialogue.
        /// </summary>
        /// <param name="npcName">Name of the NPC</param>
        /// <param name="npcDescription">Brief description of the NPC</param>
        /// <param name="currentSituation">Current interaction context</param>
        /// <param name="playerDialogue">What the player said, if applicable</param>
        /// <param name="npcGoal">What the NPC wants in this interaction</param>
        /// <param name="previousDialogue">Previous conversation for continuity</param>
        /// <returns>The generated NPC dialogue response</returns>
        public static async Task<string> GenerateNPCDialogue(
            string npcName,
            string npcDescription,
            string currentSituation,
            string playerDialogue = null,
            string npcGoal = null,
            string previousDialogue = null)
        {
            var context = new Dictionary<string, object>
            {
                { "npc_name", npcName },
                { "npc_description", npcDescription },
                { "current_situation", currentSituation }
            };
            
            if (!string.IsNullOrEmpty(playerDialogue))
            {
                context["player_dialogue"] = playerDialogue;
            }
            
            if (!string.IsNullOrEmpty(npcGoal))
            {
                context["npc_goal"] = npcGoal;
            }
            
            if (!string.IsNullOrEmpty(previousDialogue))
            {
                context["previous_dialogue"] = previousDialogue;
            }
            
            var response = await PromptManager.Instance.GenerateAsync("npc_dialogue", context);
            return response.Success ? response.Content : $"Failed to generate dialogue: {response.Error}";
        }
        
        /// <summary>
        /// Generate a location description.
        /// </summary>
        /// <param name="locationType">Type of location (e.g., "tavern", "temple")</param>
        /// <param name="settingType">Setting type (e.g., "medieval fantasy")</param>
        /// <param name="mood">Mood or atmosphere (e.g., "tense", "mysterious")</param>
        /// <param name="timeOfDay">Time of day (e.g., "night", "morning")</param>
        /// <param name="additionalParams">Additional template parameters</param>
        /// <returns>The generated location description</returns>
        public static async Task<string> GenerateLocation(
            string locationType,
            string settingType = "medieval fantasy",
            string mood = null,
            string timeOfDay = null,
            Dictionary<string, object> additionalParams = null)
        {
            var context = new Dictionary<string, object>
            {
                { "location_type", locationType },
                { "setting_type", settingType }
            };
            
            if (!string.IsNullOrEmpty(mood))
            {
                context["mood"] = mood;
            }
            
            if (!string.IsNullOrEmpty(timeOfDay))
            {
                context["time_of_day"] = timeOfDay;
            }
            
            if (additionalParams != null)
            {
                foreach (var param in additionalParams)
                {
                    context[param.Key] = param.Value;
                }
            }
            
            var response = await PromptManager.Instance.GenerateAsync("location_generation", context);
            return response.Success ? response.Content : $"Failed to generate location: {response.Error}";
        }
        
        /// <summary>
        /// Generate a quest or quest hook.
        /// </summary>
        /// <param name="questType">Type of quest (e.g., "rescue", "retrieval")</param>
        /// <param name="partyLevel">Average party level</param>
        /// <param name="settingType">Setting type</param>
        /// <param name="questTheme">Theme or motif for the quest</param>
        /// <param name="hookOnly">Whether to generate just the hook or the full quest</param>
        /// <returns>The generated quest or quest hook</returns>
        public static async Task<string> GenerateQuest(
            string questType,
            int partyLevel,
            string settingType = "medieval fantasy",
            string questTheme = null,
            bool hookOnly = false)
        {
            string templateName = hookOnly ? "quest_hook" : "quest_generation";
            
            var context = new Dictionary<string, object>
            {
                { "quest_type", questType },
                { "party_level", partyLevel },
                { "setting_type", settingType }
            };
            
            if (!string.IsNullOrEmpty(questTheme))
            {
                context["quest_theme"] = questTheme;
            }
            
            var response = await PromptManager.Instance.GenerateAsync(templateName, context);
            return response.Success ? response.Content : $"Failed to generate quest: {response.Error}";
        }
        
        /// <summary>
        /// Generate a riddle or puzzle.
        /// </summary>
        /// <param name="difficulty">Difficulty level (easy, medium, hard)</param>
        /// <param name="theme">Theme or topic for the riddle/puzzle</param>
        /// <param name="settingType">Setting in which the puzzle appears</param>
        /// <param name="includeHints">Whether to include hints</param>
        /// <returns>The generated riddle or puzzle</returns>
        public static async Task<string> GenerateRiddle(
            string difficulty = "medium",
            string theme = null,
            string settingType = "dungeon",
            bool includeHints = true)
        {
            var context = new Dictionary<string, object>
            {
                { "difficulty", difficulty },
                { "setting_type", settingType },
                { "include_hints", includeHints }
            };
            
            if (!string.IsNullOrEmpty(theme))
            {
                context["theme"] = theme;
            }
            
            var response = await PromptManager.Instance.GenerateAsync("riddle", context);
            return response.Success ? response.Content : $"Failed to generate riddle: {response.Error}";
        }
        
        /// <summary>
        /// Generate a magic item.
        /// </summary>
        /// <param name="itemType">Type of item (e.g., "weapon", "armor", "wand")</param>
        /// <param name="rarity">Rarity level (common, uncommon, rare, etc.)</param>
        /// <param name="characterLevel">Level of characters the item is designed for</param>
        /// <param name="theme">Thematic element or power source</param>
        /// <returns>The generated magic item description</returns>
        public static async Task<string> GenerateMagicItem(
            string itemType,
            string rarity = "uncommon",
            int characterLevel = 5,
            string theme = null)
        {
            var context = new Dictionary<string, object>
            {
                { "item_type", itemType },
                { "rarity", rarity },
                { "character_level", characterLevel }
            };
            
            if (!string.IsNullOrEmpty(theme))
            {
                context["theme"] = theme;
            }
            
            var response = await PromptManager.Instance.GenerateAsync("magic_item", context);
            return response.Success ? response.Content : $"Failed to generate magic item: {response.Error}";
        }
        
        /// <summary>
        /// Generate a narrative description for a scene.
        /// </summary>
        /// <param name="location">Location where the scene takes place</param>
        /// <param name="timeConditions">Time of day and weather</param>
        /// <param name="presentCharacters">Characters present in the scene</param>
        /// <param name="mood">Mood or tone of the scene</param>
        /// <param name="recentEvents">Recent events affecting the scene</param>
        /// <returns>The generated scene description</returns>
        public static async Task<string> GenerateSceneDescription(
            string location,
            string timeConditions,
            string presentCharacters,
            string mood = null,
            string recentEvents = null)
        {
            var context = new Dictionary<string, object>
            {
                { "location", location },
                { "time_conditions", timeConditions },
                { "present_characters", presentCharacters }
            };
            
            if (!string.IsNullOrEmpty(mood))
            {
                context["mood"] = mood;
            }
            
            if (!string.IsNullOrEmpty(recentEvents))
            {
                context["recent_events"] = recentEvents;
            }
            
            var response = await PromptManager.Instance.GenerateAsync("scene_setting", context);
            return response.Success ? response.Content : $"Failed to generate scene description: {response.Error}";
        }
        
        /// <summary>
        /// Generate a rumor that players might hear.
        /// </summary>
        /// <param name="topic">Topic of the rumor</param>
        /// <param name="truthLevel">How true the rumor is (true, partial, false)</param>
        /// <param name="location">Where the rumor is being spread</param>
        /// <param name="sourceType">Type of source (e.g., "drunk patron", "merchant")</param>
        /// <returns>The generated rumor text</returns>
        public static async Task<string> GenerateRumor(
            string topic,
            string truthLevel = "partial",
            string location = null,
            string sourceType = null)
        {
            var context = new Dictionary<string, object>
            {
                { "topic", topic },
                { "truth_level", truthLevel }
            };
            
            if (!string.IsNullOrEmpty(location))
            {
                context["location"] = location;
            }
            
            if (!string.IsNullOrEmpty(sourceType))
            {
                context["source_type"] = sourceType;
            }
            
            var response = await PromptManager.Instance.GenerateAsync("rumor", context);
            return response.Success ? response.Content : $"Failed to generate rumor: {response.Error}";
        }
    }
} 