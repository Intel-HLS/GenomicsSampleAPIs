"""create reference_set table

Revision ID: 4db88f2382fb
Revises:
Create Date: 2015-10-08 15:26:18.899851

"""

# revision identifiers, used by Alembic.
revision = '4db88f2382fb'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
            'reference_set',
            sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('md5_checksum', sa.String(32)),
            sa.Column('description', sa.Text),
            sa.Column('source_uri', sa.Text),
            sa.Column('is_derived', sa.Boolean),
            sa.Column('ncbi_taxon_id', sa.Integer),
            sa.Column('assembly_id', sa.String(100)),
        sa.Column('offset_factor', sa.Float)
    )

def downgrade():
    op.drop_table('reference_set')
