using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Visual_DM.Timeline.Models;

namespace Visual_DM.Utilities
{
    public class FeatDatabaseService
    {
        private readonly string _dbPath;
        private List<Feat> _cache;
        public FeatDatabaseService(string dbPath)
        {
            _dbPath = dbPath;
            Load();
        }
        public void Load()
        {
            if (!File.Exists(_dbPath))
            {
                _cache = new List<Feat>();
                return;
            }
            var json = File.ReadAllText(_dbPath);
            _cache = JsonConvert.DeserializeObject<List<Feat>>(json) ?? new List<Feat>();
        }
        public void Save()
        {
            var json = JsonConvert.SerializeObject(_cache, Formatting.Indented);
            File.WriteAllText(_dbPath, json);
        }
        public List<Feat> GetAllFeats() => _cache.ToList();
        public Feat GetFeatById(string id) => _cache.FirstOrDefault(f => f.Id == id);
        public void AddOrUpdateFeat(Feat feat)
        {
            var idx = _cache.FindIndex(f => f.Id == feat.Id);
            if (idx >= 0) _cache[idx] = feat;
            else _cache.Add(feat);
            Save();
        }
        public void DeleteFeat(string id)
        {
            _cache.RemoveAll(f => f.Id == id);
            Save();
        }
        public void BatchUpdate(IEnumerable<Feat> feats)
        {
            foreach (var feat in feats) AddOrUpdateFeat(feat);
            Save();
        }
    }
} 