using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Threading;

namespace Visual_DM.Animation.Memory
{
    /// <summary>
    /// Custom allocator for animation data to minimize fragmentation and support batch allocations.
    /// </summary>
    public class AnimationMemoryAllocator
    {
        private readonly object _lock = new();
        private readonly List<IntPtr> _blocks = new();
        private readonly int _blockSize;
        private int _allocated;
        private IntPtr _currentBlock;
        private int _currentOffset;

        public AnimationMemoryAllocator(int blockSize = 1024 * 1024)
        {
            _blockSize = blockSize;
            AllocateNewBlock();
        }

        private void AllocateNewBlock()
        {
            _currentBlock = Marshal.AllocHGlobal(_blockSize);
            _blocks.Add(_currentBlock);
            _currentOffset = 0;
        }

        public IntPtr Allocate(int size)
        {
            lock (_lock)
            {
                if (_currentOffset + size > _blockSize)
                {
                    AllocateNewBlock();
                }
                IntPtr ptr = IntPtr.Add(_currentBlock, _currentOffset);
                _currentOffset += size;
                _allocated += size;
                return ptr;
            }
        }

        public void FreeAll()
        {
            lock (_lock)
            {
                foreach (var block in _blocks)
                {
                    Marshal.FreeHGlobal(block);
                }
                _blocks.Clear();
                _allocated = 0;
                AllocateNewBlock();
            }
        }

        public int AllocatedBytes => _allocated;
    }
} 