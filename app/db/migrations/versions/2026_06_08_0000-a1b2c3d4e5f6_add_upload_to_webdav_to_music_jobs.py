"""add upload_to_webdav to music_jobs

Revision ID: a1b2c3d4e5f6
Revises: 1ade30013c25
Create Date: 2026-06-08 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "1ade30013c25"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "music_jobs",
        sa.Column(
            "upload_to_webdav",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column("music_jobs", "upload_to_webdav", server_default=None)


def downgrade():
    op.drop_column("music_jobs", "upload_to_webdav")
