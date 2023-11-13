import json

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

import models
from db import db
from os import abort
from sqlalchemy import union

from services.post_service import get_socket


def send_message(data):
    user_id = get_jwt_identity().get('user_id')
    message = data.get('message')
    receiver_id = data.get('receiver_id')

    if user_id == receiver_id:
        abort(400, 'You cannot send message to yourself')
    user = db.session.execute(db.select(models.UserModel).where(models.UserModel.id == user_id)).scalar_one_or_none()
    receiver = db.session.execute(
        db.select(models.UserModel).where(models.UserModel.id == receiver_id)).scalar_one_or_none()
    if not user or not receiver:
        abort(400, 'User not found')
    message = models.MessagesModel(sender_id=user_id, message=message, receiver_id=receiver_id)
    message.save_to_db()
    socket = get_socket(receiver_id)
    if socket is not None:
        print(f"Salje se useru {receiver_id}, sa socketom {socket}")
        data = {
            "message": message.message,
            "receiver_id": str(message.receiver_id),
            "sender_id": str(message.sender_id),
            "timestamp": str(format_message_time(message.created_at)),
        }
        socket.send(json.dumps(data))
    return jsonify({
        "message": message.message,
        "receiver_id": str(message.receiver_id),
        "sender_id": str(message.sender_id),
        "timestamp": str(format_message_time(message.created_at)),
    })


def get_messages(receiver_id):
    user_id = get_jwt_identity().get('user_id')
    user = db.session.query(models.UserModel).filter_by(id=user_id).first()
    if not user:
        abort(400, 'User not found')

    all_messages_from_user = db.session.query(models.MessagesModel).filter_by(sender_id=user_id,
                                                                              receiver_id=receiver_id).all()
    all_messages_to_user = db.session.query(models.MessagesModel).filter_by(sender_id=receiver_id,
                                                                            receiver_id=user_id).all()

    all_messages = all_messages_from_user + all_messages_to_user
    all_messages.sort(key=lambda x: x.created_at)
    return jsonify([{
        "message": message.message,
        "receiver_id": str(message.receiver_id),
        "sender_id": str(message.sender_id),
        "timestamp": str(format_message_time(message.created_at)),
    } for message in all_messages])


def get_chats():
    user_id = get_jwt_identity().get('user_id')
    user = db.session.query(models.UserModel).filter_by(id=user_id).first()
    if not user:
        abort(400, 'User not found')

    sent_messages = db.session.query(models.MessagesModel.receiver_id).filter(models.MessagesModel.sender_id == user_id)
    received_messages = db.session.query(models.MessagesModel.sender_id).filter(
        models.MessagesModel.receiver_id == user_id)

    all_message_partners = union(sent_messages, received_messages)

    users = db.session.query(models.UserModel).filter(models.UserModel.id.in_(all_message_partners)).all()

    return jsonify([{
        "username": user.username,
        "profileImageUrl": user.picture_url or "",
        "uid": str(user.id),
        "userBio": str(user.user_bio if len(user.user_bio or "") <= 25 else user.user_bio[:25] + "..."),
    } for user in users])


def get_chat(user_id):
    user = db.session.execute(db.select(models.UserModel).where(models.UserModel.id == user_id)).scalar_one_or_none()
    if not user:
        abort(400, 'User not found')

    return jsonify({
        "username": user.username,
        "profileImageUrl": user.picture_url or "",
        "uid": str(user.id),
        "userBio": str(user.user_bio if len(user.user_bio or "") <= 25 else user.user_bio[:25] + "..."),
    })


def format_message_time(timestamp):
    return timestamp.strftime("%H:%M")


