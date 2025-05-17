using System;
using System.Collections.Generic;
using System.Threading;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Thread-safe priority queue for resolving combat actions.
    /// </summary>
    public class CombatActionPriorityQueue
    {
        private class QueueItem : IComparable<QueueItem>
        {
            public CombatActionHandler Handler { get; }
            public int Priority { get; }
            public DateTime Timestamp { get; }

            public QueueItem(CombatActionHandler handler, int priority)
            {
                Handler = handler;
                Priority = priority;
                Timestamp = DateTime.UtcNow;
            }

            public int CompareTo(QueueItem other)
            {
                int cmp = -Priority.CompareTo(other.Priority); // Higher priority first
                if (cmp == 0)
                    cmp = Timestamp.CompareTo(other.Timestamp); // Earlier first
                return cmp;
            }
        }

        private readonly List<QueueItem> queue = new List<QueueItem>();
        private readonly object lockObj = new object();

        /// <summary>
        /// Enqueue a combat action handler with a given priority.
        /// </summary>
        public void Enqueue(CombatActionHandler handler, int priority)
        {
            lock (lockObj)
            {
                queue.Add(new QueueItem(handler, priority));
                queue.Sort();
            }
        }

        /// <summary>
        /// Dequeue the highest-priority combat action handler.
        /// </summary>
        public CombatActionHandler Dequeue()
        {
            lock (lockObj)
            {
                if (queue.Count == 0) return null;
                var item = queue[0];
                queue.RemoveAt(0);
                return item.Handler;
            }
        }

        /// <summary>
        /// Peek at the highest-priority combat action handler.
        /// </summary>
        public CombatActionHandler Peek()
        {
            lock (lockObj)
            {
                return queue.Count > 0 ? queue[0].Handler : null;
            }
        }

        /// <summary>
        /// Get the number of items in the queue.
        /// </summary>
        public int Count
        {
            get { lock (lockObj) { return queue.Count; } }
        }

        /// <summary>
        /// Clear the queue.
        /// </summary>
        public void Clear()
        {
            lock (lockObj)
            {
                queue.Clear();
            }
        }
    }
} 