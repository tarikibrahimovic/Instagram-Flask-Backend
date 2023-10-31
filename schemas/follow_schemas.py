from marshmallow import Schema, fields


class CheckFollowingSchema(Schema):
    is_following = fields.String(required=True)
