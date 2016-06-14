"""create field table


Revision ID: 3a0211041fd8
Revises: 43aacdccadc1
Create Date: 2015-10-27 16:02:37.086083

"""

# revision identifiers, used by Alembic.
revision = '3a0211041fd8'
down_revision = '43aacdccadc1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'field',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('field', sa.Text, nullable=False)
    )


def downgrade():
    op.drop_table('field')
