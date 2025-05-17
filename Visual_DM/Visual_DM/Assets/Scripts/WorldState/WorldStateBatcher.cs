using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;

namespace Visual_DM.WorldState
{
    // Batches world state updates for performance
    public class WorldStateBatcher
    {
        private readonly Queue<Action> _updateQueue = new Queue<Action>();
        private readonly object _lock = new object();
        private bool _isFlushing = false;
        private Stopwatch _stopwatch = new Stopwatch();
        public event Action<long> OnBatchFlushComplete; // For profiling (elapsed ms)

        private static WorldStateBatcher _instance;
        public static WorldStateBatcher Instance => _instance ?? (_instance = new WorldStateBatcher());

        private WorldStateBatcher() { }

        // Enqueue a world state update
        public void EnqueueUpdate(Action update)
        {
            lock (_lock)
            {
                _updateQueue.Enqueue(update);
            }
        }

        // Flush all queued updates (call from main thread, e.g., in Update loop or at safe points)
        public void Flush()
        {
            lock (_lock)
            {
                if (_isFlushing || _updateQueue.Count == 0)
                    return;
                _isFlushing = true;
                _stopwatch.Restart();
                while (_updateQueue.Count > 0)
                {
                    var update = _updateQueue.Dequeue();
                    try
                    {
                        update?.Invoke();
                    }
                    catch (Exception ex)
                    {
                        UnityEngine.Debug.LogError($"WorldStateBatcher: Exception during batch update: {ex}");
                    }
                }
                _stopwatch.Stop();
                OnBatchFlushComplete?.Invoke(_stopwatch.ElapsedMilliseconds);
                _isFlushing = false;
            }
        }

        // For use in Unity's Update or a custom tick system
        public void FlushIfNeeded(int maxBatchSize = 100)
        {
            lock (_lock)
            {
                if (_updateQueue.Count >= maxBatchSize)
                {
                    Flush();
                }
            }
        }

        // For profiling: get current queue size
        public int GetQueueSize()
        {
            lock (_lock)
            {
                return _updateQueue.Count;
            }
        }
    }
}