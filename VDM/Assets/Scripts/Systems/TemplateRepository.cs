using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using System.Text.Json;

namespace VisualDM.AI
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
            if (string.IsNullOrWhiteSpace(id) || template == null)
            {
                Debug.LogError("Invalid template or id.");
                return;
            }
            _idMap[id] = template;
            if (!_categoryMap.ContainsKey(category)) _categoryMap[category] = new List<PromptTemplate>();
            _categoryMap[category].Add(template);
            foreach (var tag in tags ?? new List<string>())
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

        public void SaveToDisk(string path)
        {
            try
            {
                var data = new TemplateRepoData
                {
                    IdMap = _idMap,
                    CategoryMap = _categoryMap,
                    TagMap = _tagMap
                };
                string json = JsonSerializer.Serialize(data);
                File.WriteAllText(path, json);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to save templates: {ex.Message}");
            }
        }

        public void LoadFromDisk(string path)
        {
            try
            {
                if (!File.Exists(path)) return;
                string json = File.ReadAllText(path);
                var data = JsonSerializer.Deserialize<TemplateRepoData>(json);
                if (data != null)
                {
                    _idMap.Clear();
                    _categoryMap.Clear();
                    _tagMap.Clear();
                    foreach (var kv in data.IdMap) _idMap[kv.Key] = kv.Value;
                    foreach (var kv in data.CategoryMap) _categoryMap[kv.Key] = kv.Value;
                    foreach (var kv in data.TagMap) _tagMap[kv.Key] = kv.Value;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load templates: {ex.Message}");
            }
        }

        private class TemplateRepoData
        {
            public Dictionary<string, PromptTemplate> IdMap { get; set; }
            public Dictionary<string, List<PromptTemplate>> CategoryMap { get; set; }
            public Dictionary<string, List<PromptTemplate>> TagMap { get; set; }
        }
    }
}