from db import db, BaseModelMixin, FunctionBaseMixin
from enums import NotificationType


class NotificationModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    __tablename__ = 'notifications'
    type = db.Column(db.Enum(NotificationType), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    post = db.relationship('PostModel', back_populates='notifications', lazy=False)
    user = db.relationship('UserModel', backref='user_notifications', foreign_keys=[user_id])
    followed_user = db.relationship('UserModel', backref='followed_notifications', foreign_keys=[followed_id])

    def __init__(self, type, user_id, post_id=None, followed_id=None):
        self.type = type
        self.user_id = user_id
        self.post_id = post_id
        self.followed_id = followed_id

    def __repr__(self):
        return f'[{self.id}, {self.type.value}, {self.user_id}, {self.post_id}, {self.followed_id}]'

    def save_to_db(self):
        super().save_to_db()

