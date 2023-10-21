from os import abort

from db import db, BaseModelMixin, FunctionBaseMixin
from .role import RoleModel
from enums import RoleNames
from passlib.hash import pbkdf2_sha256


class UserModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    __tablename__ = 'users'
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    verified_at = db.Column(db.String(80), nullable=True)
    picture_url = db.Column(db.String(300), nullable=True)
    fullName = db.Column(db.String(80), nullable=True)
    forgot_password_token = db.Column(db.String(300), nullable=True)

    role = db.relationship('RoleModel', backref=db.backref('users', lazy=True), cascade="all, delete")
    user_posts = db.relationship('PostModel', backref=db.backref('users', lazy=True), cascade="all, delete")
    user_comments = db.relationship('CommentModel', backref=db.backref('users', lazy=True), cascade="all, delete")
    # user_likes = db.relationship('LikeModel', backref=db.backref('users', lazy=True), cascade="all, delete")
    # notifications = db.relationship('NotificationModel', backref=db.backref('users', lazy=True), cascade="all, delete")

    def save_to_db(self):
        super().save_to_db()

    def delete_from_db(self):
        super().delete_from_db()

    def seed_admin(self):
        admin_role = db.session.execute(db.select(RoleModel).
                                        where(RoleModel.name == RoleNames.ADMIN)).scalar_one_or_none()

        if not admin_role:
            abort(404, message="Admin role not found.")

        if not db.session.execute(db.select(UserModel).where(UserModel.username == "admin")).scalar_one_or_none():
            admin = UserModel(
                username="admin",
                password=pbkdf2_sha256.hash("admin"),
                email="admin@gmail.com",
                role_id=admin_role.id,
                fullName="admin",
            )
            try:
                admin.save_to_db()
            except Exception as e:
                abort(500, message=str(e))
