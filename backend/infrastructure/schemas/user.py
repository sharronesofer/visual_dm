from marshmallow import Schema, fields

class PermissionSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()

class RoleSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    permissions = fields.Nested(PermissionSchema, many=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    is_active = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    roles = fields.Nested(RoleSchema, many=True) 