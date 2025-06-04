# XML Documentation Style Guide for Dreamforge

## Overview
This guide defines the required XML documentation tags, formatting conventions, and usage patterns for all C# scripts in the Dreamforge project. All public classes, methods, and properties must be documented according to these standards. Special attention should be given to UI and quest-related code.

## Required XML Tags
- `<summary>`: Briefly describes the purpose of the class, method, or property.
- `<param>`: Describes each parameter for methods/constructors.
- `<returns>`: Describes the return value for methods.
- `<example>`: Provides a usage example.
- `<remarks>`: Additional information, caveats, or best practices.
- `<exception>`: Documents exceptions thrown by the method (if any).

## Formatting Conventions
- Use clear, concise language.
- Write in the third person.
- Use Markdown in `<example>` tags for code formatting.
- Cross-reference related classes/methods using `<see cref="..."/>`.
- For UI and quest code, document runtime generation patterns and event hooks.

## Example: UI Component
```csharp
/// <summary>
/// Displays and manages the user profile panel at runtime.
/// </summary>
/// <remarks>
/// This panel is generated at runtime by <see cref="UIManager"/>. It subscribes to user data update events.
/// </remarks>
/// <example>
/// <code>
/// var panel = UIManager.Instance.CreateUserProfilePanel(userId);
/// panel.OnProfileUpdated += HandleProfileUpdate;
/// </code>
/// </example>
public class UserProfilePanel : MonoBehaviour { ... }
```

## Example: Quest System
```csharp
/// <summary>
/// Represents a quest and manages its state transitions.
/// </summary>
/// <param name="questId">The unique identifier for the quest.</param>
/// <returns>True if the quest is active; otherwise, false.</returns>
/// <remarks>
/// Triggers <see cref="OnQuestCompleted"/> when all objectives are met.
/// </remarks>
/// <example>
/// <code>
/// var quest = new Quest("quest_001");
/// quest.OnQuestCompleted += () => Debug.Log("Quest complete!");
/// </code>
/// </example>
public class Quest { ... }
```

## Best Practices
- Document all public APIs, including runtime-generated components.
- Always provide a usage example for UI and quest code.
- Use `<remarks>` for lifecycle, event, and integration notes.
- Keep documentation up to date with code changes.

## Anti-Patterns to Avoid
- Omitting documentation for public members.
- Using vague or generic summaries (e.g., "Does something").
- Failing to update documentation after refactoring.

## Maintenance
- All new code must follow this guide.
- Documentation coverage is checked in CI.
- Update this guide as new patterns emerge. 