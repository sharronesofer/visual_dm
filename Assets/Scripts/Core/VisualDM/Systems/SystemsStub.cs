using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems
{
    /// <summary>
    /// Stub implementations for VisualDM Systems namespace
    /// </summary>
    
    public class SystemManager
    {
        private List<ISystem> _systems = new List<ISystem>();
        
        public void Initialize()
        {
            Debug.Log("[VisualDM.Systems] SystemManager initialized");
        }
        
        public void RegisterSystem(ISystem system)
        {
            if (!_systems.Contains(system))
            {
                _systems.Add(system);
                system.Initialize();
            }
        }
        
        public void UnregisterSystem(ISystem system)
        {
            if (_systems.Contains(system))
            {
                system.Shutdown();
                _systems.Remove(system);
            }
        }
        
        public T GetSystem<T>() where T : class, ISystem
        {
            foreach (var system in _systems)
            {
                if (system is T)
                    return system as T;
            }
            return null;
        }
        
        public void UpdateSystems()
        {
            foreach (var system in _systems)
            {
                if (system.IsActive)
                    system.Update();
            }
        }
        
        public void ShutdownAllSystems()
        {
            foreach (var system in _systems)
            {
                system.Shutdown();
            }
            _systems.Clear();
        }
    }
    
    public interface ISystem
    {
        bool IsActive { get; }
        void Initialize();
        void Update();
        void Shutdown();
    }
    
    public abstract class BaseSystem : ISystem
    {
        public virtual bool IsActive { get; protected set; } = true;
        
        public virtual void Initialize()
        {
            Debug.Log($"[{GetType().Name}] System initialized");
        }
        
        public virtual void Update()
        {
            // Override in derived classes
        }
        
        public virtual void Shutdown()
        {
            IsActive = false;
            Debug.Log($"[{GetType().Name}] System shutdown");
        }
    }
} 