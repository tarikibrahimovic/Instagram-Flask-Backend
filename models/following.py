from db import db, BaseModelMixin, FunctionBaseMixin


class FollowingModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    __tablename__ = 'followers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('UserModel', foreign_keys=[user_id], backref=db.backref('followers'), lazy=True, cascade="all, delete")
    following_user = db.relationship('UserModel', foreign_keys=[following_id], backref=db.backref('followers'), lazy=True, cascade="all, delete")

    def __init__(self, user_id, following_id):
        self.user_id = user_id
        self.following_id = following_id

    def __repr__(self):
        return f'{self.id}, {self.user_id}, {self.following_id}'

    def save_to_db(self):
        super().save_to_db()

    def delete_from_db(self):
        super().delete_from_db()