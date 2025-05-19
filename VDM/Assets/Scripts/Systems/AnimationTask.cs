using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Animation.Threading
{
    /// <summary>
    /// Base class for animation system jobs.
    /// </summary>
    public abstract class AnimationTask : IComparable<AnimationTask>
    {
        public enum TaskPriority { Low, Normal, High, Critical }
        public TaskPriority Priority { get; set; } = TaskPriority.Normal;
        public List<AnimationTask> Dependencies { get; } = new List<AnimationTask>();
        public bool IsCompleted { get; protected set; }

        /// <summary>
        /// Execute the animation task. Must be thread-safe.
        /// </summary>
        public abstract void Execute();

        public int CompareTo(AnimationTask other)
        {
            if (other == null) return 1;
            return other.Priority.CompareTo(this.Priority); // Higher priority first
        }
    }
} 