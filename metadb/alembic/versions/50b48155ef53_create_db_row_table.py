"""create db row table

Revision ID: 50b48155ef53
Revises: 37ec9fe97cbf
Create Date: 2015-10-09 13:21:34.198137

"""

# revision identifiers, used by Alembic.
revision = '50b48155ef53'
down_revision = '37ec9fe97cbf'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.schema import CreateSequence, Sequence


def upgrade():
    op.execute(
        CreateSequence(
            Sequence('db_row_tile_row_id_seq', minvalue=0, start=0, increment=1)
        )
    )
    op.create_table(
        'db_row',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('db_array_id', sa.BigInteger, sa.ForeignKey('db_array.id'), nullable=False),
        sa.Column('tile_row_id', sa.BigInteger, Sequence(
            'db_row_tile_row_id_seq'), nullable=False)
    )


def downgrade():
    op.execute(DropSequence('db_row_tile_row_id_seq'))
    op.drop_table('db_row')
