# Character Sheet UI Implementation

## Overview

The Character Sheet UI provides a comprehensive interface for viewing and editing character data in Visual DM. It follows the MVC (Model-View-Controller) design pattern and supports a tabbed interface for organizing different categories of character information.

## Features

- Display of character basic info (name, description, faction)
- Stats display and editing
- Inventory management
- Abilities display and editing  
- Equipment management
- Character background display and editing
- Tabbed interface for better organization
- Edit mode for making changes
- Real-time updates via WebSocket

## Architecture

The Character Sheet UI follows the MVC architecture pattern:

### Model (CharacterSheetModel)

Stores character data and provides methods to manipulate it:

- Basic properties (name, description, faction)
- Stats dictionary
- Inventory dictionary
- Abilities dictionary
- Equipment dictionary
- Background text
- Methods for modifying data
- Property change notifications

### View (CharacterSheetView)

Responsible for rendering the UI and handling user input:

- Tab system for organization
- Display containers for different data types
- Input fields for editing
- Buttons for actions
- Event handling

### Controller (CharacterSheetController)

Mediates between the model and view:

- Initializes view and model
- Handles view events
- Updates model based on user input
- Updates view based on model changes
- Manages WebSocket communication

## Tab Organization

The Character Sheet UI organizes information into the following tabs:

1. **Stats** - Character attributes and statistics
2. **Inventory** - Items the character possesses
3. **Abilities** - Special skills and powers
4. **Equipment** - Gear the character has equipped
5. **Background** - Character history and other details

## Usage

### Creating a Character Sheet

```csharp
// Get a reference to the factory
CharacterSheetFactory factory = FindObjectOfType<CharacterSheetFactory>();

// Create a character sheet for a specific character
CharacterSheetController controller = factory.CreateCharacterSheet(character);
```

### Accessing Through UI Manager

```csharp
// Show character sheet using the UI Manager
GameObject sheet = UIManager.Instance.ShowCharacterSheet(character);

// Close a specific character sheet
UIManager.Instance.CloseCharacterSheet(character.Id);

// Close all character sheets
UIManager.Instance.CloseAllCharacterSheets();
```

## Demo

A demo scene is included to demonstrate the Character Sheet UI functionality:

1. Open the `CharacterSheetDemoScene.unity` scene in the editor
2. Run the scene
3. Click the "Show Character Sheet" button to display a sample character sheet
4. Test the different tabs and functionality

## Extending the Character Sheet

To add new types of data to the Character Sheet:

1. Add properties to the `Character` class
2. Add corresponding properties to the `CharacterSheetModel`
3. Create UI elements in the `CharacterSheetView`
4. Update the `CharacterSheetController` to handle the new data
5. Consider adding a new tab if the data warrants its own section

## WebSocket Integration

The Character Sheet UI automatically syncs changes with the backend via WebSocket:

1. Changes made in the UI update the local Character object
2. The Controller sends update messages via WebSocket
3. When a character is updated on the server, the UI is refreshed

## Future Improvements

- Support for character images/avatars
- Custom stat types from JSON definitions
- Ability to add/remove custom properties
- Performance optimizations for large character datasets
- Mobile-friendly responsive layout 