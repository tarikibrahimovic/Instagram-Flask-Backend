from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from services import notification_service


blp = Blueprint('Notification', __name__, description='Operations on notifications')


@blp.route('/notifications', methods=['GET'])
@jwt_required()
@blp.response(200, 'Success')
def get_notifications():
    """Get all notifications"""
    return notification_service.get_notifications()