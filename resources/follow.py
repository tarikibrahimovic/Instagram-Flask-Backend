from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from flask import jsonify
from functools import wraps
from services import follow_service


blp = Blueprint('Follow', __name__, description='Operations on followers')


@blp.route('/follow/<int:followed_id>', methods=['POST'])
@jwt_required()
def follow(followed_id):
    return follow_service.follow(followed_id)


@blp.route('/check-following/<int:followed_id>', methods=['GET'])
@jwt_required()
def check_following(followed_id):
    return follow_service.check_following(followed_id)


@blp.route('/approve/<int:following_id>', methods=['POST'])
@jwt_required()
def approve(following_id):
    return follow_service.approve(following_id)
