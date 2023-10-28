from marshmallow import Schema, fields, validate
from schemas.base_schemas import PlainSchema


class LoginScheme(Schema):
    email = fields.String(required=True)
    username = fields.String(required=True)
    profileImageUrl = fields.String(required=True)
    fullName = fields.String(required=True)
    id = fields.String(required=True)
    access_token = fields.String(dump_only=True)
    bio = fields.String(required=False)


class UserRequestSchema(PlainSchema):
    username = fields.Str(data_key="username", required=True, validate=validate.Length(min=1, max=64))
    email = fields.Email(data_key="email", required=True)
    password = fields.Str(data_key="password", required=True, validate=validate.Length(min=1, max=30))


class UserPatchSchema(Schema):
    old_password = fields.Str(data_key="oldPassword", required=True, validate=validate.Length(min=1, max=30))
    password = fields.Str(data_key="password", required=True, validate=validate.Length(min=1, max=30))


class RoleSchema(PlainSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)


class LoginUserSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True, load_only=True)


class RegisterSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
    email = fields.Email(required=True)
    role = fields.Nested(RoleSchema(), only=['name'], dump_only=True)


class UserSchema(Schema):
    id = fields.String(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
    fullName = fields.String(required=True)
    email = fields.Email(required=True)
    picture_url = fields.String(required=True, dump_only=True)
    # role = fields.Nested(RoleSchema(), only=['name'], dump_only=True)


class VerifySchema(Schema):
    email = fields.Email(required=True)
    code = fields.String(required=True, validate=validate.Length(min=1, max=6))


class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)
    code = fields.String(required=True, validate=validate.Length(min=1, max=6))
    password = fields.String(required=True, load_only=True)


class ForgotPasswordRequestSchema(Schema):
    email = fields.Email(required=True)


class LoginGoogleSchema(Schema):
    email = fields.Email(required=True)
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
    fullName = fields.String(required=True)
    imageURL = fields.URL(required=True)
