# Unified Emotion Model & Mapping System

## Overview

The unified emotion model provides a centralized, extensible framework for representing, managing, and synchronizing emotional states across NPCs and systems. It consolidates emotion definitions, supports hierarchical and context-driven toggling, and enables bidirectional mapping between internal state, visual representation, and behavioral output.

**Key Components:**
- `EmotionDefinition` (base class for all emotions)
- `EmotionRegistry` (singleton for managing emotion definitions)
- `EmotionMapper` (bidirectional mapping between emotion and representations)
- `EmotionSystem` (NPC-facing system for emotion evaluation and integration)

## Architecture Diagram

```
[EmotionDefinition] <--> [EmotionRegistry] <--> [EmotionMapper] <--> [EmotionSystem]
```

## Glossary
- **Emotion Layer:** Internal, visual, or behavioral representation of emotion.
- **Mapping:** Translation between emotion and its representations.
- **Context:** Data used to drive mapping decisions (e.g., NPC type, system load).

---

## API Reference

### EmotionDefinition
- `name: string`
- `intensity: number` (0.0-1.0)
- `valence: number` (-1.0 to 1.0)
- `arousal: number` (0.0-1.0)
- `metadata: EmotionMetadata`
- `parentEmotions: EmotionDefinition[]`
- `childEmotions: EmotionDefinition[]`

### EmotionRegistry
- `registerEmotion(emotion: EmotionDefinition): void`
- `getEmotionByName(name: string): EmotionDefinition | undefined`
- `getAllEmotions(): EmotionDefinition[]`

### EmotionMapper
- `registerMapping(layer: string, mapping: IEmotionMapping): void`
- `mapToRepresentation(layer: string, emotion: EmotionDefinition, context: MappingContext): EmotionMappingResult | null`
- `mapToEmotion(layer: string, representation: any, context: MappingContext): EmotionDefinition | null`
- `subscribe(layer: string, callback: EmotionMappingChangeCallback): void`
- `loadConfig(config: Record<string, any>): void`
- `getConfig(): Record<string, any>`

### EmotionSystem
- `processInteractionEmotion(npc: NPCData, result: InteractionResult): Promise<EmotionDefinition>`
- `calculateEmotionalResponse(context: EmotionContext): EmotionDefinition`
- `mapEmotionToVisual(emotion: EmotionDefinition, context: MappingContext): any`
- `mapVisualToEmotion(visual: any, context: MappingContext): EmotionDefinition | null`
- `mapEmotionToBehavioral(emotion: EmotionDefinition, context: MappingContext): any`
- `mapBehavioralToEmotion(behavioral: any, context: MappingContext): EmotionDefinition | null`
- `loadMappingConfig(config: Record<string, any>): void`

---

## Usage Examples

### Registering a Custom Emotion
```typescript
const awe = new BasicEmotion('awe', 0.6, 0.8, 0.9, { performanceCritical: false });
EmotionRegistry.instance.registerEmotion(awe);
```

### Mapping Emotion to Visual Representation
```typescript
const visual = emotionSystem.mapEmotionToVisual(joyEmotion, { npc });
```

### Subscribing to Mapping Changes
```typescript
emotionSystem.mapper.subscribe('visual', ({ emotion, representation }) => {
  // Update animation system
});
```

### Loading Configuration
```typescript
emotionSystem.loadMappingConfig({ visual: { type: 'blendshape', params: { scale: 1.2 } } });
```

---

## Integration Points

### Animation System
- Use `mapEmotionToVisual` to drive facial blend shapes or animation parameters.
- Subscribe to visual mapping changes for real-time updates.

### Dialogue System
- Use internal emotion state to select or modulate dialogue lines.
- Optionally, map behavioral cues to influence dialogue delivery.

### AI/Behavior System
- Use `mapEmotionToBehavioral` to trigger gestures, posture, or voice modulation.
- Subscribe to behavioral mapping changes for adaptive AI.

### UI System
- Use emotion state and mapping results to display emotion indicators or overlays.

---

## Migration Guide

### Step-by-Step Migration
1. Replace legacy emotion classes with `EmotionDefinition` and register with `EmotionRegistry`.
2. Refactor direct mapping logic to use `EmotionMapper` and its interfaces.
3. Update NPC systems to use `EmotionSystem` for all emotion evaluation and mapping.
4. Move configuration to the new `loadMappingConfig` method.
5. Use event subscriptions for cross-system updates.

### Breaking Changes
- All emotion mapping must go through `EmotionMapper`.
- Legacy direct property access is deprecated.
- Notification and configuration systems are now required for full integration.

### Compatibility Utilities
- Provide shims for legacy emotion-to-visual/behavioral mapping during transition.

---

## Changelog Summary
- Introduced unified emotion model with extensible, hierarchical definitions.
- Added centralized `EmotionRegistry` and `EmotionMapper` for bidirectional mapping.
- Refactored `EmotionSystem` to support context-driven mapping and notifications.
- Added configuration and event subscription systems for cross-layer synchronization.
- Provided comprehensive documentation, migration guide, and usage examples.

---

## Contributors
- System design: [Your Team]
- Implementation: [Your Team]
- Documentation: [Your Team]

---

For further details, see the full API documentation and code comments in `src/models/EmotionDefinition.ts`, `src/models/EmotionMapper.ts`, and `src/systems/npc/EmotionSystem.ts`. 