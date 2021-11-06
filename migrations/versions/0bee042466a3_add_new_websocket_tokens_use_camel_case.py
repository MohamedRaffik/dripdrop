"""add new websocket tokens, use camel case

Revision ID: 0bee042466a3
Revises: 8dea6b4253bf
Create Date: 2021-11-05 22:53:01.295534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bee042466a3'
down_revision = '8dea6b4253bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('websocket_tokens',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('username', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['username'], ['users.username'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('music_jobs', sa.Column(
        'job_id', sa.String(), nullable=False))
    op.add_column('music_jobs', sa.Column(
        'youtube_url', sa.String(), nullable=True))
    op.add_column('music_jobs', sa.Column(
        'artwork_url', sa.String(), nullable=True))
    op.drop_column('music_jobs', 'artworkURL')
    op.drop_column('music_jobs', 'youtubeURL')
    op.drop_column('music_jobs', 'jobID')
    op.create_primary_key('pk_music_jobs', 'music_jobs', ['job_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('music_jobs', sa.Column(
        'jobID', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('music_jobs', sa.Column(
        'youtubeURL', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('music_jobs', sa.Column(
        'artworkURL', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('music_jobs', 'artwork_url')
    op.drop_column('music_jobs', 'youtube_url')
    op.drop_column('music_jobs', 'job_id')
    op.drop_table('websocket_tokens')
    # ### end Alembic commands ###
