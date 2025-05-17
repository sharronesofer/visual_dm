using System.Collections.Generic;

namespace VisualDM.Grid
{
    /// <summary>
    /// Provides memory pooling for HexCell instances to reduce GC overhead.
    /// </summary>
    public class HexCellPool
    {
        private readonly Stack<HexCell> pool = new();
        private readonly int batchSize;

        public HexCellPool(int batchSize = 128)
        {
            this.batchSize = batchSize;
        }

        /// <summary>
        /// Gets a HexCell from the pool, allocating a batch if empty.
        /// </summary>
        public HexCell Get()
        {
            if (pool.Count == 0)
                AllocateBatch();
            return pool.Pop();
        }

        /// <summary>
        /// Returns a HexCell to the pool for reuse.
        /// </summary>
        public void Recycle(HexCell cell)
        {
            // Optionally reset cell state here
            pool.Push(cell);
        }

        /// <summary>
        /// Allocates a batch of HexCells and adds them to the pool.
        /// </summary>
        private void AllocateBatch()
        {
            for (int i = 0; i < batchSize; i++)
                pool.Push(new HexCell());
        }
    }
} 