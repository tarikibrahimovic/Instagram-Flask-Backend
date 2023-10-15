from flask_jwt_extended import get_jwt_identity
from sqlalchemy import and_

import models
from flask import jsonify, request
from cloudinary.uploader import upload as cloudinary_upload
from os import abort

from db import db
from enums import NotificationType


def upload():
    user_id = get_jwt_identity()['user_id']
    title = request.form.get('caption')
    file = request.files['file']
    if file:
        result = cloudinary_upload(file)
        image_url = result['secure_url']
    try:
        post = models.PostModel(user_id=user_id, title=title, image_url=image_url)
        post.save_to_db()
    except Exception as e:
        abort(500, message=str(e))
    return jsonify({"message": "Post created."}), 201


def get_all_posts():
    posts = db.session.execute(db.select(models.PostModel).order_by(models.PostModel.created_at.desc())).scalars().all()

    return jsonify([{
        "ownerUid": post.user.id,
        "ownerUsername": post.user.username,
        "caption": post.title,
        "likes": len(post.likes),
        "postId": str(post.id),
        "imageUrl": post.image_url,
        "timestamp": post.created_at,
        "ownerImageUrl": post.user.picture_url
    } for post in posts]), 200


def get_following_posts():
    user_id = get_jwt_identity()['user_id']
    following_ids = db.session.execute(db.select(models.FollowingModel.following_id)
                                       .where(models.FollowingModel.user_id == user_id)).scalars().all()
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
        "imageUrl": post.image_url,
        "postId": str(post.id),
        "timestamp": post.created_at,
        "ownerImageUrl": post.user.picture_url
    } for post in posts]), 200


def get_user_posts(uid):
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
        "imageUrl": post.image_url,
        "timestamp": post.created_at,
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
        return jsonify({"message": "Liked."}), 201


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
