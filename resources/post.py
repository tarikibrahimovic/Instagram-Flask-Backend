from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from flask import jsonify
from functools import wraps
from services import post_service


blp = Blueprint('Post', __name__, description='Operations on posts')


@blp.route('/post', methods=['POST'])
@jwt_required()
def post():
    return post_service.post()
