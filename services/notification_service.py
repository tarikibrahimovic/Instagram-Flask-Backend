from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload

import models
from flask import jsonify, request
from cloudinary.uploader import upload as cloudinary_upload
from os import abort
from services.comment_service import format_date

from db import db


def get_user_notifications():
    user_id = get_jwt_identity()['user_id']

    user_posts_ids = [post.id for post in models.UserModel.query.get(user_id).user_posts]

    notifications = models.NotificationModel.query.filter(
        or_(
            models.NotificationModel.post_id.in_(user_posts_ids),
            models.NotificationModel.followed_id == user_id
        )
    ).all()

    notifications.sort(key=lambda x: x.created_at, reverse=True)

    return jsonify([
        {
            'postId': str(notification.post_id),
            'username': notification.user.username,
            'profileImageUrl': notification.user.picture_url or "",
            'timestamp': str(format_date(notification.created_at)),
            'type': notification.type.value,
            'uid': str(notification.user_id)
        } for notification in notifications]), 200
#
