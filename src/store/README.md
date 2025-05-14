# Store Architecture

## Overview

This document outlines the store architecture for the Visual DM application. We use Zustand for state management, with a focus on modular, type-safe, and maintainable stores.

## Store Categories

### 1. Core Stores
- **Character Store** (`characterStore.ts`)
  - Manages character state and validation
  - Handles background and skill management
  - Provides calculated values and validation

- **POI Store** (`poiStore.ts`)
  - Manages Points of Interest state
  - Handles POI activation and chunk management
  - Integrates with persistence service

### 2. UI Stores
- **Wizard Store** (`wizardStore.ts`)
  - Manages wizard/setup flow state
  - Handles step validation and navigation
  - Coordinates with character store

## Store Design Patterns

### 1. State Structure
```typescript
interface Store<T> {
  // State
  data: T;
  isLoading: boolean;
  error: Error | null;

  // Selectors
  getters: {
    // Computed values and selectors
  };

  // Actions
  actions: {
    // State mutations and side effects
  };
}
```

### 2. Action Patterns
- **Atomic Updates**: Each action should be a single, atomic operation
- **Validation**: Include validation in actions that modify state
- **Error Handling**: Use try/catch and set error state
- **Loading States**: Set loading state for async operations
- **Persistence**: Handle persistence after state updates

Example:
```typescript
const useStore = create<Store>((set, get) => ({
  // Action with validation and error handling
  updateData: async (data: Data) => {
    set({ isLoading: true, error: null });
    try {
      const isValid = validateData(data);
      if (!isValid) throw new Error('Invalid data');
      
      set({ data });
      await persistData(data);
    } catch (error) {
      set({ error });
    } finally {
      set({ isLoading: false });
    }
  }
}));
```

### 3. Selector Patterns
- Use memoization for expensive computations
- Keep selectors pure and predictable
- Combine data from multiple slices when needed

Example:
```typescript
const useStore = create<Store>((set, get) => ({
  getters: {
    // Memoized selector
    getFilteredData: (filter: Filter) => 
      useMemo(() => {
        const { data } = get();
        return data.filter(applyFilter(filter));
      }, [get().data, filter])
  }
}));
```

### 4. Integration Patterns
- Use store combination for complex features
- Maintain store independence when possible
- Handle cross-store updates carefully

Example:
```typescript
// Combining stores
const useCombinedStore = () => {
  const store1 = useStore1();
  const store2 = useStore2();
  
  return {
    // Combined operations
    combinedAction: () => {
      store1.action();
      store2.action();
    }
  };
};
```

## Store Organization

### 1. File Structure
```
src/store/
├── README.md           # This documentation
├── index.ts           # Store exports
├── core/             # Core application stores
│   ├── characterStore.ts
│   └── poiStore.ts
├── ui/               # UI-specific stores
│   └── wizardStore.ts
└── utils/            # Store utilities
    ├── persistence.ts
    └── validation.ts
```

### 2. Store Creation Guidelines
- Use TypeScript for type safety
- Include JSDoc comments for complex logic
- Follow naming conventions consistently
- Keep stores focused and single-purpose

### 3. Testing Requirements
- Unit tests for all store actions
- Integration tests for store combinations
- Mock external dependencies
- Test error cases and edge conditions

## Best Practices

### 1. State Management
- Keep state normalized
- Avoid redundant data
- Use computed values for derived state
- Handle loading and error states consistently

### 2. Performance
- Minimize store updates
- Use shallow equality checks
- Implement proper memoization
- Profile store operations in development

### 3. Type Safety
- Define explicit interfaces
- Use strict TypeScript settings
- Avoid type assertions
- Document complex types

### 4. Error Handling
- Define error types
- Handle async errors properly
- Provide error recovery mechanisms
- Log errors appropriately

## Migration Plan

1. **Phase 1: Reorganization**
   - Move stores to appropriate directories
   - Update import paths
   - Create index files for exports

2. **Phase 2: Pattern Implementation**
   - Add loading states
   - Implement error handling
   - Add persistence integration
   - Update action patterns

3. **Phase 3: Testing**
   - Add missing tests
   - Update existing tests
   - Add performance tests
   - Document test patterns

4. **Phase 4: Documentation**
   - Update JSDoc comments
   - Create usage examples
   - Document store interactions
   - Add troubleshooting guides 