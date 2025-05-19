# Visual DM Component Library (Unity C#)

## Overview
This library provides runtime-only, accessible UI components for Unity 2D, following the design system tokens. All components are generated at runtime (no scene references, no prefabs, no UnityEditor code).

## Accessibility Features (All Components)
- **Keyboard and gamepad navigation**: Tab/Shift+Tab, arrow keys, Enter/Space supported
- **Screen reader support**: All visible text is exposed via `ScreenReaderLabel`
- **Color contrast**: All colors validated at runtime for WCAG 2.1 AA/AAA
- **Colorblind modes**: Palette can be toggled at runtime (see AccessibilitySettingsPanel)
- **UI scaling**: All components respond to global scaling/font size changes
- **Focus ring**: Visual indicator for focused element
- **Multi-modal feedback**: Visual, audio, and haptic feedback supported

## Components

### Button
- **Props:**
  - `Variant`: Primary, Secondary, Danger
  - `State`: Default, Hover, Active, Disabled, Loading
  - `Label`: string
  - `ScreenReaderLabel`: string (optional, defaults to Label)
  - `OnClick`: Action
- **Accessibility:** Keyboard/gamepad navigation, focus ring, screen reader, color contrast, scaling
- **Usage:**
```csharp
var buttonObj = new GameObject("Button");
var button = buttonObj.AddComponent<Button>();
button.SetLabel("Backup Now");
button.ScreenReaderLabel = "Backup Now button";
button.SetVariant(Button.Variant.Primary);
button.OnClick = () => Debug.Log("Clicked!");
```

### InputField
- **Props:**
  - `State`: Default, Focused, Error, Disabled
  - `Placeholder`: string
  - `Value`: string
  - `ScreenReaderLabel`: string (optional, defaults to Placeholder)
  - `IsPassword`: bool
  - `OnValueChanged`: Action<string>
  - `OnSubmit`: Action
- **Accessibility:** Keyboard input, focus, screen reader, color contrast, scaling
- **Usage:**
```csharp
var inputObj = new GameObject("InputField");
var input = inputObj.AddComponent<InputField>();
input.SetPlaceholder("Enter backup name...");
input.ScreenReaderLabel = "Backup name input field";
input.OnValueChanged = val => Debug.Log(val);
input.OnSubmit = () => Debug.Log("Submitted!");
```

### Icon
- **Props:**
  - `IconName`: string (sprite name in Resources)
  - `Tint`: Color
  - `Size`: float
- **Accessibility:** Decorative only; not focusable by default. Add `ScreenReaderLabel` if used as a button or interactive element.
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
  - `ScreenReaderLabel`: string (optional, defaults to "Checkbox")
  - `OnValueChanged`: Action<bool>
- **Accessibility:** Keyboard toggle (Space/Enter), focus ring, screen reader, color contrast, scaling
- **Usage:**
```csharp
var cbObj = new GameObject("Checkbox");
var checkbox = cbObj.AddComponent<Checkbox>();
checkbox.SetChecked(true);
checkbox.ScreenReaderLabel = "Accept terms checkbox";
checkbox.OnValueChanged = val => Debug.Log($"Checked: {val}");
```

### Card
- **Props:**
  - `Elevation`: int (1-4)
  - `Width`, `Height`: float
  - `BorderRadius`: float
  - `Background`: Color
- **Accessibility:** Container only; not focusable by default. Add `ScreenReaderLabel` if used as a live region or alert.
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
- All components are keyboard, gamepad, and screen reader accessible by default.
- Colorblind mode and scaling are managed globally via the AccessibilitySettingsPanel.
- Focus rings and color contrast follow WCAG guidelines.
- No hardcoded values: all styling uses design tokens.

## Runtime-Only Architecture
- No UnityEditor or scene references
- All UI is generated and managed at runtime
- Compatible with 2D SpriteRenderer and TextMeshPro

## Extending the Library
- Add new components by following the same pattern: runtime-only, design token usage, accessibility by default.
- For custom icons, add sprites to the Resources folder and reference by name.

## Example: Creating a Backup Form (Accessible)
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
input.ScreenReaderLabel = "Backup name input field";

var buttonObj = new GameObject("StartBackupButton");
buttonObj.transform.SetParent(cardObj.transform);
var button = buttonObj.AddComponent<Button>();
button.SetLabel("Start Backup");
button.ScreenReaderLabel = "Start backup button";
button.OnClick = () => Debug.Log("Backup started!");
``` 