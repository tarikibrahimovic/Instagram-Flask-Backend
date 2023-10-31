from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from flask import jsonify

from schemas import SendMessageSchema
from services import messages_service

blp = Blueprint('Messages', __name__, description='Operations on messages')


@blp.route('/send-message', methods=['POST'])
@jwt_required()
@blp.arguments(SendMessageSchema)
def send_message(data):
    return messages_service.send_message(data)


@blp.route('/get-messages/<int:receiver_id>', methods=['GET'])
@jwt_required()
def get_messages(receiver_id):
    return messages_service.get_messages(receiver_id)


@blp.route('/get-chats', methods=['GET'])
@jwt_required()
def get_conversations():
    return messages_service.get_chats()


@blp.route('/get-chat/<int:receiver_id>', methods=['GET'])
@jwt_required()
def get_chat(receiver_id):
    return messages_service.get_chat(receiver_id)
