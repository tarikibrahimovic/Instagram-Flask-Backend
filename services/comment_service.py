from flask_jwt_extended import get_jwt_identity

import models
from flask import jsonify
from os import abort

from db import db
from enums import NotificationType
from events import user_sockets


def get_comments(post_id):
    """Get all comments for a post"""
    post = db.session.execute(db.select(models.PostModel).where(models.PostModel.id == post_id)).scalar()
    if not post:
        abort(404, message="Post not found")
    return jsonify([{
        "commentText": comment.comment,
        "uid": str(comment.user_id),
        "postOwnerUid": str(post.user_id),
        "username": comment.user.username,
        "profileImageUrl": comment.user.picture_url,
        "timestamp": str(comment.created_at)
    } for comment in post.comments])


def create_comment(data):
    """Create a comment for a post"""
    user_id = get_jwt_identity()['user_id']
    post = db.session.execute(db.select(models.PostModel).where(models.PostModel.id == data['post_id'])).scalar()
    if not post:
        abort(404, message="Post not found")
    comment = models.CommentModel(user_id=user_id, post_id=data['post_id'], comment=data['comment'])
    notification = models.NotificationModel(user_id=user_id, post_id=data['post_id'], type=NotificationType.COMMENT)
    try:
        db.session.add(comment)
        db.session.add(notification)
        db.session.commit()
        user_socket = user_sockets.get(post.user_id)
        if user_socket:
            user_socket.emit('comment', {
                "commentText": comment.comment,
                "uid": str(comment.user_id),
                "postOwnerUid": str(post.user_id),
                "username": comment.user.username,
                "profileImageUrl": comment.user.picture_url,
                "timestamp": str(comment.created_at)
            })
    except Exception as e:
        abort(500, message=str(e))
    return jsonify({
        "commentText": comment.comment,
        "uid": str(comment.user_id),
        "postOwnerUid": str(post.user_id),
        "username": comment.user.username,
        "profileImageUrl": comment.user.picture_url,
        "timestamp": str(comment.created_at)
    }), 201
