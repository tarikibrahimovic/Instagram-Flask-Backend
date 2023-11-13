import json

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

import models
from db import db
from os import abort
from sqlalchemy import and_

from enums import NotificationType
from schemas import CheckFollowingSchema
from services.post_service import get_socket
from services.comment_service import format_date


def follow(followed_id):
    user_id = get_jwt_identity()['user_id']
    if user_id == followed_id:
        abort(400, message="You can't follow yourself.")
    existing_following = (db.session.execute(db.select(models.FollowingModel)
                                             .where(and_(models.FollowingModel.user_id == user_id,
                                                         models.FollowingModel.following_id == followed_id)))
                          .scalar_one_or_none())
    if existing_following:
        notification = (db.session.execute(db.select(models.NotificationModel)
                                             .where(and_(models.NotificationModel.user_id == user_id,
                                                            models.NotificationModel.followed_id == followed_id)))
                            .scalar_one_or_none())
        if notification:
            db.session.delete(notification)
        db.session.delete(existing_following)
        db.session.commit()
        return {"message": "False"}, 200
    else:
        user = (db.session.execute(db.select(models.UserModel).where(models.UserModel.id == followed_id))
                .scalar_one_or_none())
        is_approved = False
        if not user.is_private:
            is_approved = True
        following = models.FollowingModel(user_id=user_id, following_id=followed_id, approved=is_approved)
        notification = models.NotificationModel(
            user_id=user_id, followed_id=followed_id,
            type=is_approved and NotificationType.FOLLOW or NotificationType.APPROVE)

        db.session.add(notification)
        db.session.add(following)
        db.session.commit()
        user_socket = get_socket(followed_id)
        if user_socket is not None:
            data = {
                "uid": str(user_id),
                "username": following.user.username,
                "profileImageUrl": following.user.picture_url or "",
                "timestamp": str(format_date(following.created_at)),
                "type": is_approved and NotificationType.FOLLOW.value or NotificationType.APPROVE.value,
                "postId": None
            }
            user_socket.send(json.dumps(data))
        return {"message": is_approved and str("FOLLOW") or str("APPROVE")}, 201


def check_following(following_id):
    user_id = get_jwt_identity()['user_id']
    if user_id == following_id:
        return CheckFollowingSchema().dump({"is_following": "FOLLOW"}), 200
    existing_following = (db.session.execute(db.select(models.FollowingModel)
                                             .where(and_(models.FollowingModel.user_id == user_id,
                                                         models.FollowingModel.following_id == following_id)))
                          .scalar_one_or_none())
    if existing_following:
        if existing_following.approved:
            return CheckFollowingSchema().dump({"is_following": "FOLLOW"}), 200
        else:
            return CheckFollowingSchema().dump({"is_following": "APPROVE"}), 200
    else:
        return CheckFollowingSchema().dump({"is_following": "False"}), 200


def approve(following_id):
    user_id = get_jwt_identity()['user_id']
    existing_following = (db.session.execute(db.select(models.FollowingModel)
                                             .where(and_(models.FollowingModel.user_id == following_id,
                                                         models.FollowingModel.following_id == user_id)))
                          .scalar_one_or_none())
    if existing_following:
        existing_following.approved = True
        notification = (db.session.execute(db.select(models.NotificationModel)
                                           .where(and_(models.NotificationModel.user_id == following_id,
                                                       models.NotificationModel.followed_id == user_id,
                                                       models.NotificationModel.type == NotificationType.APPROVE)))
                        .scalar_one_or_none())
        notification.type = NotificationType.FOLLOW
        db.session.commit()
        return {"is_approved": True}, 200
    else:
        abort(400, message="You can't approve yourself.")


def get_followers():
    user_id = get_jwt_identity()['user_id']
    followers = db.session.execute(db.select(models.FollowingModel)
                                   .where(models.FollowingModel.following_id == user_id)).scalars().all()
    return jsonify([{
        "id": str(follower.user_id),
        "email": follower.user.email,
        "username": follower.user.username,
        "pictureUrl": follower.user.picture_url or "",
        "isApproved": follower.approved
    } for follower in followers]), 200


def get_following():
    user_id = get_jwt_identity()['user_id']
    following = db.session.execute(db.select(models.FollowingModel)
                                   .where(models.FollowingModel.user_id == user_id)).scalars().all()
    return jsonify([{
        "id": str(following_user.following_id),
        "email": following_user.following.email,
        "username": following_user.following.username,
        "picture_url": following_user.following.picture_url or "",
        "fullName": following_user.following.fullName,
        "isApproved": following_user.approved
    } for following_user in following]), 200
