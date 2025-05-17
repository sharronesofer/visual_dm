# Visual_DM Unity Client

This directory contains the Unity client for the Visual_DM project, which communicates with the Python backend.

## Project Configuration

- Unity Version: 2022.3.x LTS
- Target Platforms: Windows, macOS, iOS, Android
- Key Packages:
  - Input System (for modern input handling)
  - Addressables (for asset management)
  - UniTask (for async operations)
  - Newtonsoft.Json (for serialization)
  - TextMeshPro (for UI text rendering)

## Project Structure

- `Assets/`
  - `Scripts/` - C# code organized by feature/system
    - `Core/` - Core systems and utilities
    - `API/` - Backend communication
    - `UI/` - UI components and systems
    - `SceneManagement/` - Scene loading and management
    - `Examples/` - Example usage of systems
    - `Tests/` - Test scripts for verifying functionality
  - `Prefabs/` - Reusable game objects
  - `Scenes/` - Unity scenes
  - `Resources/` - Direct-load resources
  - `Animations/` - Animation assets
  - `Materials/` - Material assets
  - `Textures/` - Texture assets
  - `AddressableAssets/` - Assets managed by the Addressables system

## Development Setup

1. Open the project using Unity Hub with Unity 2022.3.x LTS
2. Ensure all required packages are installed
3. Configure your API endpoint in `Scripts/API/ApiConfig.cs`
4. Start with the `Main` scene

## Build Configuration

The project includes configurations for the following platforms:

### Windows/macOS
- 64-bit only
- Default graphics quality: High
- Recommended specs: 8GB RAM, dedicated GPU

### Android
- Minimum API Level: 26 (Android 8.0)
- Target API Level: 33
- Architectures: ARM64

### iOS
- Minimum version: iOS 14.0
- Metal graphics API

## Quality Settings

The project includes the following quality presets:

- **Ultra**: Full effects, high resolution textures, max shadow quality
- **High**: Optimized effects, high-quality shadows
- **Medium**: Reduced shadow quality, simpler effects 
- **Low**: Minimal effects, no shadows, reduced draw distance
- **Mobile High**: Optimized for high-end mobile devices
- **Mobile Low**: Optimized for lower-end mobile devices

## Input System

The project uses Unity's new Input System package with the following action maps:

- **UI**: Menu navigation, buttons, sliders
- **Gameplay**: Character movement, interaction, combat
- **System**: Pause, settings, quit

## Scene Management

The scene management system handles loading, transitions, and dependencies with the following scenes:

- **Boot**: Initializes core systems
- **Main**: Main menu
- **Game**: Main gameplay
- **Settings**: Game settings

## Testing

PlayMode and EditMode tests are included in the `Scripts/Tests/` directory. 