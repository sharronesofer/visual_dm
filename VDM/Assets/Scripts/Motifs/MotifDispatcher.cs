using System;
using System.Collections.Generic;

namespace VDM.Motifs
{
    /// <summary>
    /// Interface for motif observers.
    /// </summary>
    public interface IMotifObserver
    {
        void OnMotifChanged(Motif motif);
    }

    /// <summary>
    /// Singleton dispatcher for motif change notifications.
    /// </summary>
    public class MotifDispatcher
    {
        private static MotifDispatcher _instance;
        public static MotifDispatcher Instance => _instance ??= new MotifDispatcher();
        private readonly List<IMotifObserver> _observers = new();
        private MotifDispatcher() { }

        /// <summary>
        /// Register an observer.
        /// </summary>
        public void Register(IMotifObserver observer)
        {
            if (!_observers.Contains(observer))
                _observers.Add(observer);
        }

        /// <summary>
        /// Unregister an observer.
        /// </summary>
        public void Unregister(IMotifObserver observer)
        {
            _observers.Remove(observer);
        }

        /// <summary>
        /// Notify all observers of a motif change.
        /// </summary>
        public void NotifyMotifChanged(Motif motif)
        {
            foreach (var observer in _observers)
                observer.OnMotifChanged(motif);
        }
    }
} 