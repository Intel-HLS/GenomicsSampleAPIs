"""create reference table

Revision ID: 3c9c82e8dc86
Revises: 228ea4c8569d
Create Date: 2015-10-14 14:31:56.963260

"""

# revision identifiers, used by Alembic.
revision = '3c9c82e8dc86'
down_revision = '228ea4c8569d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'reference',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('length', sa.BigInteger),
        sa.Column('reference_set_id', sa.BigInteger,
                  sa.ForeignKey('reference_set.id'), nullable=False),
        sa.Column('md5_checksum', sa.String(32)),
        sa.Column('name', sa.Text),
        sa.Column('source_uri', sa.Text),
        sa.Column('is_derived', sa.Boolean),
        sa.Column('source_divergence', sa.Float),
        sa.Column('ncbi_taxon_id', sa.Integer),
        sa.Column('offset', sa.BigInteger)
    )


def downgrade():
    op.drop_table('reference')
