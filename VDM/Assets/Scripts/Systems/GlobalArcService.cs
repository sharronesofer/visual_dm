using System;
using System.Collections.Generic;
using System.Linq;
using VisualDM.Systems.EventSystem;

namespace VisualDM.Systems.Narrative
{
    /// <summary>
    /// Service for managing GlobalArc business logic and events.
    /// </summary>
    public class GlobalArcService : IGlobalArcService
    {
        private readonly IGlobalArcRepository _repository;
        private readonly List<GlobalArc> _activeArcs = new();
        public event Action<GlobalArc> OnArcProgressed;
        public event Action<GlobalArc> OnArcCompleted;

        public GlobalArcService(IGlobalArcRepository repository)
        {
            _repository = repository;
            _activeArcs = _repository.GetAll().ToList();
        }

        public void RegisterArc(GlobalArc arc)
        {
            _repository.Add(arc);
            _activeArcs.Add(arc);
        }

        public void UnregisterArc(string arcId)
        {
            _repository.Remove(arcId);
            _activeArcs.RemoveAll(a => a.Id == arcId);
        }

        public void ProgressArc(string arcId)
        {
            var arc = _activeArcs.FirstOrDefault(a => a.Id == arcId);
            if (arc == null) return;
            arc.ProgressStage();
            OnArcProgressed?.Invoke(arc);
            EventBus.Instance.Publish(new ArcProgressedEvent(arc));
            if (arc.IsComplete(null)) // Pass actual GameState in real use
            {
                CompleteArc(arcId);
            }
        }

        public void CompleteArc(string arcId)
        {
            var arc = _activeArcs.FirstOrDefault(a => a.Id == arcId);
            if (arc == null) return;
            OnArcCompleted?.Invoke(arc);
            EventBus.Instance.Publish(new ArcCompletedEvent(arc));
            // Optionally remove from active arcs
        }

        public void ValidateArc(string arcId)
        {
            var arc = _activeArcs.FirstOrDefault(a => a.Id == arcId);
            if (arc == null) return;
            arc.Validate(_activeArcs);
        }

        public void ValidateAll()
        {
            foreach (var arc in _activeArcs)
                arc.Validate(_activeArcs);
        }

        public IEnumerable<GlobalArc> GetActiveArcs() => _activeArcs;
    }

    /// <summary>
    /// Event data for arc progression.
    /// </summary>
    public record ArcProgressedEvent(GlobalArc Arc);
    /// <summary>
    /// Event data for arc completion.
    /// </summary>
    public record ArcCompletedEvent(GlobalArc Arc);

    /// <summary>
    /// Service interface for business logic operations on RegionalArc.
    /// </summary>
    public interface IRegionalArcService
    {
        void RegisterArc(RegionalArc arc);
        void UnregisterArc(string arcId);
        void ProgressArc(string arcId);
        void CompleteArc(string arcId);
        void ValidateArc(string arcId);
        void ValidateAll();
        IEnumerable<RegionalArc> GetActiveArcs();
        event Action<RegionalArc> OnArcProgressed;
        event Action<RegionalArc> OnArcCompleted;
    }

    /// <summary>
    /// Service for managing RegionalArc business logic and events.
    /// </summary>
    public class RegionalArcService : IRegionalArcService
    {
        private readonly List<RegionalArc> _activeArcs = new();
        public event Action<RegionalArc> OnArcProgressed;
        public event Action<RegionalArc> OnArcCompleted;

        public void RegisterArc(RegionalArc arc)
        {
            _activeArcs.Add(arc);
        }

        public void UnregisterArc(string arcId)
        {
            _activeArcs.RemoveAll(a => a.Id == arcId);
        }

        public void ProgressArc(string arcId)
        {
            var arc = _activeArcs.FirstOrDefault(a => a.Id == arcId);
            if (arc == null) return;
            arc.ProgressStage();
            OnArcProgressed?.Invoke(arc);
            // TODO: Publish event via EventBus if needed
            if (arc.IsComplete(Core.GameState.Gameplay)) // Pass actual GameState in real use
            {
                CompleteArc(arcId);
            }
        }

        public void CompleteArc(string arcId)
        {
            var arc = _activeArcs.FirstOrDefault(a => a.Id == arcId);
            if (arc == null) return;
            OnArcCompleted?.Invoke(arc);
            // TODO: Publish event via EventBus if needed
        }

        public void ValidateArc(string arcId)
        {
            var arc = _activeArcs.FirstOrDefault(a => a.Id == arcId);
            if (arc == null) return;
            arc.Validate(_activeArcs, new List<GlobalArc>()); // Pass actual global arcs in real use
        }

        public void ValidateAll()
        {
            foreach (var arc in _activeArcs)
                arc.Validate(_activeArcs, new List<GlobalArc>()); // Pass actual global arcs in real use
        }

        public IEnumerable<RegionalArc> GetActiveArcs() => _activeArcs;
    }
}