# Cross-System Validation Framework

## Overview
The validation framework provides a robust, extensible system for enforcing business rules and data integrity across all core systems (Economic, Reputation, Inventory, and cross-system interactions). It supports:
- Modular validation rules with severity levels
- Synchronous and asynchronous validation
- Pre/post validation hooks
- Centralized configuration and rule enablement
- Event emission and error handling integration

## Architecture
- **ValidationService**: Singleton entry point for registering, configuring, and running validation.
- **ValidationRule**: Interface for all rules. Implementations exist for each system and for cross-system consistency.
- **RuleRegistry**: Manages rules by context (e.g., 'economic', 'reputation', 'inventory', 'cross-system').
- **ValidationContext**: Collects errors, warnings, info, and metadata during validation.
- **ConsistencyChecker**: Utilities for cross-system data integrity checks.
- **EventBus**: Emits `VALIDATION_EVENT` for all validation errors/warnings.
- **ErrorHandlingService**: Centralized error logging and notification for validation failures.

## Adding New Validation Rules
1. **Implement the ValidationRule interface** in `src/core/services/validationRules.ts`:
   ```typescript
   export class MyCustomRule implements ValidationRule {
     severity = ValidationSeverity.ERROR;
     validate(data: any, context?: ValidationContext): boolean | Promise<boolean> {
       // ...logic...
     }
     getErrorMessage() { return 'Custom error message.'; }
   }
   ```
2. **Register the rule** in `ValidationService` (constructor):
   ```typescript
   this.registerRule('economic', new MyCustomRule());
   this.config.enableRule('MyCustomRule');
   ```
3. **Add tests** in `src/core/services/__tests__/ValidationService.test.ts`.

## Configuring and Enabling/Disabling Rules
- Use `ValidationConfiguration` to enable or disable rules by name.
- Example:
  ```typescript
  const config = new ValidationConfiguration();
  config.enableRule('NoNegativeBalanceRule');
  config.disableRule('SufficientFundsRule');
  validationService.setConfig(config);
  ```

## Integration with System Adapters
- All system adapters (Economic, Reputation, Inventory) invoke validation before and after key operations.
- Validation errors abort the operation and emit events.
- Example (in an adapter):
  ```typescript
  const context = await validationService.validateAsync('economic', { ... });
  if (context.errors.length > 0) throw new Error(context.errors.join('; '));
  ```

## Event Emission and Error Handling
- On validation error/warning/info, a `VALIDATION_EVENT` is emitted via EventBus.
- All validation errors are logged via ErrorHandlingService for centralized notification and retry/circuit breaker logic.
- Example event payload:
  ```json
  {
    "type": "validation_event",
    "level": "error",
    "ruleName": "NoNegativeBalanceRule",
    "message": "Agent balance cannot be negative.",
    "contextData": { ... }
  }
  ```

## Synchronous and Asynchronous Validation
- Use `validateSync(context, data)` for blocking validation.
- Use `validateAsync(context, data)` for async validation (recommended for I/O or cross-system checks).
- Both methods return a `ValidationContext` with errors, warnings, and info.

## Testing and Extension Points
- All rules and the framework are covered by Jest tests in `src/core/services/__tests__/ValidationService.test.ts`.
- Add new tests for custom rules and integration scenarios.
- Use pre/post hooks for additional logic before/after validation.

## Best Practices
- Keep rules focused and composable.
- Use severity levels to distinguish between errors, warnings, and info.
- Always add tests for new rules.
- Use cross-system rules for data integrity between systems.
- Monitor validation events and error logs for operational health.

## Troubleshooting
- If validation is not working as expected, check:
  - Rule registration and enablement in `ValidationService`
  - EventBus and ErrorHandlingService integration
  - Test coverage for new rules
  - ValidationContext for detailed error messages 