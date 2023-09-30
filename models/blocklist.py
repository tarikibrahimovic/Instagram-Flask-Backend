from db import db
from datetime import datetime
from sqlalchemy.sql import func


class BlockListModel(db.Model):
    __tablename__ = 'token_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(16), nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=func.utcnow(),
        nullable=False,
    )

    @staticmethod
    def get_all():
        return db.session.execute(db.select(BlockListModel)).scalars()