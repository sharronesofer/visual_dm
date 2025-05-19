# Accessibility Guide for Visual DM

## Overview
This document describes the accessibility features, settings, and best practices for both the Unity (C#) frontend and FastAPI (Python) backend of Visual DM. It is intended for developers, testers, and end-users.

---

## 1. Accessibility Features (Unity Frontend)

### 1.1 Keyboard and Gamepad Navigation
- All interactive UI components (Button, InputField, Checkbox, etc.) are accessible via keyboard and gamepad.
- **Tab/Shift+Tab**: Move focus between elements
- **Arrow Keys**: Navigate menus/lists
- **Enter/Space**: Activate focused element
- **Focus Ring**: Visual indicator for focused element

### 1.2 Screen Reader Support
- All visible text is exposed to screen readers at runtime.
- Each UI component has a `ScreenReaderLabel` property (defaults to visible text).
- Integrates with runtime screen reader plugin (see project dependencies).

### 1.3 Color Contrast and Colorblind Modes
- All color pairs meet WCAG 2.1 AA/AAA contrast requirements (validated at runtime).
- **Colorblind Modes**: Deuteranopia, Protanopia, Tritanopia palettes available.
- Toggle colorblind mode via settings panel or keyboard shortcut (`Ctrl+Alt+C`).

### 1.4 UI Scaling and Font Resizing
- Global UI scale and font size can be adjusted at runtime (settings panel or `Ctrl+Alt+Up/Down`).
- All UI components listen for scaling events and update accordingly.

### 1.5 Subtitles and Captions
- All audio feedback (voice, SFX) triggers a subtitle/caption event.
- Subtitles are displayed in a runtime overlay panel with timing and speaker info.
- Customizable via settings.

### 1.6 Multi-Modal Feedback
- All feedback events (success, error, warning, info) provide:
  - Visual (color flash, icon)
  - Audio (sound cue)
  - Haptic (if supported)
- Feedback modules are configurable in settings.

### 1.7 Accessibility Settings Panel
- Users can:
  - Toggle colorblind modes
  - Adjust UI scale and font size
  - Enable/disable screen reader
  - Configure feedback preferences
  - Enable/disable subtitles/captions

---

## 2. Accessibility Features (FastAPI Backend)

### 2.1 Accessible Error Messages
- All error responses are clear, concise, and actionable.
- Structured JSON: `{ "detail": ..., "code": ..., "suggestion": ... }`
- All error codes and messages are documented.

### 2.2 Validation Feedback
- Validation errors include field names, error type, and suggested fix.
- Future-proofed for localization.

### 2.3 Accessibility Support Endpoints
- Endpoints to fetch available color palettes and accessibility settings.
- Endpoints to submit user accessibility preferences for persistence.
- OpenAPI docs are accessible and well-documented.

---

## 3. Developer Guidelines
- All new UI components must:
  - Support keyboard/gamepad navigation and focus
  - Expose text for screen readers
  - Use design tokens for color and typography
  - Validate color contrast at runtime
  - Support scaling and theming
- All backend endpoints must:
  - Return accessible error/validation messages
  - Document all error codes and suggestions

---

## 4. User Guide
- Access accessibility settings from the main menu or via keyboard shortcut (`Ctrl+Alt+A`).
- Use keyboard/gamepad for all navigation and actions.
- Enable colorblind mode, scaling, and subtitles as needed.
- Contact support for additional accessibility needs.

---

## 5. Compliance
- All features are designed to meet or exceed WCAG 2.1 AA/AAA standards.
- Regular audits and user testing are conducted to ensure compliance.
- Known limitations and future improvements are tracked in project documentation.

---

## 6. References
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Unity Accessibility Plugin](https://assetstore.unity.com/packages/tools/gui/unity-accessibility-plugin-88102)
- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/) 