# Inventory System Tests

This directory contains tests for the Visual DM inventory system.

## Test Files

- **test_inventory_models.py**: Tests the core models (Item, Inventory, InventoryItem)
- **test_inventory_validator.py**: Tests validation logic for inventory operations
- **test_inventory_service.py**: Tests the inventory service and business logic

## Test Coverage

### Model Tests
The model tests ensure proper data structure, relationships, and persistence:

- Item creation and properties
- Inventory creation and capacity/weight constraints
- Inventory item relationships and stacking
- Weight calculation and limits
- Item addition and removal mechanics
- Defaults and edge cases

### Validator Tests
The validator tests check the validation logic for inventory operations:

- ValidationResult class behavior
- Inventory existence validation
- Item existence validation
- Add item validation (capacity, weight limits, stackable items)
- Remove item validation (existence, quantity)
- Transfer item validation (source, target, quantities)
- Equipment validation (equip/unequip operations)

### Service Tests
The service tests verify the business logic and service layer:

- Inventory creation (character, container, shop)
- Item operations (add, remove, calculate stats)
- Equipment operations (equip, unequip)
- Stack operations (split, merge)
- Transfer operations between inventories
- Import/export functionality
- Inventory data repair

## Running Tests

To run all inventory tests:

```bash
pytest backend/tests/systems/inventory
```

To run a specific test file:

```bash
pytest backend/tests/systems/inventory/test_inventory_models.py
```

To run a specific test:

```bash
pytest backend/tests/systems/inventory/test_inventory_models.py::TestInventoryModel::test_add_item
```

## Test Design Principles

The inventory system tests follow these key principles:

1. **Isolation**: Tests use SQLite in-memory databases for model tests and mock external dependencies for service/validator tests
2. **Comprehensive Coverage**: Tests aim for high coverage of business logic and edge cases
3. **Error Handling**: Tests validate proper error handling and validation
4. **Performance**: Tests avoid unnecessary operations and use efficient patterns
5. **Maintainability**: Tests follow a consistent structure and naming convention

## Mocking Strategy

- **Model Tests**: Use in-memory SQLite database to test actual model operations
- **Validator Tests**: Mock repositories to isolate validation logic
- **Service Tests**: Mock validators, repositories, and operations to test service coordination

## Integration Points

The inventory system integrates with:

- Character system (character equipment)
- Equipment system (equip/unequip mechanics)
- Event system (inventory events)
- Crafting system (item creation)

These integration points are tested with mocks to isolate the inventory system functionality. 