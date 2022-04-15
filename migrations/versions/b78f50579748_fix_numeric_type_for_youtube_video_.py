"""fix numeric type for youtube video category

Revision ID: b78f50579748
Revises: 411683133de6
Create Date: 2022-01-03 01:25:44.399174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b78f50579748"
down_revision = "411683133de6"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("youtube_videos_category_id_fkey", "youtube_videos")
    op.alter_column("youtube_videos", "category_id", type_=sa.Integer)
    op.alter_column("youtube_video_categories", "id", type_=sa.Integer)
    op.create_foreign_key(
        None,
        "youtube_videos",
        "youtube_video_categories",
        ["category_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("youtube_videos_category_id_fkey", "youtube_videos")
    op.alter_column("youtube_videos", "category_id", type_=sa.Numeric)
    op.alter_column("youtube_video_categories", "id", type_=sa.Numeric)
    op.create_foreign_key(
        None,
        "youtube_videos",
        "youtube_video_categories",
        ["category_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    pass
    # ### end Alembic commands ###
