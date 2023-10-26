from db import db, BaseModelMixin, FunctionBaseMixin
from sqlalchemy import text


class FollowingModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    __tablename__ = 'followers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved = db.Column(db.Boolean, default=False, server_default=text("false"), nullable=False)

    user = db.relationship('UserModel', backref='user_followers', foreign_keys=[user_id])
    following = db.relationship('UserModel', backref='following_users', foreign_keys=[following_id])

    def __init__(self, user_id, following_id, approved=False):
        self.user_id = user_id
        self.following_id = following_id
        self.approved = approved

    def __repr__(self):
        return f'{self.id}, {self.user_id}, {self.following_id}'

    def save_to_db(self):
        super().save_to_db()

    def delete_from_db(self):
        super().delete_from_db()