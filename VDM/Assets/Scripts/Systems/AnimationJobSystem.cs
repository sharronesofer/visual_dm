using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading;
using VisualDM.Systems.Animation.Memory;

namespace VisualDM.Systems.Animation.Threading
{
    /// <summary>
    /// Manages animation jobs, dependencies, and load balancing.
    /// </summary>
    public class AnimationJobSystem
    {
        private readonly ThreadPoolManager _threadPool;
        private readonly ConcurrentDictionary<Guid, AnimationTask> _activeTasks = new ConcurrentDictionary<Guid, AnimationTask>();
        private readonly ObjectPool<AnimationTask> _taskPool;

        /// <summary>
        /// Initializes the AnimationJobSystem with a thread pool and an AnimationTask object pool.
        /// </summary>
        public AnimationJobSystem(ThreadPoolManager threadPool, int poolSize = 64)
        {
            _threadPool = threadPool;
            _taskPool = new ObjectPool<AnimationTask>(poolSize, 1024, () => null); // Use factory for derived types
        }

        /// <summary>
        /// Submits a job to the system. Non-blocking. Uses object pool for AnimationTask instances.
        /// </summary>
        public void Submit(AnimationTask task)
        {
            if (task.Dependencies.Count == 0)
            {
                _threadPool.Enqueue(task);
            }
            else
            {
                // TODO: Add to dependency graph, schedule when ready
            }
            _activeTasks.TryAdd(Guid.NewGuid(), task);
        }

        /// <summary>
        /// Returns a completed AnimationTask to the pool for reuse.
        /// </summary>
        public void ReturnTask(AnimationTask task)
        {
            if (task != null)
            {
                _taskPool.Return(task);
            }
        }

        /// <summary>
        /// Attempts to steal a job for load balancing.
        /// </summary>
        public AnimationTask StealJob()
        {
            // TODO: Implement job stealing logic
            return null;
        }

        /// <summary>
        /// Rents an AnimationTask from the pool (for use by job creators).
        /// </summary>
        public AnimationTask RentTask()
        {
            return _taskPool.Rent();
        }
    }
} 