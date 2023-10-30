import json

from flask_jwt_extended import get_jwt_identity
from sqlalchemy import and_, select, join

import models
from flask import jsonify, request
from cloudinary.uploader import upload as cloudinary_upload
from os import abort

from db import db
from enums import NotificationType
from events import user_sockets
from services.comment_service import format_date


def upload():
    user_id = get_jwt_identity()['user_id']
    title = request.form.get('caption')
    files = request.files.getlist('file')
    if files is None or len(files) == 0:
        abort(400, message="No files.")
    try:
        post = models.PostModel(user_id=user_id, title=title)
        post.save_to_db()
        for file in files:
            result = cloudinary_upload(file)
            image_url = result['secure_url']
            image = models.ImagesModel(post_id=post.id, image_url=image_url)
            db.session.add(image)
        db.session.commit()
    except Exception as e:
        abort(500, message=str(e))
    return jsonify({"message": "Post created."}), 201


def get_all_posts():
    posts = db.session.execute(
        select(models.PostModel)
        .select_from(
            join(models.PostModel, models.UserModel, models.PostModel.user_id == models.UserModel.id)
        )
        .where(models.UserModel.is_private == False)
        .order_by(models.PostModel.created_at.desc())
    ).scalars().all()

    return jsonify([{
        "ownerUid": post.user.id,
        "ownerUsername": post.user.username,
        "caption": post.title,
        "likes": len(post.likes),
        "postId": str(post.id),
        "imagesUrl": [image.image_url for image in post.images],
        "timestamp": str(format_date(post.created_at)),
        "ownerImageUrl": post.user.picture_url
    } for post in posts]), 200


def get_following_posts():
    user_id = get_jwt_identity()['user_id']
    following_ids = db.session.execute(db.select(models.FollowingModel.following_id)
                                       .where(and_(models.FollowingModel.user_id == user_id,
                                                   models.FollowingModel.approved == True))).scalars().all()
    print(following_ids)
    posts = (db.session.execute(
        db.select(models.PostModel)
        .where(models.PostModel.user_id.in_(following_ids))
        .order_by(models.PostModel.created_at.desc())
    ).scalars().all())
    return jsonify([{
        "ownerUid": post.user.id,
        "ownerUsername": post.user.username,
        "caption": post.title,
        "likes": len(post.likes),
        "imagesUrl": [image.image_url for image in post.images],
        "postId": str(post.id),
        "timestamp": str(format_date(post.created_at)),
        "ownerImageUrl": post.user.picture_url
    } for post in posts]), 200


def get_user_posts(uid):
    user_id = get_jwt_identity()['user_id']
    if user_id != uid:
        following = db.session.execute(db.select(models.FollowingModel)
                                       .where(and_(models.FollowingModel.user_id == user_id,
                                                   models.FollowingModel.following_id == uid,
                                                   models.FollowingModel.approved))).scalar_one_or_none()
        if not following:
            return jsonify([]), 200
        posts = db.session.execute(
            db.select(models.PostModel)
            .where(models.PostModel.user_id == uid)
            .order_by(models.PostModel.created_at.desc())
        ).scalars().all()
    else:
        posts = db.session.execute(
            db.select(models.PostModel)
            .where(models.PostModel.user_id == uid)
            .order_by(models.PostModel.created_at.desc())
        ).scalars().all()

    return jsonify([{
        "ownerUid": post.user.id,
        "ownerUsername": post.user.username,
        "caption": post.title,
        "likes": len(post.likes),
        "postId": str(post.id),
        "imagesUrl": [image.image_url for image in post.images],
        "timestamp": str(format_date(post.created_at)),
        "ownerImageUrl": post.user.picture_url
    } for post in posts]), 200


def like(post_id):
    user_id = get_jwt_identity()['user_id']
    post = db.session.execute(db.select(models.PostModel).where(models.PostModel.id == post_id)).scalar_one_or_none()
    if not post:
        abort(400, message="Post not found.")
    existing_like = (db.session.execute(db.select(models.LikeModel)
                                        .where(models.LikeModel.user_id == user_id,
                                               models.LikeModel.post_id == post_id))
                     .scalar_one_or_none())
    if existing_like:
        db.session.delete(existing_like)

        existing_notification = (db.session.execute(db.select(models.NotificationModel)
                                                    .where(and_(models.NotificationModel.user_id == user_id,
                                                                models.NotificationModel.post_id == post_id,
                                                                models.NotificationModel.type == NotificationType.LIKE)))
                                 .scalar_one_or_none())
        if existing_notification:
            db.session.delete(existing_notification)

        db.session.commit()
        return jsonify({"message": "Unliked."}), 200
    else:
        like = models.LikeModel(user_id=user_id, post_id=post_id)
        db.session.add(like)
        notification = models.NotificationModel(user_id=user_id, post_id=post_id, type=NotificationType.LIKE)
        db.session.add(notification)
        db.session.commit()
        user_socket = get_socket(post.user_id)
        if user_socket is not None:
            data = {
                "postId": str(post.id),
                "username": like.user.username,
                "profileImageUrl": like.user.picture_url or "",
                "timestamp": str(format_date(like.created_at)),
                "type": NotificationType.LIKE.value,
                "uid": str(user_id)
            }

            user_socket.send(json.dumps(data))
        return jsonify({"message": "Liked."}), 201


def get_socket(user_id):
    for user_socket in user_sockets:
        if user_socket["user_id"] == user_id:
            return user_socket["socket"]
    return None


def is_liked(post_id):
    user_id = get_jwt_identity()['user_id']
    post = db.session.execute(db.select(models.PostModel).where(models.PostModel.id == post_id)).scalar_one_or_none()
    if not post:
        abort(400, message="Post not found.")
    existing_like = (db.session.execute(db.select(models.LikeModel)
                                        .where(models.LikeModel.user_id == user_id,
                                               models.LikeModel.post_id == post_id))
                     .scalar_one_or_none())

    if existing_like:
        return jsonify({"didLike": True}), 200
    else:
        return jsonify({"didLike": False}), 200


def get_post(post_id):
    post = db.session.execute(db.select(models.PostModel).where(models.PostModel.id == post_id)).scalar_one_or_none()
    if not post:
        abort(400, message="Post not found.")
    return jsonify({
        "ownerUid": post.user.id,
        "ownerUsername": post.user.username,
        "caption": post.title,
        "likes": len(post.likes),
        "postId": str(post.id),
        "imagesUrl": [image.image_url for image in post.images],
        "timestamp": str(format_date(post.created_at)),
        "ownerImageUrl": post.user.picture_url or ""
    }), 200
