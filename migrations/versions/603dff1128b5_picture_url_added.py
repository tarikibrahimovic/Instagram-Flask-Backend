"""picture_url added

Revision ID: 603dff1128b5
Revises: 0ec17c06ff30
Create Date: 2023-09-30 22:33:15.607879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '603dff1128b5'
down_revision = '0ec17c06ff30'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('picture_url', sa.String(length=80), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('picture_url')

    # ### end Alembic commands ###
