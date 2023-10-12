from marshmallow import  fields
from .base_schemas import PlainSchema


class NotificationSchema(PlainSchema):
    postId = fields.String()
    username = fields.String()
    profileImageUrl = fields.String()
    timestamp = fields.String()
    type = fields.Integer()
    uid = fields.String()

    # postId: String?
    # username: String
    # profileImageUrl: String
    # timestamp: String
    # type: Int
    # uid: String