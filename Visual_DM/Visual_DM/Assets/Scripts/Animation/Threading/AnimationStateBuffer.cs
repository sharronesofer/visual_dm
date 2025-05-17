using System;
using System.Threading;

namespace Visual_DM.Animation.Threading
{
    /// <summary>
    /// Double-buffered, thread-safe animation state buffer with versioning.
    /// </summary>
    public class AnimationStateBuffer<T> where T : struct
    {
        private T[] _buffers = new T[2];
        private int _activeIndex = 0;
        private int _version = 0;

        /// <summary>
        /// Gets the current active state (read-only).
        /// </summary>
        public ref readonly T ReadState => ref _buffers[_activeIndex];

        /// <summary>
        /// Gets the writeable state buffer.
        /// </summary>
        public ref T WriteState => ref _buffers[1 - _activeIndex];

        /// <summary>
        /// Atomically swaps the buffers and increments the version.
        /// </summary>
        public void SwapBuffers()
        {
            _activeIndex = 1 - _activeIndex;
            Interlocked.Increment(ref _version);
        }

        /// <summary>
        /// Gets the current version number.
        /// </summary>
        public int Version => _version;
    }
} 