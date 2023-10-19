from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
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


@blp.route('/like/<int:post_id>', methods=['POST'])
@jwt_required()
def like(post_id):
    return post_service.like(post_id)


@blp.route('/is-liked/<int:post_id>', methods=['GET'])
@jwt_required()
def is_liked(post_id):
    return post_service.is_liked(post_id)


@blp.route('/get-post/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    return post_service.get_post(post_id)
