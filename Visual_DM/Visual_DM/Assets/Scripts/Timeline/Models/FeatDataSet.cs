using System.Collections.Generic;
using System.Linq;

namespace Visual_DM.Timeline.Models
{
    public class FeatDataSet
    {
        public List<Feat> Feats { get; set; } = new List<Feat>();
        private Dictionary<string, Feat> _featById;

        public void BuildIndex()
        {
            _featById = Feats.ToDictionary(f => f.Id);
        }

        public Feat GetFeatById(string id)
        {
            if (_featById == null) BuildIndex();
            return _featById.TryGetValue(id, out var feat) ? feat : null;
        }

        public IEnumerable<Feat> GetFeatsByCategory(FeatCategory category)
        {
            return Feats.Where(f => f.Category == category);
        }

        public IEnumerable<Feat> GetFeatsByLevel(int level)
        {
            return Feats.Where(f => f.LevelRequirement <= level);
        }
    }
} 