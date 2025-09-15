from marshmallow import Schema, fields


class ClassSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    code = fields.Str(required=True)
    creator_id = fields.Int(required=True, load_only=True)
    visibility = fields.Str(dump_default='private')
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
