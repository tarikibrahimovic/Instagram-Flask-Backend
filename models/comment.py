from db import db, BaseModelMixin, FunctionBaseMixin


class CommentModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    __tablename__ = 'comments'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    comment = db.Column(db.String(300), nullable=False)

    user = db.relationship('UserModel', backref=db.backref('comments', lazy=True), cascade="all, delete")
    post = db.relationship('PostModel', backref=db.backref('comments', lazy=True), cascade="all, delete")

    def __init__(self, user_id, post_id, comment):
        self.user_id = user_id
        self.post_id = post_id
        self.comment = comment

    def __repr__(self):
        return f'{self.id}, {self.user_id}, {self.post_id}, {self.comment}'

    def save_to_db(self):
        super().save_to_db()

    def delete_from_db(self):
        super().delete_from_db()