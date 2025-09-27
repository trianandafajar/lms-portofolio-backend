from marshmallow import Schema, fields
from app.schemas.user import UserSchema


class ClassMembershipSchema(Schema):
    id = fields.Int(dump_only=True)
    role = fields.Str()
    joined_at = fields.DateTime()
    is_active = fields.Bool()
    user = fields.Nested(UserSchema, dump_only=True)


class ClassListSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    code = fields.Str(required=True)
    visibility = fields.Str(dump_default="private")
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    creator = fields.Nested(UserSchema, dump_only=True)


class ClassDetailSchema(ClassListSchema):
    memberships = fields.List(fields.Nested(ClassMembershipSchema))
