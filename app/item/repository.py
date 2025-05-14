from app.extensions import db
from app.item.models import Item, ItemCategory, ItemType, BaseItemTemplate, PropertyDefinition, ItemProperty

class ItemRepository:
    @staticmethod
    def create_category(name, description=None):
        category = ItemCategory(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def get_category_by_id(category_id):
        return ItemCategory.query.get(category_id)

    @staticmethod
    def create_type(name, category_id, description=None):
        item_type = ItemType(name=name, category_id=category_id, description=description)
        db.session.add(item_type)
        db.session.commit()
        return item_type

    @staticmethod
    def get_type_by_id(type_id):
        return ItemType.query.get(type_id)

    @staticmethod
    def create_base_template(name, type_id, base_stats, description=None):
        template = BaseItemTemplate(name=name, type_id=type_id, base_stats=base_stats, description=description)
        db.session.add(template)
        db.session.commit()
        return template

    @staticmethod
    def get_base_template_by_id(template_id):
        return BaseItemTemplate.query.get(template_id)

    @staticmethod
    def create_item(name, type_id, category_id, base_template_id=None, base_stats=None):
        item = Item(
            name=name,
            type_id=type_id,
            category_id=category_id,
            base_template_id=base_template_id,
            base_stats=base_stats or {}
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def get_item_by_id(item_id):
        return Item.query.get(item_id)

    @staticmethod
    def update_item(item_id, **kwargs):
        item = Item.query.get(item_id)
        if not item:
            return None
        for key, value in kwargs.items():
            setattr(item, key, value)
        db.session.commit()
        return item

    @staticmethod
    def delete_item(item_id):
        item = Item.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False

    @staticmethod
    def create_property_definition(name, data_type, description=None, default_value=None, allowed_values=None, formula=None):
        prop_def = PropertyDefinition(
            name=name,
            data_type=data_type,
            description=description,
            default_value=default_value,
            allowed_values=allowed_values or [],
            formula=formula
        )
        db.session.add(prop_def)
        db.session.commit()
        return prop_def

    @staticmethod
    def get_property_definition_by_id(prop_id):
        return PropertyDefinition.query.get(prop_id)

    @staticmethod
    def create_item_property(item_id, property_id, value, is_active=1, condition=None):
        item_prop = ItemProperty(
            item_id=item_id,
            property_id=property_id,
            value=str(value),
            is_active=is_active,
            condition=condition
        )
        db.session.add(item_prop)
        db.session.commit()
        return item_prop

    @staticmethod
    def get_item_property_by_id(item_property_id):
        return ItemProperty.query.get(item_property_id)

    @staticmethod
    def update_item_property(item_property_id, **kwargs):
        item_prop = ItemProperty.query.get(item_property_id)
        if not item_prop:
            return None
        for key, value in kwargs.items():
            setattr(item_prop, key, value)
        db.session.commit()
        return item_prop

    @staticmethod
    def delete_item_property(item_property_id):
        item_prop = ItemProperty.query.get(item_property_id)
        if item_prop:
            db.session.delete(item_prop)
            db.session.commit()
            return True
        return False 