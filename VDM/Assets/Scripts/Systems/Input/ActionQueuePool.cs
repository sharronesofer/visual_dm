using System.Collections.Generic;

namespace VisualDM.Systems.Input
{
    /// <summary>
    /// Object pool for QueuedAction structs to reduce memory allocation pressure
    /// Used by InputActionQueue to reuse action objects.
    /// </summary>
    public class ActionQueuePool
    {
        private readonly Stack<QueuedAction> pool = new Stack<QueuedAction>();
        private readonly int maxSize;

        public ActionQueuePool(int maxSize = 64)
        {
            this.maxSize = maxSize;
        }

        public QueuedAction Get(InputEvent input, ActionPriority priority, float enqueueTime, float expirationTime = 0, int sequenceId = 0)
        {
            if (pool.Count > 0)
            {
                var qa = pool.Pop();
                qa.Input = input;
                qa.Priority = priority;
                qa.EnqueueTime = enqueueTime;
                qa.ExpirationTime = expirationTime;
                qa.SequenceId = sequenceId;
                return qa;
            }
            return new QueuedAction(input, priority, enqueueTime, expirationTime, sequenceId);
        }

        public void Return(QueuedAction qa)
        {
            if (pool.Count < maxSize)
            {
                pool.Push(qa);
            }
        }
    }
} 