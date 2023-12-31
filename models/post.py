from db import db, BaseModelMixin, FunctionBaseMixin


class PostModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    __tablename__ = 'posts'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(80), nullable=False)

    likes = db.relationship('LikeModel', backref=db.backref('posts', lazy=True), cascade="all, delete")
    user = db.relationship('UserModel', backref=db.backref('posts', lazy=True), cascade="all, delete")
    post_comments = db.relationship('CommentModel', backref=db.backref('posts', lazy=True), cascade="all, delete")
    notifications = db.relationship('NotificationModel', backref=db.backref('posts', lazy=True), cascade="all, delete")
    post = db.relationship('ImagesModel', backref=db.backref('posts', lazy=True), cascade="all, delete")

    def __init__(self, user_id, title):
        self.user_id = user_id
        self.title = title

    def __repr__(self):
        return f'{self.id}, {self.user_id}, {self.title}'

    def save_to_db(self):
        super().save_to_db()

    def delete_from_db(self):
        super().delete_from_db()