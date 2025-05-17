using System;
using System.Collections.Generic;

namespace AI
{
    public class TemplateRepository
    {
        private readonly Dictionary<string, List<PromptTemplate>> _categoryMap = new Dictionary<string, List<PromptTemplate>>();
        private readonly Dictionary<string, List<PromptTemplate>> _tagMap = new Dictionary<string, List<PromptTemplate>>();
        private readonly Dictionary<string, PromptTemplate> _idMap = new Dictionary<string, PromptTemplate>();
        private readonly HashSet<PromptTemplate> _cache = new HashSet<PromptTemplate>();
        private const int CacheSize = 20;

        public void AddTemplate(string id, string category, List<string> tags, PromptTemplate template)
        {
            _idMap[id] = template;
            if (!_categoryMap.ContainsKey(category)) _categoryMap[category] = new List<PromptTemplate>();
            _categoryMap[category].Add(template);
            foreach (var tag in tags)
            {
                if (!_tagMap.ContainsKey(tag)) _tagMap[tag] = new List<PromptTemplate>();
                _tagMap[tag].Add(template);
            }
            AddToCache(template);
        }

        public void RemoveTemplate(string id)
        {
            if (_idMap.TryGetValue(id, out var template))
            {
                foreach (var list in _categoryMap.Values) list.Remove(template);
                foreach (var list in _tagMap.Values) list.Remove(template);
                _idMap.Remove(id);
                _cache.Remove(template);
            }
        }

        public PromptTemplate GetTemplateById(string id)
        {
            if (_idMap.TryGetValue(id, out var template))
            {
                AddToCache(template);
                return template;
            }
            return null;
        }

        public List<PromptTemplate> GetTemplatesByCategory(string category)
        {
            return _categoryMap.TryGetValue(category, out var list) ? new List<PromptTemplate>(list) : new List<PromptTemplate>();
        }

        public List<PromptTemplate> GetTemplatesByTag(string tag)
        {
            return _tagMap.TryGetValue(tag, out var list) ? new List<PromptTemplate>(list) : new List<PromptTemplate>();
        }

        private void AddToCache(PromptTemplate template)
        {
            if (_cache.Count >= CacheSize)
            {
                // Remove oldest (not LRU, but simple for now)
                var enumerator = _cache.GetEnumerator();
                if (enumerator.MoveNext()) _cache.Remove(enumerator.Current);
            }
            _cache.Add(template);
        }

        // Serialization/deserialization stubs for persistence
        public void SaveToDisk(string path) { /* TODO: Implement */ }
        public void LoadFromDisk(string path) { /* TODO: Implement */ }
    }
} 