# Shared Code Catalog

## Types

### Common Types
| Type | Current Location | Usage | Dependencies | Proposed Location |
|------|-----------------|--------|--------------|-------------------|
| `Position` | src/types/common.ts | Used for coordinates across map, character, and POI components | None | @types/common/geometry.ts |
| `ValidationResult` | src/utils/validation.ts | Used in multiple validation contexts | ValidationError | @types/validation/base.ts |
| `ValidationError` | src/utils/validation.ts, src/utils/poiValidation.ts | Used across validation utilities | None | @types/validation/base.ts |
| `ValidationRule` | src/utils/validationUtils.ts | Used for configuring validation rules | None | @types/validation/rules.ts |
| `FieldValidation` | src/utils/validationUtils.ts | Used for form field validation | None | @types/validation/fields.ts |

### Selection Types
| Type | Current Location | Usage | Dependencies | Proposed Location |
|------|-----------------|--------|--------------|-------------------|
| `SelectionType` | src/utils/SelectionManager.ts | Used for region/POI selection | None | @types/selection/base.ts |
| `SelectionAction` | src/utils/SelectionManager.ts | Used for selection operations | None | @types/selection/base.ts |
| `SelectionEvent` | src/utils/SelectionManager.ts | Used for selection event handling | SelectionType, SelectionAction | @types/selection/events.ts |
| `SelectionListener` | src/utils/SelectionManager.ts | Used for selection event listeners | SelectionEvent | @types/selection/events.ts |

### Autosave Types
| Type | Current Location | Usage | Dependencies | Proposed Location |
|------|-----------------|--------|--------------|-------------------|
| `AutosaveConfig` | src/utils/autosaveUtils.ts | Used for configuring autosave | None | @types/storage/autosave.ts |
| `AutosaveData<T>` | src/utils/autosaveUtils.ts | Used for storing autosave data | None | @types/storage/autosave.ts |

### Region Types
| Type | Current Location | Usage | Dependencies | Proposed Location |
|------|-----------------|--------|--------------|-------------------|
| `RegionUpdate` | src/types/regionMap.ts | Used for partial region updates | Region | @types/map/region.ts |
| `RenderableRegion` | src/types/regionMap.ts | Used for region rendering | Region | @types/map/region.ts |

### Statistics Types
| Type | Current Location | Usage | Dependencies | Proposed Location |
|------|-----------------|--------|--------------|-------------------|
| `POIMetrics` | src/utils/statistics.ts | Used for POI statistics | None | @types/statistics/poi.ts |

## Utilities

### Validation Utilities
| Function | Current Location | Usage | Dependencies | Proposed Location |
|----------|-----------------|--------|--------------|-------------------|
| `validationRules` | src/utils/validationUtils.ts | Common validation rules | ValidationRule | @utils/validation/rules.ts |
| `combineValidationResults` | src/utils/validationUtils.ts | Combines multiple validation results | ValidationResult | @utils/validation/helpers.ts |
| `isRenderableRegion` | src/types/regionMap.ts | Type guard for renderable regions | RenderableRegion | @utils/validation/typeGuards.ts |

### Geometry Utilities
| Function | Current Location | Usage | Dependencies | Proposed Location |
|----------|-----------------|--------|--------------|-------------------|
| `calculateDistance` | src/types/player.ts, src/utils/movementUtils.ts | Used for distance calculations | Position | @utils/geometry/distance.ts |
| `getTileKey` | src/reducers/mapReducer.ts | Used for tile identification | Position | @utils/map/tileUtils.ts |
| `calculateVisibleTiles` | src/reducers/mapReducer.ts | Used for visibility calculations | Position | @utils/map/visibilityUtils.ts |

### UI Utilities
| Function | Current Location | Usage | Dependencies | Proposed Location |
|----------|-----------------|--------|--------------|-------------------|
| `debounce` | src/utils/SelectionManager.ts | Used for event throttling | None | @utils/async/debounce.ts |
| `toKebabCase` | scripts/modules/utils.js | Used for string formatting | None | @utils/string/formatting.ts |

## Directory Structure

The proposed shared code structure:

```
shared/
├── types/
│   ├── common/
│   │   └── geometry.ts
│   ├── validation/
│   │   ├── base.ts
│   │   ├── rules.ts
│   │   └── fields.ts
│   ├── selection/
│   │   ├── base.ts
│   │   └── events.ts
│   ├── storage/
│   │   └── autosave.ts
│   ├── map/
│   │   └── region.ts
│   └── statistics/
│       └── poi.ts
└── utils/
    ├── validation/
    │   ├── rules.ts
    │   ├── helpers.ts
    │   └── typeGuards.ts
    ├── geometry/
    │   └── distance.ts
    ├── map/
    │   ├── tileUtils.ts
    │   └── visibilityUtils.ts
    ├── async/
    │   └── debounce.ts
    └── string/
        └── formatting.ts
```

## Guidelines

1. Type Organization:
   - Group related types in domain-specific files
   - Use barrel exports (index.ts) for simplified imports
   - Keep type definitions focused and single-purpose
   - Document type constraints and usage

2. Utility Organization:
   - Group utilities by domain/function
   - Keep utilities pure when possible
   - Document parameters and return types
   - Include usage examples in comments

3. Import Guidelines:
   - Use path aliases (@types/, @utils/)
   - Import from barrel files when possible
   - Avoid circular dependencies
   - Keep import paths to maximum depth of 2

4. Documentation:
   - Use JSDoc comments for all exports
   - Include examples for complex utilities
   - Document type constraints
   - Note any side effects

5. Testing:
   - Write unit tests for all utilities
   - Test edge cases and error conditions
   - Use meaningful test descriptions
   - Group related tests together 