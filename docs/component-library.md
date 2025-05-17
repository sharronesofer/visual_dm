# Visual DM Component Library (Unity C#)

## Overview
This library provides runtime-only, accessible UI components for Unity 2D, following the design system tokens. All components are generated at runtime (no scene references, no prefabs, no UnityEditor code).

## Components

### Button
- **Props:**
  - `Variant`: Primary, Secondary, Danger
  - `State`: Default, Hover, Active, Disabled, Loading
  - `Label`: string
  - `OnClick`: Action
- **Accessibility:** Keyboard navigation (Enter/Space), focus ring, mouse input
- **Usage:**
```csharp
var buttonObj = new GameObject("Button");
var button = buttonObj.AddComponent<Button>();
button.SetLabel("Backup Now");
button.SetVariant(Button.Variant.Primary);
button.OnClick = () => Debug.Log("Clicked!");
```

### InputField
- **Props:**
  - `State`: Default, Focused, Error, Disabled
  - `Placeholder`: string
  - `Value`: string
  - `IsPassword`: bool
  - `OnValueChanged`: Action<string>
  - `OnSubmit`: Action
- **Accessibility:** Keyboard input, focus, placeholder, error state
- **Usage:**
```csharp
var inputObj = new GameObject("InputField");
var input = inputObj.AddComponent<InputField>();
input.SetPlaceholder("Enter backup name...");
input.OnValueChanged = val => Debug.Log(val);
input.OnSubmit = () => Debug.Log("Submitted!");
```

### Icon
- **Props:**
  - `IconName`: string (sprite name in Resources)
  - `Tint`: Color
  - `Size`: float
- **Usage:**
```csharp
var iconObj = new GameObject("Icon");
var icon = iconObj.AddComponent<Icon>();
icon.SetIcon("backup_icon");
icon.SetTint(Colors.PrimaryDefault);
icon.SetSize(32f);
```

### Checkbox
- **Props:**
  - `IsChecked`: bool
  - `IsFocused`: bool
  - `OnValueChanged`: Action<bool>
- **Accessibility:** Keyboard toggle (Space/Enter), focus ring, mouse input
- **Usage:**
```csharp
var cbObj = new GameObject("Checkbox");
var checkbox = cbObj.AddComponent<Checkbox>();
checkbox.SetChecked(true);
checkbox.OnValueChanged = val => Debug.Log($"Checked: {val}");
```

### Card
- **Props:**
  - `Elevation`: int (1-4)
  - `Width`, `Height`: float
  - `BorderRadius`: float
  - `Background`: Color
- **Usage:**
```csharp
var cardObj = new GameObject("Card");
var card = cardObj.AddComponent<Card>();
card.SetElevation(2);
card.SetBackground(Colors.Neutral100);
card.SetSize(400f, 200f);
// Add child GameObjects for content
```

## Accessibility Notes
- All components are keyboard and mouse accessible.
- Focus rings and color contrast follow WCAG guidelines.
- No hardcoded values: all styling uses design tokens.

## Runtime-Only Architecture
- No UnityEditor or scene references
- All UI is generated and managed at runtime
- Compatible with 2D SpriteRenderer and TextMeshPro

## Extending the Library
- Add new components by following the same pattern: runtime-only, design token usage, accessibility by default.
- For custom icons, add sprites to the Resources folder and reference by name.

## Example: Creating a Backup Form
```csharp
// Create a card for the form
var cardObj = new GameObject("BackupFormCard");
var card = cardObj.AddComponent<Card>();
card.SetSize(480f, 320f);

// Add a label, input, and button as children
var inputObj = new GameObject("BackupNameInput");
inputObj.transform.SetParent(cardObj.transform);
var input = inputObj.AddComponent<InputField>();
input.SetPlaceholder("Backup name");

var buttonObj = new GameObject("StartBackupButton");
buttonObj.transform.SetParent(cardObj.transform);
var button = buttonObj.AddComponent<Button>();
button.SetLabel("Start Backup");
button.OnClick = () => Debug.Log("Backup started!");
``` 