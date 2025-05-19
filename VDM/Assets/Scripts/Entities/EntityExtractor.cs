using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace VisualDM.Entities
{
    public class EntityExtractor
    {
        public List<string> ExtractNPCs(string text)
        {
            // Example: extract capitalized words after "NPC" or "character"
            var npcs = new List<string>();
            var matches = Regex.Matches(text, @"(?:NPC|character) ([A-Z][a-zA-Z0-9_]*)");
            foreach (Match match in matches)
                npcs.Add(Normalize(match.Groups[1].Value));
            return npcs;
        }

        public List<string> ExtractLocations(string text)
        {
            // Example: extract capitalized words after "in" or "at"
            var locations = new List<string>();
            var matches = Regex.Matches(text, @"(?:in|at) ([A-Z][a-zA-Z0-9_]*)");
            foreach (Match match in matches)
                locations.Add(Normalize(match.Groups[1].Value));
            return locations;
        }

        public List<string> ExtractItems(string text)
        {
            // Example: extract words after "item" or "collect"
            var items = new List<string>();
            var matches = Regex.Matches(text, @"(?:item|collect) ([a-zA-Z0-9_]+)");
            foreach (Match match in matches)
                items.Add(Normalize(match.Groups[1].Value));
            return items;
        }

        public string Normalize(string entity)
        {
            // Simple normalization: trim, lower, remove underscores
            return entity.Trim().Replace("_", " ").ToLowerInvariant();
        }

        // Add relationship mapping and context-aware resolution as needed
    }
} 