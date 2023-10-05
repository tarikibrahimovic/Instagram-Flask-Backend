from db import db, BaseModelMixin, FunctionBaseMixin


class PostModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    __tablename__ = 'posts'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(80), nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    likes = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship('UserModel', backref=db.backref('posts', lazy=True), cascade="all, delete")
    post_comments = db.relationship('CommentModel', backref=db.backref('posts', lazy=True), cascade="all, delete")

    def __init__(self, user_id, title, image_url):
        self.user_id = user_id
        self.title = title
        self.image_url = image_url

    def __repr__(self):
        return f'{self.id}, {self.user_id}, {self.title}, {self.image_url}'

    def save_to_db(self):
        super().save_to_db()

    def delete_from_db(self):
        super().delete_from_db()