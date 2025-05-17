"""
Utility functions for inventory management.
"""

from typing import Dict, List, Optional
from ..models.character import Character
from ..models.item import Item
from app.core.database import db
from app.inventory.models.inventory import Inventory, InventoryItem
from contextlib import contextmanager
import logging
from logging.handlers import RotatingFileHandler
import threading

# Configure inventory operations logger
inventory_logger = logging.getLogger('inventory.operations')
if not inventory_logger.hasHandlers():
    inventory_logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler = RotatingFileHandler('logs/inventory_operations.log', maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    inventory_logger.addHandler(file_handler)
    inventory_logger.addHandler(console_handler)

def group_equipment_by_type(items: List[Item]) -> Dict[str, List[Item]]:
    """
    Group equipment items by their type.
    
    Args:
        items: List of equipment items
        
    Returns:
        Dictionary with equipment types as keys and lists of items as values
    """
    grouped = {}
    
    for item in items:
        if item.type not in grouped:
            grouped[item.type] = []
        grouped[item.type].append(item)
        
    # Sort items within each category
    for category in grouped:
        grouped[category].sort(key=lambda x: x.name)
        
    return grouped

def calculate_total_weight(items: List[Item]) -> float:
    """
    Calculate total weight of all equipment.
    
    Args:
        items: List of equipment items
        
    Returns:
        Total weight in pounds
    """
    return sum(item.weight * item.quantity for item in items)

def get_equipped_items(items: List[Item]) -> List[Item]:
    """
    Get list of currently equipped items.
    
    Args:
        items: List of equipment items
        
    Returns:
        List of equipped items
    """
    return [item for item in items if item.is_equipped]

def can_equip_item(character: Character, item: Item) -> Dict[str, bool]:
    """
    Check if a character can equip an item.
    
    Args:
        character: Character attempting to equip
        item: Item to equip
        
    Returns:
        Dictionary with requirements and whether they are met
    """
    result = {
        "meets_proficiency": True,
        "meets_ability_score": True,
        "meets_level": True,
        "can_equip": True
    }
    
    # Check proficiency requirements
    if item.type in ["weapon", "armor"]:
        if item.name not in character.weapon_proficiencies and item.name not in character.armor_proficiencies:
            result["meets_proficiency"] = False
            
    # Check ability score requirements
    if item.ability_requirements:
        for ability, score in item.ability_requirements.items():
            if character.ability_scores[ability] < score:
                result["meets_ability_score"] = False
                break
                
    # Check level requirements
    if item.level_requirement and character.level < item.level_requirement:
        result["meets_level"] = False
        
    # Overall result
    result["can_equip"] = all([
        result["meets_proficiency"],
        result["meets_ability_score"],
        result["meets_level"]
    ])
    
    return result

class InventoryRepository:
    """
    Repository for Inventory, InventoryItem, and Item CRUD and transactional operations.
    """
    @staticmethod
    def create_inventory(owner_id, owner_type, capacity=None, weight_limit=None):
        """Create a new inventory."""
        inventory = Inventory(
            owner_id=owner_id,
            owner_type=owner_type,
            capacity=capacity,
            weight_limit=weight_limit
        )
        db.session.add(inventory)
        db.session.commit()
        inventory_logger.info('Created inventory', extra={'user_id': ..., 'operation': 'create_inventory', 'inventory_id': inventory.id, 'details': inventory.to_dict()})
        # Example: emit event for rare item acquisition
        if hasattr(inventory, 'items') and any(getattr(item, 'rarity', None) == 'legendary' for item in getattr(inventory, 'items', [])):
            InventoryEventBus.emit('significant_event', event='rare_item_acquired', inventory_id=inventory.id, user_id=..., details=inventory.to_dict())
        return inventory

    @staticmethod
    def get_inventory_by_id(inventory_id):
        """Retrieve an inventory by its ID."""
        return Inventory.query.get(inventory_id)

    @staticmethod
    def update_inventory(inventory_id, **kwargs):
        """Update inventory fields."""
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return None
        for key, value in kwargs.items():
            setattr(inventory, key, value)
        db.session.commit()
        return inventory

    @staticmethod
    def delete_inventory(inventory_id):
        """Delete an inventory and its items."""
        inventory = Inventory.query.get(inventory_id)
        if inventory:
            # Delete all inventory items first
            InventoryItem.query.filter_by(inventory_id=inventory_id).delete()
            db.session.delete(inventory)
            db.session.commit()
            return True
        return False

    @staticmethod
    def add_item_to_inventory(inventory_id, item_id, quantity=1, position=None, is_equipped=False):
        """
        Add an item to an inventory. Transactional: rolls back on error.
        """
        from app.inventory.models.inventory import Inventory, InventoryItem, Item
        with InventoryTransaction():
            inventory = Inventory.query.get(inventory_id)
            item = Item.query.get(item_id)
            if not inventory or not item:
                raise InventoryValidationError('NOT_FOUND', 'Inventory or Item not found.')
            # Validation
            InventoryValidator.validate_add_item(InventoryContainer(inventory), item, quantity)
            # Add or update InventoryItem
            inv_item = InventoryItem.query.filter_by(inventory_id=inventory_id, item_id=item_id).first()
            if inv_item:
                inv_item.quantity += quantity
            else:
                inv_item = InventoryItem(
                    inventory_id=inventory_id,
                    item_id=item_id,
                    quantity=quantity,
                    position=position,
                    is_equipped=is_equipped
                )
                db.session.add(inv_item)
            db.session.flush()
            inventory_logger.info('Added item', extra={'user_id': ..., 'operation': 'add_item', 'inventory_id': inventory.id, 'item_id': item.id, 'quantity': quantity, 'details': inv_item.to_dict()})
            # Emit event for item value change if applicable
            if hasattr(item, 'value'):
                InventoryEventBus.emit('item_value_change', item_id=item.id, new_value=item.value, user_id=...)
            # Emit event for large transaction
            if quantity > 100:
                InventoryEventBus.emit('significant_event', event='large_transaction', inventory_id=inventory.id, item_id=item.id, user_id=..., quantity=quantity, details=inv_item.to_dict())
            return inv_item

    @staticmethod
    def remove_item_from_inventory(inventory_item_id):
        """
        Remove an item from an inventory. Transactional: rolls back on error.
        """
        from app.inventory.models.inventory import InventoryItem
        with InventoryTransaction():
            inv_item = InventoryItem.query.get(inventory_item_id)
            if not inv_item:
                raise InventoryValidationError('NOT_FOUND', 'InventoryItem not found.')
            # Validation
            InventoryValidator.validate_remove_item(InventoryContainer(inv_item.inventory), inv_item.item_id, inv_item.quantity)
            db.session.delete(inv_item)
            db.session.flush()
            inventory_logger.info('Removed item', extra={'user_id': ..., 'operation': 'remove_item', 'inventory_item_id': inventory_item_id, 'details': inv_item.to_dict()})
            # Emit event for item destruction
            InventoryEventBus.emit('significant_event', event='item_destroyed', inventory_id=inv_item.inventory_id, item_id=inv_item.item_id, user_id=..., details=inv_item.to_dict())
            return True

    @staticmethod
    def update_inventory_item(inventory_item_id, **kwargs):
        """Update fields of an inventory item."""
        inventory_item = InventoryItem.query.get(inventory_item_id)
        if not inventory_item:
            return None
        for key, value in kwargs.items():
            setattr(inventory_item, key, value)
        db.session.commit()
        return inventory_item

    @staticmethod
    def list_items_in_inventory(inventory_id):
        """List all items in an inventory."""
        return InventoryItem.query.filter_by(inventory_id=inventory_id).all()

    @staticmethod
    def batch_add_items(inventory_id, items):
        """
        Batch add items to an inventory. Transactional: rolls back on error.
        """
        with InventoryTransaction():
            results = []
            for item_id, quantity in items:
                result = InventoryRepository.add_item_to_inventory(inventory_id, item_id, quantity)
                results.append(result)
            return results

    @staticmethod
    def batch_remove_items(inventory_item_ids):
        """
        Batch remove items from an inventory. Transactional: rolls back on error.
        """
        with InventoryTransaction():
            for inventory_item_id in inventory_item_ids:
                InventoryRepository.remove_item_from_inventory(inventory_item_id)
            return True

    @staticmethod
    def backup_inventories(backup_path):
        """Export all inventories and their items to a JSON file."""
        import json
        inventories = Inventory.query.all()
        data = []
        for inv in inventories:
            inv_dict = inv.to_dict()
            inv_dict['items'] = [item.to_dict() for item in inv.items]
            data.append(inv_dict)
        with open(backup_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return backup_path

    @staticmethod
    def restore_inventories(backup_path):
        """Restore inventories and items from a JSON backup file. Overwrites existing data."""
        import json
        with open(backup_path, 'r') as f:
            data = json.load(f)
        # Clear existing data
        InventoryItem.query.delete()
        Inventory.query.delete()
        db.session.commit()
        # Restore
        for inv_dict in data:
            items = inv_dict.pop('items', [])
            inventory = Inventory(**inv_dict)
            db.session.add(inventory)
            db.session.flush()  # Get inventory.id
            for item_dict in items:
                item_dict['inventory_id'] = inventory.id
                inventory_item = InventoryItem(**item_dict)
                db.session.add(inventory_item)
        db.session.commit()
        return True

    @staticmethod
    def rotate_backups(backup_dir, max_backups=5):
        """Keep only the latest N backups in the backup directory."""
        import os
        import glob
        backups = sorted(glob.glob(f"{backup_dir}/inventory_backup_*.json"), reverse=True)
        for old_backup in backups[max_backups:]:
            os.remove(old_backup)
        return True

    @staticmethod
    def transfer_item(source_inventory_id, target_inventory_id, item_id, quantity=1):
        """
        Transfer an item from one inventory to another. Transactional: rolls back on error.
        """
        from app.inventory.models.inventory import Inventory, Item
        with InventoryTransaction():
            source_inventory = Inventory.query.get(source_inventory_id)
            target_inventory = Inventory.query.get(target_inventory_id)
            item = Item.query.get(item_id)
            if not source_inventory or not target_inventory or not item:
                raise InventoryValidationError('NOT_FOUND', 'Source, target inventory, or item not found.')
            # Validation
            InventoryValidator.validate_transfer_item(
                InventoryContainer(source_inventory),
                InventoryContainer(target_inventory),
                item_id,
                quantity
            )
            # Remove from source, add to target
            InventoryRepository.remove_item_from_inventory(
                InventoryItem.query.filter_by(inventory_id=source_inventory_id, item_id=item_id).first().id
            )
            InventoryRepository.add_item_to_inventory(target_inventory_id, item_id, quantity)
            inventory_logger.info('Transferred item', extra={'user_id': ..., 'operation': 'transfer_item', 'source_inventory_id': source_inventory.id, 'target_inventory_id': target_inventory.id, 'item_id': item.id, 'quantity': quantity, 'details': ...})
            return True

class InventoryContainer:
    """
    Encapsulates inventory logic: size limits, slot organization, weight-based restrictions, and stacking logic.
    Integrates with Inventory and InventoryItem models.
    """
    def __init__(self, inventory, items=None):
        self.inventory = inventory
        self.items = items if items is not None else list(inventory.items)
        self.capacity = inventory.capacity
        self.weight_limit = inventory.weight_limit

    def get_total_weight(self):
        return sum(item.item.weight * item.quantity for item in self.items)

    def is_full(self):
        if self.capacity is None:
            return False
        return len(self.items) >= self.capacity

    def is_overweight(self, extra_weight=0):
        if self.weight_limit is None:
            return False
        return self.get_total_weight() + extra_weight > self.weight_limit

    def can_add_item(self, item, quantity=1):
        # Check slot and weight constraints
        if self.is_full():
            return False, 'Inventory is full.'
        extra_weight = item.weight * quantity
        if self.is_overweight(extra_weight):
            return False, 'Inventory overweight.'
        return True, ''

    def add_item(self, item, quantity=1):
        can_add, reason = self.can_add_item(item, quantity)
        if not can_add:
            raise ValueError(reason)
        # Stacking logic
        if getattr(item, 'is_stackable', False):
            for inv_item in self.items:
                if inv_item.item_id == item.id and inv_item.item.is_stackable:
                    stack_limit = getattr(item, 'max_stack', 1)
                    available = stack_limit - inv_item.quantity
                    to_add = min(quantity, available)
                    inv_item.quantity += to_add
                    quantity -= to_add
                    if quantity == 0:
                        return inv_item
        # Add new stack(s)
        from app.inventory.models.inventory import InventoryItem
        while quantity > 0:
            stack_size = min(getattr(item, 'max_stack', 1), quantity)
            new_inv_item = InventoryItem(
                inventory_id=self.inventory.id,
                item_id=item.id,
                quantity=stack_size
            )
            self.items.append(new_inv_item)
            quantity -= stack_size
        return True

    def remove_item(self, item_id, quantity=1):
        for inv_item in self.items:
            if inv_item.item_id == item_id:
                if inv_item.quantity < quantity:
                    raise ValueError('Not enough quantity to remove.')
                inv_item.quantity -= quantity
                if inv_item.quantity == 0:
                    self.items.remove(inv_item)
                return True
        raise ValueError('Item not found in inventory.')

    def split_stack(self, item_id, split_quantity):
        for inv_item in self.items:
            if inv_item.item_id == item_id and inv_item.quantity > split_quantity:
                from app.inventory.models.inventory import InventoryItem
                inv_item.quantity -= split_quantity
                new_stack = InventoryItem(
                    inventory_id=self.inventory.id,
                    item_id=item_id,
                    quantity=split_quantity
                )
                self.items.append(new_stack)
                return new_stack
        raise ValueError('Cannot split stack: not enough quantity or item not found.')

    def combine_stacks(self, item_id):
        stacks = [inv_item for inv_item in self.items if inv_item.item_id == item_id]
        if not stacks:
            return
        max_stack = getattr(stacks[0].item, 'max_stack', 1)
        total = sum(s.quantity for s in stacks)
        # Remove all stacks
        for s in stacks:
            self.items.remove(s)
        # Add back as few stacks as possible
        from app.inventory.models.inventory import InventoryItem
        while total > 0:
            stack_size = min(max_stack, total)
            new_stack = InventoryItem(
                inventory_id=self.inventory.id,
                item_id=item_id,
                quantity=stack_size
            )
            self.items.append(new_stack)
            total -= stack_size

    def transfer_item(self, target_container, item_id, quantity=1):
        # Remove from self, add to target
        for inv_item in self.items:
            if inv_item.item_id == item_id and inv_item.quantity >= quantity:
                can_add, reason = target_container.can_add_item(inv_item.item, quantity)
                if not can_add:
                    raise ValueError(f'Target inventory: {reason}')
                self.remove_item(item_id, quantity)
                target_container.add_item(inv_item.item, quantity)
                inventory_logger.info('Transferred item', extra={'user_id': ..., 'operation': 'transfer_item', 'source_inventory_id': self.inventory.id, 'target_inventory_id': target_container.inventory.id, 'item_id': item_id, 'quantity': quantity, 'details': ...})
                return True
        raise ValueError('Item not found or insufficient quantity for transfer.')

class InventoryValidationError(Exception):
    """
    Exception raised for inventory validation errors.
    Includes an error code and message.
    """
    def __init__(self, code, message):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message

class InventoryValidator:
    """
    Validation layer for inventory operations. Provides static methods for validating add, remove, transfer, and update operations.
    Error codes:
      - INVALID_INPUT: Input type/range/required field error
      - STATE_NEGATIVE_QUANTITY: Negative quantity detected
      - STATE_OVERSTACK: Stack size exceeded
      - STATE_OVERWEIGHT: Inventory overweight
      - STATE_OVERFLOW: Inventory slot overflow
      - INVALID_ITEM_REF: Item reference invalid or missing
      - EXPLOIT_DUPLICATION: Duplication exploit detected
      - EXPLOIT_UNDERFLOW: Underflow exploit detected
      - EXPLOIT_OVERFLOW: Overflow exploit detected
    """
    @staticmethod
    def validate_add_item(container, item, quantity):
        if not hasattr(item, 'id') or not isinstance(quantity, int) or quantity <= 0:
            raise InventoryValidationError('INVALID_INPUT', 'Invalid item or quantity for add_item.')
        if container.is_full():
            raise InventoryValidationError('STATE_OVERFLOW', 'Inventory is full.')
        extra_weight = getattr(item, 'weight', 0) * quantity
        if container.is_overweight(extra_weight):
            raise InventoryValidationError('STATE_OVERWEIGHT', 'Inventory overweight.')
        if getattr(item, 'is_stackable', False):
            max_stack = getattr(item, 'max_stack', 1)
            for inv_item in container.items:
                if inv_item.item_id == item.id and inv_item.item.is_stackable:
                    if inv_item.quantity + quantity > max_stack:
                        raise InventoryValidationError('STATE_OVERSTACK', 'Stack size exceeded.')
        return True

    @staticmethod
    def validate_remove_item(container, item_id, quantity):
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            raise InventoryValidationError('INVALID_INPUT', 'Invalid item_id or quantity for remove_item.')
        for inv_item in container.items:
            if inv_item.item_id == item_id:
                if inv_item.quantity < quantity:
                    raise InventoryValidationError('STATE_NEGATIVE_QUANTITY', 'Not enough quantity to remove.')
                return True
        raise InventoryValidationError('INVALID_ITEM_REF', 'Item not found in inventory.')

    @staticmethod
    def validate_transfer_item(source_container, target_container, item_id, quantity):
        # Validate remove from source
        InventoryValidator.validate_remove_item(source_container, item_id, quantity)
        # Validate add to target
        item = None
        for inv_item in source_container.items:
            if inv_item.item_id == item_id:
                item = inv_item.item
                break
        if not item:
            raise InventoryValidationError('INVALID_ITEM_REF', 'Item not found for transfer.')
        InventoryValidator.validate_add_item(target_container, item, quantity)
        return True

    @staticmethod
    def validate_update_item(container, item_id, new_quantity):
        if not isinstance(item_id, int) or not isinstance(new_quantity, int) or new_quantity < 0:
            raise InventoryValidationError('INVALID_INPUT', 'Invalid item_id or new_quantity for update_item.')
        for inv_item in container.items:
            if inv_item.item_id == item_id:
                if new_quantity > getattr(inv_item.item, 'max_stack', 1):
                    raise InventoryValidationError('STATE_OVERSTACK', 'Stack size exceeded on update.')
                return True
        raise InventoryValidationError('INVALID_ITEM_REF', 'Item not found in inventory for update.')

class InventoryTransaction:
    """
    Context manager for inventory operations, providing transaction management and rollback on error.
    Usage:
        with InventoryTransaction():
            # perform inventory operations
    """
    def __enter__(self):
        self.session = db.session
        self.session.begin_nested()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        return False  # propagate exception if any

class RecoveryManager:
    """
    Utility for detecting and fixing inventory data inconsistencies, and recovering from unrecoverable errors.
    """
    @staticmethod
    def detect_inconsistencies():
        """Scan for negative quantities, orphaned items, and broken references. Returns a list of issues found."""
        from app.inventory.models.inventory import Inventory, InventoryItem, Item
        issues = []
        # Negative quantities
        for inv_item in InventoryItem.query.all():
            if inv_item.quantity < 0:
                issues.append({'type': 'NEGATIVE_QUANTITY', 'inventory_item_id': inv_item.id})
            if not inv_item.inventory or not inv_item.item:
                issues.append({'type': 'ORPHANED_ITEM', 'inventory_item_id': inv_item.id})
        # Broken references
        for inv in Inventory.query.all():
            for inv_item in inv.items:
                if not inv_item.item:
                    issues.append({'type': 'BROKEN_ITEM_REF', 'inventory_id': inv.id, 'inventory_item_id': inv_item.id})
        return issues

    @staticmethod
    def fix_inconsistencies(auto_fix=True):
        """Attempt to fix detected inconsistencies. If auto_fix is False, only report issues."""
        issues = RecoveryManager.detect_inconsistencies()
        from app.inventory.models.inventory import InventoryItem
        fixed = []
        with InventoryTransaction():
            for issue in issues:
                if issue['type'] == 'NEGATIVE_QUANTITY' and auto_fix:
                    inv_item = InventoryItem.query.get(issue['inventory_item_id'])
                    if inv_item:
                        inv_item.quantity = max(0, inv_item.quantity)
                        fixed.append(issue)
                elif issue['type'] in ('ORPHANED_ITEM', 'BROKEN_ITEM_REF') and auto_fix:
                    inv_item = InventoryItem.query.get(issue['inventory_item_id'])
                    if inv_item:
                        db.session.delete(inv_item)
                        fixed.append(issue)
        db.session.flush()
        return {'issues': issues, 'fixed': fixed}

    @staticmethod
    def recover_inventory(backup_path):
        """Restore all inventories from a backup file if unrecoverable errors are found."""
        return InventoryRepository.restore_inventories(backup_path)

# Example usage in InventoryRepository (add to docstring):
# with InventoryTransaction():
#     InventoryRepository.add_item_to_inventory(...)
#     InventoryRepository.remove_item_from_inventory(...)
#     # If any error occurs, all changes are rolled back 

# Integration hooks for external systems (observer pattern)
class InventoryEventBus:
    """
    Simple event bus for inventory integration points (Economic Agent, Reputation, etc.).
    Subscribers can register callbacks for specific event types.
    """
    _subscribers = {}

    @classmethod
    def subscribe(cls, event_type, callback):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)

    @classmethod
    def emit(cls, event_type, **kwargs):
        for cb in cls._subscribers.get(event_type, []):
            cb(**kwargs)

# Example event emission in InventoryRepository/Container:
# InventoryEventBus.emit('item_value_change', item_id=..., new_value=..., user_id=...)
# InventoryEventBus.emit('significant_event', event='rare_item_acquired', inventory_id=..., item_id=..., user_id=..., details=...)

# In Economic Agent and Reputation systems, register callbacks:
# InventoryEventBus.subscribe('item_value_change', economic_agent_callback)
# InventoryEventBus.subscribe('significant_event', reputation_system_callback)

class InventoryQueryInterface:
    """
    Thread-safe, read-only query interface for external systems to access inventory data.
    Provides filtered views based on permissions and requirements.
    """
    _lock = threading.RLock()

    @staticmethod
    def get_inventory_by_user(user_id):
        """Return a snapshot of all inventories owned by the given user ID."""
        from app.inventory.models.inventory import Inventory
        with InventoryQueryInterface._lock:
            return [inv.to_dict() for inv in Inventory.query.filter_by(owner_id=user_id).all()]

    @staticmethod
    def get_item_history(item_id):
        """Return a list of log entries for the given item ID (from inventory operations log)."""
        import os
        log_path = 'logs/inventory_operations.log'
        if not os.path.exists(log_path):
            return []
        with InventoryQueryInterface._lock, open(log_path) as f:
            return [line for line in f if f'item_id": {item_id}' in line] 