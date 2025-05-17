# Grid Management System

This directory contains the core runtime-generated grid management system for large-scale maps in Unity 2D.

## Components

- **GridChunk.cs**: Represents a fixed-size chunk of the grid, containing an array of hex cells. Supports serialization and deserialization for storage and streaming.
- **ChunkManager.cs**: Manages loading, unloading, and caching of grid chunks. Uses spatial hashing for efficient lookup and supports chunk-level caching.
- **HexCellPool.cs**: Provides memory pooling for `HexCell` instances to reduce garbage collection overhead. Supports batch allocation and recycling.
- **GridStreamer.cs**: Handles asynchronous streaming of grid data, prioritizing chunks near the player/camera. Uses Unity coroutines and async/await for background loading.
- **DynamicGrid.cs**: Supports runtime grid expansion and contraction, non-uniform grid densities, and event propagation for grid changes.
- **GridInterop.cs**: Stubs for integration with the Python-based asset management system. Handles serialization, deserialization, and (future) data compression.
- **GridTests.cs**: Contains Unity test framework tests for performance, functional, and stress testing of the grid system.

## Usage

- All grid management is runtime-generated; no scene or prefab references are used.
- The system is designed for extensibility and plugin integration.
- To use, instantiate a `DynamicGrid` and connect it to your game logic. Use `GridStreamer` to stream chunks around the player.
- Integrate with Python asset management via `GridInterop` methods.

## Extension

- Add new chunk types or cell properties by extending `GridChunk` and `HexCell`.
- Implement custom serialization or compression in `GridInterop` as needed.
- Use events in `DynamicGrid` to propagate grid changes to dependent systems.

## Testing

- Run `GridTests` with the Unity Test Runner to verify performance and correctness.
- Add new tests as you extend the system. 