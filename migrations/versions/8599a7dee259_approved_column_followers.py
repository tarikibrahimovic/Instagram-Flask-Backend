"""approved column followers

Revision ID: 8599a7dee259
Revises: 974258bb5114
Create Date: 2023-10-15 23:06:16.884451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8599a7dee259'
down_revision = '974258bb5114'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('followers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('approved', sa.Boolean(), server_default=sa.text('false'), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('followers', schema=None) as batch_op:
        batch_op.drop_column('approved')

    # ### end Alembic commands ###
