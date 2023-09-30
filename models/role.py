from db import db, BaseModelMixin
from sqlalchemy import Enum
from enums import RoleNames


class RoleModel(db.Model, BaseModelMixin):
    __tablename__ = 'roles'
    name = db.Column(Enum(RoleNames), unique=True, nullable=False)

    @staticmethod
    def seed_roles():
        # Define your roles
        roles = [RoleNames.ADMIN, RoleNames.LIBRARIAN, RoleNames.USER]

        # Check if roles already exist in the database
        existing_roles = db.session.execute(db.select(RoleModel)).scalars()
        existing_role_names = [role.name for role in existing_roles]

        for role in roles:
            if role not in existing_role_names:
                new_role = RoleModel(name=role)
                db.session.add(new_role)

        db.session.commit()
