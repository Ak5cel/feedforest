"""Add user_article_map table

Revision ID: 68bb12a77ebc
Revises: 705e3849f60f
Create Date: 2020-07-13 01:08:11.301806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68bb12a77ebc'
down_revision = '705e3849f60f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_article_map',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'article_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_article_map')
    # ### end Alembic commands ###
