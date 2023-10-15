from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from services import notification_service


blp = Blueprint('Notification', __name__, description='Operations on notifications')


@blp.route('/notifications', methods=['GET'])
class Notifications(MethodView):
    @jwt_required()
    @blp.response(200, 'Success')
    def get(self):
        """Get all notifications"""
        return notification_service.get_user_notifications()

    # @jwt_required()
    # @blp.response(200, 'Success')
    # def post(self):
    #     """Send notifications"""
    #     return notification_service.send_notifications()
