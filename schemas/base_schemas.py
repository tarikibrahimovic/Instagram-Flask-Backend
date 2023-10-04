from marshmallow import Schema, fields, post_dump
from datetime import datetime


class PlainSchema(Schema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_dump
    def convert_datetime(self, data, **kwargs):
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.strptime(data['created_at'], "%Y-%m-%dT%H:%M:%S.%f")
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = datetime.strptime(data['updated_at'], "%Y-%m-%dT%H:%M:%S.%f")