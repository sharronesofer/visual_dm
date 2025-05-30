# Visual DM Map System Architecture

## Overview

The Visual DM Map System is a comprehensive solution for managing interactive maps in a Unity game with backend integration via FastAPI. The system supports multiple maps, customizable annotations, layer management, and real-time synchronization across clients.

## System Architecture

The map system follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│                  Unity                  │
├─────────────┬───────────────┬───────────┤
│  Map Data   │ Map UI Layer  │  Network  │
│             │               │           │
│ MapManager  │   MapView     │ WebSocket │
│ MapData     │   Panels      │  Client   │
└─────┬───────┴───────┬───────┴─────┬─────┘
      │               │             │
      ▼               ▼             ▼
┌────────────────────────────────────────┐
│              REST API / WebSockets     │
├────────────────────────────────────────┤
│            FastAPI Backend             │
└────────────────────────────────────────┘
```

## Core Components

### Data Layer

#### MapManager.cs
- **Purpose**: Central singleton for managing map-related functionality
- **Responsibilities**:
  - Manages map instances (create, load, unload)
  - Handles layers (add, remove, visibility)
  - Controls annotations (create, edit, delete)
  - Provides spatial querying for annotations
  - Dispatches events for map changes

#### MapData.cs
- **Purpose**: Data structures for maps, layers, and annotations
- **Key Classes**:
  - `MapData`: Container for map information, layers, and metadata
  - `MapLayer`: Group of related annotations with visibility settings
  - `MapAnnotation`: Points of interest with type, position, and properties
- **Features**:
  - JSON serialization/deserialization for data persistence
  - Property management for custom metadata
  - Spatial indexing for efficient queries

### UI Layer

#### MapView.cs
- **Purpose**: UI component for displaying and interacting with the map
- **Features**:
  - Rendering map background and annotations
  - Handling pan and zoom interactions
  - Supporting different interaction modes (view, edit, measure)
  - Providing visual feedback for hover and selection

#### MapAnnotationPrefab.cs
- **Purpose**: UI representation of map annotations
- **Features**:
  - Visual display based on annotation type
  - Hover and click behaviors
  - Tooltip display
  - Selection indication

#### MapSelectionPanel.cs
- **Purpose**: UI for browsing and selecting available maps
- **Features**:
  - Displaying list of available maps
  - Map creation and deletion
  - Filtering and searching

#### MapAnnotationPanel.cs
- **Purpose**: UI for editing annotation properties
- **Features**:
  - Type selection with appropriate properties
  - Custom metadata editing
  - Appearance customization (color, size, icon)

### Network Layer

#### MapWebSocketClient.cs
- **Purpose**: Client for real-time synchronization with backend
- **Features**:
  - Connection management
  - Message handling for various event types
  - Automatic reconnection
  - Message queueing during disconnection

### Backend (FastAPI)

#### map_service.py
- **Purpose**: Server-side handling of map data
- **Features**:
  - REST API endpoints for CRUD operations
  - WebSocket server for real-time updates
  - File storage for map images
  - Authentication and authorization

#### map_annotation_types.json
- **Purpose**: Configuration for annotation types
- **Features**:
  - Defines available annotation types (cities, dungeons, etc.)
  - Specifies properties for each type
  - Sets default appearance settings

## Communication Flow

1. **Local Operations**:
   - User interacts with MapView
   - MapManager processes the interaction
   - UI is updated to reflect changes
   - Changes are serialized and sent to backend

2. **Remote Synchronization**:
   - Changes are sent via WebSocket
   - Backend processes changes and updates storage
   - Changes are broadcast to other connected clients
   - Clients receive updates and apply them locally

## Event System

The map system uses a robust event system for communication between components:

- **MapChanged**: Fired when the active map changes
- **AnnotationAdded/Updated/Removed**: Fired when annotations change
- **LayerVisibilityChanged**: Fired when layer visibility changes
- **MapViewModeChanged**: Fired when the interaction mode changes

## Data Persistence

Map data is persisted through:

1. **Local Storage**: Save and load from PlayerPrefs or local files
2. **Backend Storage**: REST API for long-term storage
3. **Real-time Sync**: WebSockets for cross-client synchronization

## Current Implementation Status

The system has a solid foundation with most core components implemented:

- ✅ Basic map display and navigation
- ✅ Annotation creation and placement
- ✅ Layer management
- ✅ Backend connectivity via REST and WebSockets

Areas that could be enhanced:

- 🔄 Advanced filtering for annotations
- 🔄 Full-featured search functionality
- 🔄 Comprehensive error handling
- 🔄 Performance optimization for large maps
- 🔄 Complete test coverage

## Integration Points

The map system integrates with other game systems through:

- **Event System**: For notifying other systems of map-related events
- **Entity References**: For linking annotations to game entities
- **UI Framework**: For consistent presentation with the rest of the game

## Future Enhancements

Potential improvements to consider:

1. **Advanced Annotations**: Support for lines, areas, and paths
2. **Map Measurements**: Tools for measuring distances and areas
3. **Custom Rendering**: Support for different map styles
4. **Offline Mode**: Enhanced functionality during disconnection
5. **Map Versions**: Tracking changes and reverting to previous versions

## Conclusion

The Visual DM Map System provides a robust foundation for interactive maps in the game. Its modular architecture allows for easy extension and maintenance, while its backend integration ensures data persistence and real-time collaboration. 