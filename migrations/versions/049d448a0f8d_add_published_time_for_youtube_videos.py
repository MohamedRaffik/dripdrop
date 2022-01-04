"""add published time for youtube videos

Revision ID: 049d448a0f8d
Revises: 9f43a1bd1b03
Create Date: 2021-12-31 20:57:05.702347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '049d448a0f8d'
down_revision = '9f43a1bd1b03'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('youtube_videos', sa.Column('published_at', sa.TIMESTAMP(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('youtube_videos', 'published_at')
    # ### end Alembic commands ###