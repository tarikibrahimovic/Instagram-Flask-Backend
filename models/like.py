from db import db, BaseModelMixin, FunctionBaseMixin


class LikeModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, post_id, user_id):
        self.post_id = post_id
        self.user_id = user_id

    def __repr__(self):
        return f'{self.id}, {self.post_id}, {self.user_id}'

    def save_to_db(self):
        super().save_to_db()

    def delete_from_db(self):
        super().delete_from_db()