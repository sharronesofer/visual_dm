# Visual DM Design System

## Color Palette

- **Primary:**
  - `PrimaryDefault`: #3366CC
  - `PrimaryHover`: #3F73D9
  - `PrimaryActive`: #2951A3
- **Secondary:**
  - `SecondaryDefault`: #F5A634
  - `SecondaryHover`: #FBC05C
  - `SecondaryActive`: #CC851F
- **Neutral:**
  - `Neutral100`: #FFFFFF
  - `Neutral200`: #F2F2F2
  - `Neutral300`: #D9D9D9
  - `Neutral400`: #999999
  - `Neutral500`: #4D4D4D
  - `Neutral900`: #121212

**Accessibility:**
- All color pairs must meet WCAG AA/AAA contrast for text.
- Use `Colors.MeetsWcagAA(a, b)` and `Colors.MeetsWcagAAA(a, b)` to check contrast ratios at runtime.
- Colorblind-friendly palettes are available and can be toggled at runtime (see AccessibilitySettingsPanel).
- All color assignments must use design tokens, never hardcoded values.

## Typography

- **Font Sizes:**
  - `HeadingLarge`: 32
  - `HeadingMedium`: 24
  - `HeadingSmall`: 18
  - `Body`: 14
  - `Caption`: 12
  - `Code`: 13
- **Line Heights:**
  - `HeadingLineHeight`: 1.2
  - `BodyLineHeight`: 1.4
  - `CodeLineHeight`: 1.3
- **Font Weights:**
  - `HeadingWeight`: Bold
  - `BodyWeight`: Regular
  - `CodeWeight`: Regular
- **Font Assets:**
  - Assign `Typography.SansFont` and `Typography.MonoFont` at runtime (e.g., in GameLoader)

## Spacing

- **Base Unit:** 4
- `XSmall`: 4
- `Small`: 8
- `Medium`: 16
- `Large`: 24
- `XLarge`: 32
- `Section`: 48
- `Page`: 80

## Shadows

- **Levels:**
  - `Level1`: Offset (0, -2), Blur 4, Color #0000001A
  - `Level2`: Offset (0, -4), Blur 8, Color #00000026
  - `Level3`: Offset (0, -8), Blur 16, Color #00000033
  - `Level4`: Offset (0, -12), Blur 24, Color #00000040

## Borders

- **Widths:** Thin (1), Regular (2), Thick (4)
- **Radii:** None (0), Small (4), Medium (8), Large (16)
- **Colors:** Default (Neutral300), Focus (PrimaryDefault), Error (#D93333)

## Transitions

- **Durations:** Short (0.1s), Regular (0.2s), Long (0.4s)
- **Easing:** Use `Transitions.EaseIn`, `EaseOut`, `EaseInOut` (AnimationCurve)

## Theming

- Use `ThemeManager.Instance.SetTheme(ThemeType.Light/Dark)` to switch themes at runtime.
- Subscribe to `ThemeManager.OnThemeChanged` to update UI elements.
- Store theme-specific tokens in static classes or ScriptableObjects.

## Accessibility Guidance
- **Color Contrast:** All text/background color pairs must pass WCAG 2.1 AA/AAA. Use provided helpers to validate at runtime.
- **Colorblind Modes:** Use the AccessibilitySettingsPanel to toggle colorblind-friendly palettes. All UI must remain clear and distinguishable in all modes.
- **Scaling:** All font sizes and UI elements must respond to global scaling and font size changes. Test with AccessibilitySettingsPanel.
- **Focus Indicators:** All focusable elements must display a visible focus ring using the Focus color token.
- **Screen Reader:** All text must be accessible via the `ScreenReaderLabel` property on UI components.
- **Testing:** Test theme switching, colorblind mode, and scaling in PlayMode and automated tests.

## Usage Example (C#)

```csharp
using VisualDM.UI.DesignTokens;

// Set a button background color
buttonImage.color = Colors.PrimaryDefault;

// Set text style
text.fontSize = Typography.HeadingMedium;
text.font = Typography.SansFont;

// Set padding
panel.padding = Spacing.Medium;

// Apply shadow
var shadow = Shadows.Level2;
// Use shadow.Offset, shadow.Blur, shadow.Color for custom shadow rendering

// Listen for theme changes
ThemeManager.OnThemeChanged += (theme) => { /* update UI */ };
```

## Accessibility
- All color pairs must meet WCAG AA/AAA contrast for text.
- Use provided helper methods to validate at runtime.
- Colorblind mode and scaling are managed via AccessibilitySettingsPanel.
- Test theme switching, colorblind mode, and scaling in PlayMode tests. 