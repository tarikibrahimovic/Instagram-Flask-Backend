from db import db, BaseModelMixin, FunctionBaseMixin


class ImagesModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    __tablename__ = 'images'
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    image_url = db.Column(db.String(300), nullable=True)

    post = db.relationship('PostModel', backref=db.backref('images', lazy=True), cascade="all, delete")

    def __init__(self, post_id, image_url):
        self.post_id = post_id
        self.image_url = image_url
