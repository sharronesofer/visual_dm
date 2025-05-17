using System;
using System.Collections.Generic;

namespace AI
{
    public class HookPriorityQueue
    {
        private readonly List<HookEvent> _heap = new List<HookEvent>();

        public int Count => _heap.Count;

        public void Enqueue(HookEvent hookEvent)
        {
            _heap.Add(hookEvent);
            HeapifyUp(_heap.Count - 1);
        }

        public HookEvent Dequeue()
        {
            if (_heap.Count == 0) return null;
            var top = _heap[0];
            _heap[0] = _heap[_heap.Count - 1];
            _heap.RemoveAt(_heap.Count - 1);
            HeapifyDown(0);
            return top;
        }

        public HookEvent Peek()
        {
            return _heap.Count > 0 ? _heap[0] : null;
        }

        private void HeapifyUp(int index)
        {
            while (index > 0)
            {
                int parent = (index - 1) / 2;
                if (Compare(_heap[index], _heap[parent]) > 0)
                {
                    Swap(index, parent);
                    index = parent;
                }
                else break;
            }
        }

        private void HeapifyDown(int index)
        {
            int last = _heap.Count - 1;
            while (true)
            {
                int left = 2 * index + 1;
                int right = 2 * index + 2;
                int largest = index;
                if (left <= last && Compare(_heap[left], _heap[largest]) > 0) largest = left;
                if (right <= last && Compare(_heap[right], _heap[largest]) > 0) largest = right;
                if (largest == index) break;
                Swap(index, largest);
                index = largest;
            }
        }

        private int Compare(HookEvent a, HookEvent b)
        {
            int priorityCmp = b.Priority.CompareTo(a.Priority); // Higher priority first
            if (priorityCmp != 0) return priorityCmp;
            return a.Timestamp.CompareTo(b.Timestamp); // Earlier events first
        }

        private void Swap(int i, int j)
        {
            var temp = _heap[i];
            _heap[i] = _heap[j];
            _heap[j] = temp;
        }
    }
} 