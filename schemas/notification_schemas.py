from marshmallow import  fields
from .base_schemas import PlainSchema


class NotificationSchema(PlainSchema):
    postId = fields.String(required=False, nullable=True)
    username = fields.String()
    profileImageUrl = fields.String()
    timestamp = fields.String()
    type = fields.Integer()
    uid = fields.String()
