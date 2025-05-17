# Emotion Dashboard & Mapping Editor

This module provides UI tools for monitoring emotional states and configuring emotion-to-behavior mappings in real time.

## Components

- **EmotionDashboard.tsx**: Displays a real-time table of all entities and their current emotions, with filtering and search. Uses MUI for layout and styling.
- **EmotionMappingEditor.tsx**: Node-based editor for visually connecting emotions to behaviors. Supports drag-and-drop, editable thresholds, and connection lines (to be implemented).

## Usage

Import and use the components in your main app or route:

```tsx
import { EmotionDashboard, EmotionMappingEditor } from './emotionDashboard';

<EmotionDashboard />
<EmotionMappingEditor />
```

## API Integration

- Fetches emotion data from `/api/emotions` and `/api/emotions/gpt-context`.
- Intended for integration with the backend emotion API and WebSocket for real-time updates.

## Roadmap

- Add real-time updates via WebSocket
- Implement full node-based editor UI
- Add simulation and preset management panels
- Improve entity-level emotion tracking 