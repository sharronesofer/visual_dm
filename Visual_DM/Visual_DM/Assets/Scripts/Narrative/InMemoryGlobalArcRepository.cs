using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text.Json;

namespace VisualDM.Narrative
{
    /// <summary>
    /// In-memory implementation of IGlobalArcRepository with basic JSON persistence.
    /// </summary>
    public class InMemoryGlobalArcRepository : IGlobalArcRepository
    {
        private readonly ConcurrentDictionary<string, GlobalArc> _arcs = new();
        private readonly string _savePath = "global_arcs.json";

        public GlobalArc GetById(string id) => _arcs.TryGetValue(id, out var arc) ? arc : null;
        public IEnumerable<GlobalArc> GetAll() => _arcs.Values;
        public IEnumerable<GlobalArc> Query(System.Predicate<GlobalArc> predicate) => _arcs.Values.Where(a => predicate(a));
        public void Add(GlobalArc arc) => _arcs[arc.Id] = arc;
        public void Update(GlobalArc arc) => _arcs[arc.Id] = arc;
        public void Remove(string id) => _arcs.TryRemove(id, out _);
        public void Save()
        {
            var dtos = _arcs.Values.Select(GlobalArcMapper.ToDTO).ToList();
            var json = JsonSerializer.Serialize(dtos);
            File.WriteAllText(_savePath, json);
        }
        public GlobalArc LoadDetails(string id)
        {
            // For demo, just return the arc (no lazy loading needed in-memory)
            return GetById(id);
        }
        public void Load()
        {
            if (!File.Exists(_savePath)) return;
            var json = File.ReadAllText(_savePath);
            var dtos = JsonSerializer.Deserialize<List<GlobalArcDTO>>(json);
            if (dtos != null)
            {
                foreach (var dto in dtos)
                {
                    var arc = GlobalArcMapper.FromDTO(dto);
                    _arcs[arc.Id] = arc;
                }
            }
        }
    }
}