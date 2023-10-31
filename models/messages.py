from db import db, BaseModelMixin, FunctionBaseMixin


class MessagesModel(db.Model, BaseModelMixin, FunctionBaseMixin):
    __tablename__ = 'messages'
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(80), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    sender = db.relationship('UserModel', backref=db.backref('sent_messages', lazy=True), cascade="all, delete",
                             foreign_keys=[sender_id])
    receiver = db.relationship('UserModel', backref=db.backref('received_messages', lazy=True), cascade="all, delete",
                               foreign_keys=[receiver_id])

    def __init__(self, sender_id, message, receiver_id):
        self.sender_id = sender_id
        self.message = message
        self.receiver_id = receiver_id

    def __repr__(self):
        return f'{self.id}, {self.sender_id}, {self.message}, {self.receiver_id}'

    def save_to_db(self):
        super().save_to_db()

    def delete_from_db(self):
        super().delete_from_db()