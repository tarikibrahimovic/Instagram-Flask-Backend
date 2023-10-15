from flask_jwt_extended import get_jwt_identity

import models
from db import db
from os import abort
from sqlalchemy import and_

from enums import NotificationType
from schemas import CheckFollowingSchema


def follow(followed_id):
    user_id = get_jwt_identity()['user_id']
    if user_id == followed_id:
        abort(400, message="You can't follow yourself.")
    existing_following = (db.session.execute(db.select(models.FollowingModel)
                                             .where(and_(models.FollowingModel.user_id == user_id,
                                                         models.FollowingModel.following_id == followed_id)))
                          .scalar_one_or_none())
    if existing_following:
        db.session.delete(existing_following)

        # existing_notification = (db.session.execute(db.select(models.NotificationModel)
        #                                             .where(and_(models.NotificationModel.user_id == user_id,
        #                                                         models.NotificationModel.followed_id == followed_id,
        #                                                         models.NotificationModel.type == NotificationType.FOLLOW)))
        #                          .scalar_one_or_none())
        # if existing_notification:
        #     db.session.delete(existing_notification)
        db.session.commit()
        return {"message": "Unfollowed."}, 200
    else:
        following = models.FollowingModel(user_id=user_id, following_id=followed_id)
        notification = models.NotificationModel(user_id=user_id, followed_id=followed_id, type=NotificationType.FOLLOW)
        db.session.add(notification)
        db.session.add(following)
        db.session.commit()
        return {"message": "Followed."}, 201


def check_following(following_id):
    user_id = get_jwt_identity()['user_id']
    if user_id == following_id:
        abort(400, message="You can't follow yourself.")
    existing_following = (db.session.execute(db.select(models.FollowingModel)
                                             .where(and_(models.FollowingModel.user_id == user_id,
                                                         models.FollowingModel.following_id == following_id)))
                          .scalar_one_or_none())
    if existing_following:
        return CheckFollowingSchema().dump({"is_following": True}), 200
    else:
        return CheckFollowingSchema().dump({"is_following": False}), 200


def approve(following_id):
    user_id = get_jwt_identity()['user_id']
    existing_following = (db.session.execute(db.select(models.FollowingModel)
                                             .where(and_(models.FollowingModel.user_id == following_id,
                                                         models.FollowingModel.following_id == user_id)))
                          .scalar_one_or_none())
    if existing_following:
        existing_following.approved = True
        db.session.commit()
        return {"message": "Approved."}, 200
    else:
        abort(400, message="You can't approve yourself.")
