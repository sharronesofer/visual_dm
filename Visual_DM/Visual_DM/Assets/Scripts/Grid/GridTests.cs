using NUnit.Framework;
using UnityEngine;
using System.Diagnostics;
using System;
using VisualDM.Core;
using VisualDM.Grid;

namespace VisualDM.Grid.Tests
{
    /// <summary>
    /// Contains tests for grid management optimizations.
    /// </summary>
    public class GridTests
    {
        [Test]
        public void TestChunkCreationPerformance()
        {
            var sw = Stopwatch.StartNew();
            int chunkCount = 1000;
            for (int i = 0; i < chunkCount; i++)
            {
                var chunk = new GridChunk(new Vector2Int(i, 0), 32);
                Assert.IsNotNull(chunk);
            }
            sw.Stop();
            UnityEngine.Debug.Log($"Chunk creation time for {chunkCount}: {sw.ElapsedMilliseconds}ms");
            Assert.Less(sw.ElapsedMilliseconds, 1000);
        }

        [Test]
        public void TestHexCellPooling()
        {
            var pool = new HexCellPool(256);
            var cell = pool.Get();
            Assert.IsNotNull(cell);
            pool.Recycle(cell);
            var cell2 = pool.Get();
            Assert.AreSame(cell, cell2);
        }

        [Test]
        public void TestChunkManagerLoadUnload()
        {
            var manager = new ChunkManager(32);
            var chunk = manager.GetOrLoadChunk(Vector2.zero);
            Assert.IsNotNull(chunk);
            manager.UnloadChunk(new Vector2Int(0, 0));
        }

        [Test]
        public void GridPosition_Conversion_Works()
        {
            var pos = GridPosition.FromInt(10, 20);
            var (x, y) = pos.ToInt();
            Assert.AreEqual(10, x);
            Assert.AreEqual(20, y);
            var pos2 = GridPosition.FromFloat(10.5f, 20.25f);
            var (fx, fy) = pos2.ToFloat();
            Assert.AreEqual(10.5f, fx, 1e-4);
            Assert.AreEqual(20.25f, fy, 1e-4);
        }

        [Test]
        public void GridInterop_LegacyConversion_Works()
        {
            var pos = GridInterop.FromLegacyInt(7, 8);
            var (x, y) = GridInterop.ToLegacyInt(pos);
            Assert.AreEqual(7, x);
            Assert.AreEqual(8, y);
            var pos2 = GridInterop.FromLegacyFloat(3.5f, 4.5f);
            var (fx, fy) = GridInterop.ToLegacyFloat(pos2);
            Assert.AreEqual(3.5f, fx, 1e-4);
            Assert.AreEqual(4.5f, fy, 1e-4);
        }

        [Test]
        public void GridPosition_Normalization_WrapsCorrectly()
        {
            var pos = GridPosition.FromInt(105, -7);
            var norm = new GridPosition(pos.Coord.Normalize(100, 10));
            var (x, y) = norm.ToInt();
            Assert.AreEqual(5, x);
            Assert.AreEqual(3, y);
        }
    }
} 