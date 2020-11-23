"""add user_id for productcategorues

Revision ID: 41f5780e496e
Revises: 7484826d5e85
Create Date: 2020-11-20 20:52:02.400213

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "41f5780e496e"
down_revision = "7484826d5e85"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "productcategories", sa.Column("user_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(None, "productcategories", "users", ["user_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "productcategories", type_="foreignkey")
    op.drop_column("productcategories", "user_id")
    # ### end Alembic commands ###
