from marshmallow import Schema, fields, validate


class CheckFollowingSchema(Schema):
    is_following = fields.Boolean(required=True)
