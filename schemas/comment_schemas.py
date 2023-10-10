from marshmallow import Schema, fields


class CommentSchema(Schema):
    id = fields.Integer(dump_only=True)
    post_id = fields.Integer(required=True)
    comment = fields.String(required=True)
    created_at = fields.String(dump_only=True)
