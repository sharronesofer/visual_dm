# Mod Manager UI Prefabs

This folder contains prefabs for the Mod Management UI system.

## Prefabs

### ModManagerPanel

The main panel for the mod management UI. This prefab should be placed in the UI Prefabs folder and registered with the UIManager.

**Required Components:**
- ModManagementPanel
- ModManagementView
- CanvasGroup

**Structure:**
```
ModManagerPanel (GameObject)
├── Header (GameObject)
│   ├── TitleText (Text)
│   └── CloseButton (Button)
├── ModsSection (GameObject)
│   ├── SectionTitle (Text)
│   ├── ScrollView (ScrollRect)
│   │   └── Content (RectTransform) - Container for mod entries
│   └── ButtonsPanel (GameObject)
│       ├── InstallButton (Button)
│       ├── RefreshButton (Button)
│       └── SyncButton (Button)
├── ConflictsSection (GameObject)
│   ├── SectionTitle (Text)
│   ├── ScrollView (ScrollRect)
│   │   └── Content (RectTransform) - Container for conflict entries
├── DetailsPanel (GameObject)
│   ├── ModTitleText (Text)
│   ├── VersionText (Text)
│   ├── AuthorText (Text)
│   ├── DescriptionText (Text)
│   ├── DependenciesText (Text)
│   ├── CategoriesText (Text)
│   ├── EnabledToggle (Toggle)
│   └── UninstallButton (Button)
└── LoadingIndicator (GameObject)
    └── Spinner (Graphic)
```

### ModEntryPrefab

Prefab for each mod entry in the list.

**Required Components:**
- Button (for selection)
- ModEntryUI

**Structure:**
```
ModEntryPrefab (GameObject with Button)
├── NameText (Text)
├── VersionText (Text)
├── AuthorText (Text)
├── EnabledToggle (Toggle)
└── ConflictIcon (Image)
```

### ConflictEntryPrefab

Prefab for each conflict entry in the list.

**Required Components:**
- ModConflictEntryUI

**Structure:**
```
ConflictEntryPrefab (GameObject)
├── TypeText (Text)
├── DescriptionText (Text)
├── SeverityIcon (Image)
├── PriorityButton (Button) - Use highest priority mod
└── IgnoreButton (Button) - Ignore the conflict
```

## Usage

The mod management UI is designed to be used with the ModDataManager and ModSynchronizer classes. The UI is created using the ModManagementPanelFactory and can be opened using the UIManager.

```csharp
// Show the mod management panel
UIManager.Instance.ShowModManagementPanel(modDataManager, modSynchronizer, webSocketManager);
```

The UI will automatically update when mods or conflicts change.

## Customization

The UI can be customized by modifying the prefabs. The ModManagementView class can be extended to add additional functionality.

## References
- ModManagementPanel.cs - Main panel component
- ModManagementView.cs - View component for the UI
- ModManagementController.cs - Controller for handling user interactions
- ModManagementModel.cs - Data model for the UI
- ModEntryUI.cs - UI component for mod entries
- ModConflictEntryUI.cs - UI component for conflict entries 