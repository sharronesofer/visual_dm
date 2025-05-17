using System.Collections.Generic;

namespace VisualDM.Narrative
{
    /// <summary>
    /// Service interface for business logic operations on GlobalArc.
    /// </summary>
    public interface IGlobalArcService
    {
        void ProgressArc(string arcId);
        void ValidateArc(string arcId);
        void ValidateAll();
        void CompleteArc(string arcId);
        void RegisterArc(GlobalArc arc);
        void UnregisterArc(string arcId);
        IEnumerable<GlobalArc> GetActiveArcs();
        event System.Action<GlobalArc> OnArcProgressed;
        event System.Action<GlobalArc> OnArcCompleted;
    }
}