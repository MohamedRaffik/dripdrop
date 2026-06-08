"""add cookies

Revision ID: a1b2c3d4e5f6
Revises: 1ade30013c25
Create Date: 2026-06-04 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "1ade30013c25"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cookies",
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("cookies", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["email"],
            ["users.email"],
            name="cookies_email_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("email"),
    )


def downgrade():
    op.drop_table("cookies")
