"""create callset table

Revision ID: 166594568ee4
Revises: 143878c87109
Create Date: 2015-10-13 09:22:05.369939

"""

# revision identifiers, used by Alembic.
revision = '166594568ee4'
down_revision = '143878c87109'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, Sequence


def upgrade():
    op.execute(CreateSequence(Sequence('callset_id_seq', minvalue=0, start=0)))
    op.create_table(
        'callset',
        sa.Column('id', sa.BigInteger, Sequence(
            'callset_id_seq'), primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('individual_id', sa.BigInteger,
                  sa.ForeignKey('individual.id'), nullable=False),
        sa.Column('dbrow_id', sa.BigInteger, sa.ForeignKey(
            'db_row.id'), nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('created', sa.BigInteger, nullable=False),
        sa.Column('updated', sa.BigInteger, nullable=False),
        sa.Column('info', sa.PickleType)
    )


def downgrade():
    op.execute(DropSequence('callset'))
    op.drop_table('callset')
