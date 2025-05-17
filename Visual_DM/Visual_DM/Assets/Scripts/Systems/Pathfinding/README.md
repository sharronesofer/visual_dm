# Pathfinding System

This directory contains the advanced pathfinding system for Visual DM, supporting multiple algorithms, path smoothing, dynamic obstacle handling, and path caching.

## Architecture
- **PathfindingManager**: Central manager for path requests, algorithm selection, and caching.
- **IPathfindingAlgorithm**: Interface for all algorithms (A*, JPS, Hierarchical).
- **AStarPathfinder, JPSPathfinder, HierarchicalPathfinder**: Implementations of each algorithm.
- **PathSmoother**: Static class for Bezier, string-pulling, and angle-based smoothing.
- **DynamicObstacleManager**: Handles obstacle updates and triggers path recalculation.
- **PathCache**: LRU cache for storing/retrieving paths.

## Extension Points
- Add new algorithms by implementing `IPathfindingAlgorithm` and registering with `PathfindingManager`.
- Extend smoothing techniques in `PathSmoother`.
- Integrate with grid and plugin systems as needed.

## Best Practices
- Use async/await for path requests.
- Avoid UnityEditor and scene references.
- Use only runtime-generated objects (SpriteRenderer, no prefabs).
- Document all public APIs with XML comments. 