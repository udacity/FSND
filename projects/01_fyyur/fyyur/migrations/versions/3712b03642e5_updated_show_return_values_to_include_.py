"""Updated Show return values to include starttime venueid artistid

Revision ID: 3712b03642e5
Revises: d867c344990f
Create Date: 2022-02-10 04:35:20.725507

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3712b03642e5'
down_revision = 'd867c344990f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('shows', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('shows', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
