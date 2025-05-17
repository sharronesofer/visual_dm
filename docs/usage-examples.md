# Usage Examples and Best Practices

## Table of Contents
1. [Overview](#overview)
2. [Common Operations](#common-operations)
3. [Complete Workflow Example](#complete-workflow-example)
4. [Configuration Examples](#configuration-examples)
5. [Best Practices](#best-practices)
6. [Extension Guidelines](#extension-guidelines)
7. [Custom Attribute Implementation](#custom-attribute-implementation)
8. [Event Handling and Subscription](#event-handling-and-subscription)
9. [References](#references)

---

## Overview
This section provides practical code examples and best practices for using and extending the inventory management system.

## Common Operations
```python
# Create a new inventory for a player
inv = InventoryRepository.create_inventory(owner_id=1, owner_type='player')

# Add an item to the inventory
item = ...  # Fetch or create item
InventoryRepository.add_item_to_inventory(inv.id, item.id, quantity=3)

# Remove an item from the inventory
InventoryRepository.remove_item_from_inventory(inventory_item_id=42)

# Transfer items between inventories
InventoryRepository.transfer_item(source_inventory_id=1, target_inventory_id=2, item_id=5, quantity=2)

# Query all inventories for a user
snapshots = InventoryQueryInterface.get_inventory_by_user(user_id=1)
```

## Complete Workflow Example
```python
# 1. Create inventory and items
inv = InventoryRepository.create_inventory(owner_id=2, owner_type='npc', capacity=10)
item = ...  # Create or fetch item

# 2. Add items
InventoryRepository.add_item_to_inventory(inv.id, item.id, quantity=10)

# 3. Validate and transfer
InventoryValidator.validate_transfer_item(source_container, target_container, item.id, 5)
InventoryRepository.transfer_item(source_container.inventory.id, target_container.inventory.id, item.id, 5)

# 4. Backup and restore
InventoryRepository.backup_inventories('backup.json')
InventoryRepository.restore_inventories('backup.json')
```

## Configuration Examples
- **Log Level:** Set `inventory_logger.setLevel(logging.DEBUG)` for verbose output.
- **Backup Rotation:** Use `InventoryRepository.rotate_backups('backups/', max_backups=7)` to keep 7 backups.
- **Custom Event Subscription:**
  ```python
  def on_rare_item(event, **kwargs):
      print('Rare item acquired:', kwargs)
  InventoryEventBus.subscribe('significant_event', on_rare_item)
  ```

## Best Practices
- Always validate operations before executing them, especially for user input.
- Use batch operations for efficiency when adding/removing many items.
- Regularly backup inventories and test recovery procedures.
- Subscribe to events for real-time integration with other systems.
- Use the query interface for read-only access in external systems.
- Extend via subclassing or event bus rather than modifying core logic.

## Extension Guidelines
- **Subclass InventoryContainer** for specialized inventory types (e.g., timed, decaying, restricted).
- **Add new validation rules** by extending InventoryValidator.
- **Emit new events** via InventoryEventBus for custom integration needs.
- **Implement custom attributes** by extending AttributeContainer.

## Custom Attribute Implementation
```python
class CustomAttributeContainer(AttributeContainer):
    def validate(self):
        super().validate()
        # Add custom validation logic here

item = ...
item.attributes = CustomAttributeContainer({'magic_power': 50, 'element': 'fire'})
item.attributes.validate()
```

## Event Handling and Subscription
```python
def on_item_value_change(item_id, new_value, user_id, **kwargs):
    print(f'Item {item_id} value changed to {new_value} by user {user_id}')

InventoryEventBus.subscribe('item_value_change', on_item_value_change)

# Emitting an event
InventoryEventBus.emit('item_value_change', item_id=1, new_value=200, user_id=42)
```

## References
- [System Architecture](system-architecture.md)
- [Core Components and Class Structure](core-components.md)
- [API Reference and Integration Points](api-reference.md)
- [Testing Strategy and Documentation Index](testing.md)
