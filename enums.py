from enum import Enum as PyEnum


class RoleNames(PyEnum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    USER = "user"


class NotificationType(PyEnum):
    LIKE = 1
    FOLLOW = 2
    COMMENT = 3
    APPROVE = 0
