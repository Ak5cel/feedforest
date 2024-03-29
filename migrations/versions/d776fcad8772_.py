"""empty message

Revision ID: d776fcad8772
Revises: 898324c7fe3d
Create Date: 2020-07-07 21:52:00.155638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd776fcad8772'
down_revision = '898324c7fe3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('topic',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('topic_name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('topic_name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('rss_feed',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rss_link', sa.Text(), nullable=False),
    sa.Column('site_name', sa.String(length=30), nullable=False),
    sa.Column('site_url', sa.Text(), nullable=False),
    sa.Column('topic_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('rss_link'),
    sa.UniqueConstraint('site_url')
    )
    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('link', sa.Text(), nullable=False),
    sa.Column('topic_id', sa.Integer(), nullable=False),
    sa.Column('rssfeed_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['rssfeed_id'], ['rss_feed.id'], ),
    sa.ForeignKeyConstraint(['topic_id'], ['topic.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('link')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('article')
    op.drop_table('rss_feed')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('topic')
    # ### end Alembic commands ###
