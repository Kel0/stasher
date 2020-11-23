"""add gmailletters

Revision ID: 39a75221d3ad
Revises: 042c1cee347c
Create Date: 2020-11-21 23:12:38.829434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39a75221d3ad'
down_revision = '042c1cee347c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gmailletters',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('history_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('gmailletters')
    # ### end Alembic commands ###
