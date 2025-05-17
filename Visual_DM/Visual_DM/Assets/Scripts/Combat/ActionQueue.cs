using System;
using System.Collections.Generic;
using System.Threading;

public class ActionRequest
{
    public ActionType ActionType;
    public int Priority;
    public float Timestamp;
    public object Context;
    public ActionRequest(ActionType type, int priority, float timestamp, object context = null)
    {
        ActionType = type;
        Priority = priority;
        Timestamp = timestamp;
        Context = context;
    }
}

public class ActionQueue
{
    private readonly object _lock = new object();
    private readonly List<ActionRequest> _queue = new List<ActionRequest>();
    private readonly int _maxSize = 16;
    private float _bufferWindowMs = 100f;

    public ActionQueue(float bufferWindowMs = 100f, int maxSize = 16)
    {
        _bufferWindowMs = bufferWindowMs;
        _maxSize = maxSize;
    }

    public void Enqueue(ActionRequest request)
    {
        lock (_lock)
        {
            if (_queue.Count >= _maxSize)
                _queue.RemoveAt(0); // Drop oldest if full
            _queue.Add(request);
            _queue.Sort((a, b) => b.Priority.CompareTo(a.Priority));
        }
    }

    public ActionRequest Dequeue()
    {
        lock (_lock)
        {
            if (_queue.Count == 0) return null;
            var req = _queue[0];
            _queue.RemoveAt(0);
            return req;
        }
    }

    public void BufferInput(ActionRequest request, float currentTime)
    {
        lock (_lock)
        {
            // Only buffer if within window
            if (_queue.Count > 0 && (currentTime - _queue[_queue.Count - 1].Timestamp) < _bufferWindowMs / 1000f)
                _queue.Add(request);
            else
                Enqueue(request);
        }
    }

    public int Count
    {
        get { lock (_lock) { return _queue.Count; } }
    }

    public void Clear()
    {
        lock (_lock) { _queue.Clear(); }
    }

    public List<ActionRequest> GetSnapshot()
    {
        lock (_lock) { return new List<ActionRequest>(_queue); }
    }
} 