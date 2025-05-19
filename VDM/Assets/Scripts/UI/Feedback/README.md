# UI/Feedback Directory

## Purpose
This directory contains all runtime feedback systems for the project, including:
- **AudioFeedbackModule.cs**: Handles all audio feedback for user actions and game events.
- **VisualFeedbackModule.cs**: Manages visual feedback such as screen shake, particle effects, and visual cues.
- **HapticFeedbackModule.cs**: Provides haptic (vibration) feedback for supported platforms.
- **FeedbackManager.cs**: Central manager for coordinating feedback modules and applying user settings.

All feedback modules are designed to be runtime-only, with no UnityEditor or scene dependencies. This folder is the central place for extending or modifying how the game provides feedback to the player through UI, audio, or haptics.

## Extensibility
To add new feedback types or modify existing ones, add or update modules in this directory and register them with the `FeedbackManager`. 