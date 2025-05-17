using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading;

namespace Visual_DM.Animation.Threading
{
    /// <summary>
    /// Manages a pool of worker threads for parallel animation job execution.
    /// </summary>
    public class ThreadPoolManager : IDisposable
    {
        // Configurable number of worker threads
        private int _workerCount;
        private List<Thread> _workers;
        private readonly CancellationTokenSource _cts = new CancellationTokenSource();
        private readonly ConcurrentQueue<AnimationTask> _workQueue = new ConcurrentQueue<AnimationTask>();
        private readonly AutoResetEvent _workAvailable = new AutoResetEvent(false);
        private bool _disposed;

        /// <summary>
        /// Initializes the thread pool manager with a specified number of workers.
        /// </summary>
        public ThreadPoolManager(int? workerCount = null)
        {
            _workerCount = workerCount ?? Math.Max(2, Environment.ProcessorCount - 1);
            _workers = new List<Thread>(_workerCount);
            for (int i = 0; i < _workerCount; i++)
            {
                var thread = new Thread(WorkerLoop) { IsBackground = true, Name = $"AnimWorker_{i}" };
                _workers.Add(thread);
                thread.Start();
            }
        }

        /// <summary>
        /// Enqueues an animation task for execution.
        /// </summary>
        public void Enqueue(AnimationTask task)
        {
            _workQueue.Enqueue(task);
            _workAvailable.Set();
        }

        private void WorkerLoop()
        {
            while (!_cts.IsCancellationRequested)
            {
                if (_workQueue.TryDequeue(out var task))
                {
                    try { task.Execute(); }
                    catch (Exception ex) { /* TODO: Log error */ }
                }
                else
                {
                    _workAvailable.WaitOne(10);
                }
            }
        }

        /// <summary>
        /// Disposes the thread pool and stops all workers.
        /// </summary>
        public void Dispose()
        {
            if (_disposed) return;
            _disposed = true;
            _cts.Cancel();
            _workAvailable.Set();
            foreach (var worker in _workers)
            {
                if (worker.IsAlive) worker.Join();
            }
            _cts.Dispose();
            _workAvailable.Dispose();
        }
    }
} 