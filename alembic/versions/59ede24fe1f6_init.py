"""init

Revision ID: 59ede24fe1f6
Revises: 
Create Date: 2020-11-20 17:11:32.774384

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "59ede24fe1f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "linkcategories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
    )
    op.create_table(
        "productcategories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
    )
    op.create_table(
        "banks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
    )
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("link", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["linkcategories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["productcategories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("products")
    op.drop_table("links")
    op.drop_table("banks")
    op.drop_table("users")
    op.drop_table("productcategories")
    op.drop_table("linkcategories")
    # ### end Alembic commands ###