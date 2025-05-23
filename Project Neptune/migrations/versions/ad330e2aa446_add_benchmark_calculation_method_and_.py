"""Add benchmark calculation method and period fields

Revision ID: ad330e2aa446
Revises: b46dbced3e2d
Create Date: 2025-05-16 22:49:06.512850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad330e2aa446'
down_revision = 'b46dbced3e2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('kpi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('benchmark_calculation_method', sa.String(length=20), nullable=False, server_default='manual'))
        batch_op.add_column(sa.Column('benchmark_average_period', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('kpi', schema=None) as batch_op:
        batch_op.drop_column('benchmark_average_period')
        batch_op.drop_column('benchmark_calculation_method')

    # ### end Alembic commands ###
