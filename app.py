from flask import Flask, jsonify
from flask_smorest import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sock import Sock

import models
import cloudinary
from models.blocklist import BlockListModel as TokenBlocklist
from resources.user import blp as user_blp
from resources.follow import blp as follow_blp
from resources.post import blp as post_blp
from resources.comment import blp as comment_blp
from resources.notification import blp as notification_blp
from events import user_sockets

from dotenv import load_dotenv
import os
from db import db


mail = Mail()
jwt = JWTManager()
migrate = Migrate()
sock = Sock()


def create_app():
    app = Flask(__name__)
    load_dotenv()

    # Set up the database connection.
    database_url = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # silence the deprecation warning

    db.init_app(app)

    # IF YOU WANT TO ADD A MIGRATION INVOLVING ROLES OR USERS PLEASE FIRST COMMENT OUT THE FOLLOWING THREE LINES
    with app.app_context():
        models.RoleModel.seed_roles()
        models.UserModel().seed_admin()

    app.config['API_TITLE'] = os.getenv('API_TITLE')
    app.config['API_VERSION'] = os.getenv('API_VERSION')
    app.config['OPENAPI_VERSION'] = '3.0.2'
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = True

    api = Api(app)
    mail.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    sock.init_app(app)

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token is not fresh"}), 401

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        blocked_tokens = {token.jti for token in TokenBlocklist.get_all()}
        if blocked_tokens:
            return jwt_payload["jti"] in blocked_tokens

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has been revoked"}), 401
        # this is the message that will be sent to the user if the token is in the blocklist

    @jwt.expired_token_loader
    def expire_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"message": "Request does not contain an access token"}), 401

    api.register_blueprint(follow_blp)
    api.register_blueprint(user_blp)
    api.register_blueprint(post_blp)
    api.register_blueprint(comment_blp)
    api.register_blueprint(notification_blp)

    return app


if __name__ == "__main__":
    app = create_app()
    # app.run(debug=True)


@sock.route('/echo/<int:user_id>')
def echo(sock, user_id):
    while True:
        print(user_id)
        user_sockets.append({"user_id": user_id, "socket": sock})
        print(user_sockets)
        data = sock.receive()
        sock.send("message received")


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
