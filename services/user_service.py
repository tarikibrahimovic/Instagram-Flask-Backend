import random
from datetime import datetime, timedelta
from os import abort

from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt

import schemas
from cloudinary.uploader import upload as cloudinary_upload
from models.blocklist import BlockListModel as TokenBlocklist

from db import db
import models
from schemas import UserSchema, LoginScheme
from passlib.hash import pbkdf2_sha256
from flask_smorest import abort
from flask_mail import Message
from flask import current_app


def register():
    file = request.files.get('file')
    email = request.form.get('email')
    username = request.form.get('username')
    fullname = request.form.get('fullName')
    password = request.form.get('password')
    if (db.session.execute(db.select(models.UserModel).where(models.UserModel.username == username))
            .scalar_one_or_none()):
        abort(400, message="Username already exists.")
    random_number = random.randint(100000, 999999)
    user = models.UserModel(
        username=username,
        password=pbkdf2_sha256.hash(password),
        email=email,
        role_id=3,
        fullName=fullname,
        verified_at=str(random_number)
    )
    if file:
        result = cloudinary_upload(file)
        image_url = result['secure_url']
        user.picture_url = image_url
    try:
        user.save_to_db()
        message = f"Your verification code is {random_number}"
        send_mail(email, message, "Verification code")
    except Exception as e:
        abort(500, message=str(e))
    return UserSchema().dump(user), 201


def login(data):
    user = db.session.execute(db.select(models.UserModel)
                              .where(models.UserModel.email == data["email"])).scalar_one_or_none()
    if not user:
        abort(400, message="User not found.")
    if not pbkdf2_sha256.verify(data["password"], user.password):
        abort(400, message="Invalid password.")
    if len(user.verified_at) == 6:
        return LoginScheme().dump({"access_token": "", "refresh_token": "", "email": user.email,
                                   "username": user.username}), 200
    access_token = get_tokens(user)

    return LoginScheme().dump({"access_token": access_token, "email": user.email,
                               "username": user.username, "fullName": user.fullName,
                               "profileImageUrl": user.picture_url, "id": str(user.id), "bio": user.user_bio}), 200


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
    return jsonify(message="Lozinka uspešno promenjena"), 200


def send_mail(email, body, title):
    msg_title = title
    sender="instagram@gmail.com"
    msg = Message(msg_title, sender=sender, recipients=[email])
    msg.body = body
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

        access_token = get_tokens(user)

        return LoginScheme().dump({"access_token": access_token, "email": user.email,
                                   "username": user.username, "fullName": user.fullName,
                                   "profileImageUrl": user.picture_url, "id": str(user.id), "bio": user.user_bio}), 200
    else:
        return jsonify(message="Invalid code"), 400


def get_tokens(user):
    expires = timedelta(days=10)
    access_token = create_access_token(identity={'user_id': user.id, 'role': user.role.name.value},
                                       fresh=True, expires_delta=expires)

    return access_token


def forgot_mail(data):
    user = db.session.execute(db.select(models.UserModel)
                                .where(models.UserModel.email == data["email"])).scalar_one_or_none()
    if not user:
        abort(400, message="User not found.")
    random_number = random.randint(100000, 999999)
    user.forgot_password_token = str(random_number)
    try:
        user.save_to_db()
        send_mail(data["email"], f"Your forgot password code is {random_number}", "Forgot password")
    except Exception as e:
        abort(500, message=str(e))

    return jsonify(email=data["email"]), 200


def reset_password(data):
    user = db.session.execute(db.select(models.UserModel)
                              .where(models.UserModel.email == data["email"])).scalar_one_or_none()
    if not user:
        abort(400, message="User not found.")
    if user.forgot_password_token == data["code"]:
        user.password = pbkdf2_sha256.hash(data["password"])
        user.forgot_password_token = None
        try:
            user.save_to_db()
        except Exception as e:
            abort(500, message=str(e))

        access_token = get_tokens(user)

        return LoginScheme().dump({"access_token": access_token, "email": user.email,
                                   "username": user.username}), 200
    else:
        return jsonify(message="Invalid code"), 400


def get_users():
    return UserSchema(many=True).dump(db.session.execute(db.select(models.UserModel)).scalars().all()), 200


def get_user(user_id):
    user = db.session.execute(db.select(models.UserModel).where(models.UserModel.id == user_id)).scalar_one_or_none()
    if not user:
        abort(400, message="User not found.")
    return LoginScheme().dump({"access_token": "", "email": user.email,
                               "username": user.username, "fullName": user.fullName,
                               "profileImageUrl": user.picture_url, "id": str(user.id)},), 200


def get_user_stats(user_id):
    user = db.session.execute(db.select(models.UserModel).where(models.UserModel.id == user_id)).scalar_one_or_none()
    followers = db.session.execute(db.select(models.FollowingModel).where(models.FollowingModel.following_id == user_id)).scalars().all()
    following = db.session.execute(db.select(models.FollowingModel).where(models.FollowingModel.user_id == user_id)).scalars().all()
    if not user:
        abort(400, message="User not found.")
    return jsonify({
        "followers": len(followers),
        "following": len(following),
        "posts": len(user.posts)
    }), 200


def update_user():
    user_id = get_jwt_identity()['user_id']
    user = db.session.execute(db.select(models.UserModel).where(models.UserModel.id == user_id)).scalar_one_or_none()
    if not user:
        abort(400, message="User not found.")
    file = request.files.get('file')
    username = request.form.get('username')
    fullname = request.form.get('fullName')
    user_bio = request.form.get('userBio')
    print(file)
    if (db.session.execute(db.select(models.UserModel).where(models.UserModel.username == username))
            .scalar_one_or_none()):
        abort(400, message="Username already exists.")
    if file is not None:
        try:
            result = cloudinary_upload(file)
            image_url = result['secure_url']
            user.picture_url = image_url
        except Exception as e:
            abort(500, message=str(e))
    if username:
        user.username = username
    if fullname:
        user.fullName = fullname
    if user_bio:
        user.user_bio = user_bio
    try:
        db.session.commit()
    except Exception as e:
        abort(500, message=str(e))

    return UserSchema().dump(user), 201


def google_login(data):
    user = db.session.execute(db.select(models.UserModel)
                              .where(models.UserModel.email == data["email"])).scalar_one_or_none()
    if not user:
        user = models.UserModel(
            username=data["username"],
            email=data["email"],
            role_id=3,
            fullName=data["fullName"],
            verified_at=str(datetime.utcnow()),
            password=pbkdf2_sha256.hash(data["password"]),
            picture_url=data["imageURL"]
        )
        try:
            user.save_to_db()
        except Exception as e:
            abort(500, message=str(e))

    access_token = get_tokens(user)

    return LoginScheme().dump({"access_token": access_token, "email": user.email,
                               "username": user.username, "fullName": user.fullName,
                               "profileImageUrl": user.picture_url, "id": str(user.id), "bio": user.user_bio}), 200
