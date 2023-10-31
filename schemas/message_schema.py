from marshmallow import Schema, fields


class SendMessageSchema(Schema):
    message = fields.String(required=True)
    receiver_id = fields.Integer(required=True)
    sender_id = fields.Integer(required=False)
    timestamp = fields.String(required=False)
