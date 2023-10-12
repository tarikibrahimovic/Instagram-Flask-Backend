from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

import models
from flask import jsonify, request
from cloudinary.uploader import upload as cloudinary_upload
from os import abort

from db import db
from schemas import NotificationSchema


def get_notifications():
    user_id = get_jwt_identity().get('user_id')
    # notifications = db.session.execute(
    # db.select(models.NotificationModel).where(or_(models.NotificationModel.post.user_id == user_id,
    #                                           models.NotificationModel.followed_id == user_id
    #                                           ))).scalars().all()
    notifications = db.session.query(models.NotificationModel).options(
        joinedload(models.NotificationModel.post)).filter(
        (models.NotificationModel.post.has(user_id=user_id)) |
        (models.NotificationModel.followed_id == user_id)
    ).all()

    return NotificationSchema.dump({'postId': notifications.post_id if notifications.post_id else None,
                                    'username': notifications.user.username,
                                    'profileImageUrl': notifications.user.profile_image_url,
                                    'timestamp': str(notifications.created_at),
                                    'type': notifications.type,
                                    'uid': notifications.user_id
                                    }, many=True)



def send_notifications():
    user_id = get_jwt_identity()
    return None
