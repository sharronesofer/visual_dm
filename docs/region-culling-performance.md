# Region Culling & Performance Optimization Guide

## Overview

Efficient viewport culling is essential for rendering large map datasets (thousands to millions of regions) with high performance. The culling system ensures that only regions visible in the current viewport are processed and rendered, dramatically reducing CPU and memory usage.

## Spatial Indexing

The culling system supports multiple spatial index types:

- **Grid** (default): Fast for evenly distributed regions. Configurable cell size.
- **Quadtree** (planned): Hierarchical, good for clustered/nested regions.
- **R-tree** (planned): Efficient for complex, overlapping regions.

### Configuration Example

```tsx
<RegionLayer
  regions={regions}
  viewport={viewport}
  spatialIndexType="grid" // or 'quadtree', 'rtree'
  spatialIndexOptions={{ cellSize: 128 }}
/>
```

- `spatialIndexType`: 'grid' | 'quadtree' | 'rtree'
- `spatialIndexOptions`: `{ cellSize?: number, maxDepth?: number, ... }`

## Level-of-Detail (LOD) Rendering

- When zoomed out (zoom < 1.5), RegionLayer renders region bounding boxes instead of full polygons for visible regions.
- This reduces render complexity and improves performance for large datasets.
- LOD threshold can be tuned in the code.

## Benchmarking Performance

- Use the debug overlay in RegionLayer to view real-time query time (ms), region counts, and culling efficiency.
- Test with synthetic datasets (e.g., 1K, 10K, 100K regions) to measure scaling.
- Compare performance with and without culling, and with different spatial index types and LOD settings.

### Example Debug Overlay

- Shows total, visible, and culled region counts
- Displays spatial index type and query time
- Toggle debug/culling with [D] and [C] keys

## Best Practices

- Use grid index for evenly distributed regions; try quadtree/rtree for clustered or complex datasets (when available)
- Tune cell size (grid) or maxDepth (quadtree) for your dataset size and region density
- Enable LOD for large datasets and low zoom levels
- Profile with real data and adjust parameters for your use case

## API Documentation: RegionLayer Culling Props

| Prop                | Type     | Default   | Description |
|---------------------|----------|-----------|-------------|
| spatialIndexType    | string   | 'grid'    | Type of spatial index ('grid', 'quadtree', 'rtree') |
| spatialIndexOptions | object   | {cellSize:100} | Options for the spatial index (cell size, max depth, etc.) |

## Code References

- `src/components/RegionLayer.tsx`: Main culling/render logic, debug overlay, LOD
- `src/utils/SpatialIndex.ts`: Spatial index implementations and abstraction

## Future Work

- Implement full quadtree and R-tree support
- Add worker-thread or GPU-accelerated culling for massive datasets
- Expose LOD threshold as a prop

---

For questions or contributions, see the code comments or open an issue in the repository. 