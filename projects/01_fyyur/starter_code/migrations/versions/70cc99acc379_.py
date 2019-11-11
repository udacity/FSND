"""empty message

Revision ID: 70cc99acc379
Revises: f23e16a57179
Create Date: 2019-11-10 15:41:59.593733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70cc99acc379'
down_revision = 'f23e16a57179'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('website', sa.String(length=120), nullable=True))
    op.drop_column('venues', 'website_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('website_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('venues', 'website')
    # ### end Alembic commands ###
