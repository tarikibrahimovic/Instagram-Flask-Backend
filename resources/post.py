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
    return post_service.upload()


@blp.route('/all-posts', methods=['GET'])
@blp.response(200, 'Success')
@jwt_required()
def all_posts():
    return post_service.get_all_posts()


@blp.route('/user-posts/<int:uid>', methods=['Get'])
@blp.response(200, 'Success')
@jwt_required()
def user_posts(uid):
    return post_service.get_user_posts(uid)


@blp.route('/following-posts', methods=['GET'])
@blp.response(200, 'Success')
@jwt_required()
def following_posts():
    return post_service.get_following_posts()
