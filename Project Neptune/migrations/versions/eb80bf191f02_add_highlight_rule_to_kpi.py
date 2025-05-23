"""Add highlight_rule to KPI

Revision ID: eb80bf191f02
Revises: d5740585ad93
Create Date: 2025-05-13 18:27:50.059983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb80bf191f02'
down_revision = 'd5740585ad93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('kpi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('highlight_rule', sa.String(length=10), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('kpi', schema=None) as batch_op:
        batch_op.drop_column('highlight_rule')

    # ### end Alembic commands ###
