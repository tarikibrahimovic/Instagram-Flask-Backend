from flask_jwt_extended import get_jwt_identity

import models
from flask import jsonify
from os import abort

from db import db


def get_comments(post_id):
    """Get all comments for a post"""
    post = db.session.execute(db.select(models.PostModel).where(models.PostModel.id == post_id)).scalar()
    if not post:
        abort(404, message="Post not found")
    return jsonify([{
        "commentId": comment.id,
        "comment": comment.comment,
        "ownerUid": comment.user.id,
        "ownerUsername": comment.user.username,
        "ownerImageUrl": comment.user.picture_url,
        "timestamp": comment.created_at
    } for comment in post.comments]), 200


def create_comment(data):
    """Create a comment for a post"""
    user_id = get_jwt_identity()['user_id']
    post = db.session.execute(db.select(models.PostModel).where(models.PostModel.id == data['post_id'])).scalar()
    if not post:
        abort(404, message="Post not found")
    comment = models.CommentModel(user_id=user_id, post_id=data['post_id'], comment=data['comment'])
    comment.save_to_db()
    return jsonify({
        "id": comment.id,
        "comment": comment.comment,
        "uid": comment.user_id,
        "postOwnerUid": post.user_id,
        "username": comment.user.username,
        "profileImageUrl": comment.user.picture_url,
        "timestamp": comment.created_at
    }), 201
