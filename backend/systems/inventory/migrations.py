"""
Database migrations for inventory system.

This module handles data migrations for the inventory system models.
"""

from typing import List, Dict, Any
import logging
from datetime import datetime

from backend.core.database import db
from backend.systems.inventory.models import Item, Inventory, InventoryItem

# Configure logger
logger = logging.getLogger(__name__)

def migrate_item_model_add_stackable_fields():
    """
    Add stackable item fields to the Item model.
    
    This migration adds the following fields:
    - is_stackable
    - max_stack_size
    - apply_weight_when_equipped
    - can_be_equipped
    - equipment_slot
    
    Returns:
        Success message
    """
    try:
        # Check if we need to add the columns
        # This is a SQLAlchemy specific approach
        inspector = db.inspect(db.engine)
        
        columns = [c['name'] for c in inspector.get_columns('items')]
        new_columns = [
            'is_stackable',
            'max_stack_size',
            'apply_weight_when_equipped',
            'can_be_equipped',
            'equipment_slot'
        ]
        
        # Determine which columns to add
        columns_to_add = [col for col in new_columns if col not in columns]
        
        if not columns_to_add:
            return "No columns to add - migration already completed"
            
        # SQLite doesn't support adding columns with default values directly
        # We'll use raw SQL for a more direct approach
        for column in columns_to_add:
            if column == 'is_stackable':
                db.session.execute(db.text("ALTER TABLE items ADD COLUMN is_stackable BOOLEAN DEFAULT TRUE"))
            elif column == 'max_stack_size':
                db.session.execute(db.text("ALTER TABLE items ADD COLUMN max_stack_size INTEGER"))
            elif column == 'apply_weight_when_equipped':
                db.session.execute(db.text("ALTER TABLE items ADD COLUMN apply_weight_when_equipped BOOLEAN DEFAULT TRUE"))
            elif column == 'can_be_equipped':
                db.session.execute(db.text("ALTER TABLE items ADD COLUMN can_be_equipped BOOLEAN DEFAULT FALSE"))
            elif column == 'equipment_slot':
                db.session.execute(db.text("ALTER TABLE items ADD COLUMN equipment_slot VARCHAR(50)"))
        
        db.session.commit()
        
        # Now set stackable flag based on item category
        # Weapons, armor, unique items aren't stackable by default
        # Consumables, resources, etc. are stackable
        non_stackable_categories = ['WEAPON', 'ARMOR', 'UNIQUE', 'QUEST']
        
        items = db.session.query(Item).all()
        updated_count = 0
        
        for item in items:
            if item.category in non_stackable_categories:
                item.is_stackable = False
                
                # Weapons and armor are equipped by default
                if item.category in ['WEAPON', 'ARMOR']:
                    item.can_be_equipped = True
                    # Set equipment slot based on properties or category
                    if item.properties and 'slot' in item.properties:
                        item.equipment_slot = item.properties['slot']
                    elif item.category == 'WEAPON':
                        item.equipment_slot = 'WEAPON'
                    elif item.category == 'ARMOR':
                        item.equipment_slot = 'BODY'
                
                updated_count += 1
            
            # Set reasonable max stack sizes by category
            if item.is_stackable:
                if item.category == 'RESOURCE':
                    item.max_stack_size = 100
                elif item.category == 'CONSUMABLE':
                    item.max_stack_size = 20
                elif item.category == 'AMMO':
                    item.max_stack_size = 50
                else:
                    item.max_stack_size = 10
        
        db.session.commit()
        
        return f"Added stackable fields to items table and updated {updated_count} items with appropriate values"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error migrating item model: {str(e)}")
        return f"Error: {str(e)}"

def migrate_inventory_model_add_weight_fields():
    """
    Add weight validation fields to the Inventory model.
    
    This migration adds the following fields:
    - count_equipped_weight
    - is_public
    
    Returns:
        Success message
    """
    try:
        # Check if we need to add the columns
        inspector = db.inspect(db.engine)
        
        columns = [c['name'] for c in inspector.get_columns('inventories')]
        new_columns = [
            'count_equipped_weight',
            'is_public'
        ]
        
        # Determine which columns to add
        columns_to_add = [col for col in new_columns if col not in columns]
        
        if not columns_to_add:
            return "No columns to add - migration already completed"
            
        # Add the columns
        for column in columns_to_add:
            if column == 'count_equipped_weight':
                db.session.execute(db.text("ALTER TABLE inventories ADD COLUMN count_equipped_weight BOOLEAN DEFAULT TRUE"))
            elif column == 'is_public':
                db.session.execute(db.text("ALTER TABLE inventories ADD COLUMN is_public BOOLEAN DEFAULT FALSE"))
        
        db.session.commit()
        
        # Update inventory settings based on inventory_type
        inventories = db.session.query(Inventory).all()
        updated_count = 0
        
        for inventory in inventories:
            # Merchant inventories are public by default
            if inventory.inventory_type in ['MERCHANT', 'SHOP', 'STORE']:
                inventory.is_public = True
                updated_count += 1
        
        db.session.commit()
        
        return f"Added weight validation fields to inventories table and updated {updated_count} inventories"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error migrating inventory model: {str(e)}")
        return f"Error: {str(e)}"

def run_migrations():
    """
    Run all inventory system migrations.
    
    Returns:
        List of migration results
    """
    results = []
    
    # Add stackable fields to Item model
    item_result = migrate_item_model_add_stackable_fields()
    results.append(f"Item model migration: {item_result}")
    
    # Add weight fields to Inventory model
    inventory_result = migrate_inventory_model_add_weight_fields()
    results.append(f"Inventory model migration: {inventory_result}")
    
    return results 