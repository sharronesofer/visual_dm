using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.Input;

namespace VisualDM.Systems.Input
{
    /// <summary>
    /// Priority levels for queued actions.
    /// </summary>
    public enum ActionPriority
    {
        Critical = 3,
        High = 2,
        Normal = 1,
        Low = 0
    }

    /// <summary>
    /// Represents an action queued for execution, with priority and timing info.
    /// </summary>
    public struct QueuedAction
    {
        /// <summary>
        /// The input event associated with the action.
        /// </summary>
        public InputEvent Input;
        /// <summary>
        /// The priority of the action.
        /// </summary>
        public ActionPriority Priority;
        /// <summary>
        /// The time the action was enqueued.
        /// </summary>
        public float EnqueueTime;
        /// <summary>
        /// The expiration time for the action (0 = never expires).
        /// </summary>
        public float ExpirationTime;
        /// <summary>
        /// Sequence ID for conflict resolution.
        /// </summary>
        public int SequenceId;

        public QueuedAction(InputEvent input, ActionPriority priority, float enqueueTime, float expirationTime = 0, int sequenceId = 0)
        {
            Input = input;
            Priority = priority;
            EnqueueTime = enqueueTime;
            ExpirationTime = expirationTime;
            SequenceId = sequenceId;
        }
    }

    /// <summary>
    /// Priority-based queue for player/AI actions. Supports validation, cancellation, priority adjustment, and expiration.
    /// </summary>
    public class InputActionQueue : MonoBehaviour
    {
        private List<QueuedAction> queue = new List<QueuedAction>();
        private int nextSequenceId = 0;
        private ActionQueuePool pool = new ActionQueuePool(64);

        /// <summary>
        /// Event for queue state changes.
        /// </summary>
        public event Action<List<QueuedAction>> OnQueueChanged;

        /// <summary>
        /// Maximum number of actions in the queue.
        /// </summary>
        public int Capacity { get; private set; } = 16;

        // Unified API for integration
        public void BroadcastQueueState()
        {
            OnQueueChanged?.Invoke(GetQueueSnapshot());
        }

        public InputActionQueue(int capacity = 16)
        {
            Capacity = capacity;
        }

        /// <summary>
        /// Enqueues a new action with the given priority and optional expiration, using the pool.
        /// </summary>
        public bool EnqueueAction(InputEvent input, ActionPriority priority, float expiration = 0)
        {
            if (queue.Count >= Capacity)
            {
                RemoveLowestPriority();
                if (queue.Count >= Capacity) return false;
            }
            float now = Time.time;
            var action = pool.Get(input, priority, now, expiration > 0 ? now + expiration : 0, nextSequenceId++);
            queue.Add(action);
            queue.Sort(CompareActions);
            BroadcastQueueState();
            return true;
        }

        /// <summary>
        /// Dequeues the highest-priority action, or null if empty. Returns the action to the pool after use.
        /// </summary>
        public QueuedAction? DequeueAction()
        {
            PruneExpired();
            if (queue.Count == 0) return null;
            var action = queue[0];
            queue.RemoveAt(0);
            BroadcastQueueState();
            pool.Return(action);
            return action;
        }

        /// <summary>
        /// Cancels actions matching the given predicate.
        /// </summary>
        public void CancelAction(Predicate<QueuedAction> match)
        {
            queue.RemoveAll(match);
            BroadcastQueueState();
        }

        /// <summary>
        /// Clears all actions from the queue.
        /// </summary>
        public void ClearQueue()
        {
            queue.Clear();
            BroadcastQueueState();
        }

        /// <summary>
        /// Returns a snapshot of the current queue state.
        /// </summary>
        public List<QueuedAction> GetQueueSnapshot()
        {
            PruneExpired();
            return new List<QueuedAction>(queue);
        }

        /// <summary>
        /// Adjusts the priority of all actions using the provided function.
        /// </summary>
        public void AdjustPriority(Func<QueuedAction, ActionPriority> adjustFunc)
        {
            for (int i = 0; i < queue.Count; i++)
            {
                var qa = queue[i];
                qa.Priority = adjustFunc(qa);
                queue[i] = qa;
            }
            queue.Sort(CompareActions);
        }

        private void RemoveLowestPriority()
        {
            if (queue.Count == 0) return;
            int minIdx = 0;
            for (int i = 1; i < queue.Count; i++)
            {
                if (CompareActions(queue[i], queue[minIdx]) > 0)
                    minIdx = i;
            }
            queue.RemoveAt(minIdx);
        }

        private void PruneExpired()
        {
            float now = Time.time;
            queue.RemoveAll(a => a.ExpirationTime > 0 && now > a.ExpirationTime);
        }

        private static int CompareActions(QueuedAction a, QueuedAction b)
        {
            int p = b.Priority.CompareTo(a.Priority); // Descending
            if (p != 0) return p;
            return a.SequenceId.CompareTo(b.SequenceId); // FIFO for same priority
        }
    }
} 