import random
from datetime import datetime
from os import abort

from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt

import schemas
from cloudinary.uploader import upload as cloudinary_upload
from models.blocklist import BlockListModel as TokenBlocklist

from db import db
import models
from enums import RoleNames
from schemas import UserSchema, LoginScheme
from passlib.hash import pbkdf2_sha256
from flask_smorest import abort
from flask_mail import Mail, Message
from flask import current_app


def register(data):
    if (db.session.execute(db.select(models.UserModel).where(models.UserModel.username == data["username"]))
            .scalar_one_or_none()):
        abort(400, message="Username already exists.")

    user_role = (db.session.execute(db.select(models.RoleModel).where(models.RoleModel.name == RoleNames.USER)).
                 scalar_one_or_none())
    if not user_role:
        abort(500, message="User role not found.")
    random_number = random.randint(100000, 999999)
    user = models.UserModel(
        username=data["username"],
        password=pbkdf2_sha256.hash(data["password"]),
        email=data["email"],
        role_id=user_role.id,
        verified_at=str(random_number)
    )
    try:
        user.save_to_db()
        send_mail(data["email"], random_number)
    except Exception as e:
        abort(500, message=str(e))
    return UserSchema().dump(user), 201


def login(data):
    user = db.session.execute(db.select(models.UserModel)
                              .where(models.UserModel.username == data["username"])).scalar_one_or_none()
    if not user:
        abort(400, message="User not found.")
    if not pbkdf2_sha256.verify(data["password"], user.password):
        abort(400, message="Invalid password.")
    access_token = create_access_token(identity={'user_id': user.id, 'role': user.role.name.value}, fresh=True)
    refresh_token = create_refresh_token(identity={'user_id': user.id, 'role': user.role.name.value})
    print(user, access_token)

    return LoginScheme().dump({"access_token": access_token, "refresh_token": refresh_token}), 200


def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    now = datetime.utcnow()
    db.session.add(TokenBlocklist(jti=jti, type=ttype, created_at=now))
    db.session.commit()
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")


def change_password():
    current_user_id = get_jwt_identity().get("user_id")
    user = db.get_or_404(models.UserModel, current_user_id)

    user_patch_schema = schemas.UserPatchSchema()
    errors = user_patch_schema.validate(request.json)
    if errors:
        return jsonify(errors), 400

    old_password = request.json.get('oldPassword')
    new_password = request.json.get('password')

    if not pbkdf2_sha256.verify(old_password, user.password):
        return jsonify(error="Pogrešna stara lozinka"), 400

    user.password = pbkdf2_sha256.hash(new_password)

    try:
        user.save_to_db()
    except Exception as e:
        abort(500, message=str(e))

    return jsonify(message="Lozinka uspešno promenjena"), 200


def upload():
    file = request.files['file']
    user_id = get_jwt_identity().get("user_id")
    user = db.session.execute(db.select(models.UserModel).where(models.UserModel.id == user_id)).scalar_one_or_none()
    if file:
        # Upload the image to Cloudinary
        result = cloudinary_upload(file)  # Use upload() from cloudinary.uploader
        # Access the URL of the uploaded image
        image_url = result['secure_url']
        user.picture_url = image_url
        try:
            user.save_to_db()
        except Exception as e:
            abort(500, message=str(e))
        return jsonify(image_url=image_url), 200
    else:
        return abort(500, message="No file selected")


def send_mail(email, random_number):
    msg_title = "poruka"
    sender="library@gmail.com"
    msg = Message(msg_title, sender=sender, recipients=[email])
    msg.body = f"Your verification code is {random_number}"
    current_app.extensions['mail'].send(msg)
    return jsonify(message="Mail sent successfully"), 200


def verify(data):
    user = db.session.execute(db.select(models.UserModel)
                              .where(models.UserModel.email == data["email"])).scalar_one_or_none()
    if not user:
        abort(400, message="User not found.")
    if user.verified_at == data["code"]:
        user.verified_at = str(datetime.utcnow())
        try:
            user.save_to_db()
        except Exception as e:
            abort(500, message=str(e))
        return jsonify(message="User successfully verified"), 200
    else:
        return jsonify(message="Invalid code"), 400
