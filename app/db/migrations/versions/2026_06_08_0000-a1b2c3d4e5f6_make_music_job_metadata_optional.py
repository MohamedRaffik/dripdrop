"""make music job metadata optional

Revision ID: a1b2c3d4e5f6
Revises: 1ade30013c25
Create Date: 2026-06-08 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "1ade30013c25"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("music_jobs", "title", existing_type=sa.String(), nullable=True)
    op.alter_column("music_jobs", "artist", existing_type=sa.String(), nullable=True)
    op.alter_column("music_jobs", "album", existing_type=sa.String(), nullable=True)


def downgrade():
    op.alter_column("music_jobs", "album", existing_type=sa.String(), nullable=False)
    op.alter_column("music_jobs", "artist", existing_type=sa.String(), nullable=False)
    op.alter_column("music_jobs", "title", existing_type=sa.String(), nullable=False)
