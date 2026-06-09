"""rename cookies column to content

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-09 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE cookies RENAME COLUMN cookies TO content")


def downgrade():
    op.execute("ALTER TABLE cookies RENAME COLUMN content TO cookies")
