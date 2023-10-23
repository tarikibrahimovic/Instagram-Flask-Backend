from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from schemas import UserSchema, LoginScheme, VerifySchema, LoginUserSchema, ForgotPasswordRequestSchema, \
    ForgotPasswordSchema
from flask import jsonify
from functools import wraps
from services import user_service

blp = Blueprint('Users', __name__, description='Operations on users')


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            user_role = current_user.get('role')
            if user_role in allowed_roles:
                return fn(*args, **kwargs)
            else:
                return jsonify({"message": "Unauthorized"}), 403

        return wrapper

    return decorator


@blp.route('/register')
class User(MethodView):
    @blp.response(200, UserSchema)
    # @blp.arguments(UserSchema)
    def post(self):
        return user_service.register()


@blp.route("/login")
class Login(MethodView):
    @blp.response(200, LoginScheme)
    @blp.arguments(LoginUserSchema)
    def post(self, data):
        return user_service.login(data)


@blp.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def modify_token():
    return user_service.logout()


@blp.route('/change_password', methods=['POST'])
@jwt_required(fresh=True)
def change_password():
    return user_service.change_password()


@blp.route('/verify', methods=['POST'])
@blp.arguments(VerifySchema)
def verify(data):
    return user_service.verify(data)


@blp.route('/sendMail', methods=['POST'])
@blp.arguments(ForgotPasswordRequestSchema)
def send_mail(data):
    return user_service.forgot_mail(data)


@blp.route('/resetPassword', methods=['POST'])
@blp.arguments(ForgotPasswordSchema)
def reset_password(data):
    return user_service.reset_password(data)


@blp.route('/getUsers', methods=['GET'])
@blp.response(200, UserSchema(many=True))
def get_users():
    return user_service.get_users()


@blp.route('/getUser/<int:user_id>', methods=['GET'])
@blp.response(200, LoginScheme)
def get_user(user_id):
    return user_service.get_user(user_id)


@blp.route('/getUserStats/<int:user_id>', methods=['GET'])
@blp.response(200, UserSchema)
def get_user_stats(user_id):
    return user_service.get_user_stats(user_id)