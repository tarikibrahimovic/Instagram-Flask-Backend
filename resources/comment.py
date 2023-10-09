from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from schemas import CommentSchema
from services import comment_service


blp = Blueprint('Comment', __name__, description='Operations on comments')


@blp.route('/comments/<int:post_id>', methods=['GET'])
@blp.response(200, 'Success')
@blp.response(404, 'Post not found')
def get_comments( post_id):
    """Get all comments for a post"""
    return comment_service.get_comments(post_id)


@blp.route('/comments', methods=['POST'])
@blp.response(201, 'Comment created')
@blp.response(404, 'Post not found')
@blp.arguments(CommentSchema)
@jwt_required()
def post(data):
    """Create a comment for a post"""
    return comment_service.create_comment(data)



