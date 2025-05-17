using System.Collections.Generic;

namespace VisualDM.Narrative
{
    /// <summary>
    /// Repository interface for accessing and persisting GlobalArc entities.
    /// </summary>
    public interface IGlobalArcRepository
    {
        GlobalArc GetById(string id);
        IEnumerable<GlobalArc> GetAll();
        IEnumerable<GlobalArc> Query(System.Predicate<GlobalArc> predicate);
        void Add(GlobalArc arc);
        void Update(GlobalArc arc);
        void Remove(string id);
        void Save();
        // For lazy loading
        GlobalArc LoadDetails(string id);
    }
}